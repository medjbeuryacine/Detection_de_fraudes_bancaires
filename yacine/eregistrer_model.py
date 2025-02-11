import pandas as pd

import matplotlib.pyplot as plt

from sklearn.model_selection import GridSearchCV, learning_curve
from sklearn.metrics import classification_report, confusion_matrix

import numpy as np

import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
import dill

x_train = pd.read_csv('C:\\Users\\yacine.medjbeur\\Downloads\\x_smote_tomek_train.csv', sep=';')
y_train = pd.read_csv('C:\\Users\\yacine.medjbeur\\Downloads\\y_smote_tomek_train.csv', sep=';')

y_train = y_train.values.ravel()

model = RandomForestClassifier(max_depth=30, 
                               min_samples_split=2,
                               n_estimators=200)


model.fit(x_train, y_train)

with open("modele_new.dill", 'wb') as fichier:
    dill.dump(model, fichier)
    print(model)

print(model.score(x_train, y_train))