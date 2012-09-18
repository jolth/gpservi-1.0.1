"""
Geocoding API Google

 import geomapgoogle
 geomapgoogle.geocode('San Francisco')
 
 geomapgoogle.regeocode(latlng='40.714224,-73.961452')
 
"""
import urllib, json

GEOCODE_BASE_URL = 'http://maps.google.com/maps/api/geocode/json'

def geocode(address, sensor='false', **geo_args):
	"""
	geocoding
	"""
	geo_args = ({
		'address': address,
		'sensor': sensor
	})

	url = GEOCODE_BASE_URL + '?' + urllib.urlencode(geo_args)
	result = json.load(urllib.urlopen(url))
	return json.dumps([s['formatted_address']
	                   for s in result['results']])



def regeocode(latlng, sensor='false', **geo_args):
	"""
	Reverse Geocoding
	"""
	geo_args = ({
		'latlng' : latlng,
		'sensor' : sensor
	})

	url = GEOCODE_BASE_URL + '?' + urllib.urlencode(geo_args)
	result = json.load(urllib.urlopen(url))
	return json.dumps([s['formatted_address'] 
                       for s in result['results']])

