import guidebox
import json

def get_listings():	
	return guidebox.get_listings("hulu_free")
	

if __name__ == "__main__":
	listings = json.dumps(get_listings())
	f = open("hulu_free.js", "w")
	f.write(listings)
	f.close()
