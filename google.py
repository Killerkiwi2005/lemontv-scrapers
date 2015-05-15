from urllib.request import urlopen
import json
import urllib
import lxml.html as lh

def GetUrl(url, post = None):
	print ("GetUrl :: ", url)
	headers = { }#'User-Agent' : USER_AGENT }
	encodedPost = None
	if post:
		encodedPost = urllib.parse.urlencode(post).encode('utf-8')
	opener = urllib.request.build_opener()
	req = urllib.request.Request(url, encodedPost, headers)
	response = opener.open(req)
	doc = lh.parse(response)
	return doc

all_titles = []

def get_movies(category, showtype, existing_shows):	
	start = 0
	num = 100
	previousPagehash = ""
	shows = []
	
	while True:  
		
		url = "https://play.google.com/store/movies/category/%s/collection/movers_shakers" % category
		print("page", start)
		doc = GetUrl(url, {'start': start, 'num': num, 'numChildren': 0, 'ipf' : 1, 'xhr': 1 })
		cards = doc.xpath("//div[contains(@class, 'card-list')]//div[contains(@class, 'card-content')]")
		
		# the last page repeats...
		pagehash = ""
		for card in cards:
			pagehash = pagehash + card.xpath(".//h2//a")[0].text.strip()
		print (pagehash) 
		if pagehash == previousPagehash:
			break
		previousPagehash = pagehash
		

		for card in cards:	
			a = card.xpath(".//h2//a")[0]
			img = card.xpath(".//img[contains(@class, 'cover-image')]")[0]
			price = card.xpath(".//span[contains(@class, 'display-price')]")[0]
			
			# remove duplicates
			if a.get("href") in all_titles:
				continue
			all_titles.append(a.get("href"))
			
			show = {}
			show["title"] = a.text.strip()
			show["image"] = img.get("src")
			price = price.text.strip().replace("$","")
			
			if showtype == "movie":
				show["type"] = "movie"	
				# every show has an episode even movies
				show["episodes"] = [{"show" : a.text.strip(), "uri" : "https://play.google.com" + a.get("href"), "date" : "", "s" : 0, "e" : 0, "price" : price}]
				print (show["title"], price)
				
			else:
				show["type"] = "tv"	
				# every show has an episode even movies
				show["episodes"] = [{"show" : a.text.strip(), "uri" : "https://play.google.com" + a.get("href"), "date" : "", "s" : 0, "e" : 0, "price" : price.text.strip()}]
				
			add_show = True
			
			# check does not already exist
			for s in existing_shows:
				if s["episodes"][0]["uri"] == show["episodes"][0]["uri"]:
					add_show = False
					break

			if add_show:
				shows.append(show)
		
		start = start + num

	return shows


def get_listings():
	all_titles = []
	categories = [1,2,3,4,5,6,7,8,10,27,18,25,13]
	shows = []
	for category in categories:
		shows = shows + get_movies(category, "movie", shows)
	return shows

if __name__ == "__main__":	
	all_shows = get_listings()
	print("Count ", len(all_shows))
