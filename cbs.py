import guidebox
import json

def get_listings():	
	return guidebox.get_listings("cbs")
	

if __name__ == "__main__":
	listings = json.dumps(get_listings())
	f = open("cbs.js", "w")
	f.write(listings)
	f.close()
