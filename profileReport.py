import pandas as pd
from ydata_profiling import ProfileReport

df = pd.read_csv("DS\data\Flipkart\FiPhones_01-08-25.csv")
profile = ProfileReport(df, title="Data Profiling Report", explorative=True)
profile.to_file("report.html")
