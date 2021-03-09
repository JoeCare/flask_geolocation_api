from settings import db, mm, app, conned_app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Table, Column, Integer, Text, JSON, String, \
    create_engine
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import ipaddress
from cryptography.fernet import Fernet
# Base = declarative_base()
import base64 as b64
# engine = create_engine("sqlite+pysqlite:///:memory:", echo=True)
# db = SQLAlchemy(app)
# db.app = app


class Geolocation(db.Model):
    __tablename__= 'geolocation'
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
        return {
            "id": self.id,
            # "user_input": self.input_data,
            "ip_address": self.ip,
            "ip_type": self.type,
            # "continent": self.continent_code,
            "continent_name": self.continent_name,
            # self.country_code,
            "country": self.country_name,
            "region": self.region_name,
            "city": self.city,
            "latitude": self.latitude,
            "longitude": self.longitude,
            }

    def short(self):
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
    login = Column(String, nullable=False)
    password = Column(String, nullable=False)
    user_identifier = Column(db.LargeBinary, nullable=False)

    # user_key = b'2tpdHLuGaGC4oYu-f3rNcWyF6JjB8Z87huE1_DfmvbA='

    def __init__(self, login, password, identifier=Fernet.generate_key()):
        self.login = login
        self.user_identifier = identifier
        fernet_cipher = Fernet(identifier)
        cipher_encrypt = fernet_cipher.encrypt(bytes(password, 'utf-8'))
        self.password = cipher_encrypt

        deciphered = fernet_cipher.decrypt(ciphered)
        to_text = bytes(deciphered).decode("utf-8")


class UserSchema(mm.SQLAlchemyAutoSchema):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    class Meta:
        model = User
        alchemy_session = db.session
        load_instance = True
        exclude = ['password']


def ip_validator(_ip):
    ip = _ip.replace("'","")
    try:
        return bool(ipaddress.ip_address(ip))
    except ValueError:
        return False


test_set = ['160.39.144.19',
            '134.201.250.155',
            '110.174.165.78',
            '72.229.28.185',
            '250.10.247.40',
            '58.146.87.212',
            '0.242.187.128',
            '189.147.147.15',
            '50.152.25.31',
            '74.135.229.139',
            '223.180.89.79',
            '149.154.86.1',
            '76.0.198.12',
            '179.111.92.213',
            '251.219.146.9',
            '146.150.225.180',
            '43.30.40.132',
            '88.230.139.194',
            '219.143.81.80'
            ]

second_set = [
    "241.28.103.93",
    "161.47.118.200",
    "73.98.2.50",
    "220.0.28.104",
    "39.165.71.101",
    "164.189.52.190",
    "206.80.10.154",
    "3.131.56.210",
    "155.22.16.173",
    "32.1.213.113",
    ]

third_set = []


def init_db():
    db.create_all()

        # return render_template('index.html',
            #                        message='You have already submitted feedback')

    #
    # def add_new(_name, _price, _isbn):
    #     new_location = Geolocation()
    #     db.session.add(new_location)
    #     db.session.commit()


    #
    # def get_all():
    #     return [Book.json(book) for book in Book.query.all()]
    #
    # def get_by(_isbn):
    #     return Book.query.filter_by(isbn=_isbn).first()
    #
    # def delete_by(_isbn):
    #     Book.query.filter_by(isbn=_isbn).delete()
    #     db.session.commit()
    #
    # def change_by(_isbn, **kwargs):
    #     replaced_object = Book.query.filter_by(isbn=_isbn).first()
    #     if "price" in kwargs.keys():
    #         replaced_object.price = kwargs["price"]
    #     if "name" in kwargs.keys():
    #         replaced_object.name = kwargs["name"]
    #     db.session.commit()
    #
    # def replace_by(_isbn, _name, _price):
    #     replaced_object = Book.query.filter_by(isbn=_isbn).first()
    #     print(type(replaced_object))
    #     replaced_object.price = _price
    #     replaced_object.name = _name
    #     db.session.commit()

    # def __repr__(self):
    #     book_object = {
    #         "name": self.name,
    #         "price": self.price,
    #         "isbn": self.isbn
    #     }
    #     return json.dumps(book_object)
    #     # used only for console info
