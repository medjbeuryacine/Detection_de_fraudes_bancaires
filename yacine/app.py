from flask import Flask, render_template, request, url_for, redirect, flash, session
import pymysql
import csv
import io
import pandas as pd
import pickle
import dill

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder
from sklearn.preprocessing import FunctionTransformer
import numpy as np


app = Flask(__name__)
app.secret_key = "secret_key"




def init_db():
    return pymysql.connect(
        host = "192.168.20.131", # Adresse du serveur MySQL
        user = "root",      # Nom d'utilisateur MySQL
        password =  "devIA25",  # Mot de passe MySQL
        database = "Projet_1_fraude",   # Nom de la base de données
        cursorclass=pymysql.cursors.DictCursor
    )

try:
    init_db()
    print("connecte")
except Exception as e:
    print(f"vous avez le problem: {e}")



# la première page 
@app.route("/")
def accueil():
    return render_template("accueil.html")



# la page de se connecter
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        login = request.form["username"]
        mdb = request.form["password"]

        connexion = init_db()
        with connexion.cursor() as cursor:
            sql = "SELECT * FROM utilisateur WHERE username = %s AND password = %s"
            cursor.execute(sql, (login, mdb))
            utilisateur = cursor.fetchone()

        connexion.close()

        if utilisateur:
            flash("Connexion réussie !", "success")
            return redirect(url_for('chargement'))
        else:
            flash("Nom d'utilisateur ou mot de passe incorrect.", "danger")

    return render_template("login.html")


@app.route('/logout')
def logout():
    # Supprime les données de session de l'utilisateur
    session.clear()
    # Redirige vers la page de connexion ou d'accueil
    return redirect(url_for('login'))






# -------------------------------------------------------------------------------MODEL IA-------------------------------------------------------------------------------------

# connecter à la base
db = init_db()
cursor = db.cursor()





# page de chargement de fichier et de l'afficher dans la page
@app.route("/chargement", methods=["GET","POST"], endpoint="chargement")
def chargement():
    table_data = None

    if request.method == "POST":
        file = request.files["csvFile"]
        if file:

            try:
                stream = io.StringIO(file.stream.read().decode("utf-8"))
                data = pd.read_csv(stream, sep=";")

                # selectioner les colonnes
                colonne = ['transactionId', 'step', 'type', 'amount', 'nameOrig', 'oldbalanceOrg','newbalanceOrig', 'nameDest', 'oldbalanceDest', 'newbalanceDest','isFraud']
                if not all(col in data.columns for col in colonne):
                    return "Erreur : colonne manquantes dans le fichier csv", 400
                
                data = data.fillna(0)

                # Sauvegarder la vraie valeur de `isFraud` avant de la supprimer
                true_fraud = data["isFraud"] if "isFraud" in data.columns else None

                # supprimer la colonne isFraud
                if "isFraud" in data.columns:
                    true_fraud = data["isFraud"].fillna(0)
                    true_fraud = data["isFraud"].astype(int)
                    true_fraud = true_fraud.tolist()
                    data = data.drop(columns=["isFraud"])
                else:
                    true_fraud = None


                # ouvrir le model ia
                with open("modele_finale.dill", "rb") as file:
                    model = dill.load(file)

                try:
                # prediction par ia et les colonne change apartir que les colonnes que le model fait pour predir la fraud ou pas
                    print("Avant transformation, shape =", data.shape)
                    data_transformer = model.named_steps["drop_colonnes"].transform(data)
                    print("Après drop_colonnes, shape =", data_transformer.shape)


                    data_transformer = model.named_steps["transformers"].transform(data_transformer)
                    # print("Après transformation, shape =", data_transformer.shape)

                    prediction = model.named_steps["model"].predict(data_transformer)
                    print("Format prédictions :", type(prediction), "Shape :", prediction.shape)

                    
                    if isinstance(prediction, list):
                        prediction = np.array(prediction)
                    if prediction.ndim > 1:
                        prediction = prediction.flatten()

                    data["isFraud"] = prediction.astype(str)

                except Exception as e:
                    return f"le problem {e}"

                # Convertir les données en liste pour affichage dans Jinja
                table_data = data[["transactionId", "step","type","amount","nameOrig","nameDest","isFraud"]].values.tolist()

                for index, row in data.iterrows():
                    transaction_Id = row["transactionId"]
                    is_fraud_pred = row["isFraud"]
                    true_fraud_value = true_fraud[index] if true_fraud is not None else None


                    if true_fraud_value is not None:
                        prediction_correct = True if true_fraud is not None and is_fraud_pred == true_fraud else False
                    else:
                        prediction_correct = None




                    sql = """
                            INSERT INTO Prediction (transactionId, isFraude, prediction_Correct_Ou_Non) VALUES (%s,%s,%s) 
                            ON DUPLICATE KEY UPDATE isFraude = IF(isFraude != VALUES(isFraude), VALUES(isFraude), isFraude)
                        """
                    try:
                        cursor.execute(sql, (transaction_Id, is_fraud_pred, prediction_correct))
                    except Exception as e:
                        db.rollback()
                        print("Erreur lors de l'insertion dans la base de données:", e)


                db.commit()
            except Exception as e:
                return f"Le problème est : {e}"


    return render_template("chargement.html", table_data=table_data)







if __name__ == "__main__":
    app.run(debug=True)

