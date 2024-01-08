# from datetime import datetime
#
# import pandas as pd
# from pyod.models.iforest import IForest
# from helpers import load_data, get_path, plot_anomaly
# from joblib import dump, load
# # from matplotlib import pyplot as plt
#
# path = get_path()
# fpath = path + '\ppDataCT3201General.csv'
#
# def isofo():
#     print("Load data")
#     df = load_data(fpath, "Time", True)
#     print("Data loaded successfully.")
#     print("Model is fitted using Isolation Forest algorithm")
#     if variable != "all":
#         if variable == "Humidity":
#             col = 'C3W_AI_0040'
#         else:
#             col = df.columns[1]
#         isft_uv = IForest(contamination=contamination, max_samples=1, max_features=1, behaviour='new')
#         isft_uv.fit(df[[col]].values)
#         ifo_res = df[[variable]].copy()
#         ifo_res['is_anomaly_pred'] = isft_uv.predict(df[[variable]].values)
#         ifo_anomalies = ifo_res[ifo_res['is_anomaly_pred'] == 1]
#         print("Sample outliers:")
#         print(ifo_anomalies.head(5))
#     else:
#         isft = IForest(contamination=contamination, max_samples=max_samples, max_features=max_features,behaviour='new')
#         isft.fit(df)
#         mpath = path + "\models\isft" + str(datetime.now().strftime("%Y%m%d%H%M%S")) + '.joblib'
#         dump(isft, mpath)
#         print("Model is ready.")
#         print("threshold:", isft.threshold_)
#         # load the model
#         # clf = load('clf.joblib')
#         isft_vi = isft.feature_importances_
#         importance = pd.DataFrame(isft_vi, columns=["Value"])
#         importance['Feature'] = df.columns
#         importance = importance.sort_values(by="Value", ascending=False).head(5)
#     # count_true = 1
#         print("Feature importance: ")
#         for index, row in importance.iterrows():
#             # key = str(count_true) + row['Feature']
#             print(f"{row['Feature']}: {row['Value']}")
#             # count_true = count_true + 1
#     print("Step completed.")
#
#
# def univariate(col):
#     df = load_data(fpath, "Time", True)
#     Q1 = df[col].quantile(0.25)
#     Q3 = df[col].quantile(0.75)
#     IQR = Q3 - Q1
#     c = 2
#     min_t = Q1 - c * IQR
#     max_t = Q3 + c * IQR
#     df[col + 'threshold_alarm'] = (df[col].clip(lower=min_t, upper=max_t) != df[col])
#
#
# # def show_results(model, ppdf, uni=False, col=False):
# #     if uni and col:
# #         plot_anomaly(ppdf[col], anomaly_pred=ppdf[ppdf[col + 'threshold_alarm'] == True][col + 'threshold_alarm'],
# #                      anomaly_true=None, file_name='file')
# #     else:
# #         isft = load(model)
# #         isft_vi = isft.feature_importances_
# #         results = pd.DataFrame(isft_vi, columns=["Value"])
# #         results['Feature'] = ppdf.columns
# #         results = results.sort_values(by="Value", ascending=False).head(5)
# #
# #         # Create a horizontal bar plot
# #         plt.figure(figsize=(10, 8))  # Adjust the figure size as needed
# #
# #         # Extract the "Feature" and "Value" columns
# #         features = results['Feature']
# #         values = results['Value']
# #
# #         # Create the horizontal bar plot
# #         plt.barh(features, values, color='skyblue')  # You can change the color as desired
# #
# #         # Set labels and title
# #         plt.xlabel('Importance')
# #         # plt.ylabel('Feature')
# #         plt.title('Top 5 important features')
# #
# #         # Show the plot
# #         plt.tight_layout()  # Ensures labels and titles fit within the figure
# #         plt.show()
#
#
# if __name__ == "__main__":
#     isofo()