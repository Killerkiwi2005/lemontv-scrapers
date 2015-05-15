import lxml.html as lh
from urllib.request import urlopen
import json
from lxml import etree
import re
DATA_URL = 'http://ezyflix.tv/watch-movies?dir=desc&order=created_at&p=%s'
DATA_URL_TV =  'http://ezyflix.tv/watch-tv?dir=desc&order=created_at&p=%s'
EPISODE_DATA = 'http://ezyflix.tv/tvseries/episode/product/id/%s'

def get_episodes(id, series, url):

	response = urlopen(EPISODE_DATA % str(id));
	data = json.loads(response.read().decode())
	episodes = []
	print(url)
	for obj in data:
		e = 0
		name = obj["name"]
		matches =  re.search(r"^Episode ([\d]+) : ", name.strip())
		if matches:
			e = matches.group(1)
			name = name[len(matches.group(0)):]

		price = float(re.search(r"[\d\.]+", obj["price"]).group(0))

		
		episode = {}
		episode["show"] = name
		episode["title"] = name
		episode["uri"] = url
		episode["s"] = series
		episode["e"] = e
		episode["price"] = price

		is_new = True
		for x in episodes:
			if x["e"] == e:
				is_new = False
				if x["price"] > price:
					x["price"] = price
				break
		if is_new:
			print(series, e, name, price)
			episodes.append(episode)
	return episodes


def get_listings():	
	page = 1
	totalPages = 1
	shows = []
	while page <= totalPages:
		
		response = urlopen(DATA_URL % str(page));
		data = json.loads(response.read().decode())

		totalPages = data["totalPages"]
		for product in data["data"]:

			show = {}

			show["title"] = product["name"]
			show["image"] = product["imageUrl"]
			show["type"] = "movie"	

			print(show["title"],product["prodUrl"])
			# get price from data url
			try:
				doc = lh.parse(urlopen( product["prodUrl"]))
				prices = doc.xpath(".//span[contains(@class, 'price')]")
				if len(prices) > 0:
					price = prices[0].text.strip()[1:]
					print(price)
					show["episodes"] = [{"show" : product["name"], "uri" : product["prodUrl"], "s" : 0, "e" : 0, "price" : price}]	
					shows.append(show)
			except:
				pass
		page = page + 1


	page = 1
	totalPages = 1
	while page <= totalPages:
		
		response = urlopen(DATA_URL_TV % str(page));
		data = json.loads(response.read().decode())

		totalPages = data["totalPages"]
		for product in data["data"]:

			show = {}
			id = product["id"]

			series = 0
			title = re.sub( r' (Series|Season) \d+[a-zA-Z]?\b', '', product["name"].strip() )
			
			matches =  re.search(r"\d+[a-zA-Z]?\b", product["name"].strip())
			if matches:
				series = matches.group(0)

			episodes = get_episodes(id, series, product["prodUrl"])

			for x in shows:
				# merge seasons
				if x["title"] == title:
					x["episodes"] = x["episodes"] + episodes
					break
			else:
				# new show 
				show = {}
				show["title"] = title
				show["type"] = "tv"	
				show["episodes"] = episodes
				show["image"] = product["imageUrl"]
				shows.append(show)

		page = page + 1


	return shows

if __name__ == "__main__":	
	f = open("ezyflix.js", "w")
	f.write(json.dumps(get_listings()))
	f.close()
