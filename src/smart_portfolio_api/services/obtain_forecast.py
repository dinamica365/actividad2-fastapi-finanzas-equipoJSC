from __future__ import annotations

import numpy as np
import pandas as pd


def model_forecast(df):
    media = df["Close"].mean()
    desviacion = df["Close"].std()

    resultados = np.random.normal(loc=media, scale=desviacion, size=7)

    data_resultados = pd.DataFrame()
    data_resultados["Close_Forecast"] = resultados
    return data_resultados
