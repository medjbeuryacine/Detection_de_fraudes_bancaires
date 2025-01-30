from flask import Flask, render_template, request, url_for, redirect, flash
import pymysql
import csv
import io

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












# page de chargement de fichier et de l'afficher dans la page
@app.route("/chargement", methods=["GET","POST"], endpoint="chargement")
def chargement():
    table_data = None

    if request.method == "POST":
        file = request.files["csvFile"]
        if file:
            stream = io.StringIO(file.stream.read().decode("utf-8"))
            reader = csv.reader(stream, delimiter=",")
            table_data = list(reader)

    return render_template("chargement.html", table_data=table_data)



if __name__ == "__main__":
    app.run(debug=True)