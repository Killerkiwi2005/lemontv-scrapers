import lxml.html as lh
from urllib.request import urlopen
import json
from lxml import etree
import re
DATA_URL = 'http://www.cwtv.com/shows/'
EPISODE_TEMPLATE = "http://www.cwtv.com/cw-video/%s"
EPISODE_BASE = "http://www.cwtv.com%s"

def get_episodes(href):
	url = EPISODE_TEMPLATE % (href)
	print( url)
	episodes = []
	doc = lh.parse(urlopen(url))
	print (url)
	all_media = doc.xpath("//div[contains(@class, 'full-episodes')]")

	for media in all_media:
		episode = {}
		episode["show"] =  media.xpath(".//p[contains(@class, 'et')]")[0].text
		episode["uri"] = EPISODE_BASE % media.xpath(".//a")[0].get("href")
		episode["date"] = media.xpath(".//span[contains(@class, 'd4')]")[0].text
		episode["s"] = 0
		episode["e"] = 0			
		details = media.xpath(".//p[contains(@class, 'd2')]")[0].text
		matches = re.search(r"[^\d]+(\d+)[^\d]+(\d+)", details)
		if matches:
			episode["s"]  = matches.group(1)
			episode["e"] = matches.group(2)
			print (episode["show"])
			print (episode["uri"])
			print( "We matched series '" + matches.group(1) + "' episode '" + matches.group(2) + "'")
		episodes.append(episode)
	return episodes

def get_listings_old():	
	url = DATA_URL
	doc = lh.parse(urlopen(url))
	links = doc.xpath("//a[contains(@class, 'hublink')]")

	shows = []
	for a in links:
		link = a.get("href")
		show = {}
		episodes = get_episodes(a.xpath('.//img')[0].get("title"))
		if episodes:
			show["title"] = a.xpath('.//p')[0].text
			show["image"] = a.xpath('.//img')[0].get("src")
			show["episodes"] = episodes
			shows.append(show)

	return shows

import guidebox
import json

def get_listings():	
	return guidebox.get_listings("thecw")



if __name__ == "__main__":
	f = open("cw.js", "w")
	f.write(json.dumps(get_listings()))
	f.close()
