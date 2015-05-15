# lemontv-scrappers

Python scrappers for NZ streaming websites http://www.lemontv.co.nz

The scripts all have a function get_listings() that returns a json array

Example JSON data array
```
[
	{
		title : "Breaking Bad", // Title of the tv series/movie
		type : "tv",  // type currently only tv or movie
		image : "https://upload.wikimedia.org/wikipedia/en/6/61/BreakingBadS1DVD.jpg", // A fall back image that could be used if no metadata can be found
		year : 2008 ,  // Year of release / first series
		episodes : [	// Movies currently need an episode entry with s0e0
			{
				"title" : "Pilot", 
				"uri" : "http://urlofvideofile",
				"s" : 0, 
				"e" : 0, 
				"price" : 2.00, // Optional price in NZ dollars can be
			}
		]
	}
]
```
The util module can be used to return data in a queryable format
util.get_url_json(url), returns a json python object 
util.get_url_html(url), returns an lxml html document that can be queried using xpath