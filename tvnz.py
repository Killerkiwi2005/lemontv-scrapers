import lxml.html as lh
from urllib.request import urlopen
import json
import re
import util

DATA_URL = 'http://tvnz.co.nz/content/ta_ent_video_shows_group/ta_ent_programme_result_module_skin.xinc?channel=%s'

DATA_CHANNELS = [ 'tvnz-online','kidzone24','tv-one','tv2']
EPISODE_TEMPLATE = "http://tvnz.co.nz/content/%s_episodes_group/ta_ent_ajax_searchresult_module_skin.xml"
WEBSITE = "http://tvnz.co.nz"


def strip_text(text, strip):
	if text.endswith(strip):
	    return text[:-len(strip)]
	return text

def clean_show_name(name):
	name = strip_text(name, " - Watch First")
	name = strip_text(name, " - Watch Fast")
	name = strip_text(name, " (Original online series)")
	return name

def get_episodes(href):
	parts = href.split("/")
	parts = list(filter(None, parts)) # fastest
	if len(parts) == 0:
		return []
	
	url = EPISODE_TEMPLATE % (parts[0].replace("-","_"))
	episodes = []
	try:
		doc = lh.parse(urlopen(url))
		all_media = doc.xpath('//media')
		for media in all_media:
			episode = {}
			
			episode["show"] = media.xpath(".//show")[0].text
			episode["uri"] = WEBSITE + media.xpath(".//uri")[0].text 
			episode["type"] = media.xpath(".//type")[0].text
			episode["date"] = media.xpath(".//date")[0].text
			episode["s"] = 0
			episode["e"] = 0			
			details = media.xpath(".//details")[0].text
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
		return []

def get_listings():
	shows = []
	for channel in DATA_CHANNELS:
		print ("CHANNEL: ", channel)
		url = DATA_URL % channel
		print (url)
		doc = util.get_url_html(url)
		
		shows_div = doc.xpath("//div[contains(@class, 'show')]")
		
		print( len(shows_div))
		for show in shows_div:
			
			url = show.xpath(".//li[contains(@class, 'show')]/a")[0].get("href")
			episodes = []
			# first episode is in html content and not in xml feed
			episode = {}
			episode["show"] = clean_show_name(show.xpath(".//li[contains(@class, 'show')]/a")[0].text.strip())
			episode["uri"] = WEBSITE + url
			episode["type"] = show.xpath(".//li[contains(@class, 'type')]")[0].text.strip()
			episode["date"] = show.xpath(".//li[contains(@class, 'date')]")[0].text.strip()
			episode["s"] = 0
			episode["e"] = 0			
			details = show.xpath(".//li[contains(@class, 'details')]")[0].text
			matches =  re.search(r"[^\d]+(\d+)[^\d]+(\d+)", details)

			
			if matches:
				episode["s"]  = matches.group(1)
				episode["e"] = matches.group(2)
			print( episode["s"], episode["e"], episode["show"])

			episodes.append(episode)
			episodes = episodes + get_episodes(url)
			
			s = {}
			s["title"] = clean_show_name(show.xpath(".//h5/a")[0].text.strip())
			s["episodes"] = episodes
			shows.append(s)

	return shows

if __name__ == "__main__":
	f = open("tvnz.json", "w")
	listings = get_listings()
	print (listings)
	f.write(listings)
	f.close()
