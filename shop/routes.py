from flask import render_template, redirect, url_for, flash, request, session
from . import app, db, bcrypt
from .models import Item, User, Review
from .forms import SortForm, RegistrationForm, LoginForm, CheckoutForm
from flask_login import login_required, login_user, current_user, logout_user
from sqlalchemy import desc
import re
from flask_wtf.csrf import CSRFError


checkout = False

@app.errorhandler(404)
def page_not_found(e):
  return render_template("404.html", title="Page not found", error=e.description), 404

@app.errorhandler(500)
def server_error(e):
  return render_template("500.html", title="Server error", error=e.description), 500

@app.errorhandler(CSRFError)
def csrf_error(e):
    return render_template("csrf_error.html", title="Token error", error=e.description), 400


@app.route("/")
@app.route("/home", methods=["GET","POST"])
def home(): 
  items = Item.query.order_by(desc(Item.price)).all()
  
  form = SortForm()
  if form.validate_on_submit():   
    sort_type = form.sort_type.data 
    if sort_type == "price_high":
      items = Item.query.order_by(desc(Item.price)).all()
    elif sort_type == "price_low":
      items = Item.query.order_by(Item.price).all()    
    elif sort_type == "eco_low":
      items = Item.query.order_by(Item.eco).all()

  query = str(request.args.get("query")).lower()
  query = re.sub("[^a-z]", " ", query).split()  
  if query and query[0] != "none":
    query_items = []
    for i in items:
      query_item = (i.name + " " + i.description + " " + i.description2).lower()
      query_item = re.sub("[^a-z]", " ", query_item)
      item_valid = True
      for q in query:
        if q not in query_item:
          item_valid = False
          break
      if item_valid:
        query_items.append(i)
    items = query_items

  reviews_table = Review.query.all()
  reviews = {}
  for i in reviews_table:
    if i.reviewitem in reviews:
      reviews[i.reviewitem] += 1
    else:
      reviews[i.reviewitem] = 1  

  return render_template("home.html", title="Menu", items=items, query=query, form=form, reviews=reviews)


@app.route("/item/<int:item_id>")
def item(item_id):
  item = Item.query.get_or_404(item_id)
  reviews = Review.query.filter_by(reviewitem = item_id)
  return render_template("item.html", title = item.name, item=item, reviews=reviews) 


@app.route("/register", methods=["GET","POST"])
def register():
  if current_user.is_authenticated:
    flash("You are registered and logged in. To register another user, please log out first.")
    return redirect(url_for("home"))
  form = RegistrationForm()
  if form.validate_on_submit():
    hp = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
    user = User(username = form.username.data, hashed_password = hp)
    db.session.add(user)
    db.session.commit()
    flash(f'The user "{user.username}" has been created.')
    return redirect(url_for("login"))
  return render_template("register.html", title="Register", form=form)


@app.route("/login", methods=["GET","POST"])
def login():  
  if current_user.is_authenticated:
    flash("You are already logged in. To use another account, please log out first.")
    return redirect(url_for("home"))
  form = LoginForm()
  if form.validate_on_submit():
    user = User.query.filter_by(username = form.username.data).first()
    if user is not None and bcrypt.check_password_hash(user.hashed_password, form.password.data):
      login_user(user)
      next_page = request.args.get("next")      
      if "carts" not in session:
        session["carts"] = {}     
      if current_user.username not in session["carts"]:
        session["carts"][current_user.username] = {}           
      return redirect(next_page) if next_page and next_page != "/addcart" else redirect(url_for("home"))
    else:      
      return redirect(url_for("error"))    
  return render_template("login.html", title="Login", form=form)


@app.route("/logout")
def logout():  
  logout_user()   
  return redirect(url_for("home"))


@app.route("/addcart", methods=["GET","POST"])
@login_required
def addcart():
  item_id = request.form.get("item_id")
  quantity = request.form.get("quantity")
  item = Item.query.filter_by(itemid = item_id).first()     
  if item_id and quantity:      
      if item_id in session["carts"][current_user.username]:
        session["carts"][current_user.username][item_id]["quantity"] += int(quantity)
      else:
        session["carts"][current_user.username][item_id] = {"picture":item.picture, "name":item.name, "price":item.price, "quantity":int(quantity)}  
      session.modified = True      
  return redirect(request.referrer)


@app.route("/cart")
@login_required
def cart():   
  if len(session["carts"][current_user.username]) == 0:
      flash("Your shopping basket is empty.")
      return redirect(url_for("home"))   
  total = 0
  for i in session["carts"][current_user.username].values():
    total += i["price"] * i["quantity"]  
  return render_template("cart.html", title="Shopping basket", total=total)  


@app.route("/remove", methods=["POST"])
@login_required
def remove():
  item_id = request.form.get("item_id")
  quantity = request.form.get("quantity")
  q = int(quantity)   
  if q == session["carts"][current_user.username][item_id]["quantity"]:
    session["carts"][current_user.username].pop(item_id, None)
  else:
    session["carts"][current_user.username][item_id]["quantity"] -= q
  session.modified = True  
  return redirect(url_for("cart")) 


@app.route("/checkout", methods=["GET","POST"])
@login_required
def checkout(): 
  if len(session["carts"][current_user.username]) == 0:
      flash("Your shopping basket is empty.")
      return redirect(url_for("home"))    
  form = CheckoutForm()    
  total = 0
  for i in session["carts"][current_user.username].values():
    total += i["price"] * i["quantity"]  
  if form.validate_on_submit(): 
    global checkout
    checkout = True
    return redirect(url_for("checkouts"))    
  return render_template("checkout.html", title="Checkout", form=form, total=total)


@app.route("/checkouts")
@login_required
def checkouts():   
  if len(session["carts"][current_user.username]) == 0:
      flash("Your shopping basket is empty.")
      return redirect(url_for("home"))
  else:
    global checkout   
    if checkout == True:  
      checkout = False  
      session["carts"][current_user.username] = {}
      session.modified = True
      return render_template("checkouts.html", title="Checkout success")
    else:
      flash("Please enter your payment details first.")
      return redirect(url_for("checkout"))


@app.route("/error")
def error():     
  if current_user.is_authenticated:
    flash("You are already logged in.")
    return redirect(url_for("home"))
  return render_template("error.html", title="Login error")


@app.route("/addreview/<int:item_id>", methods=["GET","POST"])
@login_required
def addreview(item_id):    
  review_nick = request.form.get("review_nick")
  review_text = request.form.get("review_text")  
  if item_id and review_nick and review_text:
    review = Review(reviewnick=review_nick, reviewtext=review_text, reviewitem=item_id)     
    db.session.add(review)
    db.session.commit()    
    return redirect(request.referrer)   
  return redirect(url_for("item", item_id=item_id))