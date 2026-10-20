import streamlit as st
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@700&display=swap" rel="stylesheet">
<style>
h1, h2, h3, .stMetric {font-family: 'Orbitron', monospace !important;}
div[data-testid="stMetricValue"] {color: #FFD700 !important; text-shadow: 0 0 10px #FFD700;}
.tarjeta-f1 {border: 2px solid #FFD700; animation: respira 2s infinite alternate; border-radius:15px; padding:15px;}
@keyframes respira {0%{box-shadow:0 0 5px #FFD700} 100%{box-shadow:0 0 20px #FFD700, 0 0 30px #00FF88}}
.boton-verde {animation: late 0.8s infinite alternate;}
@keyframes late {0%{transform:scale(1)} 100%{transform:scale(1.05); box-shadow:0 0 25px #00FF88}}
</style>
""", unsafe_allow_html=True)
import yfinance as yf
import requests
import time
import math
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from bot_telegram import notificar_f1
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="F1 V21 SEMAFORO PRO", page_icon="🏎️", layout="wide")
st_autorefresh(interval=15*60*1000, key="f1v21_auto")

# SECRETS
A_KEY = st.secrets["alpaca"]["API_KEY"]
A_SECRET = st.secrets["alpaca"]["SECRET"]
T_TOKEN = st.secrets["telegram"]["BOT_TOKEN"]
T_CHAT = st.secrets["telegram"]["CHAT_ID"]
client = TradingClient(A_KEY, A_SECRET, paper=True)

def calcular_quant(precios):
    n = len(precios)
    x_bar = np.mean(precios)
    s = np.std(precios, ddof=1)
    z = (precios[-1] - x_bar) / (s / math.sqrt(n)) if s>0 else 0
    log_ret = math.log(precios[-1]/precios[-2]) if precios[-2]>0 else 0
    return x_bar, s, z, log_ret

def get_semaforo(price, fib, z, log_ret):
    # 1. FIB: ¿Está barato? Abajo de dorada = oferta
    # 2. Z: ¿Regalado? -2 a -7 = pánico = oportunidad
    # 3. LOG: ¿Crash? -0.62% ok, -5% no tocar
    if price < fib and z < -2.0 and -0.008 < log_ret < -0.0002:
        return "VERDE", "🟢 COMPRAR $2", "#00FF88"
    elif log_ret < -0.05 or z > 1.0:
        return "ROJO", "🔴 NO COMPRAR - Crash/Caro", "#FF3B3B"
    else:
        return "AMARILLO", "🟡 ESPERAR - Paciencia", "#FFD60A"

# ========== TARJETA PRO MEGA PRO ==========
st.markdown('<div class="tarjeta-f1">', unsafe_allow_html=True)
st.markdown("""
<style>
.pro-card {
    background: linear-gradient(135deg, #0E1117 0%, #1A1D29 100%);
    border: 1px solid gold; border-radius: 16px; padding: 20px;
    box-shadow: 0 0 20px rgba(255,215,0,0.15);
}
.pro-title {color: gold; font-size: 22px; font-weight: 800; margin-bottom: 10px;}
.pro-row {display:flex; gap:12px; margin-top:12px;}
.pro-box {flex:1; background:#111; border-radius:12px; padding:12px; border-left:4px solid;}
.pro-box p {margin:4px 0; color:#CCC; font-size:13px;}
.pro-box b {color:white;}
</style>
<div class="pro-card">
    <div class="pro-title">🏎️ F1 V21 SEMÁFORO - Cómo leer en 30 seg</div>
    <p style="color:#AAA; font-size:14px;">Sin fórmulas. Solo 3 preguntas para no perder tu poco dinero.</p>
    <div class="pro-row">
        <div class="pro-box" style="border-color: gold;">
            <b>1. ¿Está barato? Fib 0.618</b><p>Línea dorada. Si BTC está abajo de ella, es como aguacate en oferta. $81.5 vs $82 normal.</p>
        </div>
        <div class="pro-box" style="border-color: #00FF88;">
            <b>2. ¿Está regalado? z = -6.96</b><p>z -2 a -7 = pánico. La gente lo remata. Mientras más negativo, más oportunidad. Tu ejemplo: -6.96 = súper regalado.</p>
        </div>
        <div class="pro-box" style="border-color: #FF3B3B;">
            <b>3. ¿Se cae a pedazos? log -0.62%</b><p>-0.62% = bajó 62 centavos de $100 = normal. -5% = crash = no tocar. Solo compramos bajaditas chiquitas.</p>
        </div>
    </div>
    <p style="margin-top:14px; color:gold; font-size:13px;">🟢 VERDE = Barato + Regalado + Bajadita chiquita → Compras $2 | 🟡 AMARILLO = Esperas, no perder es ganar | 🔴 ROJO = Freno total</p>
</div>
""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

st.write("")
# CONTROLES
c1,c2,c3 = st.columns([2,1,1])
with c1:
    symbol = st.selectbox("Activo", ["BTC/USD", "AAPL", "ETH/USD"], index=0)
with c2:
    iniciar = st.button("🏁 ANALIZAR V21", type="primary", use_container_width=True)
with c3:
    if st.button("🚨 PANICO", use_container_width=True):
        try: client.close_all_positions(cancel_orders=True); st.error("Vendido")
        except Exception as e: st.error(e)

if iniciar:
    ticker = "BTC-USD" if symbol=="BTC/USD" else symbol
    if symbol=="BTC/USD": ticker="BTC-USD"
    if symbol=="AAPL": ticker="AAPL"
    if symbol=="ETH/USD": ticker="ETH-USD"
    h = yf.Ticker(ticker).history(period="1mo")
    precios = h['Close'].values
    fib = h['High'].max()-(h['High'].max()-h['Low'].min())*0.618
    price = precios[-1]
    x_bar, s, z, log_ret = calcular_quant(precios)
    estado, texto, color = get_semaforo(price, fib, z, log_ret)

    # METRICAS PRO
    m1,m2,m3,m4 = st.columns(4)
    m1.metric(symbol, f"${price:,.2f}", f"Fib: ${fib:,.2f}")
    m2.metric("z-score", f"{z:.2f}", "Compra si < -2")
    m3.metric("log ret", f"{log_ret*100:.3f}%", "-0.8% a -0.02% ideal")
    m4.markdown(f"<div style='background:{color}; color:black; padding:18px; border-radius:12px; text-align:center; font-weight:900; font-size:20px;'>{texto}<br><span style='font-size:12px;'>{estado}</span></div>", unsafe_allow_html=True)

    # GRAFICO
    fig, ax = plt.subplots(figsize=(10,4))
    fig.patch.set_facecolor('#0E1117'); ax.set_facecolor('#0E1117')
    ax.plot(precios, color='#00FF88', label='Precio')
    ax.axhline(fib, color='gold', linestyle='--', label='Fib 0.618 Barato')
    ax.axhline(x_bar, color='cyan', alpha=0.4, label='Media')
    if estado=="VERDE": ax.scatter(len(precios)-1, price, color='white', s=200, edgecolors='gold', linewidth=2, zorder=5)
    ax.legend(facecolor='#0E1117', edgecolor='gold', labelcolor='white')
    ax.tick_params(colors='white'); st.pyplot(fig)

    # TELEGRAM SONIDO
    if estado=="VERDE":
        notificar_f1(symbol, "$2", price, tipo="verde", fib=fib, z=z, log=log_ret)
        st.success(f"✅ Señal VERDE detectada. Si fuera real, comprarías $2 de {symbol}. Sonido F1 largo enviado.")
    elif estado=="ROJO":
        notificar_f1(symbol, "$2", price, tipo="rojo", fib=fib, z=z, log=log_ret)
        st.error("🔴 ROJO - No comprar, te cuida tu dinero.")
    else:
        st.warning("🟡 AMARILLO - Esperar. No perder también es ganar.")

    st.caption(f"z=(x̄-μ0)/(σ/√n) | log=ln(Pt/Pt-1) | V21 -0.008 conservador para $30 reales | {datetime.now().strftime('%H:%M:%S')}")
