# app.py
from flask import Flask, render_template,request,redirect,url_for,Response
import joblib
import pandas as pd
import sqlite3
import csv

app = Flask(__name__)

# Load the model using joblib
model_01 = joblib.load("models\Trained_model_01.joblib")
model_BMR = joblib.load("models\Trained_model_BMR.joblib")

# Créer une connexion à la base de données
conn = sqlite3.connect('base_de_données_BMR.db')

# Créer un curseur pour exécuter des requêtes SQL
c = conn.cursor()

# Si la table n'existe pas, la créer
c.execute("""CREATE TABLE IF NOT EXISTS patient01  (
    Durée infection float,
    S_à_entrée float,
    Age float,
    Cathéters centrau float,
    HTA float,
    OFLO float,
    CIPRO float,
    Qsofa float,
    DT2 float,
    LEVOFLO float
)""")

c.execute("""CREATE TABLE IF NOT EXISTS patientBMR  (
    Durée infection float,
    Age float,
    S_à_entrée float,
    Qsofa float,
    Cathéters_centrau float,
    Cathéters_artériels float,
    DYSLIPEDIIE float,
    AINOSIDE float,
    HTA float,
    AZITHRO float
)""")

# Enregistrer les changements et fermer la connexion
conn.commit()
conn.close()


@app.route('/')
def home():
    return render_template('home2.html')

@app.route('/afficher')
def afficher():
    conn = sqlite3.connect('base_de_données_BMR.db')
    c = conn.cursor()
    patients = c.execute("SELECT * FROM patient01").fetchall()
    conn.close()
    return render_template('accueil.html', patients=patients)

@app.route('/export_patient')
def export_patient():
    conn = sqlite3.connect('base_de_données_BMR.db')
    c = conn.cursor()
    c.execute("SELECT * FROM patient01")

    # Write data to CSV file
    with open('patient.csv', 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow([i[0] for i in c.description]) # write headers
        csvwriter.writerows(c)

    conn.close()

    # Return CSV file as a response
    with open('patient.csv', 'r') as f:
        csv_data = f.read()

    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-disposition":
                 "attachment; filename=patient.csv"})
   

@app.route('/afficher_BMR')
def afficher_BMR():
    conn = sqlite3.connect('base_de_données_BMR.db')
    c = conn.cursor()
    patients = c.execute("SELECT * FROM patientBMR").fetchall()
    conn.close()
    return render_template('accueil_BMR.html', patients=patients)

@app.route('/export_patientBMR')
def export_patientBMR():
    conn = sqlite3.connect('base_de_données_BMR.db')
    c = conn.cursor()
    c.execute("SELECT * FROM patientBMR")

    # Write data to CSV file
    with open('patientBMR.csv', 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow([i[0] for i in c.description]) # write headers
        csvwriter.writerows(c)

    conn.close()

    # Return CSV file as a response
    with open('patientBMR.csv', 'r') as f:
        csv_data = f.read()

    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-disposition":
                 "attachment; filename=patientBMR.csv"})
   

@app.route('/form01')
def form01():
    return render_template('form.html')


@app.route('/predict01', methods=['POST'])
def predict_01():
    
    # Get the user input from the form
    input_data = {}
    for k, v in request.form.items():
        # Handle empty input fields by providing a default value
        try:
            input_data[k] = float(v)
        except ValueError:
            # Handle the case where the input field is empty or not a valid number
            input_data[k] = 0.0

    conn = sqlite3.connect('base_de_données_BMR.db')
    c = conn.cursor()
    c.execute('INSERT INTO patient01 VALUES (?, ?, ?,?, ?, ?,?, ?, ?,?)',
               tuple(input_data[k] for k in input_data.keys()))
    conn.commit()
    conn.close()
    # return redirect(url_for('afficher'))
    

    # Debugging statements
    print(request.form)
    print(input_data)

    # You'll need to process the input data to match the format expected by your model
    data = pd.DataFrame([input_data])

    print(data)

    # Use the loaded model to make predictions
    # You'll need to call your model's predict method here
    result = model_01.predict(data)

    # Return the prediction result to the user
    if result[0]== 0 :
        return render_template('result.html', prediction="À 84%, le patient ne sera pas infecté")
    else:
        return render_template('result.html', prediction="À 84%, le patient sera infecté")

@app.route('/BMR')
def form_BMR():
    return render_template('form_BMR.html')

@app.route('/predictBMR', methods=['POST'])
def predict_BMR():
    # Get the user input from the form
    input_data = {}
    for k, v in request.form.items():
        # Handle empty input fields by providing a default value
        try:
            input_data[k] = float(v)
        except ValueError:
            # Handle the case where the input field is empty or not a valid number
            input_data[k] = 0.0

    conn = sqlite3.connect('base_de_données_BMR.db')
    c = conn.cursor()
    c.execute('INSERT INTO patientBMR VALUES (?, ?, ?,?, ?, ?,?, ?, ?,?)',
               tuple(input_data[k] for k in input_data.keys()))
    conn.commit()
    conn.close()

    # Create a DataFrame with the correct column names and an index
    data = pd.DataFrame([input_data])

    # Use the loaded model to make predictions
    # You'll need to call your model's predict method here
    result = model_BMR.predict(data)

    if result[0]== 0:
        return render_template('result.html', prediction="À 88%, le patient ne sera pas infecté")
        


    #--------------------------coding the result ---------------------
    d={}
    #'Acineto ', 'ABR','acineto2','Pseudo ', 'PBR', 'E.cloacae', 'EBR', 'Kp', 'KBR', 'S.aureus ', 'SBR','E.faeciu ', 'FBR'
    d[0] = set(['nothing'])
    d[1] = set(['Acineto '])
    d[2] = set(['Acineto ', 'ABR'])
    d[3] = set(['ABR','acineto2'])
    d[4] = set(['Acineto ', 'ABR','acineto2'])
    d[5] = set(['Pseudo '])
    d[6] = set(['Pseudo ', 'PBR'])
    d[7] = set(['E.cloacae'])
    d[8] = set(['E.cloacae', 'EBR'])
    d[9] = set(['Kp'])
    d[10] = set(['Kp', 'KBR'])
    d[11] = set(['S.aureus '])
    d[12] = set(['S.aureus ', 'SBR'])
    d[13] = set(['E.faeciu '])
    d[14] = set(['E.faeciu ', 'FBR'])

    d2={}
    d3={}
    d4={}
    d5={}
    d6={}
    x=max(d.keys())
    for i in range(1,15):
        for j in range(1,15):
            if ((d[i] | d[j])not in d2.values()) and ((d[i] | d[j])not in d.values()):
                d2[x] = d[i] | d[j]
                x+=1
    x=max(d2.keys())
    for i in d2.keys():
        for j in range(1,15):
            if ((d2[i] | d[j]) not in d3.values()) and ((d2[i] | d[j])not in d2.values()) :
                d3[x]=d2[i] | d[j]
                x+=1
    x=max(d3.keys())
    for i in d3.keys():
        for j in range(1,15):
            if ((d3[i] | d[j]) not in d3.values()) and ((d3[i] | d[j])not in d4.values()):
                d4[x]=d3[i] | d[j]
                x+=1
    x=max(d4.keys())
    for i in d4.keys():
        for j in range(1,15):
                if ((d4[i] | d[j]) not in d4.values()) and ((d4[i] | d[j])not in d5.values()) :
                    d5[x]=d4[i] | d[j]
                    x+=1
    x=max(d5.keys())
    for i in d5.keys():
        for j in range(1,15):
            if ((d5[i] | d[j]) not in d5.values()) and ((d5[i] | d[j])not in d6.values()):
                d6[x]=d5[i] | d[j]
                x+=1
    code={}
    code.update(d)
    code.update(d2)
    code.update(d3)
    code.update(d4)
    code.update(d5)
    code.update(d6)

    
    result = code[result[0]]

    # Return the prediction result to the user
    return render_template('result.html', prediction="À 88%, le patient sera infecté par : {}".format(result))

if __name__ == '__main__':
    app.run(debug=True)