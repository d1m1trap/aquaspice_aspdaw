from datetime import datetime

import pandas as pd


# def checkAnomalies(data=None, column=None, latest=3, bias=30, continuous=True):
#     random_data_std = data[column].std()
#     random_data_mean = data[column].mean()
#     anomaly_cut_off = random_data_std * 3
#
#     lower_limit = random_data_mean - anomaly_cut_off
#     # upper_limit = random_data_mean + anomaly_cut_off
#     anomalies = data[data[column] < lower_limit][column].tail(3)
#     data_res = data[data.index >= anomalies.tail(3).index[0]][column].head(3)
#     li = data_res.index == anomalies.tail(3).index
#     if li.all():
#         return True
#     return False

def append_alert(fpath, data_list, anomalies, column, datetimes=["Time", "Created"]):
    anom = pd.read_csv(fpath)
    for c in datetimes:
        anom[c] = pd.to_datetime(anom[c])
        anom = anom.sort_values(by=[c])

    last_time_index = anomalies.tail(1).index[0]

    # Filter rows based on the 'Time' condition
    matching_rows = anom[anom['Time'] == last_time_index]
    # Filter further based on the 'Variable' condition
    matching_rows = matching_rows[matching_rows['Tag'] == column]

    if not matching_rows.empty:
        print("Matching rows found.")
    else:
        anom = anom.append(pd.DataFrame([data_list], columns=anom.columns), ignore_index=True)
        anom.to_csv(fpath, index=False)


def alert(a_type, column, x_latest=3, values=None):
    # API call send the event
    if values is not None:
        print(values)


def checkAnomalies(data, column, labels, x_latest=3, upper_limit=None, lower_limit=None, send_alert=True, res=True,
                   to_file=True):
    synth = labels[labels['Tag'] == column]['Synth'].values[0]
    if upper_limit is None or lower_limit is None:
        data_std = data[column].std()
        data_mean = data[column].mean()
        anomaly_cut_off = data_std * 3
    if upper_limit is None:
        upper_limit = data_mean + anomaly_cut_off
    if lower_limit is None:
        lower_limit = data_mean - anomaly_cut_off
    anomalies_lower = data[data[column] < lower_limit][column]
    anomalies_upper = data[data[column] > upper_limit][column]
    li_lower = li_upper = False
    if x_latest and x_latest <= len(anomalies_lower):
        data_res_lower = data[data.index >= anomalies_lower.tail(x_latest).index[0]][column].head(x_latest)
        anomalies_lower = anomalies_lower.tail(x_latest)
        li_lower = data_res_lower.index == anomalies_lower.index
        if li_lower.all():
            li_lower = True
            if send_alert:
                alert("low", column, x_latest, values=anomalies_lower)
                if to_file:
                    data_list = [
                        str(anomalies_lower.tail(1).index[0]), column, synth, anomalies_lower.tail(1)[0],
                        "Low limit alert was sent", datetime.now()
                    ]
                    append_alert('data/alerts/alerts.csv', data_list, anomalies_lower, column)
        else:
            li_lower = False
    if x_latest and x_latest <= len(anomalies_upper):
        data_res_upper = data[data.index >= anomalies_upper.tail(x_latest).index[0]][column].head(x_latest)
        anomalies_upper = anomalies_upper.tail(x_latest)
        li_upper = data_res_upper.index == anomalies_upper.index
        if li_upper.all():
            li_upper = True
            if send_alert:
                alert("high", column, x_latest, values=anomalies_upper)
                if to_file:
                    data_list = [
                        str(anomalies_upper.tail(1).index[0]), column, synth, anomalies_upper.tail(1)[0],
                        "High limit alert was sent", datetime.now()
                    ]
                    append_alert('data/alerts/alerts.csv', data_list, anomalies_upper, column)
        else:
            li_upper = False
    if res:
        return [li_lower, li_upper]
