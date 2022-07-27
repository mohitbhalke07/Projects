from flask import Flask,render_template,request,redirect
from flask_cors import CORS,cross_origin
import pickle
import pandas as pd
import numpy as np

app = Flask(__name__)
cors = CORS(app)
model = pickle.load(open("Mobile_Price_Prediction.pkl",'rb'))
car = pd.read_csv('Cleaned_Mobile_Details.csv')

@app.route('/',methods=['GET','POST'])
def index():
    brands = sorted(car['Brand'].unique())
    names = sorted(car['Product Name'].unique(),reverse=True)
    rams = sorted(car['RAM'].unique())
    storages = sorted(car['Internal storage'].unique())
    batteries = sorted(car['Battery capacity (mAh)'].unique())


    #print(companies)
    #companies.insert(0,'Select Company')
    return render_template('Mobile_Price_Predictor.html',brands=brands, names=names, rams=rams, storages=storages,batteries=batteries)


@app.route('/predict',methods=['POST'])
@cross_origin()
def predict():

    brands = request.form.get('brand')
    names = request.form.get('name')
    rams = request.form.get('ram')
    storages = request.form.get('storage')
    batteries = request.form.get('battery')
    rear_camera = request.form.get('rear_camera')
    front_camera = request.form.get('front_camera')
    screen_size = request.form.get('screen_size')

    #print(company_name,year,kilometer_driven,fuel_type,transmission,owner_type,mileage,engine,horsepower,seats)

    prediction = model.predict(pd.DataFrame(columns=["Brand", "Product Name", "RAM", "Internal storage", "Battery capacity (mAh)", "Rear camera", "Front camera", "Screen size (inches)"],
                                            data=np.array([brands,names,rams,storages,batteries,rear_camera,front_camera,screen_size]).reshape(1,8)))

    print(prediction)

    return str(np.round(prediction[0],2))



if __name__=='__main__':
    app.run(debug=True, port=5003)