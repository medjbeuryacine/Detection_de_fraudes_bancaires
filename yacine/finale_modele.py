import pandas as pd
import numpy as np
import dill
import pickle
from sklearn.preprocessing import FunctionTransformer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline


with open("modele_new.dill", "rb") as f :
    model = dill.load(f)



# # _________________________________________________________________fonction drop colonne___________________________________________________
def drop_colonne(df):
    colonne_drop = ["transactionId","step",'nameOrig','nameDest','oldbalanceDest','newbalanceOrig']
    colonne_drop = [col for col in colonne_drop if col in df.columns]
    df =  df.drop(columns= colonne_drop, axis=1)
    return df

supprimer_colonne = FunctionTransformer(drop_colonne, validate=False)




# #__________________________________________________fonction covertir en nombre_________________________________________
def convert_to_float(df):
    colonnes = ['amount', 'oldbalanceOrg', 'newbalanceDest']
    df = df.copy()
    for col in colonnes:
        if col in df.columns:
            if df[col].dtype == object:
                # Si la colonne contient une virgule, on applique la transformation
                if df[col].str.contains(',').any():
                    # On supprime le point (séparateur des milliers) puis on remplace la virgule par le point
                    df[col] = df[col].str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
            # Conversion finale en float (les valeurs non convertibles deviendront NaN)
            df[col] = pd.to_numeric(df[col], errors='coerce')
    return df


covertir_transfomer = FunctionTransformer(convert_to_float, validate=False)



## ____________________________________________________________drop nan_____________________________________________________
from sklearn.impute import SimpleImputer
simply = SimpleImputer(strategy="most_frequent")
plans = {
    'numeric': ['mean',"median" , "drop"],            
    'categorical': 'most_frequent'  
}
# 0 : mean
# 1 : medien
# 2 : drop


def drop_nan_numerique(df, plan):

    df = df.copy()
    # Sélection des colonnes numériques
    numeric_cols = [col for col in df.columns if pd.api.types.is_numeric_dtype(df[col])]

    if plan == "drop":
        # Si une colonne numérique contient des NaN, on supprime toute la ligne
        if df[numeric_cols].isnull().any().any():
            df.dropna(axis=0, inplace=True)
    else:
        for col in numeric_cols:
                if df[col].isnull().any():
                    if plan == "mean":
                        df[col].fillna(df[col].mean(), inplace=True)
                    elif plan == "median":
                        df[col].fillna(df[col].median(), inplace=True)
    return df
    
                


def drop_nan_categorique(df):
    df = df.drop()
    # Sélection des colonnes de type object
    categorical_cols = [col for col in df.columns if df[col].dtype == object]

    for col in categorical_cols:
        if df[col].isnull().any():
            # Récupère la valeur la plus fréquente (mode) de la colonne
            mode_val = df[col].mode()
            if not mode_val.empty:
                df[col].fillna(mode_val[0], inplace=True)
    return df

# plan  : ["mean", "median" , "drop"]


def imputer_transformer(df):

    df = df.copy()
    if df.isnull().sum().sum() > 0:
        df = drop_nan_numerique(df, plans['numeric'][0])
        df = drop_nan_categorique(df)

    return df

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
   ("covertir_transfomer", covertir_transfomer),
   ("nan_transformer", nan_transformer),
   ("transformers",transformers),
   ("model", model)
])


# ___________________________________________________________________enregistrer le model_____________________________________________________
with open("modele_finale_2_new.dill", "wb") as fichier:
    dill.dump(model_final, fichier)

