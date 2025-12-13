#  Financial Analysis Dashboard with Python & Machine Learning

Aplicación web interactiva desarrollada con **Python** y **Streamlit** para el análisis, visualización y predicción de datos financieros, integrando datos históricos desde archivos CSV y datos reales obtenidos con **yfinance**.

---

##  Overview

Este proyecto centraliza información financiera dispersa y la transforma en métricas claras, visualizaciones interactivas y predicciones basadas en Machine Learning.
Está orientado a fines educativos y analíticos, demostrando cómo combinar **Data Science**, **Machine Learning** y **Finanzas** en una sola aplicación funcional.

---

##  Team

**Team Name:** **SPAGHETTI CODERS**
**Course:** Samsung Innovation Campus
**Classroom:** PA09

### Members

* Ovidio Roberto Calderón Esquivel
* Diego Alexander Gordón Ruiz
* Chen Enrique Alex Fong Fan
* Anthony Praxedes Torres Silleros
* Lia Anyeline Cárdenas Berrio

---

##  Features

* Data sources:

  * Local CSV file
  * Live financial data using **yfinance**
* Individual company financial analysis
* Company comparison
* Key financial metrics visualization:

  * Revenue
  * Net Income
  * Profit Margins
  * ROE / ROA
  * P/E Ratio
* Interactive charts and descriptive statistics
* Financial forecasting using Machine Learning
* Model comparison with performance evaluation
* Anomaly detection in financial time series
* Company clustering by financial profile
* Web-based UI built with **Streamlit**

---

##  Machine Learning Models

### Supervised Learning (Prediction)

* Linear Regression
* Polynomial Regression (degree 2)
* Random Forest Regressor

### Unsupervised Learning

* Isolation Forest (anomaly detection)
* KMeans (company clustering)

Model evaluation is performed using **MAE** and **MAPE** metrics.

---

##  Technologies Used

* Python
* Streamlit
* Pandas
* NumPy
* Matplotlib
* Seaborn
* Scikit-learn
* yfinance

---

##  Project Structure

```bash
financial-dashboard/
│
├── app_analisis_financiero.py
├── Financial Statements.csv
├── README.md
├── requirements.txt
```

---

##  Installation & Usage

### 1. Clone the repository

```bash
git clone <repository-url>
cd financial-dashboard
```

### 2. (Optional) Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate        
venv\Scripts\activate           
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the application

```bash
streamlit run app_analisis_financiero.py
```

---

##  Dataset: Financial Statements.csv

The CSV file contains historical financial data for multiple companies, including:

| Column            | Description            |
| ----------------- | ---------------------- |
| Company           | Company name or ticker |
| Year              | Financial year         |
| Revenue           | Company revenue        |
| Net Income        | Net profit             |
| Gross Profit      | Gross profit           |
| Market Cap        | Market capitalization  |
| ROE               | Return on Equity       |
| ROA               | Return on Assets       |
| Net Profit Margin | Net profit margin      |

---

##  How the Application Works

1. The user selects the data source (CSV or yfinance).
2. The system cleans and processes the data automatically.
3. Financial metrics and charts are displayed.
4. The user can:

   * Analyze a single company
   * Compare companies
   * Explore descriptive statistics
   * Generate forecasts using Machine Learning
5. Models are evaluated and results are interpreted automatically.

---

##  Project Relevance

This project demonstrates how **Python**, **financial analysis**, **Machine Learning**, and **data visualization** can be integrated into a single, scalable and educational application.
It is suitable as a final academic project or as a portfolio piece for data-related roles.

---

##  Notes

* Predictions are for educational purposes only.
* Financial data depends on availability from Yahoo Finance.
* The application focuses on interpretability rather than high-frequency trading accuracy.
