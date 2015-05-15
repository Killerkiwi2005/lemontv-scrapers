import lxml.html as lh
from urllib.request import urlopen
import json
from lxml import etree
import re
import util

DATA_URL = 'http://www.tv3.co.nz/tabid/4086/default.aspx'
EPISODE_TEMPLATE = "http://www.tv3.co.nz/OnDemand/ShowEpisodesDetail.aspx?MCat=%s"

def get_episodes(href):
	parts = href.split("/")
	parts = list(filter(None, parts)) # fastest
	if len(parts) == 0:
		return []
	
	url = EPISODE_TEMPLATE % (parts[-2].replace("-","_"))
	
	episodes = []
	try:
		doc = util.get_url_html(url)
		all_media = doc.xpath("//div[contains(@class, 'listWrapper')]")
		print( url)
		for media in all_media:
			#print etree.tostring(media)

			# skip headers
			if len(media.xpath(".//a")) == 0:
				continue
		
			episode = {}
			episode["show"] = media.xpath(".//a")[0].text
			episode["uri"] = media.xpath(".//a")[0].get("href")
			#episode["type"] = media.xpath(".//type")[0].text
			episode["date"] = media.xpath(".//div[contains(@class, 'epDetailDate')]")[0].text
			episode["s"] = 0
			episode["e"] = 0			
			details = media.xpath(".//a")[0].text
			matches =  re.search(r"[^\d]+(\d+)[^\d]+(\d+)", details)
			if matches:
				episode["s"]  = matches.group(1)
				episode["e"] = matches.group(2)
			print( episode["s"], episode["e"], episode["show"])
			episodes.append(episode)
		return episodes
	except:
		print ("Error getting episode listing")
		print (url)
		return 
		
def get_listings():	
	url = DATA_URL
	doc = util.get_url_html(url)
	divs = doc.xpath("//div[contains(@class, 'grid_2')]")
	
	shows = []
	for div in divs:
		link = div.xpath('.//p[@class="artTitle"]/a')[0]
		title = re.sub( r' S\d+\b', '', link.text.strip() )
		show = {}
		print (title)
		episodes = get_episodes(link.get("href"))
		image = div.xpath('.//img')[0].get("src")
		
		if episodes:
			show["title"] = title
			show["image"] = image
			show["episodes"] = episodes
			shows.append(show)

	return shows
	
if __name__ == "__main__":
	f = open("tv3.js", "w")
	f.write(json.dumps(get_listings()))
	f.close()
