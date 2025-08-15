# Data-Analyst-Agent-API

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)  
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)  
[![LLM Powered](https://img.shields.io/badge/LLM-Powered-orange.svg)]()  
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)  

An **AI-powered API** that can **source, prepare, analyze, and visualize data** based on plain English instructions.  
This project automates **end-to-end data analysis** — from fetching datasets to returning ready-to-use insights and visualizations.  

---

## Key Features

✅ Accepts **natural language** queries for analysis  
✅ Handles **multiple input formats** (`.csv`, `.json`, `.png`, `.jpg`, `.txt`)  
✅ **Scrapes & fetches** data from external sources if required  
✅ Performs **data cleaning, transformation, and statistical analysis**  
✅ Generates **charts & visualizations** (Base64-encoded images)  
✅ Returns **results in the requested format** (JSON arrays, objects, or data URIs)  
✅ **Deployed on Render** for reliable cloud hosting  

---

## ⚙️ Tech Stack

- **Backend:** Python + FastAPI  
- **LLM Integration:** OpenAI / Groq / OpenRouter 
- **Data Processing:** Pandas, NumPy, DuckDB  
- **Visualization:** Matplotlib, Seaborn  
- **Deployment:** Render Cloud  

---

## Example Request

```bash
curl "http://localhost:8000/api/" \
  -F "questions.txt=@questions.txt" \
  -F "data.csv=@dataset.csv"
```
---

## Example Use Cases

💰 **Movies Data** – Scrape Wikipedia for highest-grossing films and analyze trends  
⚖️ **Judgement Data** – Query and visualize 1TB+ of Indian High Court judgments  
📈 **Sales & Finance** – Correlation analysis, forecasting, regression plots  
🌦 **Weather** – Historical trend visualization, anomaly detection  

---

## Run Locally

1️. **Clone the repository**
```bash
git clone https://github.com/ckritk/Data-Analyst-Agent-API.git
cd data-analyst-agent
```

2️. **Set up environment variables**  
Copy the `ENV_TEMPLATE` file to `.env` and fill in your keys/config:
```bash
cp ENV_TEMPLATE .env
```

3️. **Install dependencies**
```bash
pip install -r requirements.txt
```

4️. **Run the application**
```bash
bash start.sh
```

The app will now be running locally at:
```
http://127.0.0.1:8000
```

---

## License

This project is licensed under the [MIT License](LICENSE).
