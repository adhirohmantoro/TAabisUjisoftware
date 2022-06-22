import os
import math   
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

#classification Library
from tensorflow.keras.preprocessing.image import load_img
from tensorflow.keras.models import Model, load_model
from tensorflow.keras.applications import inception_v3
import PIL
from PIL import Image

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

model = inception_v3.InceptionV3(
    include_top=True,
    weights=None,
    input_tensor=None,
    input_shape=(224,224,3),
    pooling=None,
    classes=3,
    classifier_activation="softmax",
    )
model.load_weights('Inception_Unmasked.hdf5')

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

@app.route("/cari/<nik>", methods=['GET'])
def cari(nik):
    # Get the patient
    cursor = mysql.connection.cursor()
    cursor.execute(''' SELECT * FROM patients WHERE nik=%s AND nik=%s ORDER BY id DESC ''', (nik, nik))
    patients = cursor.fetchall()
    print(patients)
    #Tabel Hasil Search Data Riwayat Pasien
    return render_template("Cari.html", patients=enumerate(patients))


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
        image = Image.open(UPLOAD_FOLDER+'/data_x_ray_'+patient_id+'.jpg')
        newsize = (224,224)
        image = image.resize(newsize)
        # image = target_size=None
        prediction = model.predict(image)

        print(prediction)

    return render_template("Form.html")

@app.route("/screening/<patient_id>", methods=['GET'])
def view_screening(patient_id):
    # Get the patient
    cursor = mysql.connection.cursor()
    cursor.execute(''' SELECT * FROM patients WHERE id=%s AND id=%s ''', (patient_id, patient_id))
    patient = cursor.fetchone()
    # Get the patient data
    patient_id = patient[0]
    nama = patient[1].split(' ')
    nik = patient [2]
    jenis_kelamin = patient[3]
    if jenis_kelamin == 'l':
        jenis_kelamin = 'Laki-laki'
    else:
        jenis_kelamin = 'Perempuan'
    tmpt_tgl_lahir = patient[4]+', '+patient[5]
    alamat = patient[6]
    no_telp = patient[7]
    # Get file, convert CSV file to array
    data_arduino_file = open('storage/data_arduino_'+str(patient_id)+'.csv', "r").readlines()
    data_respiration_file = open('storage/data_respiration_rate_'+str(patient_id)+'.csv', "r").readlines()
    # Get the average HEARTRATE, SPO2, respiration
    avg_heartrate = 0
    avg_spo2 = 0
    avg_respiration = 0
    for line_pos, line in enumerate(data_arduino_file):
        if line_pos != 0:
            line_arr = line.split(',')
            avg_heartrate += int(line_arr[1])
            avg_spo2 += int(line_arr[2])
    else:
        avg_heartrate /= (len(data_arduino_file) -  1)
        avg_spo2 /= (len(data_arduino_file) -  1)
        avg_heartrate = math.ceil(avg_heartrate)
        avg_spo2 = math.ceil(avg_spo2)

    for line_pos, line in enumerate(data_respiration_file):
        if line_pos != 0:
            avg_respiration += int(line.split(',')[1])
    else:
        avg_respiration /= (len(data_respiration_file) -  1)
        avg_respiration = math.ceil(avg_respiration)

    return render_template(
        "HasilSkrining.html", 
        nama=nama, 
        nik=nik, 
        jenis_kelamin=jenis_kelamin, 
        tmpt_tgl_lahir=tmpt_tgl_lahir, 
        alamat=alamat, 
        no_telp=no_telp,
        avg_heartrate=avg_heartrate,
        avg_spo2=avg_spo2,
        avg_respiration=avg_respiration
    )



if __name__ == "__main__":
    app.run(debug=True)