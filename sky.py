import lxml.html as lh
from urllib.request import urlopen
import json
from lxml import etree
import re
import util
DATA_URL = 'http://www.skygo.co.nz/services/ProductService.svc/GetPagedProducts?section=all&category=all&filterString=latest&rating=all&start=0&tvod=%s&end=1000&productType=all'
EPISODE_TEMPLATE = "http://www.skygo.co.nz/product/%s.aspx"

def get_details(data):
	print (getValue(data, "SeriesNumber"), getValue(data, "EpisodeNumber"), getValue(data, "EpisodeTitle")) 
	episode = {}
	episode["show"] = getValue(data, "EpisodeTitle") 

	episode["uri"] = EPISODE_TEMPLATE % (getValue(data, "productID"))
	#episode["type"] = media.xpath(".//type")[0].text
	episode["date"] = ""
	episode["e"] = getValue(data, "EpisodeNumber")
	episode["s"] = getValue(data, "SeriesNumber")
	if getValue(data["CurrentProductOfferingInfo"], "Price"):
		episode["price"] = getValue(data["CurrentProductOfferingInfo"], "Price")
	return episode

# some of the json keys seem to change case productId / ProductID
def getValue(data, key):
	if hasattr(data, "keys"):
		for k in data.keys():
			if k.lower() == key.lower():
				return data[k]

def get_episodes(product):

	# ignore sports
	if product["scodes"] == "Sport":
		return None, None


	if product["episodeCount"] > 0 or product["seriesNumber"]:
		url = EPISODE_TEMPLATE % (getValue(product, "productID"))
	
		doc = util.get_url_html(url)
		 
		scripts = doc.xpath("//script")
		episodes = []

		for script in scripts:
			key = "isky.bootstrap.episodes = "
			if str(script.text).startswith(key):
				episodes_data = json.loads( str(script.text)[len(key):] )
				if getValue(episodes_data, "productID"):
					episodes.append(get_details(episodes_data ))
				else:
					for data in episodes_data:
						if getValue(data, "productID"):
							episodes.append(get_details(data))
		return episodes, "tv"

	# non tv shows as they have no episodes
	episode = {}
	episode["show"] = product["productTitle"] 
	episode["title"] = product["productTitle"]
	episode["uri"] = EPISODE_TEMPLATE % (getValue(product, "productID"))
	#episode["type"] = media.xpath(".//type")[0].text
	episode["date"] = product["productTitle"]
	episode["s"] = 0
	episode["e"] = 0
	if product["priceCode"]:
		episode["price"] = product["priceCode"]
	return [episode], "movie"


def get_listings(tvod = "false"):	
	url = DATA_URL % tvod
	data = util.get_url_json(url)
	shows = []
	count  = 0
	for product in data["products"]:

		episodes, show_type = get_episodes(product)
		if episodes:
			title = product["productTitle"].replace(" (HD)","").strip()
			title = re.sub( r' Season \d+[a-zA-Z]?\b', '', title ).strip()
			title = re.sub( r' Episode \d+[a-zA-Z]?\b', '', title ).strip()
			title = re.sub( r'\,+$', '', title )
			print(title)
			for x in shows:
				# merge seasons
				if x["title"] == title:
					x["episodes"] = x["episodes"] + episodes
					break
			else:
				# new show 
				show = {}
				show["title"] = title
				show["episodes"] = episodes
				show["type"] = show_type
				show["image"] = "http://www.skygo.co.nz" + product["imageURL"]
				shows.append(show)
	
		count = count + 1
	return shows

if __name__ == "__main__":	
	f = open("sky.js", "w")
	f.write(json.dumps(get_listings()))
	f.close()
