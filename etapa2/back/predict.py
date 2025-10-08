
from last_model import get_last_model
import pandas as pd
from utils import clean_df

def predict(text):
    df = pd.DataFrame({
        "textos":[text]
    })
    df_clean = clean_df(df, use_short_text=True)
    
    model = get_last_model()
    return model.predict(df_clean)

print(predict("La salud en Colombia está mal"))
