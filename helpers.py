from misc.run import json, Geolocation, db, conned_app
import os

app = conned_app

# get_details = requests.get(
# 	f'http://api.ipstack.com/check?access_key'
# 	f'={os.getenv("ipstackKey")}&security=1&output=json')
# print(get_details)
# json_data = get_details.content.decode()
# print(json_data)
# data1 = json.loads(json_data)

# for k, v in data1.items():
data1 ={"ip":"189.147.147.15","type":"ipv4","continent_code":"NA",
  "continent_name":"North America","country_code":"MX","country_name":"Mexico","region_code":"CMX","region_name":"Mexico City","city":"Magdalena Contreras","zip":"01000","latitude":19.348430633544922,"longitude":-99.19747924804688,"location":{"geoname_id":3523760,"capital":"Mexico City","languages":[{"code":"es","name":"Spanish","native":"Espa\u00f1ol"}],"country_flag":"http:\/\/assets.ipstack.com\/flags\/mx.svg","country_flag_emoji":"\ud83c\uddf2\ud83c\uddfd","country_flag_emoji_unicode":"U+1F1F2 U+1F1FD","calling_code":"52","is_eu":false}}

# def add_new(_name, _price, _isbn):
#     new_location = Geolocation()
#     db.session.add(new_location)
#     db.session.commit()

app_root = app.root_path
loc = app_root + '\\example.json'

with open(loc) as json_file:
	data = json.load(json_file)
	for k, v in data.items():
		print(k, v)

# Delete database file if it exists currently
if os.path.exists('misc/geo.db'):
	os.remove('misc/geo.db')

# Create the database
db.create_all()

# Iterate over the PEOPLE structure and populate the database
# for person in- :
# 	p = Geolocation, fname=person['fname'])
# 	db.session.add(p)
g = Geolocation(input=data['ip'], dictionary=data)
db.session.commit()
