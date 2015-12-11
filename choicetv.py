from datetime import datetime
import pytz
import dateutil.parser
import json
import util
import urllib

# SHIFT API Documentation
# http://indiereign.github.io/shift72-docs/

TV_DATA_URL = "https://www.choicetv.co.nz/services/meta/v3/tv/index"
FILM_DATA_URL = "https://www.choicetv.co.nz/services/meta/v2/film/index"
FILM_DETAILS_TEMPLATE = "https://www.choicetv.co.nz/services/meta/v2{0}/show_multiple"
URI_TEMPLATE = "https://www.choicetv.co.nz/#!/browse{0}/{1}"
TV_SEASON_TEMPLATE = "https://www.choicetv.co.nz/services/meta/v2/tv/season/show_multiple?items={0}"
AVAILABILITIES_URL = "https://www.choicetv.co.nz/services/content/v1/availabilities?items={0}"

def get_movie(slug):
	# find movie
	data = util.get_url_json(FILM_DETAILS_TEMPLATE.format(slug))[0]

	# TODO: Need to check availabilities
	show = {}
	show["title"] = data["title"]
	show["type"] = "movie"
	show["image"] = data["image_urls"]["portrait"]
	show["year"] = data["release_date"][:4]

	# every show has an episode even movies
	show["episodes"] = [{"show" : data["title"], "uri" : URI_TEMPLATE.format(slug, urllib.parse.quote_plus(data["title"])), "s" : 0, "e" : 0}]
	return show

def get_tv(slug):
	show = {}

	# find seasons
	season = util.get_url_json(TV_SEASON_TEMPLATE.format(slug))["seasons"]
	if season:
		availabilities = util.get_url_json(AVAILABILITIES_URL.format(slug))
		data = season[0]

		show["title"] = data["show_info"]["title"]
		show["type"] = "tv"
		show["image"] = data["image_urls"]["portrait"]
		show["year"] = data["show_info"]["release_date"][:4]

		show["episodes"] = []
		for e in data["episodes"]:
			episode_slug = slug + "/episode/" + str(e["episode_number"])

			# Get the availability of the episode
			for a in availabilities:
				if a["slug"] == episode_slug:
					date_from = dateutil.parser.parse(a["from"]).replace(tzinfo=pytz.utc)
					date_to = dateutil.parser.parse(a["to"]).replace(tzinfo=pytz.utc)

			# Only include the episode if it's available now
			if datetime.now(pytz.utc) > date_from:
				if datetime.now(pytz.utc) < date_to:
					episode = {}
					episode["title"] = e["title"]
					episode["uri"] = URI_TEMPLATE.format(slug, urllib.parse.quote_plus(data["show_info"]["title"]))
					episode["s"] = data["season_num"]
					episode["e"] = e["episode_number"]
					show["episodes"].append(episode)

	return show

def get_listings():
	shows = []

	# Get TV listings. Make sure the season is published
	tv_data = util.get_url_json(TV_DATA_URL)
	for show in tv_data:
		for season in show["seasons"]:
			if season["status_id"] == 2:
				print("Season: " + str(season["slug"]))
				shows.append(get_tv(season["slug"]))

	# Get Film listings. Make sure the film is currently published
	film_data = util.get_url_json(FILM_DATA_URL)
	for film in film_data:
		if film["status_id"] == 2:
			published_date = dateutil.parser.parse(film["published_date"]).replace(tzinfo=pytz.utc)
			if datetime.now(pytz.utc) > published_date:
				slug = "/film/" + str(film["id"])
				print("Film: " + slug)
				shows.append(get_movie(slug))

	return shows

if __name__ == "__main__":
	# Test works
	f = open("choicetv.js", "w")
	f.write(json.dumps(get_listings()))
	f.close()
