from models import db, ip_validator, Geolocation, LocationData, init_db
from settings import *
from flask import json, request, Response, jsonify, render_template_string
import requests


@app.route('/localizations/input_ip=<input_ip>', methods=['POST'])
def localization_by_ip(input_ip):
	if ip_validator(input_ip):
		if request.method == 'POST':
			# request_data = request.get_json()
			get_details = requests.get(
				f'http://api.ipstack.com/{input_ip}?access_key'
				f'={os.getenv("ipstackKey")}&security=1&output=json')
			if get_details.status_code == 200:
				details = json.loads(get_details.content.decode())
					# for k, v in details.items():
			# if db.session.query(Geolocation).filter(
			# 		Geolocation.localization_input ==
			# 		localization_input).count() == 0:
				new_geo = Geolocation(localization_input=input_ip)
				new_loc = LocationData(details)
				db.session.add(new_loc)
				db.session.add(new_geo)
				db.session.commit()
				return jsonify({"Geolocation data collected for": input_ip},
							   details)
	else:
		return Response("Unprocessable input. Not correct IPv4/IPv6 address.",
						status=422, mimetype='application/json')


@app.route('/localizations/input_url=<input_url>', methods=['POST'])
def localization_by_url(input_url):
	if ip_validator(input_url):
		if request.method == 'POST':
			# request_data = request.get_json()
			get_details = requests.get(
				f'http://api.ipstack.com/{input_url}?access_key'
				f'={os.getenv("ipstackKey")}&security=1&output=json')
			if get_details.status_code == 200:
				details = json.loads(get_details.content.decode())
				new_geo = Geolocation(localization_input=input_url)
				new_loc = LocationData(details)
				db.session.add(new_loc)
				db.session.add(new_geo)
				db.session.commit()
				return jsonify({"Geolocation data collected for": input_url},
							   details)
			else:
				return Response(
					"Unprocessable input. Not correct IPv4/IPv6 address.",
					status=422, mimetype='application/json')




@app.route('/geo/')
def geolocalizations():
	locations = Geolocation.query.all()
	return jsonify([loc.serialize() for loc in locations])

@app.route('/localizations/')
def all_localizations():
	locations = LocationData.query.all()
	return jsonify([loc.serialize() for loc in locations])


@app.route('/localizations/id=<_id>')
def localization(_id):
	location = LocationData.query.filter_by(id=_id).one()
	return jsonify(location.serialize())


if __name__ == '__main__':
	init_db()
	app.run(debug=True)
