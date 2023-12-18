from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_pymongo import PyMongo
from pymongo import MongoClient

client = MongoClient('mongodb+srv://vercel-admin-user-641df86deec22841cd00f989:U7MK7TOONktRvOOR@cluster0.myy76mk.mongodb.net/myFirstDatabase?retryWrites=true&w=majority')
app.config['MONGO_URI'] = 'mongodb+srv://vercel-admin-user-641df86deec22841cd00f989:U7MK7TOONktRvOOR@cluster0.myy76mk.mongodb.net/myFirstDatabase?retryWrites=true&w=majority'
app.config['SECRET_KEY'] = 'a6d217d048fdcd227661b755'
db = client['Reno_admin_databases']
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)

from App import routes 
