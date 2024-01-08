import streamlit as st
import pandas as pd
from pyod.models.iforest import IForest
from anomalies_alerts import checkAnomalies
from descriptive import hide_streamlit_style
from helpers.helpers import sidestuff
from helpers.helpers import load_df
from joblib import dump, load
import os
from helpers.plots import show_anomaly_plot

st.markdown(hide_streamlit_style, unsafe_allow_html=True)
def anomalies():
    def convert_df(dframe):
        return dframe.to_csv(index=False).encode('utf-8')




    df = load_df()
    if "selected_column" in st.session_state:
        selected_column = st.session_state.selected_column
    else:
        selected_column = df.columns[0]
    labels = pd.read_csv('data/labels.csv')
    local_css("css/streamlit.css")
    sidestuff(df, labels, selected_column)

    # st.subheader("Anomaly Detection")
    # exp_mad = setup(df, normalize=True, session_id=124)
    # if uploaded_file is not None:
    #     path = 'models/DowB'
    # else:

    path = 'models/DataCT3201'
    start_date = st.session_state.start_date
    end_date = st.session_state.end_date

    if start_date and end_date:
        if start_date <= end_date:
            the_df = df.loc[start_date:end_date]
        else:
            st.error('Invalid date range! Please select a valid range')
    else:
        the_df = df
    isft = load(path + '/mv_isftv2.joblib')

    st.subheader("Cooling Towers - Overview")

    # except (FileNotFoundError, Exception) as e:
    #     isft = IForest(contamination=0.05, max_samples=df.shape[1], max_features=df.shape[1], behaviour='new')
    #     isft.fit(df.values)
    #     mpath = path + '/mv_isftv2.joblib'
    #     dump(isft, mpath)
    #     isft = load(path +'/mv_isftv2.joblib')
    #     try:
    #         upload_model(local_file_path=path +'/mv_isftv2.joblib')
    #     except:
    #         pass
    # if st.button('Get New Model'):
    #     download_model()
    #     isft = load(path + '/mv_isftv.joblib')
    pred = isft.predict(df.values)
    isft_vi = isft.feature_importances_
    importance = pd.DataFrame(isft_vi, columns=["Value"])
    importance['Feature'] = df.columns
    importance = importance.sort_values(by="Value", ascending=False).head(5)

    data = df.copy()
    data['is_anomaly_pred'] = pred
    ifo_anomalies = data[data['is_anomaly_pred'] == 1]
    name = labels['Tag'].tolist()
    synthesis = labels['Synth'].tolist()
    dic = dict(zip(name, synthesis))
    displ = ifo_anomalies.rename(columns=dic)
    # ifo_anomalies = ifo_res[ifo_res['Anomaly'] == 1]
    # ifo_anomalies = ifo_anomalies.astype(float).round(decimals=3)


    ca = checkAnomalies(df, selected_column, labels)
    st.markdown("**Latest Anomalies**")

    if displ.empty:
        st.write("No anomalies were found in the selected date range.")
    else:
        # d_anom = ifo_anomalies.copy()
        st.dataframe(displ.drop(['is_anomaly_pred'], axis=1).tail(3))
        st.download_button(
            "Download",
            convert_df(displ),
            "isolationforestanomalies.csv",
            "text/csv",
            key='download-csv-ifo'
        )

    synth = labels[labels['Tag'] == selected_column]['Synth'].values[0]

    fig_e = show_anomaly_plot(isft, the_df, labels)
    st.markdown("""---""")
    st.plotly_chart(fig_e, use_container_width=True)
    alerts = pd.read_csv("data/alerts/alerts.csv")

    st.markdown("""---""")
    st.markdown("**Latest Alerts**")
    if alerts.empty:
        st.write("No alerts were found.")
    else:
        aler = alerts.tail(3).copy()
        st.dataframe(aler.tail(3).drop(['Tag'], axis=1))
        st.download_button(
            "Download",
            convert_df(alerts),
            "alerts.csv",
            "text/csv",
            key='download-csv-alerts'
        )

    st.markdown("""---""")
    st.subheader("Variable Explorer")
    st.markdown('*Outliers*')
    # colm1, colm2 = st.columns(2)
    # with colm1:
    mpath = path + "/" + selected_column + 'isft_uv.joblib'
    try:
        isft_uv = load(mpath)
    except Exception as e:
        isft_uv = IForest(contamination=0.06, max_samples='auto', max_features=1, behaviour='new')
        dump(isft_uv, mpath)
    isft_uv.fit(the_df[[selected_column]].values)
    ifo_res = the_df[[selected_column]].copy()
    ifo_res['is_anomaly_pred'] = isft_uv.predict(the_df[[selected_column]].values)
    ifo_anomalies = ifo_res[ifo_res['is_anomaly_pred'] == 1]
    adufig = show_anomaly_plot(isft_uv, the_df, labels, selected_column=selected_column, synth=synth, ifo_res=ifo_res,
                               ifo_anomalies=ifo_anomalies)
    st.plotly_chart(adufig, use_container_width=True)
    st.markdown("""---""")
    st.markdown('*Alerts*')
    if selected_column:

        # st.warning("Last 3 metrics are low. Alert was sent.")
        # st.write(f":blue[{temperature}]")
        cola, colb = st.columns(2)
        with cola:
            if not alerts[alerts['Tag'] == selected_column].empty:
                ale = alerts.copy()
                st.dataframe(ale[ale['Tag'] == selected_column].drop(columns='Tag'))
            else:
                st.write("No recent alerts were found.")
        with colb:
            if ca[0]:
                st.error(f"Last 3 metrics for {synth} are low. Alert was sent.")
            if ca[1]:
                st.error(f"Last 3 metrics for {synth} are high. Alert was sent.")
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
        anomalies()
    else:
        acc_ctr = st.error("Unauthorised")