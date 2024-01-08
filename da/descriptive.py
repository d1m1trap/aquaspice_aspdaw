import os
import streamlit as st
import pandas as pd
from helpers.helpers import sidestuff
from helpers.plots import descriptive_table, plot_violin, plot_line, corr_plot, trendline, autocorr_plot, ts_decompose
from preprocess import preprocess

st.set_page_config(page_title='Descriptive', layout='wide', page_icon="🗠", initial_sidebar_state='expanded')

hide_streamlit_style = """
                <style>
                div[data-testid="stToolbar"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                div[data-testid="stDecoration"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                div[data-testid="stStatusWidget"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                #MainMenu {
                visibility: hidden;
                height: 0%;
                }
                header {
                visibility: hidden;
                height: 0%;
                }
                footer {
                visibility: hidden;
                height: 0%;
                }
                iframe{
                position:absolute;
                left:-9999px;
                }
                </style>
                """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

def main():
    # Loading CSS
    local_css("css/streamlit.css")
    if 'df' in st.session_state.keys():
        df = st.session_state.df
    else:
        df = pd.read_csv('data/transformed/DataCT3201General.csv')
        time_column = "Time"
        df = preprocess(df, time_column)
        st.session_state.df = df
    labels = pd.read_csv('data/labels.csv')
    # if authentication_status == False:
    #     st.error('Username/password is incorrect')
    # elif authentication_status is None:
    #     st.warning('Please enter your username and password')
    # if authentication_status:
    # authenticator.logout('Logout', 'main')
    # st.write(f'Welcome *{name}*')
    # st.file_uploader("Choose a file")

    # Retrieve the data from session state

    if "selected_column" in st.session_state:
        selected_column = st.session_state.selected_column
    else:
        selected_column = df.columns[0]
    sidestuff(df, labels, selected_column)
    start_date = st.session_state.start_date
    end_date = st.session_state.end_date
    if start_date and end_date:
        if start_date <= end_date:
            the_df = df.loc[start_date:end_date]
        else:
            st.error('Invalid date range! Please select a valid range')
    else:
        the_df = df
    if st.session_state and st.session_state.selected_column:
        selected_column = st.session_state.selected_column
    table = descriptive_table(df, labels)
    st.subheader("Cooling Towers - Overview")
    st.markdown("***Descriptive Statistics***")
    st.dataframe(table.style.format(subset=table.columns, formatter="{:.3f}"))
    st.markdown("""---""")
    # selected_column = st.selectbox('Select a variable', df.columns, key='descript') here
    # Get the minimum and maximum dates from the DataFrame index

    # start_date = st.date_input('Select start date', min_value=min_date, max_value=max_date, value=min_date)
    # end_date = st.date_input('Select end date', min_value=min_date, max_value=max_date, value=max_date)


    st.markdown('**Scaled Data**')
    st.caption("Select additional variables from legend to add to the plot")
    plot_l = plot_line(the_df, selected_column, labels, False)
    st.plotly_chart(plot_l, use_container_width=True)
    # st.markdown("""---""")
    # st.markdown("***Correlations***")
    # st.plotly_chart(corr_plot(the_df, labels['Synth']), use_container_width=True)
    st.markdown("""---""")
    st.subheader('Variable Explorer')
    # unit = labels[labels['Tag'] == selected_column]['Unit'].values[0]
    # label = labels[labels['Tag'] == selected_column]['Description'].values[0]
    synth = labels[labels['Tag'] == selected_column]['Synth'].values[0]
    plot_v = plot_violin(the_df, selected_column, synth)
    st.plotly_chart(plot_v, use_container_width=True)
    st.markdown("""---""")
    plot_sel = plot_line(the_df, selected_column, synth)
    st.plotly_chart(plot_sel, use_container_width=True)
    st.markdown("""---""")
    trend_simple=trendline(the_df, selected_column, synth)
    st.plotly_chart(trend_simple, use_container_width=True)


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
        main()
    else:
        acc_ctr = st.error("Unauthorised")

# aquaspice main blue  #145a9d
# aquaspice yellow #bbcc2e
# aquaspice grey #d8d8d7
# aquaspice whitey #fbfcf6
# aquaspice light blue #90bbe4
# aquaspice portal light blue #f5f8fa
# prev background color #FF786
# prev prim color #bbcc2e

# Plotly:
# paper_bgcolor='#ffffff', plot_bgcolor='#ffffff',
# fig_line.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#ebf0f8')
# fig_line.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#ebf0f8')
# html(my_html)