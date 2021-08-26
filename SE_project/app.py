from flask import Flask, jsonify, flash, redirect, render_template, request, session, url_for
import os
from flask_pymongo import PyMongo
import bcrypt
import pandas as pd
import joblib
import numpy as np
import pickle
from flask_mongoengine import MongoEngine
from flask_user import login_required, UserManager, UserMixin

app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'Medical_prediction'
app.config['MONGO_URI'] = 'mongodb+srv://Aash:aash@secluster.mi2ch.mongodb.net/Medical_prediction?retryWrites=true&w=majority'


mongo = PyMongo(app)

app.secret_key = 'whydowedothis'


MONGODB_SETTINGS = {
        'db': 'Medical_prediction',
        'host': 'mongodb+srv://Aash:aash@secluster.mi2ch.mongodb.net/<Medical_prediction>?retryWrites=true&w=majority'}


model = pickle.load(open('model.pkl','rb'))

diabetesDF = pd.read_csv('diabetes.csv')


@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/home')
def home():
    return render_template('Home.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/predict',  methods=['POST', 'GET'])
def predict():
    if request.method == 'POST':
        name = request.form['name']
        Glucose = request.form['Glucose']
        Blood_Pressure = request.form['Blood_Pressure']
        Skin_Thickness = request.form['Skin_Thickness']
        Pregnancies = request.form['Pregnancies']
        D_pre_degree_function = request.form['D_pre_degree_function']
        Insulin = request.form['Insulin']
        BMI = request.form['BMI']
        Heart_Rate = request.form['Heart_Rate']
        Age = request.form['Age']
        Cigarettes = request.form['Cigarettes']
        Cholesterol = request.form['Cholesterol']

        dfTrain = diabetesDF[:650]

        trainData = np.asarray(dfTrain.drop('Outcome', 1))

        means = np.mean(trainData, axis=0)
        stds = np.std(trainData, axis=0)

        int_features = [Pregnancies, Glucose, Blood_Pressure, Skin_Thickness, Insulin, BMI, D_pre_degree_function, Age]
        final_features = [np.asarray(int_features)]

        predictionProbability = model.predict_proba(final_features)
        prediction = model.predict(final_features)
        print(prediction)
        if prediction == '[0]':
            text = "The Result Says No. Chances Of You Not Having Diabetes Are:"
            colour = "green"

        else:
            text = "The Result Says Yes. Chances Of You Having Diabetes Are:"
            colour = "red"

        return render_template('predict.html', prediction_text=prediction, Probability=predictionProbability, text=text,
                               name=name, colour=colour, Glucose=Glucose, Blood_Pressure=Blood_Pressure,
                               Skin_Thickness=Skin_Thickness, Pregnancies=Pregnancies, D_pre_degree_function=D_pre_degree_function,
                               Insulin=Insulin, BMI=BMI, Heart_Rate=Heart_Rate, Age=Age, Cigarettes=Cigarettes, Cholesterol=Cholesterol)
    else:
        return render_template('predict.html')


@app.route('/search', methods=['POST', 'GET'])
def search():
    if request.method == 'POST':
        ds = mongo.db.disease_symptom
        disease = ds.find_one({'name': request.form['des_search']})

        if disease:
            disease_symp = disease['description']
            disease_name = disease['name']
            return render_template('search.html', name=disease_name, symp=disease_symp)
        else:
            return render_template('search.html', error="Disease Not Found")

    return render_template('search.html')


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        re_password = request.form['re_password']

        if password != re_password:
            return render_template('signup.html', error="Password Does Not Match", name=name, email=email, password=password)

        if name != "" and email != "" and password != "" and re_password != "":
            users = mongo.db.users
            existing_user = users.find_one({'name': request.form['name']})
            if existing_user is None:
                hashpass = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt())
                users.insert({'name': request.form['name'], 'email': request.form['email'], 'password': hashpass})
                session['name'] = request.form['name']
                return redirect(url_for('home'))

            return render_template('signup.html', error2="That Username Already Exists!", email=email, password=password, re_password=re_password)
        else:
            return render_template('signup.html')

    return render_template('signup.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']

        if name and password:
            users = mongo.db.users
            login_user = users.find_one({'name': request.form['name']})

            if login_user:
                if bcrypt.hashpw(request.form['password'].encode('utf-8'), login_user['password']) == login_user['password']:
                    session['name'] = request.form['name']
                    return redirect(url_for('home'))

            return render_template('login.html', error="Invalid Username or Password")

        else:
            return render_template('login.html')

    return render_template('login.html')


@app.route('/help')
def help():
    return render_template('help.html')


if __name__ == '__main__':
    app.secret_key = 'whydowedothis'
    app.run(debug=True)
