from datetime import timedelta

import pandas as pd
import streamlit as st

from preprocess import preprocess

def load_df():
    df_l = pd.read_csv('data/transformed/DataCT3201General.csv')
    time_column = "Time"
    df_l = preprocess(df_l, time_column)
    st.session_state.df = df_l
    # print(st.session_state.keys())
    # if 'df' not in st.session_state.keys():
    #     print("Not st.session_state.df")
    #     # if uploaded_file is not None:
    #     #     try:
    #     #         df = pd.read_csv(uploaded_file)
    #     #         st.write(df)
    #     #         time_column = st.selectbox('Select a the datetime column', df.columns, key='datetime')
    #     #     except Exception as error:
    #
    #     if os.path.isfile('data/transformed/DataCT3201General.csv'):
    #         df = pd.read_csv('data/transformed/DataCT3201General.csv')
    #         time_column = "Time"
    #         df = preprocess(df, time_column)
    #         st.session_state.df = df
    #     else:
    #         print("An error occurred during file processing.")
    # else:
    #     df =st.session_state.df
    # else:
    #     df = pd.read_csv('data/transformed/DataCT3201General.csv')
    #     time_column = "Time"
    #     df = preprocess(df, time_column)
    #     st.session_state.df = df
    return df_l

def sidestuff(df, labels, a=None):
    if a is not None:
        aint = df.columns.get_loc(a)
    else:
        aint = 0
    st.sidebar.subheader("Filters")
    st.sidebar.write("Variables")
    options = df.columns.tolist()
    values = labels['Description'].tolist()
    dic = dict(zip(options, values))
    st.sidebar.selectbox('Select a variable', options, key='selected_column', index=aint, format_func=lambda x: dic[x])
    min_date = df.index.min().date()
    max_date = df.index.max().date()

    if (max_date - timedelta(days=40, hours=0)) > min_date:
        default_min = (max_date - timedelta(days=40, hours=0))
    else:
        default_min = (max_date - timedelta(days=2, hours=0))

    # Date range selection - col1
    st.sidebar.write("Dates")
    col1, col2 = st.sidebar.columns(2)
    with col1:
        start_date = st.date_input('Select Start Date', min_value=min_date, max_value=max_date, value=default_min,
                                   key='start_date')


    # Date range selection - col2
    with col2:
        end_date = st.date_input('Select End Date', min_value=min_date, max_value=max_date, value=max_date,
                                 key='end_date')
    def reset():
        st.session_state.selected_column = df.columns[0]
        st.session_state.descr_sdate = default_min
        st.session_state.descr_edate = max_date

    st.sidebar.button('Reset', on_click=reset)