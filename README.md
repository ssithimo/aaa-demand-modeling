# 📈 AAA Call Volume Forecasting

This project was conducted to help AAA Washington forecast emergency roadside assistance call volume — a service that represents over one-third of the organization’s operating budget. Through three modeling phases, we applied statistical and time series methods to predict call volume and extract actionable business insights.

---

## 🧩 Problem Context

AAA Washington noticed that call volumes were increasing faster than membership growth or inflation could explain. The operations VP hired me to investigate potential drivers and build models to improve forecasting accuracy for operational and financial planning.

---

## 🚦 Project Phases

### 📊 Phase 1: Linear Regression on Temperature

- **Goal**: Assess whether daily average temperature predicts call volume.
- **Methods**: Simple linear regression.
- **Key Insight**: Call volume increases as temperature drops. The model explains **~51%** of the variance.
- **Limitations**: Residuals showed non-constant variance and autocorrelation.

> 📄 `Phase1_Temperature_Regression.Rmd`

---

### 🔁 Phase 2: SARIMA Time Series Forecasting

- **Goal**: Model temporal patterns in call volume not explained by temperature.
- **Methods**: Seasonal ARIMA (Box-Jenkins approach).
- **Key Insight**: SARIMA(1,0,0)(1,1,0)[12] performed best, with **MAPE ~4.4%** on test data.
- **Strengths**: Captured seasonality and lag structures better than linear regression.

> 📄 `Phase2_ARIMA_Modeling.Rmd`

---

### 🧮 Phase 3: ADL Model with Exogenous Variables

- **Goal**: Build a multivariate model including:
  - Transformed temperature (distance from optimal 60°F)
  - Lagged unemployment rate (economic proxy)
- **Methods**: Time series regression (ADL model).
- **Key Insight**: Model explains **~64%** of variation with **MAPE ~3.4%**.
- **Business Value**: Stronger predictive power using operational and macroeconomic indicators.

> 📄 `Phase3_ADL_Multivariate_Modeling.Rmd`

---

## 📁 Files

| File | Description |
|------|-------------|
| `Phase1_Temperature_Regression.Rmd` | Linear regression analysis |
| `Phase2_ARIMA_Modeling.Rmd` | Seasonal ARIMA modeling |
| `Phase3_ADL_Multivariate_Modeling.Rmd` | ADL regression with temp & unemployment |
| `data/AAA.csv` | Cleaned data set with monthly call volume, temperature, state unemployment rate, rainfall average, and membership data|

---

## 🛠 Technologies Used

- R & RMarkdown
- `forecast`, `lmtest`, `ggplot2`, `tslm`
- Time Series Analysis (ARIMA, SARIMA)
- Regression Modeling (Linear, Autoregressive Distributive Lag)
- Cross-Correlation Function (CCF)
- Residual Diagnostics (ACF, QQ plots, Durbin-Watson test)

---

## 🧠 Key Takeaways

- Emergency service call volume is driven by **seasonal**, **temperature**, and **economic** factors.
- Time series regression using transformed variables improved forecast accuracy.
- Multiphase modeling showed an understanding of iterative, stakeholder-driven analytics.

---

## 📬 Contact

Feel free to reach out with questions, collaborations, or feedback.
