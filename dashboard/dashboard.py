import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency

# Set seaborn style
sns.set(style='dark')

# Load dataset
@st.cache_data
def load_data():
    # Ganti 'bike_sharing_data.csv' dengan path yang benar jika perlu
    df = pd.read_csv('all_data.csv')
    df['dteday'] = pd.to_datetime(df['dteday'])
    return df

# Helper functions
def create_day_df(data):
    return data.groupby(by="weathersit").agg(
        casual_nunique=('casual', 'nunique'),
        cnt_max=('cnt', 'max'),
        cnt_min=('cnt', 'min'),
        cnt_mean=('cnt', 'mean'),
        cnt_std=('cnt', 'std')
    ).reset_index()

def create_weekday_df(data):
    return data.groupby(by="weekday").agg(
        cnt_nunique=('cnt', 'nunique')
    ).reset_index().sort_values(by="cnt_nunique", ascending=False)

def create_workingday_df(data):
    return data.groupby(by="workingday").agg(
        cnt_sum=('cnt', 'sum')
    ).reset_index()

def create_sum_day_hour_df(data):
    return data.groupby("weathersit")[['registered', 'cnt', 'casual']].sum().sort_values(by='cnt', ascending=False).reset_index()

def create_rfm_df(data):
    rfm_df = data.groupby(by="mnth", as_index=False).agg({
        "dteday": "max",  
        "cnt": "sum"         
    })
    recent_date = data['dteday'].max()
    rfm_df['recency'] = (recent_date - rfm_df['dteday']).dt.days
    rfm_df['frequency'] = rfm_df['cnt']
    rfm_df['monetary'] = rfm_df['cnt']
    return rfm_df[['mnth', 'recency', 'frequency', 'monetary']]

# Memuat data
data = load_data()

# Sidebar filter untuk rentang waktu
with st.sidebar:
    st.image("https://raw.githubusercontent.com/delyuu/Bike-Sharing/main/sepeda.jpg")
    start_date, end_date = st.date_input(
        label='Rentang Waktu',
        min_value=data["dteday"].min(),
        max_value=data["dteday"].max(),
        value=[data["dteday"].min(), data["dteday"].max()]
    )

# Filter data berdasarkan rentang waktu
filtered_data = data[(data["dteday"] >= pd.to_datetime(start_date)) & (data["dteday"] <= pd.to_datetime(end_date))]

# Membuat dataframe yang dibutuhkan
day_df = create_day_df(filtered_data)
weekday_df = create_weekday_df(filtered_data)
workingday_df = create_workingday_df(filtered_data)
sum_day_hour_df = create_sum_day_hour_df(filtered_data)
rfm_df = create_rfm_df(filtered_data)

# Dashboard title
st.header('Bike Sharing Dashboard :sparkles:')

# Plot 1: Pengaruh Cuaca Terhadap Peminjaman Sepeda
st.subheader("Pengaruh Cuaca Terhadap Peminjaman Sepeda")

fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(24, 6))
colors = ["#72BCD4", "#D3D3D3", "#FF6347"]

# Total Peminjaman Sepeda
sns.barplot(x="cnt_max", y="weathersit", data=day_df, palette=colors, ax=ax[0])
ax[0].set_title("Total Peminjaman Sepeda", fontsize=15)
ax[0].set_xlabel("Jumlah Peminjam")
ax[0].set_ylabel("Cuaca")
ax[0].tick_params(axis='y', labelsize=12)

# Peminjaman Non-Terdaftar
sns.barplot(x="casual_nunique", y="weathersit", data=day_df, palette=colors, ax=ax[1])
ax[1].set_title("Peminjaman Sepeda Non-Terdaftar", fontsize=15)
ax[1].set_xlabel("Jumlah Peminjam")
ax[1].set_ylabel("Cuaca")
ax[1].tick_params(axis='y', labelsize=12)

# Peminjaman Terdaftar
sns.barplot(x="registered", y="weathersit", data=sum_day_hour_df, palette=colors, ax=ax[2])
ax[2].set_title("Peminjaman Sepeda Terdaftar", fontsize=15)
ax[2].set_xlabel("Jumlah Peminjam")
ax[2].set_ylabel("Cuaca")
ax[2].tick_params(axis='y', labelsize=12)

plt.suptitle("Pengaruh Cuaca Terhadap Peminjaman Sepeda", fontsize=20)
st.pyplot(fig)

# Plot 2: Perbandingan Jumlah Peminjam Sepeda saat Hari Kerja dan Hari Libur
st.subheader("Perbandingan Jumlah Peminjam Sepeda saat Hari Kerja dan Hari Libur")

fig, ax = plt.subplots(figsize=(10, 5))
colors = ["#72BCD4", "#D3D3D3"]

sns.barplot(
    y="cnt_sum", 
    x="workingday",
    data=workingday_df.sort_values(by="cnt_sum", ascending=False),
    palette=colors,
    hue="workingday",
    dodge=False
)
plt.title("Hari Kerja vs Libur (0=Libur, 1=Kerja)", fontsize=15)
plt.ylabel("Jumlah Peminjam")
plt.xlabel("Hari Kerja")
plt.xticks(ticks=[0, 1], labels=["Libur", "Kerja"], fontsize=12)
plt.yticks(fontsize=12)
plt.legend([], [], frameon=False)  # Menghilangkan legend
st.pyplot(fig)

# Plot 3: Perbandingan Jumlah Peminjam Sepeda Setiap Harinya
st.subheader("Perbandingan Jumlah Peminjam Sepeda Setiap Harinya")

fig, ax = plt.subplots(figsize=(10, 5))
colors = ["#72BCD4", "#FFC0CB", "#FF6347", "#8FBC8F", "#FFD700", "#6A5ACD", "#4682B4"]

sns.barplot(
    y="cnt_nunique", 
    x="weekday",
    data=weekday_df.sort_values(by="cnt_nunique", ascending=False),
    palette=colors,
    hue="weekday",
    dodge=False
)
plt.title("Jumlah Peminjam Sepeda Setiap Hari (0=Minggu, 6=Sabtu)", fontsize=15)
plt.ylabel("Jumlah Peminjam")
plt.xlabel("Hari")
plt.xticks(ticks=range(7), labels=["Minggu", "Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu"], fontsize=12)
plt.yticks(fontsize=12)
plt.legend([], [], frameon=False)  # Menghilangkan legend
st.pyplot(fig)

# Plot 4: RFM Analysis berdasarkan Bulan
st.subheader("RFM Analysis berdasarkan Bulan")

fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(24, 6))
colors = ["#72BCD4", "#5C9BC6", "#4682B4", "#3078A8", "#1B6492", "#FFD700", "#FF6347"]

sns.barplot(y="recency", x="mnth", data=rfm_df.sort_values(by="recency", ascending=True).head(5), palette=colors, ax=ax[0])
ax[0].set_title("By Recency (days)", fontsize=18)
ax[0].set_xlabel("Bulan")
ax[0].tick_params(axis='x', labelsize=15)

sns.barplot(y="frequency", x="mnth", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), palette=colors, ax=ax[1])
ax[1].set_title("By Frequency", fontsize=18)
ax[1].set_xlabel("Bulan")
ax[1].tick_params(axis='x', labelsize=15)

sns.barplot(y="monetary", x="mnth", data=rfm_df.sort_values(by="monetary", ascending=False).head(5), palette=colors, ax=ax[2])
ax[2].set_title("By Monetary", fontsize=18)
ax[2].set_xlabel("Bulan")
ax[2].tick_params(axis='x', labelsize=15)

plt.suptitle("Peminjaman Terbanyak pada Bulan apa?", fontsize=20)
st.pyplot(fig)

# Menampilkan footer
st.write("Dashboard powered by Streamlit")
