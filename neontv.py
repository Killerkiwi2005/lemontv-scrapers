import lxml.html as lh
from urllib.request import urlopen
import json
from lxml import etree
import re
DATA_URLS = ["https://www.neontv.co.nz/navajo-ws/rest/feed/74?assetTypes=448x336_4x3_1,1560x880_16x9&numberOfResults=51&offset=%s&sortOrder=programYearDesc",
	   	"https://www.neontv.co.nz/navajo-ws/rest/feed/73?assetTypes=448x336_4x3_1,1560x880_16x9&numberOfResults=51&offset=%s&sortOrder=programYearDesc"]
PLAY_URL = "https://www.neontv.co.nz/watch?assetId=%s"
EPISODE_URL = "https://www.neontv.co.nz/navajo-ws/rest/tvSeasons/%s"

def get_listings():
	shows = []
	for data_url in DATA_URLS:
		offset = 0
		
		while True:
			print (offset)
			url = data_url % offset
			response = urlopen(url);
			all_data = json.loads(response.read().decode())
		
			if len(all_data) == 0:
				break
		
			for data in all_data:
			
				print (data["title"])
				show = {}
				show["title"] = data["title"]
				show["type"] = "movie"
				show["image"] = data["images"]["448x336_4x3_1"]
				show["episodes"] = []
				
				if data["episodesById"]:
				
					# Trim the season from the title
					show["title"] = re.sub(r"\: Season (\d+)", "", show["title"]).strip()
					show["type"] = "tv"
					print (show["title"])
					
					# skip show if already in set
					for x in shows:
						if x["type"] == "tv" and x["title"] == show["title"]:
							break
					else:
					
						# Add episodes
						seasons = json.loads(urlopen(EPISODE_URL % data["assetId"]).read().decode())
						for s in seasons["seasons"]:
							data_s = seasons["seasons"][s]
							season_title = data_s["title"]
							for e in seasons["episodes"][s]:
								
								data_e = seasons["episodes"][s][e]
								print("s", s, "e", e, "\t", data_e["title"])
								episode = {}
								episode["title"] = data_e["title"]
								episode["uri"] = PLAY_URL % data_e["articleId"]
								#episode["date"] = data_s["year"]
								episode["e"] = e
								episode["s"] = s
								show["episodes"].append(episode)
								
						shows.append(show)
				else:
					show["episodes"] = [{"title" :  data["title"], "uri" : PLAY_URL % data["assetId"],  "s" : 0, "e" : 0 }]
					shows.append(show)
				
	
					
				offset = offset + 1
	return shows

if __name__ == "__main__":	
	f = open("neontv.js", "w")
	f.write(json.dumps(get_listings()))
	f.close()
