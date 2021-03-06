from app import app, json, Geolocation, request
import requests, os

get_details = requests.get(
	f'http://api.ipstack.com/check?access_key'
	f'={os.getenv("ipstackKey")}&security=1&output=json')
print(get_details)
json_data = get_details.content.decode()
print(json_data)
data1 = json.loads(json_data)

# for k, v in data1.items():

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
