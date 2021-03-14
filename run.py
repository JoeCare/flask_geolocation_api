from flask_jwt_extended import create_access_token
from models import (db, app, conned_app, ip_validator, Geolocation,
	GeolocationSchema, User, UserSchema, init_db, third_set)
from flask import json, request, Response, jsonify, redirect
import requests, os
from connexion.resolver import RestyResolver
#==========
import time
import six
from werkzeug.exceptions import Unauthorized
from jose import JWTError, jwt
# app = settings.app
# conned_app = settings.conned_app
# conned_app.add_api("swagger.yml", resolver=RestyResolver('run'))


def create():
	"""
	Create a new geolocation record from data object passed with request
	:param geolocation:    table of which record will be created; instance class
	:return:        201 on success, 406 if instance exists
	"""
	if request.method == 'POST':
		dict_data = request.get_json()
		new_loc = Geolocation(dict_data)
		db.session.add(new_loc)
		db.session.commit()
		return jsonify(
			201, f"Geolocation created for: {new_loc.id}", dict_data)


# @app.route('/localizations/input_ip=<input_ip>', methods=['POST'])
def create_with_ip(input_ip):
	"""
	Create a new geolocation record from data collected basing on given IP
	:param input_ip:	IPv4 or IPv6 address passed to endpoints URL
	:return:            201 on success, 406 if instance exists, 422 on input
	unprocessable in geolocalization process
	"""
	if ip_validator(input_ip):
		if request.method == 'POST':
			get_details = requests.get(
				f'http://api.ipstack.com/{input_ip}?access_key'
				f'={os.getenv("ipstackKey")}&security=1&output=json')
			if get_details.status_code == 200:
				details = json.loads(get_details.content.decode())
				third_set.append(details)
				new_loc = Geolocation(details, input_ip)
				db.session.add(new_loc)
				db.session.commit()
				return jsonify(
					201, f"Geolocation data collected for: {input_ip}", details)
	else:
		return jsonify(
			422, "Unprocessable input. Not correct IPv4/IPv6 address.")


# @app.route('/localizations/input_domain=<input_domain>', methods=['POST'])
def create_with_domain(input_domain):
	"""
	Create a new geolocation record from data collected basing on given domain
	:param input_domain:	domain address passed to endpoints URL
	:return:            201 on success, 406 if instance exists, 422 on input
	unprocessable in geolocalization process
	"""
	if request.method == 'POST':
		get_details = requests.get(
			f'http://api.ipstack.com/{input_domain}?access_key'
			f'={os.getenv("ipstackKey")}&output=json')
		if get_details.status_code == 200:
			details = json.loads(get_details.content.decode())
			third_set.append(details)
			new_loc = Geolocation(details, input_domain)
			db.session.add(new_loc)
			db.session.commit()
			return jsonify(
				{"Geolocation data collected for": input_domain}, details)
		else:
			return jsonify(
				422, "Unable to collect geolocation data. \
				Please check your input or try again in a while.")


def update_one(loc_id, geolocation):
	"""
	Update an existing record with given data
	:param loc_id:			ID of the record to update
	:param geolocation:		data given to update record
	:return:            	200, updated record, 404 if ID not found
	"""
	to_update = Geolocation.query.filter(
		Geolocation.id == loc_id).one_or_none()
	if to_update:
		# # use db model schema
		schema = GeolocationSchema()
		# geolocation object (dict) -> db model geolocation instance
		input_to_db = schema.load(geolocation, session=db.session)
		# Set the id to the person we want to update

		input_to_db.id = to_update.id
		db.session.merge(input_to_db)
		db.session.commit()
		#
		# # return updated person in the response
		output_dump = schema.dump(input_to_db)

		return 200, output_dump
	else:
		return 404, f"Person not found for Id:"


def retrieve_all():
	"""
	Retrieve list of all records in data table
	:return:            list of matching objects
	"""
	locations = Geolocation.query.filter(Geolocation.visible == 1).all()
	if not locations:
		return jsonify(f"Records not found.")

	return jsonify([loc.serialize() for loc in locations])


def retrieve_one(loc_id):
	"""
	Return one record from the collection matching given ID

	:param loc_id:   	record ID for localization data
	:return:            matching data object
	"""
	query = Geolocation.query.filter(Geolocation.visible == 1).filter(
		Geolocation.id == loc_id).one_or_none()
	# query = Geolocation.query.filter_by(id=loc_id)
	# print(jsonify(query))
	if query is not None:
		schema = GeolocationSchema()
		data = schema.dump(query)
		return data
	else:
		return jsonify(f"Record not found for ID: {loc_id}")


# @app.route('/localizations/<_id>')
def safe_delete(loc_id):
	"""
	Remove object from main collection but leaving record in database
	:param loc_id:		ID of the record to delete
	:return:            200 on successful delete, 404 if not found
	"""
	location = Geolocation.query.filter_by(id=loc_id).one_or_none()
	if location:
		# db.session.remove(location)
		location.visible = 0
		db.session.merge(location)
		db.session.commit()
		return jsonify(
			200, f"Successfully deleted record for ID: {loc_id}")
	else:
		jsonify(404, f"Record not found in database for ID: {loc_id}")


def list_deleted():
	"""
	List of records removed from API by safe_delete
	:return:            list of records on success, 404 if not found
	"""
	locations = Geolocation.query.filter(Geolocation.visible == 0).all()
	if locations:
		schema = GeolocationSchema(many=True)
		data = schema.dump(locations)
		return jsonify(f"You've {len(locations)} records safely removed from main "
				f"collection.", [loc.short() for loc in locations])
	else:
		return jsonify(404, "No records stored after safe-delete.")


def restore_deleted(loc_id):
	"""
	Restore record of given ID from safe_deleted list to main API
	:param loc_id:				ID of the record to restore
	:return:            		200 on success, 404 if not found
	"""
	location = Geolocation.query.filter(Geolocation.visible == 0).filter_by(
		id=loc_id).one_or_none()
	if location:
		if request.method == 'PUT':
			location.visible = 1
			db.session.merge(location)
			db.session.commit()
			return jsonify(
				200, f"Record restored for ID: {loc_id}")
		else:
			return jsonify("Valid methods: PUT, DELETE")
	else:
		jsonify(404, f"Record not found in database for ID: {loc_id}")


def remove_deleted(loc_id):
	"""
	Delete permanently record of given ID from safe_deleted list
	:param loc_id:				ID of the record to restore
	:return:            		200 on success, 404 if not found
	"""
	location = Geolocation.query.filter(Geolocation.visible == 0).filter_by(
		id=loc_id).one_or_none()
	if location:
		if request.method == 'DELETE':
			db.session.delete(location)
			db.session.commit()
			return jsonify(
				200, f"Record permanently removed for ID: {loc_id}")
		return jsonify("Valid methods: PUT, DELETE")
	else:
		jsonify(404, f"Record not found in database for ID: {loc_id}")


def retrieve_all_users():
	locations = User.query.all()
	if locations:
		return jsonify([loc.serialize() for loc in locations])
	return jsonify(f"Records not found.")


# AUTH
#========================
JWT_ISSUER = 'com.zalando.connexion'
JWT_SECRET = 'change_this'
JWT_LIFETIME_SECONDS = 600
JWT_ALGORITHM = 'HS256'


def generate_token(user_id):
	timestamp = _current_timestamp()
	payload = {
		"iss": JWT_ISSUER,
		"iat": int(timestamp),
		"exp": int(timestamp + JWT_LIFETIME_SECONDS),
		"sub": str(user_id),
	}

	return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token):
	try:
		return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
	except JWTError as e:
		six.raise_from(Unauthorized, e)


def get_secret(user, token_info) -> str:
	return '''
	You are user_id {user} and the secret is 'wbevuec'.
	Decoded token claims: {token_info}.
	'''.format(user=user, token_info=token_info)


def _current_timestamp() -> int:
	return int(time.time())


def register():
	login = request.json.get("login", None)
	password = request.json.get("password", None)
	if len(password) < 8:
		return jsonify({"msg": "Please set password for at least 8"
							   "characters"}), 401
	else:
		if User.query.filter(User.login == login):
			return jsonify({"msg": "Given login already taken"})
		else:
			new_user = User(login, password)
			db.session.add(new_user)
			db.session.commit()
			return generate_token(new_user.id)
	# 	access_token = create_access_token(identity=login)
	# return jsonify(access_token=access_token)



def login():

	user_login = request.json.get("login", None)
	password = request.json.get("password", None)
	if User.parse_on_login(User, _login=user_login, _password= password):
		query = User.query.filter_by(login=user_login).one_or_none()
		if query:
			schema = GeolocationSchema()
			data = schema.dump(query)
			return generate_token(data['id'])
	return jsonify({"msg": "Invalid credentials"}), 401
	# access_token = create_access_token(identity=user_login)
	# return jsonify(access_token=access_token)


if __name__ == '__main__':
	init_db()
	conned_app.add_api('openapi.yaml', resolver=RestyResolver('run'))
	conned_app.run(host='127.0.0.1', port=5000, debug=True)
	# conned_app.add_api("openapi.yaml", resolver=RestyResolver('run'))
	# conned_app.run(host='127.0.0.1', port=5000, debug=True)
