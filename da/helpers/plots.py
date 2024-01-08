import numpy as np
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from preprocess import scaleData

from plotly.subplots import make_subplots
from statsmodels.tsa.seasonal import DecomposeResult, seasonal_decompose

from statsmodels.tsa.stattools import pacf, acf

@st.cache()
def descriptive_table(df, labels, columns=None):
    # df = data.copy()
    # cols = df.columns if columns is None else columns
    # cols = [c for c in cols if c not in "Year"]
    # res = df[cols].describe().round(3).transpose()
    # res = pd.DataFrame(df[cols].describe().round(3).transpose(), columns=cols)
    d1 = df[df.columns].describe().round(3).transpose()
    d1['index_column'] = d1.index

    def set_label(x):
        x = labels[labels['Tag'] == x['index_column']]
        if len(x) > 0:
            return x.iloc[0].Synth
        return None

    d1['label'] = d1.apply(lambda x: set_label(x), axis=1)
    d1 = d1.set_index('label').copy()
    d1 = d1.drop(['index_column'], axis=1)
    return d1


# @st.experimental_memo

def plot_violin(data, column, yaxis_title):
    fig = px.violin(data, y=column, points='all', color_discrete_sequence=['#1f77b4'])
    fig.update_layout(title="Violin Plot", yaxis_title=yaxis_title)
    return fig

def plot_line(data, column, labels, single=True):
    if single:
        # col1, col2 = st.columns(2)
        # with col1:

        # with col2:
        # st.markdown('**Line Plot**')
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data.index, y=data[column], mode='lines', line_color='#1f77b4'))
        fig.update_layout(xaxis_title='Date', yaxis_title=labels, title="Line plot")
    else:
        # st.markdown('**Scaled Data**')
        # st.caption("Select additional variables from legend to add to the plot")
        data = scaleData(data)
        # st.markdown('**Violin Plot**')
        # fig = px.violin(data, color_discrete_sequence=['#1f77b4'])
        # st.plotly_chart(fig, use_container_width=True)
        # st.markdown('**Line Plot**'
        # )
        name = labels['Tag'].tolist()
        synth = labels['Synth'].tolist()
        dic = dict(zip(name, synth))

        def update_trace_name(trace):
            trace.name = dic[trace.name]

        all_cols = data.columns.to_list()
        if column in data.columns:
            all_cols.remove(column)
        fig = px.line(data)  # render_mode="svg", color_discrete_sequence=px.colors.sequential.Viridis

        fig.for_each_trace(lambda trace: trace.update(visible="legendonly") if trace.name in all_cols else ())
        fig.for_each_trace(update_trace_name)

        fig.update_layout(title="Scaled Data - Line Plot")
    return fig


@st.cache(allow_output_mutation=True)
def trendline(data, column, label):
    fig = px.scatter(data, x=data.index, y=column, trendline="ols",
                     title="Linear Trendline - Ordinary Least Squares Regression",
                     color_discrete_sequence=['#1f77b4'], trendline_color_override="#0e1e56")
    fig.update_layout(yaxis_title=label)
    return fig


# @st.experimental_memo

def corr_plot(data, labels):
    correlation_matrix = data.corr().round(2)
    # Mask to matrix
    mask = np.zeros_like(correlation_matrix, dtype=bool)
    mask[np.triu_indices_from(mask)] = True
    # Viz
    df_corr_viz = correlation_matrix.mask(mask).dropna(how='all')
    fig = px.imshow(df_corr_viz, color_continuous_scale="ylgnbu", aspect='auto')  # teal
    fig.update_xaxes(tickvals=list(range(len(labels))))
    fig.update_xaxes(ticktext=labels, tickangle=45)
    fig.update_yaxes(tickvals=list(range(len(labels))))
    fig.update_yaxes(ticktext=labels)
    fig.update_layout(height=600, width=700)
    fig.update_layout(title="Matrix Heatmap")
    return fig


def plot_seasonal_decompose(result: DecomposeResult, dates: pd.Series = None, title: str = "Seasonal Decomposition"):
    x_values = dates if dates is not None else np.arange(len(result.observed))
    return (
        make_subplots(
            rows=4,
            cols=1,
            subplot_titles=["Observed", "Trend", "Seasonal", "Residuals"],
        )
        .add_trace(
            go.Scatter(x=x_values, y=result.observed, mode="lines", name='Observed'),
            row=1,
            col=1,
        )
        .add_trace(
            go.Scatter(x=x_values, y=result.trend, mode="lines", name='Trend'),
            row=2,
            col=1,
        )
        .add_trace(
            go.Scatter(x=x_values, y=result.seasonal, mode="lines", name='Seasonal'),
            row=3,
            col=1,
        )
        .add_trace(
            go.Scatter(x=x_values, y=result.resid, mode="lines", name='Residual'),
            row=4,
            col=1,
        )
        .update_layout(
            height=900, title=f'<b>{title}</b>', margin={'t': 100}, title_x=0.5, showlegend=False
        )
    )


def ts_decompose(data, column, label):
    try:
        decomposition = seasonal_decompose(data[column], model='additive')
    except ValueError:
        try:
            decomposition = seasonal_decompose(data[column], model='additive', period=20)
        except Exception as ex:
            st.error("Inconsistent frequency in data. Decomposition can not be preformed.")
            return
    fig = plot_seasonal_decompose(decomposition, dates=data.index, title=label)

    return fig


def autocorr_plot(df, column, lags=100):
    # fig, ax = plt.subplots(figsize=(8, 4))
    # plot_acf(df[column], lags=100, ax=ax, title='')
    # # Customize the x-axis title
    # plt.xlabel("Lag")
    # # Display the plot using Streamlit
    # st.pyplot(fig)

    df_acf = acf(df[column], nlags=lags)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=np.arange(len(df_acf)),
        y=df_acf,
        name='ACF',
    ))
    fig.update_xaxes(rangeslider_visible=True)
    fig.update_layout(
        title="Autocorrelation",
        xaxis_title="Lag",
        yaxis_title="Autocorrelation",
        #     autosize=False,
        #     width=500,
        height=500,
    )
    st.plotly_chart(fig, use_container_width=True)

    df_pacf = pacf(df[column], nlags=lags)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=np.arange(len(df_pacf)),
        y=df_pacf,
        name='PACF',
    ))
    fig.update_xaxes(rangeslider_visible=True)
    fig.update_layout(
        title="Partial Autocorrelation",
        xaxis_title="Lag",
        yaxis_title="Partial Autocorrelation",
        #     autosize=False,
        #     width=500,
        height=500,
    )
    return fig

    # st.markdown('**Partial Autocorrelation**')
    # fig, ax = plt.subplots(figsize=(8, 4))
    # plot_pacf(df[column], lags=100, ax=ax, title='')
    # # Customize the x-axis title
    # plt.xlabel("Lag")
    # # Display the plot using Streamlit
    # st.pyplot(fig)
    #


def show_anomaly_plot(model, ppdf, labels, selected_column=False, synth=False, ifo_res=None, ifo_anomalies =None):
    if selected_column:
        fig = px.line(ifo_res, x=ifo_res.index, y=[selected_column], title='Detected Outliers', width=1200, height=550)
        fig.update_traces(line_color='#1f77b4')
        outlier_dates_isofo = ifo_anomalies.index
        y_values_isofo = [ifo_res.loc[i][selected_column] for i in outlier_dates_isofo]
        # outlier_dates_lof = lf_anomalies.index
        # y_values_lof = [lf_res.loc[i][selected_column] for i in outlier_dates_lof]
        #
        # fig.add_trace(go.Scatter(x=outlier_dates_lof, y=y_values_lof, mode='markers',
        #                          name='Local Outlier Factor Anomaly',
        #                          marker=dict(color='red', size=7)))
        fig.add_trace(go.Scatter(x=outlier_dates_isofo, y=y_values_isofo, mode='markers',
                                 name='Anomaly',
                                 marker=dict(color='lightcoral', size=7)))
        fig.update_layout(
            xaxis_title="Datetime",
            yaxis_title=synth,
            # legend_title="Legend",
            # font=dict(
            #     family="Courier New, monospace",
            #     size=18,
            #     color="RebeccaPurple"
            # )
        )
        return fig
    else:


        isft_vi = model.feature_importances_
        results = pd.DataFrame(isft_vi, columns=["Value"])
        results['Feature'] = labels['Synth']
        results = results.sort_values(by="Value", ascending=False).head(5)

        fig = px.bar(
            results,
            x='Value',  # Values will be plotted on the x-axis
            y='Feature',  # Features will be on the y-axis
            orientation='h',  # Horizontal orientation for bar chart
            color='Value',  # You can change the color scale as desired
            title='Top 5 Contributing Features',
            color_continuous_scale="blues"
        )

        # Customize the layout (optional)
        fig.update_layout(
            yaxis_title='Feature',
            xaxis_title='Importance',
            yaxis_categoryorder='total ascending',  # Sort the features by total ascending value
            xaxis_showgrid=True,  # Show gridlines on the x-axis
            yaxis_showgrid=False,  # Hide gridlines on the y-axis
            bargap=0.15,  # Adjust the gap between bars
            margin=dict(l=100),  # Add left margin for long feature names
        )
        return fig

