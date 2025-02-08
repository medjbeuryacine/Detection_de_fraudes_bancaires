import dill
import pandas as pd
from sklearn.exceptions import NotFittedError

x_train = pd.read_csv('C:\\Users\\yacine.medjbeur\\Documents\\GitHub\\Projet_fraude\\yacine\\entrainement_de_model\\x_smote_tomek_train.csv', sep=';')


# Vérifier si le modèle est bien entraîné avant d'enregistrer
try:
    with open("model.dill", "rb") as file:
        model = dill.load(file)
    
    # Vérifier si le modèle est bien entraîné
    try:
        model.predict(x_train[:5])  # Essayer de prédire sur un échantillon
        print("✅ Le modèle est bien entraîné et prêt à être utilisé !")
    except NotFittedError:
        print("❌ Le modèle n'est pas encore entraîné !")
except FileNotFoundError:
    print("❌ Le fichier 'model_finale.dill' n'existe pas. Vérifiez que vous l'avez bien enregistré.")
