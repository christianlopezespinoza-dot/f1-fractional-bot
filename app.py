# APP.PY V21 SEMAFORO EDITION - ESTETICA + UX NOVATOS
# Solo cambia la parte visual, formulas igual que V20
import streamlit as st
import yfinance as yf, requests, time, math, numpy as np
from datetime import datetime
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
import matplotlib.pyplot as plt

st.set_page_config(page_title="F1 V21 SEMAFORO", layout="wide", page_icon="🚦")

# --- ESTETICA V21 ---
st.markdown("""
<style>
.card {padding:20px; border-radius:15px; border:1px solid #333; background:linear-gradient(135deg,#0E1117,#1A1A2E)}
.semaforo-verde {background:radial-gradient(#00FF88,#004400); padding:30px; border-radius:20px; text-align:center; border:3px solid #00FF88; box-shadow:0 0 30px #00FF88}
.semaforo-amarillo {background:radial-gradient(#FFD700,#664400); padding:30px; border-radius:20px; text-align:center; border:3px solid #FFD700; box-shadow:0 0 30px #FFD700}
.semaforo-rojo {background:radial-gradient(#FF4444,#660000); padding:30px; border-radius:20px; text-align:center; border:3px solid #FF4444; box-shadow:0 0 30px #FF4444}
</style>
""", unsafe_allow_html=True)

# --- TU CODIGO SECRETS IGUAL ---
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

def calcular_baldor(precios):
    n=len(precios); x_bar=np.mean(precios); s=np.std(precios, ddof=1)
    z=(precios[-1]-x_bar)/(s/math.sqrt(n)) if s>0 else 0
    log_ret=np.log(precios[-1]/precios[-2]) if precios[-2]>0 else 0
    return x_bar,s,z,log_ret

# --- SEMAFORO LOGICA ---
def get_semaforo(price, fib, z, log_ret):
    if price < fib and z < -2.0 and -0.0035 < log_ret < -0.0004:
        return "VERDE", "🟢 COMPRAR AHORA", "Negativo bueno, sobrevendido. Es tu oportunidad V20", "semaforo-verde"
    elif log_ret < -0.05 or z < -8:
        return "ROJO", "🔴 CRASH - NO COMPRAR", "Caída muy fuerte, espera que se calme", "semaforo-rojo"
    else:
        return "AMARILLO", "🟡 ESPERAR", "Aún no está en descuento, paciencia", "semaforo-amarillo"

# UI
try: st.image("car_btc_eth_sol_aapl.jpg", use_container_width=True)
except: pass

col_title, col_sema = st.columns([2,1])
with col_title:
    st.title("🚦 F1 V21 SEMÁFORO EDITION")
    st.caption("V20 Congelado en fórmulas + V21 UX para novatos - Ganar-Ganar")

symbol = st.selectbox("Activo", ["BTC/USD","ETH/USD","SOL/USD","AAPL"], index=0)

if st.button("🔍 ANALIZAR AHORA - V21", type="primary", use_container_width=True):
    ticker="AAPL" if symbol=="AAPL" else symbol.split("/")[0]+"-USD"
    h=yf.Ticker(ticker).history(period="1mo")
    precios=h['Close'].values
    fib=h['High'].max()-(h['High'].max()-h['Low'].min())*0.618
    price=precios[-1]
    x_bar,s,z,log_ret = calcular_baldor(precios)
    
    estado, texto, desc, clase = get_semaforo(price, fib, z, log_ret)
    
    # SEMAFORO GIGANTE
    st.markdown(f'<div class="{clase}"><h1>{texto}</h1><h3>{symbol} ${price:.2f}</h3><p>{desc}</p><p>z={z:.2f} | log={log_ret:.4f} | Fib=${fib:.2f}</p></div>', unsafe_allow_html=True)
    
    c1,c2,c3 = st.columns(3)
    c1.metric("Precio vs Fib", f"${price:.2f}", f"{'Barato' if price<fib else 'Caro'}")
    c2.metric("z = (x̄-μ0)/(σ/√n)", f"{z:.2f}", "Sobrevendido" if z<-2 else "Normal")
    c3.metric("log = ln(Pt/Pt-1)", f"{log_ret:.4f}", "Negativo bueno" if log_ret<0 else "Subiendo")

    # GRAFICO ESTETICO V21
    fig, ax = plt.subplots(figsize=(10,3))
    fig.patch.set_facecolor('#0E1117')
    ax.set_facecolor('#0E1117')
    ax.plot(precios, color='#00FF88', lw=2)
    ax.axhline(fib, color='gold', ls='--', label='Fib 0.618')
    ax.tick_params(colors='white')
    ax.legend()
    st.pyplot(fig)

    if estado=="VERDE":
        if st.button("🚀 EJECUTAR COMPRA V21 $10", type="primary"):
            req=MarketOrderRequest(symbol=symbol, notional=10, side=OrderSide.BUY, time_in_force=TimeInForce.GTC)
            order=client.submit_order(req)
            telegram(f"🟢 V21 SEMAFORO VERDE\n{symbol} COMPRA $10\nz={z:.2f} log={log_ret:.4f}\nOrder {order.id}", True)
            st.balloons()
            st.success("Compra V21 ejecutada")
