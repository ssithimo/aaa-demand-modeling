import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime
from dateutil.relativedelta import relativedelta
from statsmodels.tsa.statespace.sarimax import SARIMAX

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AAA Washington – ERS Demand Forecaster",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>

/* =====================================================
   AAA ROAD SERVICE FORECASTING DASHBOARD

   Design Goals:
   - Executive reporting aesthetic
   - Corporate branding palette
   - KPI-driven layout
   - Forecast visualization containers
   - Staffing recommendation highlights

   Fonts:
   - Playfair Display (headings)
   - DM Sans (body text)
   ===================================================== */
            
/* ============
   GOOGLE FONTS
   ============ */

@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700;900&family=DM+Sans:wght@300;400;500;600&display=swap');

/* ============
   COLOR PALETTE
   ============ */ 

:root {
    --navy:#0f1f3d; --blue:#1a3a6b; --accent:#e8a020;
    --light:#f5f4f0; --white:#ffffff; --text:#1a1a2e;
    --muted:#5a6480; --green:#2d6a4f; --green-light:#d8f3dc;
    --orange:#e07b39; --orange-light:#fef0e4;
    --red:#c8282e; --border:#e0ddd8;
}

/* ========================
    GLOBAL PAGE STYLING
    default fonts, bg, text
   ======================= */

html,body,[class*="css"]{font-family:'DM Sans',sans-serif;background:var(--light);color:var(--text);}

/* ========================
   DASHBOARD-SPECIFIC STYLES
   ======================= */

.main .block-container{padding:2rem 3rem;max-width:1400px;}

/* Dashboard header with gradient background and decorative circle */
            
.dashboard-header{background:linear-gradient(135deg, #e63946 0%, #1a3560 100%);border-radius:16px;padding:2.5rem 3rem;margin-bottom:2rem;position:relative;overflow:hidden;}
.dashboard-header::before{content:'';position:absolute;top:-60px;right:-60px;width:280px;height:280px;border-radius:50%;background:rgba(200,40,46,0.08);}
.header-label{font-size:.72rem;font-weight:600;letter-spacing:.15em;text-transform:uppercase;color:var(--accent);margin-bottom:.4rem;}
.header-title{font-family:'Playfair Display',serif;font-size:2.3rem;font-weight:900;color:var(--white);line-height:1.1;margin-bottom:.4rem;}
.header-sub{font-size:.95rem;color:rgba(255,255,255,.6);}

/* KPI cards with dynamic delta coloring */
            
.kpi-card{background:var(--white);border-radius:12px;padding:1.3rem 1.5rem;border:1px solid var(--border);box-shadow:0 2px 8px rgba(0,0,0,.04);}
.kpi-label{font-size:.70rem;font-weight:600;letter-spacing:.1em;text-transform:uppercase;color:var(--muted);margin-bottom:.4rem;}
.kpi-value{font-family:'Playfair Display',serif;font-size:1.85rem;font-weight:700;color:var(--navy);line-height:1;margin-bottom:.25rem;}
.kpi-delta{font-size:.80rem;font-weight:500;}
.kpi-delta.up{color:var(--green);} .kpi-delta.neutral{color:var(--muted);} .kpi-delta.warn{color:var(--orange);}

/* Section headers and subtitles */
            
.section-header{font-family:'Playfair Display',serif;font-size:1.25rem;font-weight:700;color:var(--navy);margin-bottom:.2rem;padding-bottom:.45rem;border-bottom:2px solid var(--accent);display:inline-block;}
.section-sub{font-size:.83rem;color:var(--muted);margin-bottom:1.1rem;}

/* Chart container with white background, rounded corners, and subtle shadow */

.chart-box{background:var(--white);border-radius:12px;padding:1.4rem;border:1px solid var(--border);box-shadow:0 2px 8px rgba(0,0,0,.04);}
.insight-box{border-left:3px solid var(--blue);border-radius:0 8px 8px 0;padding:.85rem 1.1rem;margin-top:.9rem;font-size:.86rem;color:var(--text);background:#f0f4ff;}
.insight-box.warn{background:var(--orange-light);border-left-color:var(--orange);}
.insight-box.info{background:#f0f4ff;border-left-color:var(--blue);}

/* Staffing recommendation cards with color coding based on forecasted demand level */

.staffing-card{border-radius:12px;padding:1.3rem 1.5rem;border:1px solid var(--border);margin-top:.8rem;}
.staffing-card.low{background:var(--green-light);border-color:#74c69d;}
.staffing-card.med{background:var(--orange-light);border-color:#f4a261;}
.staffing-card.high{background:#fde8e8;border-color:#e07070;}

/* Custom table styles for forecast detail table */

.divider{height:1px;background:var(--border);margin:1.8rem 0;}
.footer{text-align:center;padding:1.2rem;font-size:.76rem;color:var(--muted);margin-top:1.5rem;}
.custom-table{width:100%;border-collapse:collapse;font-size:.87rem;}
.custom-table th{background:var(--navy);color:var(--white);padding:.65rem 1rem;text-align:left;font-size:.75rem;letter-spacing:.05em;text-transform:uppercase;}
.custom-table td{padding:.6rem 1rem;border-bottom:1px solid var(--border);}
.custom-table tr:last-child td{border-bottom:none;}
.custom-table tr:hover td{background:var(--light);}

/* Model badges for quick visual comparison */

.model-badge{display:inline-block;padding:.2rem .7rem;border-radius:20px;font-size:.75rem;font-weight:600;}
.badge-best{background:var(--green-light);color:var(--green);}
.badge-ok{background:#f0f4ff;color:var(--blue);}
</style>
""", unsafe_allow_html=True)

# ── Monthly temp defaults from historical data ────────────────────────────────
MONTHLY_TEMP_DEFAULTS = {
    1: 40.8, 2: 41.5, 3: 45.5, 4: 51.5, 5: 55.6,
    6: 60.6, 7: 64.7, 8: 64.9, 9: 60.7, 10: 52.0,
    11: 45.9, 12: 39.8
}
MONTH_NAMES = {
    1:'Jan',2:'Feb',3:'Mar',4:'Apr',5:'May',6:'Jun',
    7:'Jul',8:'Aug',9:'Sep',10:'Oct',11:'Nov',12:'Dec'
}

# ── Load data ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv('aaa_washington.csv')
    df['date'] = pd.to_datetime(df['date'])
    df['newtemp'] = abs(df['Temp'] - 60)
    df['lagrate11'] = df['Rate'].shift(11)
    df['month'] = df['date'].dt.month
    df['year']  = df['date'].dt.year
    df['month_name'] = df['date'].dt.strftime('%b %Y')
    df['pred_p1'] = 27414.06 + (-117.58) * df['Temp']
    df_p3 = df.dropna(subset=['lagrate11']).copy()
    df['pred_p3'] = np.nan
    df.loc[df_p3.index, 'pred_p3'] = (
        19748.61 + 181.31 * df_p3['newtemp'] + (-43.04) * df_p3['lagrate11']
    )
    return df

df = load_data()

# ── SARIMA Model ────────────────────────────────────────────────────
# SARIMA(1,0,0)(1,1,0)[12]

sarima_order = (1,0,0)
sarima_sorder = (1,1,0,12)

@st.cache_resource #model only fits once on app load, results cached for fast reuse
def fit_sarima(calls_series):
    model = SARIMAX(
        calls_series,
        order = sarima_order,
        seasonal_order = sarima_sorder,
        enforce_stationarity = False,
        enforce_invertibility = False
    )
    results = model.fit(disp = False)
    return results

sarima_results = fit_sarima(df['Calls'])

def sarima_forecast(n_months):
    forecast_obj = sarima_results.get_forecast(steps=n_months)
    mean = forecast_obj.predicted_mean.values.astype(int).tolist()
    ci = forecast_obj.conf_int(alpha = 0.05)
    ci_lower = ci.iloc[:, 0].values.astype(int).tolist()
    ci_upper = ci.iloc[:, 1].values.astype(int).tolist()
    return mean, ci_lower, ci_upper

# ── Forecast helpers ──────────────────────────────────────────────────────────
def p1_forecast(temp_f):
    return int(27414.06 + (-117.58) * temp_f)

def p3_forecast(temp_f, forecast_date):
    newtemp = abs(temp_f - 60)
    lag_date = forecast_date - pd.DateOffset(months=11)
    
    rate_row = df.loc[df['date'] == lag_date, 'Rate']
    
    if rate_row.empty:
        unemp_rate = df['Rate'].iloc[-1]  # last available rate
    else:
        unemp_rate = rate_row.values[0]
    
    return int(19748.61 + 181.31 * newtemp + (-43.04) * unemp_rate)

def get_forecast_dates(n_months):
    last_date = df['date'].iloc[-1]
    return [last_date + relativedelta(months=i+1) for i in range(n_months)]

# staffing recommendation helper based on forecasted calls vs historical average
# returns a tuple of (css_class, label_text, recommendation_text)
def staffing_label(calls):
    avg = df['Calls'].mean()
    std = df['Calls'].std()

    if calls < avg - 0.5*std:
        return 'low',  '✅ Below Average', 'Standard staffing adequate.'
    elif calls < avg + 0.5*std:
        return 'med',  '⚠️ Near Average',  'Monitor closely. Pre-approve contingency overtime.'
    else:
        return 'high', '🔴 Above Average', 'Elevated demand. Activate standby dispatchers.'

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="dashboard-header">
    <div class="header-label">AAA Washington · Operations Analytics · 1988–1992</div>
    <div class="header-title">Emergency Road Service Demand Forecaster</div>
    <div class="header-sub">Three-phase analysis identifying temperature and unemployment as primary call volume drivers. Use the model comparison panel to forecast and compare all three approaches.</div>
</div>
""", unsafe_allow_html=True)

# ── KPI row ───────────────────────────────────────────────────────────────────
k1,k2,k3,k4,k5 = st.columns(5)
avg_calls = int(df['Calls'].mean())
max_calls = int(df['Calls'].max())
min_calls = int(df['Calls'].min())
max_month = df.loc[df['Calls'].idxmax(),'month_name']
min_month = df.loc[df['Calls'].idxmin(),'month_name']

with k1:
    st.markdown(f'<div class="kpi-card"><div class="kpi-label">Avg Monthly Calls</div><div class="kpi-value">{avg_calls:,}</div><div class="kpi-delta neutral">Over 52 months</div></div>', unsafe_allow_html=True)
with k2:
    st.markdown(f'<div class="kpi-card"><div class="kpi-label">Peak Month</div><div class="kpi-value">{max_calls:,}</div><div class="kpi-delta warn">{max_month}</div></div>', unsafe_allow_html=True)
with k3:
    st.markdown(f'<div class="kpi-card"><div class="kpi-label">Lowest Month</div><div class="kpi-value">{min_calls:,}</div><div class="kpi-delta up">{min_month}</div></div>', unsafe_allow_html=True)
with k4:
    st.markdown(f'<div class="kpi-card"><div class="kpi-label">SARIMA MAPE</div><div class="kpi-value">2.5%</div><div class="kpi-delta up">Phase 2 validation</div></div>', unsafe_allow_html=True)
with k5:
    st.markdown(f'<div class="kpi-card"><div class="kpi-label">ADL Adj. R²</div><div class="kpi-value">57.1%</div><div class="kpi-delta neutral">Phase 3 in-sample</div></div>', unsafe_allow_html=True)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ── TABS ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs([
    "📈 Historical Analysis",
    "🔮 Model Comparison & Forecast",
    "📋 Model Summary"
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1: Historical Analysis
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown('<br>', unsafe_allow_html=True)
    st.markdown('<div class="section-header">Historical Call Volume</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Monthly emergency roadside service calls with fitted model lines, May 1988 to August 1992</div>', unsafe_allow_html=True)

    fig_hist = go.Figure()

    # Winter shading
    for yr in range(1988, 1993):
        fig_hist.add_vrect(
            x0=f'{yr}-11-15', x1=f'{yr+1}-03-15',
            fillcolor='rgba(200,40,46,0.05)',
            layer='below', line_width=0
        )

    fig_hist.add_trace(go.Scatter(
        x=df['date'], y=df['Calls'],
        mode='lines', name='Actual Calls',
        line=dict(color='#0f1f3d', width=2.5),
        hovertemplate='%{x|%b %Y}<br><b>Actual: %{y:,}</b><extra></extra>'
    ))
    fig_hist.add_trace(go.Scatter(
        x=df['date'], y=df['pred_p1'],
        mode='lines', name='Phase 1: Temp Regression',
        line=dict(color='#c8282e', width=1.8, dash='dash'),
        hovertemplate='%{x|%b %Y}<br>Phase 1: %{y:,.0f}<extra></extra>'
    ))
    fig_hist.add_trace(go.Scatter(
        x=df.dropna(subset=['pred_p3'])['date'],
        y=df.dropna(subset=['pred_p3'])['pred_p3'],
        mode='lines', name='Phase 3: ADL Model',
        line=dict(color='#e8a020', width=1.8, dash='dot'),
        hovertemplate='%{x|%b %Y}<br>Phase 3 ADL: %{y:,.0f}<extra></extra>'
    ))

    fig_hist.update_layout(
        plot_bgcolor='white', paper_bgcolor='white',
        height=360, margin=dict(t=20,b=10,l=10,r=10),
        legend=dict(orientation='h',yanchor='bottom',y=1.02,xanchor='right',x=1,
                    font=dict(size=11,family='DM Sans')),
        xaxis=dict(tickformat='%b %Y',gridcolor='rgba(0,0,0,0)',
                   tickfont=dict(size=11,family='DM Sans')),
        yaxis=dict(tickformat=',',gridcolor='#f0ede8',
                   tickfont=dict(size=11,family='DM Sans'),
                   title=dict(text='Monthly Calls',font=dict(size=11,family='DM Sans'))),
        hovermode='x unified'
    )

    st.markdown('<div class="chart-box">', unsafe_allow_html=True)
    st.plotly_chart(fig_hist, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="insight-box info">
        <strong>Reading the chart:</strong> Phase 1 (red dashed) uses raw temperature only —
        it captures the broad seasonal pattern but misses finer variation. Phase 3 ADL (gold dotted)
        incorporates temperature deviation from 60°F plus lagged unemployment, tracking more
        closely to actual call volume. Winter months (shaded) consistently show demand peaks.
        Phase 2 SARIMA fitted values are shown in the Model Comparison tab.
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # Temperature analysis
    st.markdown('<div class="section-header">Temperature Driver Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">The 60°F threshold — vehicle failures accelerate as temperatures deviate from this point</div>', unsafe_allow_html=True)

    tc1, tc2 = st.columns(2)
    with tc1:
        fig_temp = go.Figure()
        fig_temp.add_trace(go.Scatter(
            x=df['Temp'], y=df['Calls'], mode='markers',
            marker=dict(color=df['newtemp'], colorscale='RdYlBu_r', size=9,
                        colorbar=dict(title=dict(text='|T-60°F|',font=dict(size=10))),
                        line=dict(color='white',width=0.5)),
            hovertemplate='Temp: %{x}°F<br>Calls: %{y:,}<extra></extra>'
        ))
        temp_range = np.linspace(33, 70, 100)
        fig_temp.add_trace(go.Scatter(
            x=temp_range, y=27414.06 + (-117.58)*temp_range,
            mode='lines', line=dict(color='#c8282e',width=2,dash='dot'),
            name='Phase 1 fit', hoverinfo='skip'
        ))
        fig_temp.add_vline(x=60, line_dash='dash', line_color='#2d6a4f', line_width=2,
                           annotation_text='60°F',
                           annotation_font=dict(size=10,color='#2d6a4f',family='DM Sans'))
        fig_temp.update_layout(
            plot_bgcolor='white', paper_bgcolor='white',
            height=300, margin=dict(t=20,b=10,l=10,r=10), showlegend=False,
            xaxis=dict(title=dict(text='Avg Monthly Temp (°F)',font=dict(size=11,family='DM Sans')),
                       gridcolor='#f0ede8',tickfont=dict(size=11,family='DM Sans')),
            yaxis=dict(title=dict(text='Monthly Calls',font=dict(size=11,family='DM Sans')),
                       gridcolor='#f0ede8',tickfont=dict(size=11,family='DM Sans'),tickformat=',')
        )
        st.markdown('<div class="chart-box">', unsafe_allow_html=True)
        st.plotly_chart(fig_temp, use_container_width=True, config={'displayModeBar': False})
        st.markdown('</div>', unsafe_allow_html=True)

    with tc2:
        fig_dev = go.Figure()
        fig_dev.add_trace(go.Scatter(
            x=df['newtemp'], y=df['Calls'], mode='markers', name = 'Call Volume',
            marker=dict(color='#1a3a6b',size=9,opacity=0.75,
                        line=dict(color='white',width=0.5)),
            hovertemplate='Dev from 60°F: %{x:.1f}°<br>Calls: %{y:,}<extra></extra>'
        ))
        dev_range = np.linspace(0, 27, 100)
        mean_rate = df['Rate'].mean()
        fig_dev.add_trace(go.Scatter(
            x=dev_range,
            y=19748.61 + 181.31*dev_range + (-43.04)*mean_rate,
            mode='lines', line=dict(color='#e8a020',width=2.5),
            name='ADL fit (mean unemployment)', hoverinfo='skip'
        ))
        fig_dev.update_layout(
            plot_bgcolor='white', paper_bgcolor='white',
            height=300, margin=dict(t=20,b=10,l=10,r=10),
            legend=dict(orientation='h',yanchor='bottom',y=1.02,xanchor='right',x=1,
                        font=dict(size=10,family='DM Sans')),
            xaxis=dict(title=dict(text='Temperature Deviation from 60°F (°)',
                                  font=dict(size=11,family='DM Sans')),
                       gridcolor='#f0ede8',tickfont=dict(size=11,family='DM Sans')),
            yaxis=dict(title=dict(text='Monthly Calls',font=dict(size=11,family='DM Sans')),
                       gridcolor='#f0ede8',tickfont=dict(size=11,family='DM Sans'),tickformat=',')
        )
        st.markdown('<div class="chart-box">', unsafe_allow_html=True)
        st.plotly_chart(fig_dev, use_container_width=True, config={'displayModeBar': False})
        st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2: Model Comparison & Forecast
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<br>', unsafe_allow_html=True)
    st.markdown('<div class="section-header">Model Comparison & Forecast</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Set forecast conditions below. Phase 1 and Phase 3 lines update dynamically. SARIMA extends from its own time series history and stays fixed.</div>', unsafe_allow_html=True)

    # ── Controls ──────────────────────────────────────────────────────────────
    ctrl1, ctrl2 = st.columns([1, 2])

    #forecast slider
    with ctrl1:
        st.markdown('<div class="chart-box">', unsafe_allow_html=True)
        st.markdown("**Forecast Settings**")

        horizon = st.select_slider(
            'Forecast Horizon',
            options=[1, 3, 6, 9, 12],
            value=6,
            help='Number of months to forecast beyond August 1992'
        )

        st.markdown(f"""
        <div style="background:#f5f4f0;border-radius:8px;padding:.8rem 1rem;
                    margin-top:.8rem;font-size:.81rem;color:#5a6480;line-height:1.5;">
            <strong>Note:</strong> Unemployment coefficient in the ADL model is
            not statistically significant (p = 0.78). It shifts the ADL forecast
            modestly and serves as a directional signal only. Temperature is the
            dominant driver.
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # temperature inputs
    with ctrl2:
        st.markdown('<div class="chart-box">', unsafe_allow_html=True)
        st.markdown("**Monthly Temperature Assumptions** — pre-populated from historical averages, editable")

        forecast_dates = get_forecast_dates(horizon)
        forecast_months = [d.month for d in forecast_dates]
        forecast_labels = [d.strftime('%b %Y') for d in forecast_dates]

        # Build temperature inputs in columns
        temp_inputs = {}
        n_cols = min(horizon, 6)
        cols = st.columns(n_cols)
        for i, (fdate, fmonth, flabel) in enumerate(zip(forecast_dates, forecast_months, forecast_labels)):
            col_idx = i % n_cols
            with cols[col_idx]:
                temp_inputs[flabel] = st.number_input(
                    flabel,
                    min_value=25.0, max_value=80.0,
                    value=float(MONTHLY_TEMP_DEFAULTS[fmonth]),
                    step=0.5,
                    key=f"temp_{flabel}"
                )
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Compute forecasts ──────────────────────────────────────────────────────
    p1_forecasts  = [p1_forecast(temp_inputs[lbl]) for lbl in forecast_labels]
    sar_forecasts, sar_ci_lower, sar_ci_upper = sarima_forecast(horizon)
    p3_forecasts = [p3_forecast(temp_inputs[lbl], forecast_dates[i]) for i, lbl in enumerate(forecast_labels)]

    # Confidence intervals (based on residual standard errors)
    rse_p1  = 1225   # from Phase 1 summary
    rse_p3  = 1073   # from Phase 3 summary
    rse_sar = 1286   # sigma from SARIMA (sqrt(1654509))

    # ── Build chart ────────────────────────────────────────────────────────────
    fig_cmp = go.Figure()

    # Winter shading on historical
    for yr in range(1988, 1994):
        fig_cmp.add_vrect(
            x0=f'{yr}-11-15', x1=f'{yr+1}-03-15',
            fillcolor='rgba(200,40,46,0.04)',
            layer='below', line_width=0
        )

    # Vertical line separating historical from forecast
    last_date = df['date'].iloc[-1]
    fig_cmp.add_vline(
        x=last_date, line_dash='dash',
        line_color='#999', line_width=1.5,
        annotation_text='Forecast starts →',
        annotation_font=dict(size=10, color='#666', family='DM Sans'),
        annotation_position='top right'
    )

    # ── Historical: Actual ────────────────────────────────────────────────────
    fig_cmp.add_trace(go.Scatter(
        x=df['date'], y=df['Calls'],
        mode='lines', name='Actual Calls',
        line=dict(color='#0f1f3d', width=2.5),
        hovertemplate='%{x|%b %Y}<br><b>Actual: %{y:,}</b><extra></extra>'
    ))

    # ── Forecast: connect from last actual ───────────────────────────────────
    conn_dates = [last_date] + forecast_dates
    conn_p1    = [int(df['pred_p1'].iloc[-1])]  + p1_forecasts
    conn_sar   = [int(df['Calls'].iloc[-1])]    + sar_forecasts
    conn_p3    = [int(df['pred_p3'].dropna().iloc[-1])] + p3_forecasts

    # ── Historical: Phase 1 fitted ────────────────────────────────────────────
    fig_cmp.add_trace(go.Scatter(
        x=df['date'], y=df['pred_p1'],
        mode='lines', name='Phase 1 (Temp Regression)',
        line=dict(color="#F30707", width=1.5, dash='dash'),
        hovertemplate='%{x|%b %Y}<br>Phase 1 fitted: %{y:,.0f}<extra></extra>'
    ))

    # Phase 1 forecast + CI
    # forecast
    fig_cmp.add_trace(go.Scatter(
        x=conn_dates, y=conn_p1,
        mode='lines+markers', name='Phase 1 Forecast',
        legendgroup='Phase 1',
        line=dict(color='#F30707', width=2.5),
        marker=dict(size=7, color='#c8282e'),
        hovertemplate='%{x|%b %Y}<br><b>Phase 1 Forecast: %{y:,}</b><extra></extra>'
    ))
    # confidence interval
    p1_hi = [v + 1.96*rse_p1 for v in conn_p1]
    p1_lo = [v - 1.96*rse_p1 for v in conn_p1]
    fig_cmp.add_trace(go.Scatter(
        x=conn_dates + conn_dates[::-1],
        y=p1_hi + p1_lo[::-1],
        fill='toself', fillcolor='rgba(200,40,46,0.08)',
        legendgroup='Phase 1',
        line=dict(color='rgba(0,0,0,0)'),
        name='Phase 1 95% CI', showlegend=False, hoverinfo='skip'
    ))

    # ── Historical: Phase 2 SARIMA fitted ───────────────────────────────

    sarima_fitted = sarima_results.fittedvalues.astype(int).tolist()

    fig_cmp.add_trace(go.Scatter(
        x=df['date'], y=sarima_fitted,
        mode='lines', name='Phase 2 (SARIMA)',
        line=dict(color="#1c3de0", width=1.5, dash='dashdot'),
        hovertemplate='%{x|%b %Y}<br>SARIMA fitted: %{y:,.0f}<extra></extra>'
    ))

    # Phase 2 SARIMA forecast + CI
    # forecast
    fig_cmp.add_trace(go.Scatter(
        x=conn_dates, y=conn_sar,
        mode='lines+markers', name='Phase 2 SARIMA Forecast',
        legendgroup='Phase 2',
        line=dict(color="#1c3de0", width=2.5),
        marker=dict(size=7, color="#5692e1"),
        hovertemplate='%{x|%b %Y}<br><b>SARIMA Forecast: %{y:,}</b><extra></extra>'
    ))
    # confidence interval
    # Prepend last actual value to connect CI bands from historical to forecast
    sar_hi = [int(df['Calls'].iloc[-1])] + sar_ci_upper
    sar_lo = [int(df['Calls'].iloc[-1])] + sar_ci_lower

    fig_cmp.add_trace(go.Scatter(
        x=conn_dates + conn_dates[::-1],
        y=sar_hi + sar_lo[::-1],
        fill='toself', fillcolor='rgba(26,138,107,0.08)',
        legendgroup='Phase 2',
        line=dict(color='rgba(0,0,0,0)'),
        name='SARIMA 95% CI', showlegend=False, hoverinfo='skip'
    ))
   
    # ── Historical: Phase 3 fitted ────────────────────────────────────────────
    df_p3_hist = df.dropna(subset=['pred_p3'])
    fig_cmp.add_trace(go.Scatter(
        x=df_p3_hist['date'], y=df_p3_hist['pred_p3'],
        mode='lines', name='Phase 3 (ADL Model)',
        line=dict(color='#e8a020', width=1.5, dash='dot'),
        hovertemplate='%{x|%b %Y}<br>Phase 3 fitted: %{y:,.0f}<extra></extra>'
    ))

    # Phase 3 forecast + CI
    # forecast
    fig_cmp.add_trace(go.Scatter(
        x=conn_dates, y=conn_p3,
        mode='lines+markers', name='Phase 3 ADL Forecast',
        legendgroup='Phase 3',
        line=dict(color='#e8a020', width=2.5),
        marker=dict(size=7, color='#e8a020'),
        hovertemplate='%{x|%b %Y}<br><b>Phase 3 Forecast: %{y:,}</b><extra></extra>'
    ))
    # confidence interval
    p3_hi = [v + 1.96*rse_p3 for v in conn_p3]
    p3_lo = [v - 1.96*rse_p3 for v in conn_p3]
    fig_cmp.add_trace(go.Scatter(
        x=conn_dates + conn_dates[::-1],
        y=p3_hi + p3_lo[::-1],
        fill='toself', fillcolor='rgba(232,160,32,0.08)',
        legendgroup='Phase 3',
        line=dict(color='rgba(0,0,0,0)'),
        name='Phase 3 95% CI', showlegend=False, hoverinfo='skip'
    ))

    fig_cmp.update_layout(
        plot_bgcolor='white', paper_bgcolor='white',
        height=440, margin=dict(t=20,b=10,l=10,r=10),
        legend=dict(orientation='h', yanchor='bottom', y=1.02,
                    xanchor='right', x=1, font=dict(size=11,family='DM Sans')),
        xaxis=dict(tickformat='%b %Y', gridcolor='rgba(0,0,0,0)',
                   tickfont=dict(size=11,family='DM Sans')),
        yaxis=dict(tickformat=',', gridcolor='#f0ede8',
                   tickfont=dict(size=11,family='DM Sans'),
                   title=dict(text='Monthly Calls',font=dict(size=11,family='DM Sans'))),
        hovermode='x unified'
    )

    st.markdown('<div class="chart-box">', unsafe_allow_html=True)
    st.plotly_chart(fig_cmp, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Forecast table ────────────────────────────────────────────────────────
    st.markdown('<br>', unsafe_allow_html=True)
    st.markdown('<div class="section-header">Forecast Detail</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Month-by-month comparison across all three models</div>', unsafe_allow_html=True)

    st.markdown('<div class="chart-box">', unsafe_allow_html=True)

    rows = ""
    for i, lbl in enumerate(forecast_labels):
        p1v   = p1_forecasts[i]
        p3v   = p3_forecasts[i]
        sarv  = sar_forecasts[i]
        level, level_lbl, _ = staffing_label(p3v)
        badge_color = {'low':'#2d6a4f','med':'#e07b39','high':'#c8282e'}[level]
        badge_bg    = {'low':'#d8f3dc','med':'#fef0e4','high':'#fde8e8'}[level]
        temp_shown  = temp_inputs[lbl]
        rows += f"""
        <tr>
            <td><strong>{lbl}</strong></td>
            <td>{temp_shown:.1f}°F</td>
            <td>{p1v:,}</td>
            <td>{sarv:,}</td>
            <td>{p3v:,}</td>
            <td><span style="background:{badge_bg};color:{badge_color};
                padding:.2rem .6rem;border-radius:20px;font-size:.75rem;font-weight:600;">
                {level_lbl}</span></td>
        </tr>"""

    st.markdown(f"""
    <table class="custom-table">
        <thead>
            <tr>
                <th>Month</th>
                <th>Temp Input</th>
                <th>Phase 1 (Temp Reg)</th>
                <th>Phase 2 (SARIMA)</th>
                <th>Phase 3 (ADL)</th>
                <th>Staffing Signal</th>
            </tr>
        </thead>
        <tbody>{rows}</tbody>
    </table>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="insight-box warn">
        <strong>How to read model divergence:</strong> When Phase 1, 2, and 3forecasts
        are close together, all three methods agree — high confidence in the estimate. When they
        diverge, it signals that external conditions (temperature or unemployment) are pulling
        demand in a direction pure time series cannot see. Large divergence between ADL and
        SARIMA is the most operationally meaningful signal.
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3: Model Summary
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<br>', unsafe_allow_html=True)
    st.markdown('<div class="section-header">Three-Phase Model Summary</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Progressive modeling — each phase added explanatory power and operational value</div>', unsafe_allow_html=True)

    st.markdown('<div class="chart-box">', unsafe_allow_html=True)
    st.markdown("""
    <table class="custom-table">
        <thead>
            <tr>
                <th>Phase</th>
                <th>Model</th>
                <th>Key Variables</th>
                <th>Performance</th>
                <th>Strength</th>
                <th>Limitation</th>
                <th>Best Used For</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><strong>Phase 1</strong></td>
                <td>Linear Regression</td>
                <td>Temperature (raw)</td>
                <td>R² = 45.3%<br>MAPE = 4.78%</td>
                <td>Simple, interpretable baseline</td>
                <td>Residual autocorrelation, misses seasonal structure</td>
                <td>Explaining temperature as primary driver</td>
            </tr>
            <tr>
                <td><strong>Phase 2</strong></td>
                <td>SARIMA(1,0,0)(1,1,0)[12]</td>
                <td>Temporal patterns only</td>
                <td><span class="model-badge badge-best">MAPE = 2.5%</span></td>
                <td>Best raw forecast accuracy, captures seasonality and AR structure</td>
                <td>Cannot explain WHY volume changes, no external variables</td>
                <td>Annual budget and headcount planning</td>
            </tr>
            <tr>
                <td><strong>Phase 3</strong></td>
                <td>ADL Regression</td>
                <td>|Temp − 60°F| + Unemployment lag 11</td>
                <td>Adj. R² = 57.1%<br>MAPE = 3.58% (in-sample)</td>
                <td><span class="model-badge badge-best">Most interpretable</span> — connects forecast to observable conditions</td>
                <td>Unemployment coefficient not statistically significant (p = 0.78)</td>
                <td>In-season adjustments and early warning monitoring</td>
            </tr>
        </tbody>
    </table>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="insight-box warn">
        <strong>Why two models are better than one:</strong> SARIMA wins on pure forecast
        accuracy (2.5% MAPE) but cannot tell operations leadership <em>why</em> demand
        is shifting. The ADL model wins on interpretability — it connects forecast changes
        to temperature and unemployment conditions that managers can observe and act on.
        Using SARIMA for annual planning and ADL for in-season monitoring captures the
        strengths of both.
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    st.markdown('<div class="section-header">Model Coefficients</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Fitted parameters from R — all models</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div class="chart-box">', unsafe_allow_html=True)
        st.markdown("""
        <div style="font-family:'Playfair Display',serif;font-size:1rem;font-weight:700;
                    color:#0f1f3d;margin-bottom:.8rem;">Phase 1 — Temperature Regression</div>
        <table class="custom-table">
            <thead><tr><th>Term</th><th>Estimate</th><th>p-value</th></tr></thead>
            <tbody>
                <tr><td>Intercept</td><td>27,414.06</td><td>&lt; 0.001 ***</td></tr>
                <tr><td>Temperature</td><td>−117.58</td><td>&lt; 0.001 ***</td></tr>
                <tr><td colspan="3" style="color:#5a6480;font-size:.8rem;padding-top:.5rem;">
                    R² = 45.3% &nbsp;|&nbsp; RSE = 1,225</td></tr>
            </tbody>
        </table>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="chart-box">', unsafe_allow_html=True)
        st.markdown("""
        <div style="font-family:'Playfair Display',serif;font-size:1rem;font-weight:700;
                    color:#0f1f3d;margin-bottom:.8rem;">Phase 2 — SARIMA(1,0,0)(1,1,0)[12]</div>
        <table class="custom-table">
            <thead><tr><th>Term</th><th>Estimate</th><th>Std. Error</th></tr></thead>
            <tbody>
                <tr><td>AR1</td><td>0.4098</td><td>0.1428</td></tr>
                <tr><td>SAR1</td><td>−0.2723</td><td>0.1804</td></tr>
                <tr><td colspan="3" style="color:#5a6480;font-size:.8rem;padding-top:.5rem;">
                    AIC = 691.33 &nbsp;|&nbsp; σ² = 1,654,509</td></tr>
            </tbody>
        </table>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c3:
        st.markdown('<div class="chart-box">', unsafe_allow_html=True)
        st.markdown("""
        <div style="font-family:'Playfair Display',serif;font-size:1rem;font-weight:700;
                    color:#0f1f3d;margin-bottom:.8rem;">Phase 3 — ADL Regression</div>
        <table class="custom-table">
            <thead><tr><th>Term</th><th>Estimate</th><th>p-value</th></tr></thead>
            <tbody>
                <tr><td>Intercept</td><td>19,748.61</td><td>&lt; 0.001 ***</td></tr>
                <tr><td>|Temp − 60°F|</td><td>181.31</td><td>&lt; 0.001 ***</td></tr>
                <tr><td>Unemployment (lag 11)</td><td>−43.04</td><td>0.778 (n.s.)</td></tr>
                <tr><td colspan="3" style="color:#5a6480;font-size:.8rem;padding-top:.5rem;">
                    Adj. R² = 57.1% &nbsp;|&nbsp; RSE = 1,073</td></tr>
            </tbody>
        </table>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="footer">
    Built by Sam Sithimolada · USC Marshall M.S. Business Analytics ·
    <a href="https://github.com/ssithimo/aaa-demand-modeling" style="color:#1a3a6b;">
    GitHub Repository</a>
</div>
""", unsafe_allow_html=True)