import streamlit as st
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@700&display=swap" rel="stylesheet">
<style>
h1, h2, h3, .stMetric {font-family: 'Orbitron', monospace !important;}
div[data-testid="stMetricValue"] {color: #FFD700 !important; text-shadow: 0 0 10px #FFD700;}
.tarjeta-f1 {border: 2px solid #FFD700; border-radius:15px; padding:15px;}
</style>
""", unsafe_allow_html=True)
import yfinance as yf
import time
import math
import numpy as np
import matplotlib.pyplot as plt
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from bot_telegram import notificar_f1, responder_comandos
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="F1 V22 GANAR GANAR", page_icon="🏎️", layout="wide")
auto_count = st_autorefresh(interval=15*60*1000, key="f1v22_auto")
if "last_update_id" not in st.session_state:
    st.session_state.last_update_id = 0
if "last_verde_price" not in st.session_state:
    st.session_state.last_verde_price = 0
    
responder_comandos()

A_KEY = st.secrets["alpaca"]["API_KEY"]
A_SECRET = st.secrets["alpaca"]["SECRET"]
client = TradingClient(A_KEY, A_SECRET, paper=True)

# ALPACA EXIGE MINIMO $10 EN CRYPTO - GANAR GANAR
ORDER_NOTIONAL = 10

def calcular_quant(precios):
    n = len(precios)
    x_bar = np.mean(precios)
    s = np.std(precios, ddof=1)
    z = (precios[-1] - x_bar) / (s / math.sqrt(n)) if s>0 else 0
    log_ret = math.log(precios[-1]/precios[-2]) if precios[-2]>0 else 0
    return x_bar, s, z, log_ret

def get_semaforo(price, fib, z, log_ret):
    if price < fib and z < -2.0 and -0.008 < log_ret < -0.0002:
        return "VERDE", "🟢 COMPRAR $10", "#00FF88"
    elif log_ret < -0.05 or z > 1.0:
        return "ROJO", "🔴 NO COMPRAR", "#FF3B3B"
    else:
        return "AMARILLO", "🟡 ESPERAR", "#FFD60A"

c1,c2,c3 = st.columns([2,1,1])
with c1:
    symbol = st.selectbox("Activo", ["BTC/USD", "AAPL", "ETH/USD"], index=0)
with c2:
    iniciar = st.button("🏁 ANALIZAR V22", type="primary", use_container_width=True)
with c3:
    if st.button("🚨 PANICO", use_container_width=True):
        try: client.close_all_positions(cancel_orders=True); st.error("Vendido")
        except Exception as e: st.error(e)

if iniciar or auto_count > 0:
    ticker = "BTC-USD" if symbol=="BTC/USD" else symbol
    if symbol=="AAPL": ticker="AAPL"
    if symbol=="ETH/USD": ticker="ETH-USD"
    h = yf.Ticker(ticker).history(period="1mo")
    precios = h['Close'].values
    fib = h['High'].max()-(h['High'].max()-h['Low'].min())*0.618
    price = precios[-1]
    x_bar, s, z, log_ret = calcular_quant(precios)
    estado, texto, color = get_semaforo(price, fib, z, log_ret)

    m1,m2,m3,m4 = st.columns(4)
    m1.metric(symbol, f"${price:,.2f}", f"Fib: ${fib:,.2f}")
    m2.metric("z-score", f"{z:.2f}", "Compra si < -2")
    m3.metric("log ret", f"{log_ret*100:.3f}%", "-0.8% a -0.05%")
    m4.markdown(f"<div style='background:{color}; color:black; padding:10px; border-radius:10px'><b>{texto}</b></div>", unsafe_allow_html=True)

    fig, ax = plt.subplots(figsize=(10,4))
    fig.patch.set_facecolor('#0E1117'); ax.set_facecolor('#0E1117')
    ax.plot(precios, color='#00FF88', label='Precio')
    ax.axhline(fib, color='gold', linestyle='--', label='Fib')
    ax.axhline(x_bar, color='cyan', alpha=0.4, label='Media')
    if estado=="VERDE": ax.scatter(len(precios)-1, price, color='lime', s=100)
    ax.legend(facecolor='#0E1117', edgecolor='gold', labelcolor='white')
    ax.tick_params(colors='white'); st.pyplot(fig)

    if estado=="VERDE":
        if abs(price - st.session_state.last_verde_price) > 10:
            notificar_f1(f"🏁 VERDE {symbol} COMPRAR ${ORDER_NOTIONAL} REAL\nPrecio ${price:.2f}\nFib ${fib:.2f}\nZ {z:.2f}\nLog {log_ret*100:.3f}%")
            try:
                orden = MarketOrderRequest(symbol=symbol, notional=ORDER_NOTIONAL, side=OrderSide.BUY, time_in_force=TimeInForce.GTC)
                client.submit_order(orden)
                st.success(f"Orden REAL ${ORDER_NOTIONAL} enviada - GANAR GANAR")
            except Exception as e:
                st.error(f"Error Alpaca: {e}")
            st.session_state.last_verde_price = price
        st.success(f"🟢 VERDE: {texto}")
    elif estado=="ROJO":
        st.error(f"🔴 ROJO: {texto}")
    else:
        st.warning(f"🟡 AMARILLO: {texto}")
