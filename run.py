from models import (
	db, app, conned_app, ip_validator, Geolocation, GeolocationSchema,
	User, UserSchema, init_db, third_set, fourth_set, gpass, chpass,
	load_dotenv, find_dotenv)
from flask import json, request, jsonify, make_response
import requests, os, time, six
from connexion.resolver import RestyResolver
from werkzeug.exceptions import Unauthorized
from jose import JWTError, jwt

load_dotenv(find_dotenv())


def main_page():
	response = {"Main endpoints":
					{
						"Geolocations": "/geolocations",
						"Users": "/users",
						"Login": "/auth/login",
						"Swagger UI": "/ui",
						"spec file": "/openapi.json",
						}
		}
	return jsonify(response)


def create():
	"""
	Create a new geolocation record from data object passed with request
	:param geolocation:    table of which record will be created; instance
	class
	:return:        201 on success, 406 if instance exists
	"""
	if request.method == 'POST':
		dict_data = request.get_json()
		new_loc = Geolocation(dict_data)
		db.session.add(new_loc)
		db.session.commit()
		return jsonify(
			201, f"Geolocation created for: {new_loc.id}", dict_data)


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
				f'={os.getenv("IPSTACK_KEY")}&output=json')
			if get_details.status_code == 200:
				details = json.loads(get_details.content.decode())
				third_set.append(details)
				new_loc = Geolocation(details, input_ip)
				db.session.add(new_loc)
				db.session.commit()
				return jsonify(
					201, f"Geolocation data collected for: {input_ip}",
					details)
	else:
		return jsonify(
			422, "Unprocessable input. Not correct IPv4/IPv6 address.")


def create_with_domain(input_domain):
	"""
	Create a new geolocation record from data collected basing on given domain
	:param input_domain:		domain address passed to endpoints URL
	:return:					201 on success, 406 if instance exists,
	422 on input unprocessable in geolocalization process
	"""
	if request.method == 'POST':
		get_details = requests.get(
			f'http://api.ipstack.com/{input_domain}?access_key'
			f'={os.getenv("IPSTACK_KEY")}&output=json')
		if get_details.status_code == 200:
			details = json.loads(get_details.content.decode())
			third_set.append(details)
			new_loc = Geolocation(details, input_domain)
			db.session.add(new_loc)
			db.session.commit()
			return jsonify(201, f"Record created for: {input_domain}", details)
		else:
			return jsonify(
				422, "Unable to collect geolocation data. \
				Please check your input or try again in a while.")


def retrieve_all():
	"""
	Retrieve list of all records in data table
	:return:            list of matching objects
	"""
	locations = Geolocation.query.filter(Geolocation.visible == 1).all()
	if locations:
		return jsonify([loc.serialize() for loc in locations])

	return jsonify(404, f"Records not found.")


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
		return jsonify(404, f"Record not found for ID: {loc_id}")


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

		return jsonify(200, output_dump)
	else:
		return jsonify(404, f"Person not found for Id: {loc_id}")


def safe_delete(loc_id):
	"""
	Remove object from main collection but leaving record in a database
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
			202, f"Removed record from main API for ID: {loc_id}")
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
		return jsonify(
			200, f"You've {len(locations)} records safely removed from main "
			f"collection.", [loc.short() for loc in locations])
	else:
		return jsonify(404, "No records stored after safe-delete.")


def restore_deleted(loc_id):
	"""
	PUT request sent to this endpoint restore record of given ID to main API
	view. Works on records which were previously removed with default
	safe_delete method.
	list to
	main API
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
			return jsonify(405, "Valid methods on that endpoint: PUT, DELETE")
	else:
		jsonify(404, f"Record not found in database for ID: {loc_id}")


def remove_deleted(loc_id):
	"""
	Delete permanently record of given ID from safe_deleted list.
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
		return jsonify(405, "Valid methods on that endpoint: PUT, DELETE")
	else:
		jsonify(404, f"Record not found in database for ID: {loc_id}")


# AUTH simple JWT with jose
#========================
JWT_ISSUER = 'com.zalando.connexion'
JWT_SECRET = os.getenv("JWT_SECRET")
JWT_LIFETIME_SECONDS = 900
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")


def generate_token(public_id):
	"""
	Simple token generator returning encoded JWT
	:param public_id:	unique string user identification
	:return 	JWT:	authorization token for given public_id
	"""
	# if User.query.filter_by(public_id=public_id).one_or_none() is None:
	# 	return jsonify(404, "ID unverified")
	# else:
	timestamp = int(time.time())
	payload = {
		"iss": JWT_ISSUER,
		"iat": int(timestamp),
		"exp": int(timestamp + JWT_LIFETIME_SECONDS),
		"sub": str(public_id),
		}
	return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token):
	try:
		return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
	except JWTError as e:
		six.raise_from(Unauthorized, e)


def refresh_token(token):
	"""Get new token from last stored in cookies"""
	try:
		token_dict = jwt.decode(
			token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
		print("expired to refresh:", token_dict)
	except JWTError as e:
		print("JWTError with dict occured:", e)
	else:
		user_pub_id = token_dict['sub']
		return jsonify({"Refreshed_token": generate_token(user_pub_id)})


def cookie_token():
	"""Get new token from last stored in cookies
	With cheating - decoder omits token expiration time
	and should always return new JWT."""
	access_token = request.cookies.get('jwttoken')
	try:
		jwt_dict = jwt.decode(
			access_token, JWT_SECRET,
			algorithms=[JWT_ALGORITHM], options={'verify_exp': False}
			)
		print("!!!!!!!!!",jwt_dict, access_token)
	except AttributeError as e:
		print("JWTError occurred decoding to dict:", e)
	else:
		user_pub_id = jwt_dict['sub']
		return jsonify(
			{"Authenticated": user_pub_id,
			 "Bearer": generate_token(user_pub_id)})


# USERS
#=======================

def retrieve_all_users():
	"""
	Retrieve list of all records in Users table
	:return:            list of matching objects
	"""
	users = User.query.all()
	if users:
		return jsonify(200, [usr.serialize() for usr in users])
	else:
		return jsonify(204, f"Records not found.")


def retrieve_one_user(user_id):
	"""
	Return one record from the collection matching given ID
	:param user_id:   	user basic ID number
	:return:            matching data object
	"""
	query = User.query.filter(User.id == user_id).one_or_none()
	if query:
		return jsonify(200, query.detailed())
	else:
		return jsonify(404, f"Record not found for ID: {user_id}")


def register():
	"""
	Create new User instance from given credentials and optional extra data
	:param login:		given user login
	:param password:	given password for authentication
	:param first_name:	user first name
	:param last_name:	user last name
	:param email:		user email address
	:return:            list of matching objects
	"""
	login = request.json.get("login", None)
	password = request.json.get("password", None)
	first_name = request.json.get("first_name")
	last_name = request.json.get("last_name")
	email = request.json.get("email")
	print(login, password, first_name, last_name, email)

	query = User.query.filter_by(login=login).one_or_none()

	if query:
		return jsonify(
			201, "Similar instance already exists. Try different login.")
	else:
		new_user = User(login, password)
		if first_name:
			new_user.first_name = first_name
		if last_name:
			new_user.last_name = last_name
		if email:
			new_user.email = email
		fourth_set.append(new_user.serialize())
		db.session.add(new_user)
		db.session.commit()
		new = User.query.filter_by(login=login).one()
		return jsonify({
				"Registered with": new_user.public_id,
				"Bearer": generate_token(new.public_id)
				})


def log_in():
	"""
	The Simplest API login.
	:param 		requestBody: require passing correct login and password of
	existing user
	:return 	JWT: encoded authorization token for given user on success,
	401/404 on incorrect credentials
	"""
	user = request.get_json()
	lgn = user['login']
	pwd = user['password']

	query = User.query.filter_by(login=lgn).one_or_none()
	if query:
		check = chpass(query.password, pwd)
		if check:
			# print(f"Credentials correct for {lgn}")
			jwt_token = generate_token(query.public_id)
			auth_dict = {
				"Authenticated as": query.login,
				"Bearer": jwt_token
				}
			response = make_response(jsonify(auth_dict))
			# response.headers["Authorization"] = f"Bearer {jwt_token}"
			# response.set_cookie(key='jwttoken', value=jwt_token)
			return response
		else:
			jsonify(401, "Wrong password.")
	else:
		return jsonify(404, "Login not found in database. Please check Your "
							"input again or register.")


def to_json():
	third_set.extend(fourth_set)
	data_set = json.dumps(third_set)
	with open('backup.json', 'a') as backup:
		backup.write(third_set)


if __name__ == '__main__':
	init_db()
	conned_app.add_api('openapi.yaml', resolver=RestyResolver('run'))
	# conned_app.run(host='127.0.0.1', port=5000, debug=True)
	# port = int(os.environ.get('PORT', 5000))
	# conned_app.run(host='0.0.0.0', port=port, debug=False)
	conned_app.run()
