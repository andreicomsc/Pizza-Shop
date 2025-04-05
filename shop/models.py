from . import db, login_manager
from flask_login import UserMixin


class Item(db.Model):
  itemid = db.Column(db.Integer, primary_key=True)  
  name = db.Column(db.Text, nullable=False)
  description = db.Column(db.Text, nullable=False)
  description2 = db.Column(db.Text, nullable=False)
  picture = db.Column(db.String(20), nullable=False)
  price = db.Column(db.Float, nullable=False)
  eco = db.Column(db.Integer, nullable=False)

  def __repr__(self):
    return f"User('{self.itemid}', '{self.name}', '{self.price}')"


class User(db.Model, UserMixin):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(25), unique=True, nullable=False)
  hashed_password = db.Column(db.String(128))

  def __repr__(self):
    return f"User('{self.username}', '{self.hashed_password}')"

@login_manager.user_loader
def load_user(user_id):
  return User.query.get(int(user_id))


class Review(db.Model):
  reviewid = db.Column(db.Integer, primary_key=True)  
  reviewnick = db.Column(db.Text, nullable=False)
  reviewtext = db.Column(db.Text, nullable=False)
  reviewitem = db.Column(db.Integer, db.ForeignKey("item.itemid"), nullable=False)