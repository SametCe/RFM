import pandas as pd
import datetime as dt
pd.set_option('display.max_rows', 10)
pd.set_option('display.max_columns', 10)
pd.set_option('display.width', 700)

df_ = pd.read_excel("Week_03/datasets/online_retail_II.xlsx", sheet_name="Year 2010-2011")

df = df_.copy()
df.head()

# Multiply "Quantity" with "Price" to get total price for each item in invoice.
df["TotalPrice"] = df["Quantity"] * df["Price"]

# Nulls
df.isnull().sum()
df.dropna(inplace=True)

# Drop the returned invoices. They contains "C" in "Invoice".
df = df[~df["Invoice"].str.contains("C", na=False)]

# Find the max invoice date time, this is needed to define ranges for recency and frequency parameters in RFM model.
df["InvoiceDate"].max()

today_date = dt.datetime(2011, 12, 11)

# Creating RFM parameters.
rfm = df.groupby("Customer ID").agg({"InvoiceDate" : lambda date: (today_date - date.max()).days,
                                     "Invoice" : lambda num : num.nunique(),
                                     "TotalPrice" : lambda price : price.sum()})

rfm.columns = ["Recency", "Frequency", "Monetary"]

# Extract values that could be considered outliers
rfm = rfm[(rfm["Monetary"]) > 0 & (rfm["Frequency"] > 0)]

# Creating RFM score.
rfm["Recency_Score"] = pd.qcut(rfm["Recency"], 5, labels=[5, 4, 3, 2, 1])

rfm["Frequency_Score"] = pd.qcut(rfm["Frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])

rfm["Monetary_Score"] = pd.qcut(rfm["Monetary"], 5, labels=[1, 2, 3, 4, 5])

rfm.head()

rfm["RFM_SCORE"] = (rfm["Recency_Score"].astype(str) +
                    rfm["Frequency_Score"].astype(str) +
                    rfm["Monetary_Score"].astype(str))

# Defining RFM segments.
seg_map = {
    r'[1-2][1-2]': 'Hibernating',
    r'[1-2][3-4]': 'At_Risk',
    r'[1-2]5': 'Cant_Loose',
    r'3[1-2]': 'About_to_Sleep',
    r'33': 'Need_Attention',
    r'[3-4][4-5]': 'Loyal_Customers',
    r'41': 'Promising',
    r'51': 'New_Customers',
    r'[4-5][2-3]': 'Potential_Loyalists',
    r'5[4-5]': 'Champions'
}


# Recency and Frequency is two main parameter for RFM score.
rfm["Segment"] = rfm["Recency_Score"].astype(str) + rfm["Frequency_Score"].astype(str)

rfm["Segment"] = rfm["Segment"].replace(seg_map, regex=True)

rfm.head()

# Evaluating segments
rfm[["Segment", "Recency", "Frequency", "Monetary"]].groupby("Segment").agg(["count", "mean", "max"])