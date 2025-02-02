from flask import Flask, render_template, request, url_for, redirect, flash, session
import pymysql
import csv
import io
import pandas as pd
import pickle



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
    print(e)



# la première page 
@app.route("/")
def accueil():
    return render_template("accueil.html")



# la page de se connecter
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        login = request.form["username"]
        #.get("username")
        mdb = request.form["password"]
        #.get("mdb")

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

# ouvrir le model ia
with open("", "rb") as file: #il manque le model ia
    model_ia = pickle.load(file)




# page de chargement de fichier et de l'afficher dans la page
@app.route("/chargement", methods=["GET","POST"], endpoint="chargement")
def chargement():
    table_data = None

    if request.method == "POST":
        file = request.files["csvFile"]
        if file:
            stream = io.StringIO(file.stream.read().decode("utf-8"))
            data = pd.read_csv(stream, sep=";")

            # selectioner les colonnes
            colonne = ['transactionId', 'step', 'type', 'amount', 'nameOrig', 'oldbalanceOrg','newbalanceOrig', 'nameDest', 'oldbalanceDest', 'newbalanceDest','isFraud']
            if not all(col in data.columns for col in colonne):
                return "Erreur : colonne manquantes dans le fichier csv", 400
            

            # Sauvegarder la vraie valeur de `isFraud` avant de la supprimer
            true_fraud = data["isFraud"] if "isFraud" in data.columns else None

            # supprimer la colonne isFraud
            data = data.drop(columns=["isFraud"])
            
            # prediction par ia et les colonne change apartir que les colonnes que le model fait pour predir la fraud ou pas
            data["isFraud"] = model_ia.predict(data[["amount","oldbalanceOrg","newbalanceDest","type"]])

            # Convertir les données en liste pour affichage Jinja
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
                        INSERT INTO transactions (transactionId, isFraud, prediction_Correct_Ou_Non) VALUES (%s,%s,%s)
                      """
                cursor.execute(sql, (transaction_Id, is_fraud_pred, prediction_correct))


            db.commit()

    return render_template("chargement.html", table_data=table_data)







if __name__ == "__main__":
    app.run(debug=True)




# reader = csv.reader(stream, delimiter=",")
# table_data = list(reader)