import json
import util
import urllib

DATA_URL = 'https://ondemand.nzfilm.co.nz/services/meta/v3/featured/show/home_page'
DETAILS_TEMPLATE = "https://ondemand.nzfilm.co.nz/services/meta/v2/{0}/{1}/show_multiple"
PRICE_TEMPLATE = "https://ondemand.nzfilm.co.nz/services/pricing/v2/prices/show_multiple?items=/film/{0}&location=nz"
IMAGE_TEMPLATE = "https://s3-ap-southeast-2.amazonaws.com/s72-client-3-assets/production/posters-and-backdrops/282x422/film-{0}.jpg"
URI_TEMPLATE = "https://ondemand.nzfilm.co.nz/#!/browse/{0}/{1}/{2}"

TV_SEASON_TEMPLATE = "https://ondemand.nzfilm.co.nz/services/meta/v2/tv/season/show_multiple?items={0}"

def get_movie(id):

	# find seasons
	data = util.get_url_json(DETAILS_TEMPLATE.format("film", id))[0]
	price_data = util.get_url_json(PRICE_TEMPLATE.format(id))
	
	show = {}
	show["title"] = data["title"]
	show["type"] = "movie"	
	show["image"] = IMAGE_TEMPLATE.format(id)
	show["year"] = data["release_date"][:4]
	
	# lowest price
	if "sd" in price_data["prices"][0]["rent"]:
		price = price_data["prices"][0]["rent"]["sd"]
	else:
		price = price_data["prices"][0]["rent"]["hd"]
	
	# every show has an episode even movies
	show["episodes"] = [{"show" : data["title"], "uri" : URI_TEMPLATE.format("film", id, urllib.parse.quote_plus(data["title"])), "s" : 0, "e" : 0, "price" : price}]
	return show
	
def get_tv(path):

	# find seasons
	id = path.split('/')[2]
	data = util.get_url_json(DETAILS_TEMPLATE.format("tv", id))[id]
	season_data = util.get_url_json(TV_SEASON_TEMPLATE.format(path))["seasons"][0]
	
	#https://ondemand.nzfilm.co.nz/services/pricing/v2/prices/show_multiple?items=/tv/6/season/1&location=nz
	
	show = {}
	show["title"] = data["title"]
	show["type"] = "tv"	
	#show["image"] = IMAGE_TEMPLATE.format(id)
	show["year"] = data["published_date"][:4]
	
	# lowest price
	#if "sd" in price_data["prices"][0]["rent"]:
	#	price = price_data["prices"][0]["rent"]["sd"]
	#else:
	#	price = price_data["prices"][0]["rent"]["hd"]

	show["episodes"] = []
	for e in season_data["episodes"]:
			episode = {}
			print("s" + str(season_data["season_num"]) + "e" + str(e["episode_number"]) + " - " + e["title"])
			episode["title"] = e["title"]
			episode["uri"] = URI_TEMPLATE.format("tv", id, "season/{0}/{1}".format(season_data["season_num"], urllib.parse.quote_plus(data["title"])))
			episode["s"] = season_data["season_num"]
			episode["e"] = e["episode_number"]
			episode["year"] = e["air_date"][:4]
			show["episodes"].append(episode)
	
	return show	

def get_listings():
	shows = []	
	data = util.get_url_json(DATA_URL)

	all = []
	for feature in data["features"]:
		if "/film/" in feature["item"]:
			shows.append(get_movie(feature["item"].replace("/film/", "")))
		else:
			shows.append(get_tv(feature["item"]))

	return shows

if __name__ == "__main__":	
	# Test works
	f = open("nzfilm.js", "w")
	f.write(json.dumps(get_listings()))
	f.close()
