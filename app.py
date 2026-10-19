import streamlit as st
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

st.set_page_config(page_title="F1 V18 QUANT GOLD", layout="wide")

# TU IMAGEN GOLD F1 BITCOIN COMO HEADER - no cambia flyer
try:
    st.image("dashboard_gold.jpg", use_container_width=True)
except:
    st.warning("Sube dashboard_gold.jpg a tu repo para ver el coche dorado")

st.title("🏎️ F1 V18 QUANT GOLD - Bolsa + Crypto")

# SECRETS
A_KEY = st.secrets["alpaca"]["API_KEY"]
A_SECRET = st.secrets["alpaca"]["SECRET"]
T_TOKEN = st.secrets["telegram"]["BOT_TOKEN"]
T_CHAT = st.secrets["telegram"]["CHAT_ID"]
client = TradingClient(A_KEY, A_SECRET, paper=True)

def telegram(msg, largo=True):
    try:
        requests.post(f"https://api.telegram.org/bot{T_TOKEN}/sendMessage", json={"chat_id": T_CHAT, "text": msg}, timeout=10)
        audio = "https://cdn.pixabay.com/audio/2022/03/24/audio_5a70a1157b.mp3" if largo else "https://cdn.pixabay.com/audio/2022/03/10/audio_c8c8a73467.mp3"
        requests.post(f"https://api.telegram.org/bot{T_TOKEN}/sendAudio", json={"chat_id": T_CHAT, "audio": audio}, timeout=10)
    except: pass

# TUS 10 FORMULAS
def calcular_quant(precios):
    n = len(precios)
    x_bar = np.mean(precios) # 1. Estimador
    s = np.std(precios, ddof=1)
    EE = s / math.sqrt(n) if n>0 else 0 # 2. Error Estandar
    z = (precios[-1] - x_bar) / (s / math.sqrt(n)) if s>0 else 0 # 3. z
    IC_inf = x_bar - 1.96 * s / math.sqrt(n) # 5. IC
    IC_sup = x_bar + 1.96 * s / math.sqrt(n)
    derivada = (precios[-1] - precios[-6]) / 5 if n>6 else 0 # f'(x)
    ciclo = math.sin(2*math.pi*datetime.now().hour/24) # Circulo unitario
    return x_bar, s, EE, z, IC_inf, IC_sup, derivada, ciclo

if "running" not in st.session_state:
    st.session_state.running=False
    st.session_state.last_buy=0
    st.session_state.buy_count=6

# CONTROLES
c1,c2,c3,c4 = st.columns(4)
with c1:
    symbol = st.selectbox("Activo", ["AAPL", "BTC/USD", "ETH/USD", "SOL/USD"], index=0)
with c2:
    if st.button("🏁 INICIAR V18 GOLD", type="primary"):
        st.session_state.running=True
        telegram(f"🏁 F1 LARGO F1 V18 GOLD INICIADO\n{symbol} - 10 formulas + Gold Car activo\n{datetime.now().strftime('%H:%M:%S')}", True)
with c3:
    if st.button("Stop"): st.session_state.running=False
with c4:
    if st.button("🚨 PANICO VENDER"):
        try:
            client.close_all_positions(cancel_orders=True)
            telegram("🚨 PANICO PANICO - Todo vendido", False)
            st.success("Vendido")
        except Exception as e: st.error(e)

# LOGICA V18
if st.session_state.running:
    ticker = "AAPL" if symbol=="AAPL" else symbol.split("/")[0]+"-USD"
    h = yf.Ticker(ticker).history(period="1mo")
    precios = h['Close'].values
    fib = h['High'].max()-(h['High'].max()-h['Low'].min())*0.618
    price = precios[-1]
    x_bar, s, EE, z, IC_inf, IC_sup, derivada, ciclo = calcular_quant(precios)

    # METRICAS
    m1,m2,m3,m4 = st.columns(4)
    m1.metric(symbol, f"${price:.2f}", f"Fib 0.618: ${fib:.2f}")
    m2.metric("z-score", f"{z:.2f}", "Compra si <-2")
    m3.metric("f'(x) Derivada", f"{derivada:.3f}", "Momentum")
    m4.metric("Ciclo", f"{ciclo:.2f}")

    # GRAFICO CHINGON
    fig, (ax1, ax2) = plt.subplots(2,1, figsize=(10,6), gridspec_kw={'height_ratios': [3,1]})
    fig.patch.set_facecolor('#0E1117')
    ax1.set_facecolor('#0E1117')
    ax1.plot(precios, color='#00FF88', label='Precio')
    ax1.axhline(fib, color='gold', linestyle='--', label='Fib 0.618')
    ax1.axhline(x_bar, color='cyan', linestyle='-', alpha=0.5, label='Media x_bar')
    ax1.fill_between(range(len(precios)), IC_inf, IC_sup, color='gold', alpha=0.1, label='IC 95%')
    if price <= fib and z < -2:
        ax1.scatter(len(precios)-1, price, color='white', s=200, edgecolors='gold', linewidth=2, zorder=5)
    ax1.legend()
    ax2.plot([np.mean(precios[max(0,i-20):i+1]) for i in range(len(precios))], color='orange', label='z rolling')
    ax2.set_title("Z-SCORE ANALYSIS 95% CONFIDENCE INTERVAL Z=(X-μ)/σ", color='gold', fontsize=8)
    st.pyplot(fig)

    # COMPRA QUANT CON TEXTO V15 INTACTO
    if price <= fib and z < -2.0 and derivada > -0.1 and (time.time()-st.session_state.last_buy)>45:
        try:
            req = MarketOrderRequest(symbol=symbol, notional=10, side=OrderSide.BUY, time_in_force=TimeInForce.DAY if symbol=="AAPL" else TimeInForce.GTC)
            order = client.submit_order(req)
            st.session_state.buy_count+=1
            st.session_state.last_buy=time.time()
            # TEXTO IDENTICO A TU FLYER V15
            texto_v15 = f"""🏁🔊🔊🔊 SONIDO F1 LARGO - COMPRA
✅ COMPRA REAL #{st.session_state.buy_count}
{symbol} $10
Fib 0.618: {fib:.2f}
Ejecutado: {price:.2f}
z: {z:.2f} EE: {EE:.2f} f'(x): {derivada:.3f}
IC: [{IC_inf:.2f}-{IC_sup:.2f}]
Order: {order.id}"""
            telegram(texto_v15, True)
            st.success(f"Compra #{st.session_state.buy_count} OK")
        except Exception as e: st.error(e)

    time.sleep(5)
    st.rerun()
