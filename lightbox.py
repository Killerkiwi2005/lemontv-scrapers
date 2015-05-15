import json
import util

DATA_URL = 'https://aws-tnz-api-v2.xstream.dk/media/series?limit={0}&offset={1}'
SERIES_TEMPLATE = "https://www.lightbox.co.nz/xstream/media/series/{0}"
SEASON_TEMPLATE = "https://aws-tnz-api-v2.xstream.dk/media/series/{0}/seasons/{1}/episodes?order=asc&sort=episode&limit=30"
EPISODE_TEMPLATE = "https://www.lightbox.co.nz/#/play-video/series/{0}/season/{1}/episode/{2}/media/{2}"

def get_episodes(series_id):
	episodes = []

	# find seasons
	data = util.get_url_json(SERIES_TEMPLATE.format(series_id))

	for season in data["seasons"]:
		season_id = season["id"]
		
		print(SEASON_TEMPLATE.format(series_id, season_id))
		 
		data = util.get_url_json(SEASON_TEMPLATE.format(series_id, season_id))
		
		for e in data["episodes"]:
			episode = {}
			print("s" + str(season["season_number"]) + "e" + str(e["episode"]) + " - " + e["titles"]["default"])
			episode["title"] = e["titles"]["default"]
			episode["uri"] = EPISODE_TEMPLATE.format(series_id, season_id, e["id"])
			episode["s"] = season["season_number"]
			episode["e"] = e["episode"]
			if "year" in e["details"]:
				episode["year"] = e["details"]["year"]
			episodes.append(episode)
	return episodes

def get_listings():
		
	limit = 50 # seems to be the limit
	count = 0
	shows = []
	while True:
	
		data = util.get_url_json(DATA_URL.format(limit, limit*count))

		if len(data["series"]) == 0:
			break

		for series in data["series"]:
			show = {}
			print(series["titles"]["default"])
			show["title"] = series["titles"]["default"]
			show["episodes"] = get_episodes(series["id"])
			show["type"] = "tv"
			
			# note tmdb images are  used on the site, but supply image if available
			if "Web_4_3_tv_thumb" in series["images"][0]["format"]:
				show["image"] = series["images"][0]["format"]["Web_4_3_tv_thumb"]["source"]
			shows.append(show)

		count = count + 1
	return shows

def get_recent():
	shows = []
	data = util.get_url_json("https://www.lightbox.co.nz/xstream/sections/lists/21/elements?limit=10&offset=0")
	
	for series in data["elements"]["series"]:
		show = {}
		print(series["titles"]["default"])
		show["title"] = series["titles"]["default"]
		show["episodes"] = get_episodes(series["id"])
		show["type"] = "tv"
		
		# note tmdb images are  used on the site, but supply image if available
		if "Web_4_3_tv_thumb" in series["images"][0]["format"]:
			show["image"] = series["images"][0]["format"]["Web_4_3_tv_thumb"]["source"]
		shows.append(show)

	return shows
	
	
if __name__ == "__main__":	
	# Test works
	f = open("lightbox.js", "w")
	f.write(json.dumps(get_recent()))
	f.close()
