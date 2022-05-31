from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from requests import request
from wtforms import StringField, PasswordField, BooleanField
from wtforms import validators
from wtforms.validators import InputRequired, Email, Length
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'iniadalahsecretkey'
Bootstrap(app)

# Login Form
class LoginForm(FlaskForm):
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('remember me')

# Regist Form
class RegisterForm(FlaskForm):
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])
    email = StringField('email', validators=[InputRequired(), Email(message='Email Tidak Benar'), Length(max=50)])

# Routing Flask
@app.route("/")
def login():
    form = LoginForm()

    return render_template("Login.html", form=form)

@app.route("/homepage")
def homepage():
    return render_template("Homepage.html")

# @app.route("/signup")
# def signup():
#     #Form Pendaftaran Akun
#     form = RegisterForm()

#     return render_template("Sign Up.html", form=form)

@app.route("/riwayat", methods=['GET'])
def riwayat():
    #Form Search Riwayat Data Pasien
    return render_template("Riwayat.html")

@app.route("/cari", methods=['GET'])
def cari():
    #Tabel Hasil Search Data Riwayat Pasien
    return render_template("Cari.html")


@app.route("/screening", methods=['GET', 'POST'])
def screening():
    #Form Uploading Data Pasien
    return render_template("Form.html")

if __name__ == "__main__":
    app.run(debug=True)