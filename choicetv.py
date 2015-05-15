import util
import re
import json
DATA_URL = 'http://choicetv.e-cast.co.nz/media/showall'

def get_episodes(url, series):

	episodes = []

	doc = util.get_url_html(url)
	divs = doc.xpath("//div[contains(@class, 'video')]//div[contains(@class, 'video')]")

	for div in divs:
		title = div.xpath('.//span[@class="title"]')[0].text
		image = div.xpath('.//img')[0].get("src")
		link = div.xpath('.//a')[0].get("href")
		episode_text = div.xpath('.//span[@class="episode"]')[0].text
	
		episode = {}
		episode["title"] =title
		episode["uri"] = link
		episode["s"] = series
		episode["e"] = 0	
		matches = re.search(r"([\d]+)", episode_text)
		if matches:
			episode["e"] = matches.group(1)
		
		print( episode["s"], episode["e"], episode["title"])
		
		episodes.append(episode)
	return episodes

		
def get_listings():	
	doc = util.get_url_html(DATA_URL)
	divs = doc.xpath("//div[contains(@class, 'video')]")
	
	shows = []
	for div in divs:
		title = div.xpath('.//span[@class="title"]')[0].text
		image = div.xpath('.//img[@src]')[0].get("src")
		link = div.xpath('.//a')[0].get("href")
		series = div.xpath('.//strong')[0].text
		episode = div.xpath('.//span[@class="episode"]')[0].text
		
		print(title)
		
		episode_count = 1
		matches = re.search(r"([\d]+)", episode)
		if matches:
			episode_count = int(matches.group(1))
			

		series = re.search(r"([\d]+)", series).group(1)

		show = {}
		if episode_count > 1:
			episodes = get_episodes(link, series)
		else:
			# this is a direct link to an episode
			episode = {}
			episode["title"] = title
			episode["uri"] = link
			episode["s"] = series
			episode["e"] = episode_count	
			print( episode["s"], episode["e"], episode["title"])
			episodes = [episode]
			
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
