import pandas as pd
import numpy as np
import dill
import pickle
from sklearn.preprocessing import FunctionTransformer
from sklearn.compose import ColumnTransformer
from imblearn.pipeline import Pipeline as pi
from sklearn.pipeline import Pipeline


with open("model.dill", "rb") as f :
    model = dill.load(f)


# # _________________________________________________________________fonction drop colonne___________________________________________________
def drop_colonne(df):
    colonne_drop = ["transactionId","step",'nameOrig','nameDest','oldbalanceDest','newbalanceOrig']
    colonne_drop = [col for col in colonne_drop if col in df.columns]
    df =  df.drop(columns= colonne_drop, axis=1)
    return df

supprimer_colonne = FunctionTransformer(drop_colonne, validate=False)





## ____________________________________________________________drop nan_____________________________________________________
from sklearn.impute import SimpleImputer
simply = SimpleImputer(strategy="most_frequent")

def drop_nan_numerique(df, plan):
    for col in df.columns:
        if df[col].isna().sum() > 0:
            if plan == "mean" and df[col].dtypes in [float, int]:
                df[col].fillna(np.mean(df[col]), inplace=True)
            elif plan == "median" and df[col].dtypes in [float, int]:
                df[col].fillna(df[col].median(), inplace=True)
            elif plan == "drop":
                df.dropna(axis=0, inplace=True)
                 
    return df
plans = {
    'numeric': ['mean',"median" , "drop"],            
    'categorical': 'most_frequent'  
}
# 0 : mean
# 1 : medien
# 2 : drop

def imputer_transformer(df):
    df = drop_nan_numerique(df, plans['numeric'][0])
    df = drop_nan_categorique(df)

    return df

def drop_nan_categorique(df):
    for col in df.columns:
        if df[col].dtypes == object:
            df[col] = simply.fit_transform(df[[col]]).ravel()
    return df

# plan  : ["mean", "median" , "drop"]

nan_transformer = FunctionTransformer(imputer_transformer, validate=False)





#  _________________________________________________________________________fonction encoder _____________________________________________________
from sklearn.preprocessing import OneHotEncoder

# _____________________________________________________________________fonction normaliser données____________________________________________________

from sklearn.preprocessing import MinMaxScaler




#______________________________________________________________________________ fonction transformer _______________________________________________________
def transformer(df):
    numerical_cols = df.select_dtypes(include=np.number).columns
    categorical_cols = df.select_dtypes(include=object).columns

    processeur = ColumnTransformer([
        ("numerical", MinMaxScaler(), numerical_cols),
        ("categorical", OneHotEncoder(sparse_output=False), categorical_cols)
    ])

    df_transformer = processeur.fit_transform(df)

    return df_transformer

transformers = FunctionTransformer(transformer, validate=False)


# ______________________________________________________________________modele finale_________________________________________________________

model_final = Pipeline([
   ("drop_colonnes",supprimer_colonne),
   ("transformers",transformers),
   ("model", model)
])


# ___________________________________________________________________enregistrer le model_____________________________________________________
with open("modele_finale.dill", "wb") as fichier:
    dill.dump(model_final, fichier)

