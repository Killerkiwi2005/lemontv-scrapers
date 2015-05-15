import guidebox
import json

def get_listings():	
	return guidebox.get_listings("nbc")
	

if __name__ == "__main__":
	listings = json.dumps(get_listings())
	f = open("nbc.js", "w")
	f.write(listings)
	f.close()
