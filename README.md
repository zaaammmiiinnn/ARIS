# 🔐 Aadhaar Risk Intelligence System (ARIS)

ARIS is a **data analytics and visualization dashboard** built using **Streamlit** to analyze Aadhaar update datasets and highlight **risk patterns across India**.

The system follows a **clean backend–frontend architecture**, processes Aadhaar data into risk metrics, and presents insights through an interactive web interface.

---

## 🎯 Project Objectives

- Clean and preprocess Aadhaar demographic & biometric datasets
- Generate **risk indicators** at state and district levels
- Visualize insights through an interactive dashboard
- Maintain a scalable and modular architecture

---

## 🧠 System Architecture

UIDAI Raw Data
↓
Data Cleaning Pipeline
↓
Risk Engine
↓
Processed CSVs
↓
Streamlit Dashboard


---

## 🛠️ Tech Stack

- **Python**
- **Streamlit** – Dashboard framework
- **Pandas** – Data processing
- **Plotly** – Charts & analytics
- **Folium** – Reliable India map rendering
- **GeoJSON (Survey of India)** – National boundary

---

## 📂 Project Structure

```text
ARIS/
│
├── backend/
│   ├── api_clients/
│   │   └── uidai_api.py
│   ├── data_pipeline/
│   │   ├── clean_data.py
│   │   └── risk_engine.py
│
├── data/
│   ├── cleaned/
│   │   ├── biometric_cleaned.csv
│   │   ├── demographic_cleaned.csv
│   │   └── enrolment_cleaned.csv
│   └── processed/
│       ├── district_risk.csv
│       └── state_risk.csv
│
├── frontend/
│   ├── assets/
│   │   └── india-soi.geojson
│   └── app.py
│
├── .env
├── .gitignore
├── requirements.txt
└── README.md


##📊 Dashboard Features**
🇮🇳 India Map Overview

Uses Survey of India (SOI) GeoJSON

Rendered using Folium for full reliability

**📈 Key Metrics**

States analysed

Districts analysed

National average risk percentage

**🚨 Top 5 Risky States**

Correctly ordered by highest risk

Clear visual bar chart

**📊 State‑level Risk Table**

Sorted, searchable, and readable

**🎨 Professional UI**

Card‑based KPIs

Clean layout and styling
