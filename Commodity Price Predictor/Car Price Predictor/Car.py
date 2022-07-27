from flask import Flask,render_template,request,redirect
from flask_cors import CORS,cross_origin
import pickle
import pandas as pd
import numpy as np

app = Flask(__name__)
cors = CORS(app)
model = pickle.load(open("Car_Price_Prediction.pkl",'rb'))
car = pd.read_csv('Cleaned_Car_Details.csv')

@app.route('/',methods=['GET','POST'])
def index():
    companies = sorted(car['Name'].unique())
    year = sorted(car['Year'].unique(),reverse=True)
    fuel_type = sorted(car['Fuel_Type'].unique())
    transmission = sorted(car['Transmission'].unique())
    owner_type = sorted(car['Owner_Type'].unique())
    seats = sorted(car['Seats'].unique())

    print(companies)
    companies.insert(0,'Select Company')
    return render_template('Car_Price_Predictor.html',companies=companies, year=year, fuel_type=fuel_type, transmission=transmission,
                           owner_type=owner_type, seats=seats)


@app.route('/predict',methods=['POST'])
@cross_origin()
def predict():

    company_name = request.form.get('company_name')
    fuel_type = request.form.get('fuel_type')
    year = int(request.form.get('year'))
    kilometer_driven = float(request.form.get('kilometer_driven'))
    transmission = request.form.get('transmission')
    mileage = float(request.form.get('mileage'))
    owner_type = request.form.get('owner_type')
    engine = request.form.get('engine')
    horsepower = float(request.form.get('horsepower'))
    seats = request.form.get('seats')

    print(company_name,year,kilometer_driven,fuel_type,transmission,owner_type,mileage,engine,horsepower,seats)

    prediction = model.predict(pd.DataFrame(columns=["Name", "Year", "Kilometers_Driven", "Fuel_Type", "Transmission", "Owner_Type", "Mileage", "Engine","Power", "Seats"],
                                            data=np.array([company_name,year,kilometer_driven,fuel_type,transmission,owner_type,mileage,engine,horsepower,seats]).reshape(1,10)))
    print(prediction)

    return str(np.round(prediction[0],2))



if __name__=='__main__':
    app.run(debug=True)