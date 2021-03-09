from models import db, ip_validator, Geolocation, GeolocationSchema, init_db, third_set
# from settings import *
import settings
from flask import json, request, Response, jsonify
import requests, os
from connexion.resolver import RestyResolver

# app = settings.app
conned_app = settings.conned_app
conned_app.add_api("swagger.yml", resolver=RestyResolver('run'))


def start():
	hello = ["Hello",  "it's the default response'"]
	return jsonify(hello)


@app.route('/localizations/input_ip=<input_ip>', methods=['POST'])
def localization_by_ip(input_ip):
	if ip_validator(input_ip):
		if request.method == 'POST':
			get_details = requests.get(
				f'http://api.ipstack.com/{input_ip}?access_key'
				f'={os.getenv("ipstackKey")}&security=1&output=json')
			if get_details.status_code == 200:
				details = json.loads(get_details.content.decode())
				third_set.append(details)
				new_loc = Geolocation(input_ip, details)
				db.session.add(new_loc)
				db.session.commit()
				return jsonify({"Geolocation data collected for": input_ip},
							   details)
	else:
		return Response("Unprocessable input. Not correct IPv4/IPv6 address.",
						status=422, mimetype='application/json')


@app.route('/localizations/input_url=<input_url>', methods=['POST'])
def localization_by_url(input_url):
	if request.method == 'POST':
		# request_data = request.get_json()
		get_details = requests.get(
			f'http://api.ipstack.com/{input_url}?access_key'
			f'={os.getenv("ipstackKey")}&security=1&output=json')
		if get_details.status_code == 200:
			details = json.loads(get_details.content.decode())
			third_set.append(details)
			new_loc = Geolocation(input_url, details)
			db.session.add(new_loc)
			db.session.commit()
			return jsonify({"Geolocation data collected for": input_url},
						   details)
		else:
			return Response(
				"Unprocessable input. Not correct IPv4/IPv6 address.",
				status=422, mimetype='application/json')


@app.route('/localizations/')
def all_localizations():
	locations = Geolocation.query.all()
	return jsonify([loc.serialize() for loc in locations])


@app.route('/localizations/<_id>')
def localization(_id):
	location = LocationData.query.filter_by(id=_id).one()
	return jsonify(location.serialize())


@app.route('/localizations/<_id>')
def remove_localization(_id):
	location = LocationData.query.filter_by(id=_id).one()
	db.session.remove(location)
	db.session.commit()
	return jsonify({"Succesfully removed from database": location.serialize()})


if __name__ == '__main__':
	init_db()
	# app.run(debug=True)
	conned_app.run(debug=True)
