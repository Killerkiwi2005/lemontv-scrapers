import lxml.html as lh
from urllib.request import urlopen
import json
import re
import urllib
DATA_URL = 'http://videoezyondemand.co.nz/watch-movies?offer=19&p=%s'
# http://videoezyondemand.co.nz/tvseries/episode/product/id/19142
def get_episodes(series_id):
	episodes = []

	# find seasons
	html = GetUrl(SERIES_TEMPLATE % series_id)
	data = re.search(r'APPDATA\.season_data = (.*);', html).group(1) # inline json
	seasons = json.loads(data)

	for season in seasons:
		season_id = season["id"]
		
		print(SEASON_TEMPLATE % (series_id, season_id))
		response = urlopen(SEASON_TEMPLATE % (series_id, season_id));
		 
		data = json.loads(response.read().decode())

		for e in data["episodes"]:
			episode = {}
			print("s" + str(season["season_number"]) + "e" + str(e["episode"]) + " - " + e["titles"]["default"])
			episode["show"] = e["titles"]["default"]
			episode["title"] = e["titles"]["default"]
			episode["uri"] = EPISODE_TEMPLATE % (series_id, season_id, e["id"])
			#episode["date"] = product["productTitle"]
			episode["s"] = season["season_number"]
			episode["e"] = e["episode"]
			#episode["price"] = product["priceCode"] no prices yet
			episodes.append(episode)
	return episodes

def get_listings():
		
	count = 1
	shows = []
	while True:
		response = urlopen(DATA_URL % (limit, limit*count));
		data = json.loads(response.read().decode())

		for series in data["data"]:
			show = {}
			print(series["name"])
			show["title"] = series["name"]
			show["episodes"] = [{uri : series["prodUrl"] , "s" : 0, "e" : 0}]
			show["type"] = "movie"
			show["image"] = series["imageUrl"]
			shows.append(show)

		count = count + 1

		if count > data["totalPages"]:
			break
			
	return shows

if __name__ == "__main__":	
	f = open("videoezy.js", "w")
	f.write(json.dumps(get_listings()))
	f.close()
