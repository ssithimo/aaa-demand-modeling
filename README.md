# 🚗 AAA Washington — Emergency Road Service Demand Forecasting

> *Call volumes were rising faster than membership growth could explain. The operations VP needed to know why and how to plan for it.*

---

Click here for [dashboard](https://aaa-calls-modeling.streamlit.app/)

## 🧩 Business Context
Emergency roadside service represents over one-third of AAA Washington's operating budget. When call volume exceeds forecast, the organization 
faces unplanned overtime costs and service delays. When it falls short, resources sit idle. Either direction is expensive.

AAA Washington's operations VP noticed call volumes were rising faster than membership growth or inflation could explain and needed two things: 
an explanation of what was actually driving demand, and a reliable forecast to support staffing and budget planning.

This project worked through three iterative modeling phases to answer both questions.

---

## 🚦 Modeling Approach

### Phase 1: Temperature Regression

**Question:** Does temperature predict call volume?

Simple linear regression revealed that call volume increases as temperature drops, with the model explaining approximately 45% of variance. The relationship seemed intuitive as colder weather causes more vehicle failures. However, residuals showed non-constant variance and autocorrelation, indicating temperature alone was insufficient and temporal patterns needed to be modeled explicitly.

> Notebook: `Phase1_Temp_Regression.Rmd`

---

### Phase 2: SARIMA Time Series Forecasting

**Question:** What temporal patterns exist beyond temperature?

A seasonal ARIMA model (SARIMA(1,0,0)(1,1,0)[12]) captured monthly seasonality and lag structures that pure regression missed, achieving MAPE of 2.5% on test data. This established a strong time series baseline but left room to incorporate the economic and environmental drivers identified in Phase 1.

> Notebook: `Phase2_ARIMA_Modeling.Rmd`

---

### Phase 3: ADL Model with Exogenous Variables

**Question:** Can macroeconomic and environmental factors improve accuracy?

An Autoregressive Distributed Lag (ADL) model incorporated two engineered variables:

- **Temperature deviation from 60°F**

  centered at the threshold below which vehicle failures accelerate, improving linearity
  
- **Lagged unemployment rate**
  identified via cross-correlation analysis as a leading economic indicator of call volume, reflecting that economic stress correlates with deferred vehicle maintenance

The ADL model explained 57% of call volume variation at MAPE of 3.6%. While MAPE is slightly higher than the pure SARIMA model, the ADL model provides something SARIMA cannot: an explanation of *why* volume changes, giving operations leadership levers to anticipate demand shifts before they appear in the data.

> Notebook: `Phase3_ADL_Modeling.Rmd`

---

## 📊 Model Comparison

| Model | MAPE | Variance Explained | Business Value |
|-------|------|-------------------|----------------|
| Temperature Regression | — | ~45% | Identifies temperature as primary driver |
| SARIMA(1,0,0)(1,1,0)[12] | 2.5% | — | Best raw forecast accuracy |
| ADL (Temp + Unemployment Lag) | 3.6% | ~57% | Explains drivers, supports planning |

SARIMA wins on forecast accuracy. ADL wins on interpretability and operational utility. For budget and staffing planning, the ADL model is the more actionable output — it tells us not just what call volume will be, but what conditions are driving it.

---

## 🧠 Key Findings

1. **Temperature deviation from 60°F is the primary demand driver**

   vehicle failure rates accelerate as temperatures drop below this threshold, making it the single most reliable predictor of high-volume service periods. Winter staffing decisions should be anchored to temperature forecasts.

2. **Unemployment rate predicts call volume with a lag**

   when unemployment rises, members defer vehicle maintenance, leading to higher failure rates and service calls several months later. This gives operations leadership an early warning signal available from public economic data before the demand spike arrives.

3. **Call volume has strong seasonal structure**

   SARIMA's 2.5% MAPE confirms that monthly patterns are highly predictable from historical data alone, providing a reliable baseline for annual budget planning.

---

## 📝 Operational Recommendations

1. **Use SARIMA for annual budget forecasting**

   its 2.5% MAPE provides a reliable baseline for headcount and resource planning at the yearly planning cycle

3. **Use ADL for in-season operational adjustments**

   when unemployment trends upward or temperature forecasts show an unusually cold period approaching, the ADL model quantifies the expected demand impact before it arrives

5. **Monitor unemployment rate as a leading indicator**

   publicly available monthly unemployment data can be fed directly into the ADL model to generate rolling demand updates without additional data collection

---

## 📁 Files

| File | Description |
|------|-------------|
| `Phase1_Temp_Regression.Rmd` | Linear regression on temperature |
| `Phase2_ARIMA_Modeling.Rmd` | Seasonal ARIMA modeling |
| `Phase3_ADL_Modeling.Rmd` | ADL model with temperature and unemployment |
| `data/aaa_washington.csv` | Monthly call volume, temperature, unemployment, rainfall, membership |
| `executive-summary-aaa.pdf` | One-page non-technical summary |

---

## 🔧 Tools
R, RMarkdown, `forecast`, `lmtest`, `ggplot2`, `tslm`
Time Series: SARIMA, ADL, Cross-Correlation Function (CCF)
Diagnostics: ACF, QQ plots, Durbin-Watson test

