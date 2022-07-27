from flask import Flask,render_template,request,redirect
from flask_cors import CORS,cross_origin
import pickle
import pandas as pd
import numpy as np

app = Flask(__name__)
cors = CORS(app)
model = pickle.load(open("Bike_Price_Prediction.pkl",'rb'))
car = pd.read_csv('Clened_Bike_Details.csv')

@app.route('/',methods=['GET','POST'])
def index():
    names = sorted(car['bike_name'].unique())
    brands = sorted(car['brand'].unique())
    owners = sorted(car['owner'].unique())


    #print(companies)
    #companies.insert(0,'Select Company')
    return render_template('Bike_Price_Predictor.html',names=names, brands=brands, owners=owners)


@app.route('/predict',methods=['POST'])
@cross_origin()
def predict():

    name = request.form.get('name')
    brand = request.form.get('brand')
    kms = request.form.get('kms')
    owner = request.form.get('owner')
    age = request.form.get('age')
    power = request.form.get('power')

    #print(company_name,year,kilometer_driven,fuel_type,transmission,owner_type,mileage,engine,horsepower,seats)

    prediction = model.predict(pd.DataFrame(columns=["bike_name", "kms_driven", "owner", "age", "power", "brand"],
                                            data=np.array([name,kms,owner,age,power,brand]).reshape(1,6)))

    print(prediction)

    return str(np.round(prediction[0],2))



if __name__=='__main__':
    app.run(debug=True, port=5004)