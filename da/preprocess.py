import pandas as pd
import streamlit as st
from sklearn.preprocessing import MinMaxScaler
def preprocess(df, datetime_column=None):
    if datetime_column is None:
        if 'Time' in df.columns:
            datetime_column = "Time"
        elif 'Date' in df.columns:
            datetime_column = "Date"
        elif "Datetime" in df.columns:
            datetime_column = "Datetime"
        else:
            st.error('Date time column not found.')
    try:
        df[datetime_column] = pd.to_datetime(df[datetime_column])
        df = df.sort_values(by=[datetime_column])
        df = df.set_index(datetime_column)
        df = df.loc[(df != 0).all(axis=1)]
        # df.to_csv('C:\\Users\\user\\PycharmProjects\\basf\\data\\transformed\\DataCT3201General.csv')
        return df
    except Exception as error:
        st.error("An error occurred during file processing.", error)
def scaleData(df, datetime_column="Time"):
    scaler = MinMaxScaler()
    df_scaled = scaler.fit_transform(df.to_numpy())
    cols = df.columns.to_list()
    if datetime_column in cols:
        cols.remove(datetime_column)
    df_scaled = pd.DataFrame(df_scaled, columns=cols)
    df_scaled.index = df.index
    return df_scaled
