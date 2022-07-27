from flask import Flask, render_template, request
import pandas as pd
import pickle

app = Flask(__name__)
data = pd.read_csv("Cleane_House_Details.csv")
pipe = pickle.load(open("House_Price_Prediction.pkl","rb"))

@app.route("/")
def index():
    locations = sorted(data["site_location"].unique())
    balconaies = sorted(data["balcony"].unique())
    bathrooms = sorted(data["bath"].unique())
    bhks = sorted(data["size"].unique())

    return render_template("House_Price_Predictor.html", locations=locations, balconaies=balconaies, bathrooms=bathrooms, bhks=bhks)


@app.route("/predict", methods=["POST"])
def predict():
    location = request.form.get('location')
    balcony = request.form.get('balcony')
    bathroom = request.form.get('bathroom')
    sqfeet = float(request.form.get('sqfeet'))
    bhk = request.form.get('bhk')

    print(location,balcony,bathroom,sqfeet,bhk)

    input = pd.DataFrame([[bhk,sqfeet,bathroom,balcony,location]], columns=["size", "total_sqft", "bath", "balcony", "site_location"])

    prediction = pipe.predict(input)[0]

    return str(prediction)


if __name__ == "__main__":
    app.run(debug=True,port=5001)