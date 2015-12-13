import json
import util
import urllib

# SHIFT API Documentation
# http://indiereign.github.io/shift72-docs/

DATA_URL = 'https://ondemand.nzfilm.co.nz/services/meta/v4/featured/8'
FILM_DETAILS_TEMPLATE = "https://ondemand.nzfilm.co.nz/services/meta/v2{0}/show_multiple"
PRICE_TEMPLATE = "https://ondemand.nzfilm.co.nz/services/pricing/v2/prices/show_multiple?items={0}&location=nz"
URI_TEMPLATE = "https://ondemand.nzfilm.co.nz/#!/browse{0}/{1}"
TV_SEASON_TEMPLATE = "https://ondemand.nzfilm.co.nz/services/meta/v2/tv/season/show_multiple?items={0}"

def get_movie(slug):
	# find movie
	data = util.get_url_json(FILM_DETAILS_TEMPLATE.format(slug))[0]
	price_data = util.get_url_json(PRICE_TEMPLATE.format(slug))

	show = {}
	show["title"] = data["title"]
	show["type"] = "movie"
	show["image"] = data["image_urls"]["portrait"]
	show["year"] = data["release_date"][:4]

	# lowest price
	price = ""
	if price_data["prices"]:
		if price_data["prices"][0]["rent"]["hd"]:
			price = price_data["prices"][0]["rent"]["hd"]
		else:
			price = price_data["prices"][0]["buy"]["hd"]

	# every show has an episode even movies
	show["episodes"] = [{"show" : data["title"], "uri" : URI_TEMPLATE.format(slug, urllib.parse.quote_plus(data["title"])), "s" : 0, "e" : 0, "price" : price}]
	return show

def get_tv(slug):
	# find seasons
	data = util.get_url_json(TV_SEASON_TEMPLATE.format(slug))["seasons"][0]
	price_data = util.get_url_json(PRICE_TEMPLATE.format(slug))

	show = {}
	show["title"] = data["show_info"]["title"]
	show["type"] = "tv"
	show["image"] = data["image_urls"]["portrait"]
	show["year"] = data["show_info"]["release_date"][:4]

	# Price is per season. No prices per episode
	# lowest price
	price = ""
	if price_data["prices"]:
		price = price_data["prices"][0]["rent"]["hd"]
	print ("TV Price: " + price)

	show["episodes"] = []
	for e in data["episodes"]:
			episode = {}
			episode["title"] = e["title"]
			episode["uri"] = URI_TEMPLATE.format(slug, urllib.parse.quote_plus(data["show_info"]["title"]))
			episode["s"] = data["season_num"]
			episode["e"] = e["episode_number"]
			episode["price"] = price
			show["episodes"].append(episode)

	return show

def get_listings():
	shows = []
	data = util.get_url_json(DATA_URL)

	all = []
	for slug in data["items"]:
		if "/film/" in slug:
			shows.append(get_movie(slug))
		else:
			shows.append(get_tv(slug))

	return shows

if __name__ == "__main__":
	# Test works
	f = open("nzfilm.js", "w")
	f.write(json.dumps(get_listings()))
	f.close()
