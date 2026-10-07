# Sales Data Analytics Dashboard using Python

**Author:** Archit Mahajan  
**Program:** IBM SkillsBuild Data Analytics with AI Academic Internship 2026 (BharatCares | AICTE)  
**GitHub Repository:** https://github.com/archit-mahajan-dev/sales-data-analytics-dashboard

## Project Description
An end-to-end sales analytics project. It loads retail sales data, cleans it, analyses sales and profit by time, category, region and sub-category, and forecasts the next months of sales with a Linear Regression model. Results are shown in a Jupyter Notebook and in an interactive Streamlit dashboard with filters and KPI cards.

## Dataset
- **Superstore Sales Dataset (Kaggle):** https://www.kaggle.com/datasets/vivek468/superstore-dataset-final
- Download `Sample - Superstore.csv` and place it in the same folder as the notebook and `app.py`.
- If the CSV is not found, the code generates a small sample dataset with the same columns so the project still runs.

## Technologies Used
Python, Pandas, NumPy, Matplotlib, Scikit-learn (Linear Regression), Streamlit, Jupyter Notebook

## Project Files
| File | Purpose |
|---|---|
| `ArchitMahajan_SalesDashboard.ipynb` | Full analysis and forecasting notebook |
| `app.py` | Streamlit dashboard |
| `requirements.txt` | Python dependencies |
| `ArchitMahajan_ProjectReport.docx` | Project report |

## Setup and Run
```bash
# 1. (optional) create a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS / Linux

# 2. install dependencies
pip install -r requirements.txt

# 3. run the notebook
jupyter notebook ArchitMahajan_SalesDashboard.ipynb

# 4. run the dashboard
streamlit run app.py
```

## Key Features
- Data cleaning (duplicates, date parsing, missing values)
- KPIs: total sales, total profit, profit margin, record count
- Charts: monthly trend, category, region share, top sub-categories
- 6-month sales forecast with MAE, RMSE and R2 evaluation
- Dashboard filters for year, region and category

## Key Information
- The model uses a simple time index, so it captures the overall trend but not seasonality. A seasonal model (for example SARIMA or Prophet) would be a natural improvement.
