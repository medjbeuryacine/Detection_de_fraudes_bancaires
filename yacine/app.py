from flask import Flask, render_template, request, url_for, redirect


app = Flask(__name__)




@app.route("/")
def accueil():
    return render_template("accueil.html")

@app.route("/Se connecter")
def login():
    return render_template("login.html")


@app.route("/chargement")
def chargement():
    # user_name = "Jean Dupont" 
    return render_template("parcourir.html")


@app.route("/upload")
def upload():
    return render_template("upload.html")




if __name__ == "__main__":
    app.run(debug=True)