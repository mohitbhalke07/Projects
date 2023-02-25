from flask import Flask, render_template, request, redirect
from flask_cors import CORS, cross_origin
import pickle
import pandas as pd
import numpy as np

app = Flask(__name__)
cors = CORS(app)
model = pickle.load(open("Loan_Sanction_Amount_model.pkl",'rb'))
data = pd.read_csv('Cleaned_Loan_Details (1).csv')

@app.route('/',methods=['GET','POST'])
def index():
    # age
    # income
    income_stabilitys = sorted(data['Income Stability'].unique())
    professions = sorted(data['Profession'].unique())
    type_emps = sorted(data['Type of Employment'].unique())
    locations = sorted(data['Location'].unique())
    # loan_amo_req
    # credit_score
    defaults = sorted(data['No. of Defaults'].unique())
    cards = sorted(data['Has Active Credit Card'].unique())
    prop_locations = sorted(data['Property Location'].unique())
    applicants = sorted(data['Co-Applicant'].unique())

    return render_template('Loan_Eligibility_Prediction.html',income_stabilitys=income_stabilitys, professions=professions, type_emps=type_emps, locations=locations, defaults=defaults, cards=cards, prop_locations=prop_locations,
                           applicants=applicants)


@app.route('/predict',methods=['POST'])
@cross_origin()
def predict():

    age = request.form.get('age')
    income = request.form.get('income')
    income_stabilitys = request.form.get('income_stabilitys')
    profession = request.form.get('profession')
    type_emps = request.form.get('type_emps')
    locations = request.form.get('locations')
    reqlnam = request.form.get('reqlnam')
    crdscore = request.form.get('crdscore')
    defaults = request.form.get('defaults')
    cards = request.form.get('cards')
    prop_locations = request.form.get('prop_locations')
    applicant = request.form.get('applicants')
    proprice = request.form.get('proprice')


    # print(age,income,profession,reqlnam,crdscore,defaults,cards,location,applicant,proprice,gender)

    prediction = model.predict(pd.DataFrame(columns=["Age", "Income (USD)", "Income Stability", "Profession", "Type of Employment", "Location", "Loan Amount Request (USD)", "Credit Score", "No. of Defaults", "Has Active Credit Card", "Property Location","Co-Applicant", "Property Price"],
                                            data=np.array([age,income,income_stabilitys,profession,type_emps,locations,reqlnam,crdscore,defaults,cards,prop_locations,applicant,proprice]).reshape(1,13)))
    print(prediction)

    return str(np.round(prediction[0],2))



if __name__=='__main__':
    app.run(debug=True)