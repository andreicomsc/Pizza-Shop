from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Regexp, EqualTo, ValidationError
from .models import User
import re


class SortForm(FlaskForm):
  sort_type=SelectField("Sort by: ",
  choices=[("price_high", "Price: High to Low"), ("price_low", "Price: Low to High"), ("eco_low", "Eco: Low to High")],
  default="price_high", render_kw={"onchange": "this.form.submit()"})


class RegistrationForm(FlaskForm):
  username = StringField("Username", validators=[DataRequired(), Length(min=5, max=20),
                                     Regexp("^[a-zA-Z0-9]{5,20}$",
                                     message="Username can contain letters and numbers only.")])
  password = PasswordField("Password", validators=[DataRequired(), Length(min=5, max=20)])
  confirm_password = PasswordField("Confirm Password", validators=[DataRequired(),
                                                       EqualTo("password",
                                                       message="Passwords do not match.")])
  submit = SubmitField("Register")

  def validate_username(self, username):
    user = User.query.filter_by(username=username.data).first()
    if user:
      raise ValidationError("This username already exists.")

  def validate_password(self, password):
    if not re.match("^[a-zA-Z0-9]{5,20}$", password.data):
      raise ValidationError("Password can contain letters and numbers only.")


class LoginForm(FlaskForm):
  username = StringField("Username", validators=[DataRequired(), Length(min=5, max=20)])
  password = PasswordField("Password", validators=[DataRequired(), Length(min=5, max=20)])
  submit = SubmitField("Login")


class CheckoutForm(FlaskForm):
  name = StringField("Name on card: ", validators=[DataRequired(), 
                                                  Regexp("^[a-z A-Z]{3,30}$", 
                                                  message="The name can contain letters only.")])
  card_no = StringField("Card number: ", validators=[DataRequired(),
                                                    Regexp("^[\\d]{16}$",
                                                    message="Please enter a 16 digits card number without spaces.")],
                                                    render_kw={"placeholder": "Enter a 16 digit card number."})
  submit = SubmitField("Pay")