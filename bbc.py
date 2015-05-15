from urllib.request import urlopen
import json
import re
import util

API_KEY = 'q5wcnsqvnacnhjap7gzts9y6' # This is the android app key
DATA_URL = 'http://ibl.api.bbci.co.uk/ibl/v1/channels/%s/programmes?lang=en&rights=tv&availability=available&api_key=%s&page=%s'
EPISODE_BASE = "http://www.bbc.co.uk/iplayer/episode/%s"
CHANNELS = ["bbc_one_london", "bbc_two_england", "bbc_three", "bbc_four" ,"cbbc", "cbeebies"]

# Programmes on BBC One
# http://ibl.api.bbci.co.uk/ibl/v1/channels?lang=en&api_key=q5wcnsqvnacnhjap7gzts9y6
# http://www.bbc.co.uk/iplayer/episode/[ID]

def get_listings():	
	shows = []
	for channel in CHANNELS:
		page = 0
		data = None
		while page == 0 or (data and len(data) > 0):
			
			page = page + 1

			url = DATA_URL % (channel, API_KEY, page)
			print(url)

			data = util.get_url_json(url)["channel_programmes"]["elements"]

			for show_entry in data:
		
				show_title = show_entry["title"]

				for entry in show_entry["initial_children"]:
				
					episode = {}
					episode["show"] = entry["title"]
					#episode["date"] = entry["release_date"]
					episode["uri"] = EPISODE_BASE % entry["id"]
					episode["s"] = 0
					episode["e"] = 0

					if "subtitle" in entry:

						
						sub_title = entry["subtitle"]
						episode["show"] = sub_title
						#episode["e"] = sub_title

						matches = re.search(r"Series (\d+)\: (\d+)", sub_title)
						if matches:
							episode["s"] = matches.group(1)
							episode["e"] = matches.group(2)

						else:
							matches = re.search(r"Series (\d+)", sub_title)
							if matches:
								episode["s"] = matches.group(1)

							else:
								matches = re.search(r"Episode (\d+)", sub_title)
								if matches:
									episode["s"] = 1
									episode["e"] = matches.group(1)


							matches = re.search(r"Episode (\d+)", sub_title)
							if matches:
								if episode["s"] == 0:
									episode["s"] = 1
								episode["e"] = matches.group(1)
				
							"""if episode["s"] != 0 and episode["e"] == 0:
								title2 = entry.xpath(".//link[contains(@rel, 'self')]")[0].get('title')
								matches = re.search(r"(\d+)", title2)
								if matches:
									episode["e"] = matches.group(1)
									print("Episode b : ", episode["e"])"""



					print (" - ", episode["s"], episode["e"], episode["show"]) 
					print ("   ", episode["uri"]) 

					# Add to parent show
					for x in shows:
						# merge shows
						if x["title"] == show_title:
							x["episodes"] = x["episodes"] + [episode]
							break
					else:
						# new show 
						show = {}
						show["title"] = show_title
						show["episodes"] = [episode]
						show["type"] = "tv"
						show["image"] = show_entry["images"]["standard"].replace("{recipe}","192x108")
						shows.append(show)

	return shows
	
if __name__ == "__main__":
	f = open("bbc.js", "w")
	f.write(json.dumps(get_listings()))
	f.close()
