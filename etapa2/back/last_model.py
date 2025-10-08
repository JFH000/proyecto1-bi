
import joblib
import os

first_model = joblib.load('etapa2/first_model.pkl')
folder_path = "etapa2/retrain_models"

def get_last_model():
    files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]

    latest_file = max(files, key=os.path.getctime)
    if os.path.basename(latest_file) == ".gitkeep":
        print("El último archivo es .gitkeep")
        return first_model
    else:
        print("El último archivo NO es .gitkeep:", latest_file)
        actual_model = joblib.load(latest_file)
        return actual_model
    pass

get_last_model()