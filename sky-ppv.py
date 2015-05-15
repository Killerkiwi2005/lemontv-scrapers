import sky
import json

def get_listings(tvod = "false"):	
	return sky.get_listings("true")

if __name__ == "__main__":	
	f = open("sky-ppv.js", "w")
	f.write(json.dumps(get_listings()))
	f.close()
