# V48.2 FINAL LOCKED - FUSION COMPLETA
# V44 SEMAFORO AGUACATE OPCION B + V30 DIAMANTE + INTERLAGOS + MERCADO PAGO FAST 15D
# Va porque va - Tuxtla Gutierrez - 20 Oct 2026

import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="V48.2 FINAL LOCKED", page_icon="🏁", layout="wide")

# TOP CARRIL
st.markdown("<div style='background:#111;border:2px solid #FFD700;border-radius:12px;padding:10px;display:flex;justify-content:space-between;'><span>🏁 BANDERA ESQUINA</span><span>🏎️💨 🪙🪙🪙</span><span>V48.2 bar ultimate 🏆</span></div>", unsafe_allow_html=True)

def semaforo_aguacate_B(color_name):
    colors = {"green":"#00FF00","yellow":"#FFD700","red":"#FF0000"}
    c = colors.get(color_name,"#00FF00")
    st.markdown(f"<div style='display:flex;gap:10px;justify-content:center;padding:10px;background:#111;border-radius:15px;border:2px solid #FFD700;'><div style='width:70px;height:70px;border-radius:50%;background:{c};box-shadow:0 0 25px {c};border:4px solid #000'></div><div style='width:70px;height:70px;border-radius:50%;background:{c};box-shadow:0 0 25px {c};border:4px solid #000'></div><div style='width:70px;height:70px;border-radius:50%;background:{c};box-shadow:0 0 25px {c};border:4px solid #000'></div></div><p style='text-align:center;color:{c};font-weight:bold'>🥑 SEMAFORO {color_name.upper()} - OPCION B</p>", unsafe_allow_html=True)

semaforo_aguacate_B("green")

col_a, col_b = st.columns(2)
with col_a: st.markdown("<div style='background:#0a2a0a;border:2px solid #00FF00;padding:12px;border-radius:10px;text-align:center'>🛡️ BOX ASEGURADO - HOLD</div>", unsafe_allow_html=True)
with col_b: st.markdown("<div style='background:#2a1a00;border:2px solid #FFD700;padding:12px;border-radius:10px;text-align:center'>⏱️ COOLDOWN: 12s</div>", unsafe_allow_html=True)

st.divider()
st.markdown("### 💰 ALPACA PAPER - $99,996")
c1,c2 = st.columns(2)
with c1: st.link_button("📊 Ver en Alpaca", "https://app.alpaca.markets", use_container_width=True, type="primary")
with c2: st.link_button("🚀 Abrir Dashboard de Alpaca", "https://app.alpaca.markets/dashboard", use_container_width=True)

st.markdown("### 🏆 TABLA POSICIONES - V30 DIAMANTE")
b1,b2,b3,b4 = st.columns(4)
b1.metric("💎 COINS", "1,250"); b2.metric("🔥 HEAT", "87%"); b3.metric("🏆 MEJOR", "BTC +5.2%"); b4.metric("💎 DIAMANTE", "HOLD 15d")

st.markdown("## $81,353 / z / log")
fig_btc = go.Figure(); fig_btc.add_trace(go.Scatter(y=[80500,81200,80900,81500,81353,81800,81353], line=dict(color="#00FF00", width=3), fill='tozeroy', fillcolor='rgba(0,255,0,0.1)')); fig_btc.update_layout(height=350, paper_bgcolor="#0A0A0A", plot_bgcolor="#0A0A0A", font=dict(color="white"), margin=dict(l=0,r=0,t=20,b=0)); st.plotly_chart(fig_btc, use_container_width=True)

tab1,tab2,tab3,tab4 = st.tabs(["24H","7D","30D","vs MAX"])
with tab1: st.write("Backtest 24H +2.1%"); 
with tab2: st.write("Backtest 7D +4.3%"); 
with tab3: st.write("Backtest 30D +12%"); 
with tab4: st.write("Backtest vs MAX +180%");

st.divider()
st.markdown("## 📊 MERCADO PAGO FAST - BTC MXN")
sel_mp = st.radio("Periodo Mercado", ["1 dia","1 semana","15 dias","1 año","Todo"], horizontal=True, index=2)
n_points = {"1 dia":30,"1 semana":100,"15 dias":150,"1 año":300,"Todo":500}.get(sel_mp,150)
np.random.seed(42); base=1504696; prices_mp = base + np.cumsum(np.random.randn(n_points)*1500)
min_mp,max_mp,curr_mp = float(np.min(prices_mp)),float(np.max(prices_mp)),float(prices_mp[-1])
change_mp = (curr_mp-prices_mp[0])/prices_mp[0]*100; color_mp="#00FF00" if change_mp>=0 else "#FF0000"
fig_mp=go.Figure(); fig_mp.add_trace(go.Scatter(y=prices_mp, line=dict(color=color_mp, width=2.5))); fig_mp.update_layout(height=320, paper_bgcolor="#0A0A0A", plot_bgcolor="#0A0A0A", font=dict(color="white"), margin=dict(l=0,r=0,t=10,b=0)); st.plotly_chart(fig_mp, use_container_width=True)
cmin,cmax,cpct = st.columns(3); cmin.metric("MIN", f"${min_mp:,.0f}"); cmax.metric("MAX", f"${max_mp:,.0f}"); cpct.metric(f"% {sel_mp.upper()}", f"{change_mp:+.2f}%")

st.divider()
col_mercado,col_alpaca = st.columns(2)
with col_mercado: st.link_button(f"🔵 MERCADO PAGO ${curr_mp:,.0f} →", "https://www.mercadopago.com.mx", use_container_width=True, type="primary")
with col_alpaca: st.link_button(f"🟡 ALPACA $81,353 →", "https://app.alpaca.markets", use_container_width=True)
