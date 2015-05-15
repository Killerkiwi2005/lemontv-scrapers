import lxml.html as lh
from urllib.request import urlopen
import urllib
import json
from lxml import etree
import re
DATA_URL = 'https://quickflix.co.nz/Catalogue/GetCollectionForSortingAndSubGenre?category=%s&collection=All&keywordIds=All&keywordIds=&sortOption=StreamingForMePublic&page=%s&pageSize=100&contentAvailability=%s&listId=&likeDigitalCode=&collectionType=All&catalogueFunction=MenuNav'

EPISODE_TEMPLATE = "http://www.quickflix.co.nz/%s"
PRICE_URL = 'https://www.quickflix.co.nz/Member/CatalogueItem/T%s'

MOVIES = "Movies"
TV = "TV"
SUBSCRIBTION = "streaming-subscription"
PPV = "streaming-premium"

PRICE_URL = "https://www.quickflix.co.nz/Member/CatalogueItem/%s"

def get_episodes(url, series, filterContent):


	print( url)
	episodes = []
	#try:
	doc = lh.parse(urlopen(url))
	all_media = doc.xpath("//ul[contains(@class, 'episode-list')]//li")

	#id = re.search( r"/(S[^\?]*)", url ).group(1)
	#print ("ID:", id)
	
	#if filterContent == PPV:
	#	response = urlopen(PRICE_URL % (id));
	#	price_data = json.loads(response.read().decode())

	for media in all_media:

		# http://www.quickflix.co.nz/Catalogue/Boxset/ATouchofFrostSeries1/308?catalogueFunction=16&redirect=true
		episode = {}
		
		title = media.xpath(".//span[contains(@class, 'episode-title')]")[0].text.strip()
		
		episode["show"] = title
		episode["uri"] = url
		#episode["type"] = media.xpath(".//type")[0].text
		episode["date"] = ""
		episode["s"] = series
		episode["e"] = media.xpath(".//span[contains(@class, 'episode-number')]")[0].text.strip().replace(".","")

		if filterContent == PPV:
			#price_span = media.xpath("..//button")[0]
			#print (price_span.text )	
			episode["price"] = -1 #price_span.text.strip()[1:]
			#print (episode["price"] )

		#https://www.quickflix.co.nz/Member/CatalogueItem/S011206?_=1412721106414

		print(episode["s"] , episode["e"], title)
		episodes.append(episode)
	return episodes
	#except:
	##	print "Error getting episode listing"
	##	print url
	##	return 
		
def get_listings(filterContent = SUBSCRIBTION):
	return   get_data(TV, filterContent ) + get_data(MOVIES, filterContent)	 

def get_data(contentType, filterContent ):

	page = 0
	shows = []
	while True:

		url = DATA_URL % (contentType, page, filterContent)
		print(url)

		try:
			doc = lh.parse(urlopen(url))
			listitems = doc.xpath("//li//div[contains(@class, 'cover')]")
		except:
			break

		

		if len(listitems) == 0:
			break

		count  = 0
		
		for listitem in listitems:

			link = listitem.xpath(".//a")[0]
			img = listitem.xpath(".//img")[0]
			print (count, " of " , len(listitems))
			series = 0
			show_title = re.sub( r' \- (Series|Season) \d+[a-zA-Z]?\b', '',img.get('alt').strip() )
			print("title", show_title)
			matches =  re.search(r"\d+[a-zA-Z]?\b",  img.get('alt').strip())
			if matches:
				series = matches.group(0)

			url = EPISODE_TEMPLATE % link.get("href")

			episodes = None
			if contentType == TV:
				#try:
				if series == 0:
					series = 1
				episodes = get_episodes(url, series, filterContent)
				#except:
				#	continue

			if episodes:
				title = re.sub( r' \- (Series|Season) \d+[a-zA-Z]?\b', '', link.get('title').strip() )
				

				for x in shows:
					# merge seasons
					if x["title"] == title:
						x["episodes"] = x["episodes"] + episodes
						break
				else:
					# new show 
					show = {}
					show["title"] = show_title
					show["type"] = "tv"	
					show["episodes"] = episodes
					show["image"] =  link.xpath(".//img")[0].get("src")
					shows.append(show)
			else:
				show = {}
				show["title"] = show_title
				show["type"] = "movie"	
				# every show has an episode even movies
				price = 0
				
				if filterContent == PPV:
					matches =  re.search(r"\/(T\d+)\?\b", url)
					if matches:
						id = matches.group(1)
						data = json.loads(urlopen(PRICE_URL % id).read().decode())
						price = data["Products"][0]["PersonalisedPrice"]
						print("PRICE", price)
				show["episodes"] = [{"show" : show_title, "uri" : url, "date" : "", "s" : 0, "e" : 0, "price" : price}]
				shows.append(show)

			count = count + 1
		page = page + 1
	return shows

if __name__ == "__main__":
	text = get_listings()
	
	f = open("quickflix.js", "w")
	f.write(json.dumps(text))
	f.close()
	print ("COMPLETE")		
