# AloeGreen Backend API 🌿

AloeGreen is a FastAPI-based backend system for a smart agriculture platform. It integrates multiple AI/ML models, IoT data processing, and a community alert system to support Aloe vera farming.

## 🚀 Features

- 🌿 Disease Detection (Image-based ML)
- 🌱 Fertilizer Recommendation
- 📊 Yield Prediction
- 💰 Price Prediction & Risk Analysis
- 🌦️ Weather Forecasting
- 📡 IoT Data Handling (MQTT → MongoDB)
- 📢 Community Alert System

## 🛠️ Tech Stack

- FastAPI, Uvicorn
- TensorFlow / Keras / TFLite
- Scikit-learn, XGBoost
- MongoDB (PyMongo, Motor)
- MQTT (Paho-MQTT)
- Pandas, NumPy

## 📂 Run the Backend

```bash
venv\Scripts\activate
uvicorn App:app --host 0.0.0.0 --port 8000 --reload
````

## 🌐 Access

Backend:
[http://localhost:8000](http://localhost:8000)

Mobile (use your PC IP):
http://YOUR_IP:8000

## 📡 API Docs

[http://localhost:8000/docs](http://localhost:8000/docs)

## 📦 Modules

* Disease Detection
* Fertilizer System
* Yield Prediction
* Price Prediction
* Weather Forecast
* Community Alerts
* IoT Data System

## ⚙️ Setup

```bash
pip install -r requirements.txt
```

## 📌 Notes

* Use same Wi-Fi for mobile & backend
* Replace localhost with your IP for mobile testing
* Ensure MongoDB & MQTT are configured properly

---

**AloeGreen 🌿 – Smart Farming with AI**

