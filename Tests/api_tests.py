import httpie, httpie_jwt_auth
from httpie.config import Config

class HttpieConfig(Config):


# Variables:
base_url = "http://127.0.0.1:5000/"
first_endpoint = "geolocations/"
auth = [{"login": "admin", "password": "admini"}]

# Syntax legend:
# $ http [flags] [METHOD] URL [ITEM [ITEM]]

#     HTTPmethod,        HTTPheaders and  JSONs:
# $ http PUT pie.dev/put X-API-Token:123 name=John

test_endpoint = {
	"geo/":
		"http --verbose GET :5000/geolocations/",
	"/login/":
		"http --verbose POST :5000/auth/login login=admin password=admini",
	"users":
		"http --format-options json.indent:4 :5000/users"
	}



# -v [flag] Print the whole HTTP exchange (request and response).
# This option also enables --all (see below).
