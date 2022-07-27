from flask import Flask,render_template,request,redirect
from flask_cors import CORS,cross_origin
import pickle
import pandas as pd
import numpy as np

app = Flask(__name__)
cors = CORS(app)
model = pickle.load(open("Laptop_Price_Prediction.pkl",'rb'))
car = pd.read_csv('Cleaned_Laptop_Details.csv')

@app.route('/',methods=['GET','POST'])
def index():
    names = sorted(car['Name'].unique())
    processors = sorted(car['Processor'].unique(),reverse=True)
    rams = sorted(car['RAM'].unique())
    operating_system = sorted(car['Operating System'].unique())
    storages = sorted(car['Storage'].unique())

    #print(companies)
    #companies.insert(0,'Select Company')
    return render_template('Laptop_Price_Predictor.html',names=names, processors=processors, rams=rams, operating_system=operating_system,
                           storages=storages)


@app.route('/predict',methods=['POST'])
@cross_origin()
def predict():

    name = request.form.get('name')
    processor = request.form.get('processor')
    ram = int(request.form.get('ram'))
    display = float(request.form.get('display'))
    operating = request.form.get('operating')
    storage = float(request.form.get('storage'))


    #print(company_name,year,kilometer_driven,fuel_type,transmission,owner_type,mileage,engine,horsepower,seats)

    prediction = model.predict(pd.DataFrame(columns=["Name", "Processor", "RAM", "Operating System", "Storage", "Display"],
                                            data=np.array([name,processor,ram,operating,storage,display]).reshape(1,6)))
    print(prediction)

    return str(np.round(prediction[0],2))



if __name__=='__main__':
    app.run(debug=True, port=5002)