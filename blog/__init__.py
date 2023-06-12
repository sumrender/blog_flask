import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from dotenv import load_dotenv

print(load_dotenv("/home/booklists/blog_flask/.env"))
print(os.environ)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'WE4U932U4DJKDFAJF993'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'user.login'
# 'login' is the name of the function
login_manager.login_message_category = 'info'

# routes placed here to prevent circular imports
from blog.user.routes import user
from blog.post.routes import post
from blog.main.routes import main
from blog.error.routes import error

app.register_blueprint(user)
app.register_blueprint(post)
app.register_blueprint(main)
app.register_blueprint(error)

print("=================  Application is live! ====================")
sender=os.environ.get('EMAIL_USER')
print(f"current email sender: {sender}")