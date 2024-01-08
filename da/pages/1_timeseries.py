import os
import pandas as pd
import streamlit as st
from descriptive import local_css, hide_streamlit_style
from helpers.helpers import sidestuff
from helpers.plots import ts_decompose
from preprocess import preprocess

st.markdown(hide_streamlit_style, unsafe_allow_html=True)
def timeseries():
# df = load_df()
    if 'df' in st.session_state.keys():
        df = st.session_state.df
    else:
        df = pd.read_csv('data/transformed/DataCT3201General.csv')
        time_column = "Time"
        df = preprocess(df, time_column)
        st.session_state.df = df
    if "selected_column" in st.session_state:
        selected_column = st.session_state.selected_column
    else:
        selected_column = df.columns[0]
    labels = pd.read_csv('data/labels.csv')
    local_css("css/streamlit.css")
    sidestuff(df, labels, selected_column)
    min_date = df.index.min().date()
    max_date = df.index.max().date()
    start_date = st.session_state.start_date
    end_date = st.session_state.end_date
    if start_date and end_date:
        if start_date <= end_date:
            the_df = df.loc[start_date:end_date]
        else:
            st.error('Invalid date range! Please select a valid range')
    else:
        the_df = df
    selected_column = st.session_state.selected_column
    synth = labels[labels['Tag'] == selected_column]['Synth'].values[0]
    st.subheader("Cooling Towers")
    st.markdown("**Seasonal Decomposition**")
    fig = ts_decompose(the_df, selected_column, synth)
    st.plotly_chart(fig, use_container_width=True)
    # st.markdown('**Autocorrelation**')
    # fig2 = autocorr_plot(the_df, selected_column)
    # st.plotly_chart(fig2, use_container_width=True)
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


def auth():
    token = None
    query = st.experimental_get_query_params()
    if query:
        token = query.get('_kw')[0]
    if token and token == os.environ.get('ASP_TOKEN') or token =='9WnuZijZH0z5XwNWkKohwQhYWqw9Nrw8':
        return True
    return False


if __name__ == '__main__':
    acc_ctr=''
    if auth():
        if acc_ctr:
            acc_ctr.empty()
        timeseries()
    else:
        acc_ctr = st.error("Unauthorised")