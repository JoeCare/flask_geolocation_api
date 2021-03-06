from sqlalchemy import Column, Integer, Text, JSON, String
from werkzeug.security import generate_password_hash as gpass
from werkzeug.security import check_password_hash as chpass
import ipaddress, uuid
from dotenv import load_dotenv, find_dotenv
from app import db, mm

load_dotenv(find_dotenv())


class Geolocation(db.Model):
    __tablename__ = 'geolocation'
    id = Column(Integer, primary_key=True, autoincrement=True,
                nullable=True)
    input_data = Column(Text, nullable=True)
    ip = Column(String, nullable=True)
    type = Column(String, nullable=True)
    continent_code = Column(String, nullable=True)
    continent_name = Column(String, nullable=True)
    country_code = Column(String, nullable=True)
    country_name = Column(String, nullable=True)
    region_name = Column(String, nullable=True)
    city = Column(String, nullable=True)
    latitude = Column(String, nullable=True)
    longitude = Column(String, nullable=True)
    location = Column(JSON, nullable=True)
    visible = Column(Integer, nullable=False, default=1)

    def __init__(self, dictionary, user_input='check'):
        setattr(self, "input_data", user_input)
        for k, v in dictionary.items():
            setattr(self, k, v)

    def serialize(self):
        """Serialize record fields for list view"""
        return {
            "id": self.id,
            "ip_address": self.ip,
            "ip_type": self.type,
            "continent_name": self.continent_name,
            "country": self.country_name,
            "region": self.region_name,
            "city": self.city,
            "latitude": self.latitude,
            "longitude": self.longitude,
            }

    def short(self):
        """Serialize record output with most essential fields."""
        return {
            "id": self.id,
            "ip_address": self.ip,
            "county_code": self.country_code,
            "city": self.city,
            }


class GeolocationSchema(mm.SQLAlchemyAutoSchema):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    class Meta:
        model = Geolocation
        alchemy_session = db.session
        load_instance = True
        exclude = ['visible']


class User(db.Model):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    public_id = Column(String(50), unique=True)
    login = Column(String, nullable=False)
    password = Column(Text, nullable=False)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    email = Column(String, nullable=True)

    def __init__(self, login, password):
        self.password = gpass(password, salt_length=6)
        self.login = login
        self.public_id = str(uuid.uuid4())

    def detailed(self):
        """Serialize record with all available data"""
        return {
            "user_id": self.id,
            "login": self.login,
            "password_hash": self.password,
            "firstname": self.first_name,
            "lastname": self.last_name,
            "email": self.email,
            "public_id": self.public_id,
            }

    def serialize(self):
        """Serialize record output without password"""
        return {
            "user_id": self.id,
            "login": self.login,
            "firstname": self.first_name,
            }

    @staticmethod
    def login_validation(_password, current_pass=password, usr_id=id):
        if current_pass == _password:
            return usr_id
        elif chpass(current_pass, _password):
            return usr_id
        else:
            return False


class UserSchema(mm.SQLAlchemyAutoSchema):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    class Meta:
        model = User
        alchemy_session = db.session
        load_instance = True
        exclude = ['password', 'email']


def ip_validator(_ip):
    ip = _ip.replace("'","")
    try:
        return bool(ipaddress.ip_address(ip))
    except ValueError:
        return False


# def init_db():
#     db.create_all()
# db.create_all()
