from urllib.request import urlopen
import lxml 
import lxml.html as lh
import json
import os
import string
import time
import tempfile
import urllib

MAX_AGE = 4 # cache age in hours
MAX_ATTEMPTS = 5 # retry before giving up
CACHE = os.path.join(tempfile.gettempdir(), "lemontv", "cache")
USER_AGENT = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'

def format_filename(s):
	valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
	filename = ''.join(c for c in s if c in valid_chars)
	filename = filename.replace(' ','_') # I don't like spaces in filenames.
	return filename

def get_from_cache(url):
	clean_cache()
	filename = CACHE + "/" + format_filename(url)
	if os.path.exists(filename):
			with open(filename, "r") as f:
				contents = f.read()
				if len(contents) > 0:
					try:
						return contents
					except:
						print ("load error delete the file")	
	return None
	
def save_to_cache(url, data):
	filename = CACHE + "/" + format_filename(url)
	with open(filename, "w+") as f:
		f.write(data) 	

def clean_cache():

	if not os.path.exists(CACHE):
		os.makedirs(CACHE)

	for file in os.listdir(CACHE):
		fullpath = os.path.join(CACHE, file)
		file_mod_time = os.stat(fullpath).st_mtime
		# Time in minutes since last modification of file
		last_time = (time.time() - file_mod_time) / 60

		if last_time > 60 * MAX_AGE: # delete all cached files older than N hours
			os.remove(fullpath) 
	
def get_url_json(url, cache=True, cookiejar=None):

	print("GET :: ", url)

	if cache:
		data = get_from_cache(url)
		if data:
			return json.loads(data)

	attempts = 0
	while True:
	
		try:
			cookieProcessor = None
			if cookiejar:
				cookieProcessor = urllib.request.HTTPCookieProcessor(cookiejar)
				opener = urllib.request.build_opener(cookieProcessor)
			else:
				opener = urllib.request.build_opener()
			req = urllib.request.Request(url, None, { 'User-Agent' : USER_AGENT })
			response = opener.open(req)
		
		
			response = urlopen(url);
			data = json.loads(response.read().decode())
			
			save_to_cache(url, json.dumps(data))
			return data
			 
		except:
			
			attempts = attempts + 1
			if attempts > MAX_ATTEMPTS:
				raise
				
			print( "Http error retry in 1 second")
			time.sleep(1)    # pause 5 seconds
			continue

def get_url_html(url, cache=True, cookiejar=None):

	print("GET :: ", url)
	
	if cache:
		data = get_from_cache(url)
		if data:
			return lh.document_fromstring(data)
	
	attempts = 0
	while True:
	
		try:
			response = urlopen(url);
			html = urlopen(url).read().decode('utf8')
			save_to_cache(url, html)
			return lh.document_fromstring(html)
			 
		except:
			
			attempts = attempts + 1
			if attempts > MAX_ATTEMPTS:
				raise
				
			print( "Http error retry in 1 second")
			time.sleep(1)    # pause 5 seconds
			continue
