# V48.2 FINAL LOCKED - FUSION V44+V30+INTERLAGOS+MERCADO PAGO FAST 15D
# Semáforo V44 aguacate Opción B - va porque va

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="V48.2 FINAL", layout="wide")

# ===== TOP: CARRIL V44 BANDERA ESQUINA + CARRITO + MONEDAS =====
st.markdown("""
<div style='background:#111;border:2px solid #FFD700;border-radius:12px;padding:8px;display:flex;justify-content:space-between;'>
<span>🏁 BANDERA ESQUINA</span><span>🏎️💨 COINS 🪙🪙🪙</span><span>V48.2 bar ultimate 🏆</span>
</div>
""", unsafe_allow_html=True)

# ===== SEMAFORO V44 AGUACATE OPCION B - 3 FOCOS MISMO COLOR =====
color_semaforo = "green" # green / yellow / red - los 3 focos mismo color
def semaforo_v44_aguacate_B(color):
    cols = st.columns(3)
    col_map = {"green":"#00FF00","yellow":"#FFFF00","red":"#FF0000"}
    for c in cols:
        c.markdown(f"<div style='width:60px;height:60px;border-radius:50%;background:{col_map[color]};box-shadow:0 0 15px {col_map[color]};border:3px solid #000;'></div>", unsafe_allow_html=True)
    st.markdown(f"🥑 SEMAFORO {color.upper()} - OPCION B - 3 FOCOS IGUAL")

semaforo_v44_aguacate_B(color_semaforo)

# ===== BOX ASEGURADO + COOLDOWN =====
st.markdown("<div style='background:#0a2a0a;border:2px solid #00FF00;padding:10px;border-radius:10px'>🛡️ BOX ASEGURADO | COOLDOWN: 12s</div>", unsafe_allow_html=True)

# ===== ALPACA PAPER BAR OBLIGATORIO =====
st.markdown("### 💰 Alpaca Paper $99,996 - va porque va")
col1, col2 = st.columns(2)
with col1:
    st.link_button("📊 Ver en Alpaca", "https://app.alpaca.markets")
with col2:
    st.link_button("🚀 Abrir Dashboard de Alpaca", "https://app.alpaca.markets/dashboard")

# ===== TABLA POSICIONES + 4 BOXES DIAMANTE V30 =====
st.markdown("### 🏆 TABLA POSICIONES")
c1,c2,c3,c4 = st.columns(4)
c1.metric("💎 COINS", "1,250")
c2.metric("🔥 HEAT", "87%")
c3.metric("🏆 MEJOR", "BTC +5.2%")
c4.metric("💎 DIAMANTE", "HOLD 15d")

# ===== INTERLAGOS HEATMAP =====
st.markdown("### 🏁 Interlagos HD Heatmap")
# tu heatmap code aqui
st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/3/36/Interlagos_circuit_map.svg/800px-Interlagos_circuit_map.svg.png")

# ===== VALORES GRANDES + GRAFICO BTC VERDE =====
st.markdown("## $81,353 / z / log")
st.markdown("Gráfico BTC verde va aqui - plotly verde")
fig = go.Figure()
fig.add_trace(go.Scatter(y=[81000,81500,81353], line=dict(color="#00FF00", width=3)))
st.plotly_chart(fig, use_container_width=True)

# ===== 24H / 7D / 30D / vs MAX + BACKTEST =====
t1,t2,t3,t4 = st.tabs(["24H","7D","30D","vs MAX"])
with t1: st.write("Backtest 24H +2.1%")
with t2: st.write("Backtest 7D +4.3%")
with t3: st.write("Backtest 30D +12%")
with t4: st.write("Backtest vs MAX +180%")

st.divider()

# ===== MERCADO PAGO FAST - ASI COMO VENIAMOS TRABAJANDO - VA PORQUE VA =====
st.markdown("## 📊 MERCADO PAGO FAST - 15 DIAS FIX")
sel = st.radio("Periodo", ["1 dia","1 semana","15 dias","1 año","Todo"], horizontal=True, index=2)

# Simula datos MXN
prices_mp = np.random.normal(1500000, 20000, 100)
min_mp, max_mp = min(prices_mp), max(prices_mp)
change_mp = (prices_mp[-1]-prices_mp[0])/prices_mp[0]*100
color_mp = "#00FF00" if change_mp>=0 else "#FF0000"

fig_mp = go.Figure()
fig_mp.add_trace(go.Scatter(y=prices_mp, line=dict(color=color_mp, width=2.5)))
fig_mp.update_layout(height=300, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor="#0A0A0A", plot_bgcolor="#0A0A0A")
st.plotly_chart(fig_mp, use_container_width=True)

c_min, c_max, c_pct = st.columns(3)
c_min.metric("MIN", f"${min_mp:,.0f}")
c_max.metric("MAX", f"${max_mp:,.0f}")
c_pct.metric("% PERIODO", f"{change_mp:+.2f}%")

st.divider()
m1, m2 = st.columns(2)
with m1:
    st.link_button("🔵 MERCADO PAGO $1,504,696 →", "https://www.mercadopago.com.mx")
with m2:
    st.link_button("🟡 ALPACA $81,352 →", "https://app.alpaca.markets")

# ANTI-PLANO 3D - NO PLANO
st.markdown("<style>div{box-shadow: 2px 2px 8px rgba(0,0,0,0.5);}</style>", unsafe_allow_html=True)
