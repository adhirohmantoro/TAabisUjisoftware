import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
# from requests import request
import sqlalchemy
from wtforms import StringField, PasswordField, BooleanField
from wtforms import validators
from wtforms.validators import InputRequired, Email, Length
from flask_sqlalchemy import SQLAlchemy
from flask_mysqldb import MySQL

UPLOAD_FOLDER = 'storage'

app = Flask(__name__)
app.config['SECRET_KEY'] = 'iniadalahsecretkey'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'flask_app'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

 
mysql = MySQL(app)

Bootstrap(app)

# Login Form
class LoginForm(FlaskForm):
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('remember me')

# # Regist Form (tidak dipakai)
# class RegisterForm(FlaskForm):
#     username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
#     password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])
#     email = StringField('email', validators=[InputRequired(), Email(message='Email Tidak Benar'), Length(max=50)])

# Routing Flask
@app.route("/", methods=['GET'])
def login():
    # sudah logged in
    # if session['username']:
    #     return redirect(url_for('homepage'))
    form = LoginForm()
    return render_template("Login.html", form=form)

@app.route("/login", methods=['POST'])
def login2():
    username = request.form['usr']
    password = request.form['password']
    cursor = mysql.connection.cursor()

    cursor.execute(''' SELECT * FROM user WHERE username=%s AND password=%s LIMIT 1 ''', (username, password))
    rows = cursor.fetchall()

    if len(rows):
        session['username'] = username
        return redirect(url_for('homepage'))
    else:
        return render_template("Login.html")

@app.route("/logout", methods=['POST'])
def logout():
    session.pop('username')
    return redirect(url_for('login'))


@app.route("/homepage")
def homepage():
    username = session['username']
    return render_template("Homepage.html", username=username)

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
    if request.method == 'POST':
        # Create new patient
        cursor1 = mysql.connection.cursor()
        sql = ''' INSERT INTO patients (nama, nik, jenis_kelamin, tempat_lahir, tanggal_lahir, alamat, telp, berat_badan, tinggi_badan, gejala) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) '''
        gejala = ' '.join(request.form.getlist('gejala[]'))
        values = (
            request.form['name'], request.form['nik'], 
            request.form['jkelamin'], request.form['tmpt_lahir'], 
            request.form['tgl_lahir'], request.form['alamat'], 
            request.form['telp'], request.form['bb'], 
            request.form['tb'], gejala
        )
        cursor1.execute(sql, values)
        mysql.connection.commit()

        # Get the created patient ID
        cursor2 = mysql.connection.cursor()
        cursor2.execute(''' SELECT MAX(id) FROM patients ''')
        patient_id = cursor2.fetchone()
        patient_id = str(patient_id[0])

        # Save the patient files
        data_arduino_file = request.files['data_arduino']
        data_respiration_rate_file = request.files['data_respiration_rate']
        data_x_ray_file = request.files['data_x_ray']

        data_arduino_file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'data_arduino_'+patient_id+'.csv'))
        data_respiration_rate_file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'data_respiration_rate_'+patient_id+'.csv'))
        data_x_ray_file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'data_x_ray_'+patient_id+'.jpg'))

        # Classification


    return render_template("Form.html")



if __name__ == "__main__":
    app.run(debug=True)