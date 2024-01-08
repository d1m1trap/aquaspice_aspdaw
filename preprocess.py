import pandas as pd
import os
from helpers import load_data, get_path

# def train_pre_process(data_df=None):
#     data =[]
#     print("Preprocess Started")
#     target = 'BFWTOC'
#     if os.path.exists("cleaned00WAP1820.csv"):
#         return
#     else:
#         filepath = "00_Corr_Witznitz_AfterDemin_P104_2018-2020.csv"
#         data = pd.read_csv(filepath, sep=";")
#         data.columns = [c.split("[", 1)[0] for c in data.columns]
#         data.columns = data.columns.str.replace('[#,@,&,-,_,.,/,-, ,-]', '', regex=True)
#         df = data.copy()
#         df['Date'] = pd.to_datetime(df['Date'], format="%d.%m.%Y")
#         df = df[(df['Date'] < '2019-01-01') | (df['Date'] >= '2020-01-01')]
#         df.set_index(df['Date'], inplace=True)

#         df = df.drop(
#             columns=['Date', 'BFWpH', 'BFWSiO', 'BFWT', 'BFWEC', 'BFWCu', 'BFWFetotal', 'BFWNa', 'BFWCaMg', 'BFWCl'])

#         df = df.dropna(how='all', axis='columns')

#         df = df.dropna(how='all', axis='columns', thresh=5)
#         df = df.interpolate(method="pad", limit=3)
#         df = df.interpolate(method="bfill")
#         df.to_csv('cleaned00WAP1820.csv', index=True)
#     print(filepath)
print("Preprocess started.")

variable = 'all'
# path = get_path()
path = os.getenv('data_path', '/')
fpath = path + '/DataCT3201General.csv'
outpath = path + '/ppDataCT3201General.csv'


def preprocess(variable):
    print('preprocess')
    df = load_data(fpath)
    datetime_column = 'Time'
    if datetime_column is None:
        if 'Time' in df.columns:
            datetime_column = "Time"
        elif 'Date' in df.columns:
            datetime_column = "Date"
        elif "Datetime" in df.columns:
            datetime_column = "Datetime"
        else:
            raise ValueError('Date time column not found.')
    if variable != 'all':
        all_cols = []
        for c in df.columns:
            if c != variable and c!=datetime_column:
                all_cols.append(c)
        all_cols
        df = df.drop(columns=all_cols)
    df[datetime_column] = pd.to_datetime(df[datetime_column])
    df = df.sort_values(by=[datetime_column])
    df = df.set_index(datetime_column)
    df = df.loc[(df != 0).all(axis=1)]
    df.to_csv(outpath)
    print("Preprocess completed.")
    return df

if __name__ == "__main__":
    preprocess(variable)
