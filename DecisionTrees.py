

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.preprocessing import LabelEncoder


model = None
feature_columns = None
le_target = None

def train_model_and_get_data():
    """
    Función central que carga datos, entrena el modelo y lo prepara para evaluación y predicción.
    """
    global model, feature_columns, le_target
    
    file_path = 'Datasets/becas.csv'
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"El archivo {file_path} no fue encontrado.")
    
    data = pd.read_csv(file_path)

    # Preprocesamiento
    le_target = LabelEncoder()
    data['elegibilidad_beca'] = le_target.fit_transform(data['elegibilidad_beca'])
    
    data = pd.get_dummies(data, columns=['tipo_institucion'], drop_first=True)

    X = data.drop('elegibilidad_beca', axis=1)
    y = data['elegibilidad_beca']
    
    feature_columns = X.columns.tolist() # Guardamos los nombres de las columnas

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42)

    model = DecisionTreeClassifier(random_state=42)
    model.fit(X_train, y_train)
    
    return X_test, y_test




def evaluate():
    """
    Evalúa el modelo. Esta función ahora siempre entrena de nuevo para asegurar consistencia.
    """
    # Esta llamada asegura que los datos siempre se carguen y preprocesen de la misma manera.
    X_test, y_test = train_model_and_get_data()

    y_pred = model.predict(X_test)

    # Métricas
    accuracy = accuracy_score(y_test, y_pred)
    report_dict = classification_report(y_test, y_pred, target_names=['Rechazado', 'Aprobado'], output_dict=True)
    
    # Matriz de Confusión
    conf_matrix = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(8, 6))
    sns.heatmap(conf_matrix, annot=True, fmt='d', cmap='Blues', 
                xticklabels=['Rechazado', 'Aprobado'], 
                yticklabels=['Rechazado', 'Aprobado'])
    plt.xlabel('Predicción')
    plt.ylabel('Valor Real')
    plt.title('Matriz de Confusión')
    
    img_dir = 'static/images'
    if not os.path.exists(img_dir):
        os.makedirs(img_dir)
    img_path = os.path.join(img_dir, 'dt_matriz_confusion.png')
    plt.savefig(img_path)
    plt.close()
    
    results = {
        "accuracy": f"{accuracy:.4f}",
        "reporte_dict": report_dict,
        "matriz_path": "images/dt_matriz_confusion.png"
    }
    return results



def predict_label(promedio, ingresos, personas, tipo_inst_privada):
    """
    Realiza una predicción para un nuevo conjunto de características pasadas como argumentos.
    """
    if model is None or feature_columns is None:
        train_model_and_get_data()

    # Crear un diccionario con las claves correctas que el modelo espera.
    # Solo necesitamos 'tipo_institucion_Privada'
    features_dict = {
        'promedio_academico': promedio,
        'ingresos_familiares': ingresos,
        'numero_personas_hogar': personas,
        'tipo_institucion_Privada': tipo_inst_privada
    }
    
    input_df = pd.DataFrame([features_dict])
    # Aseguramos que el DataFrame tenga todas las columnas que el modelo necesita, en el orden correcto.
    # Si alguna falta (aunque no debería), se llenaría con 0.
    input_df = input_df.reindex(columns=feature_columns, fill_value=0)

    # Realizar la predicción
    pred_proba = model.predict_proba(input_df)[0]
    prediction_index = model.predict(input_df)[0]
    
    prediction_label = le_target.inverse_transform([prediction_index])[0]
    probability = pred_proba[prediction_index]

    return prediction_label, probability