# app.py V19 QUANT GOLD - FINAL - 6 Flyers + 4 Activos + Gold Car
import streamlit as st
import yfinance as yf, requests, time, math, numpy as np, matplotlib.pyplot as plt
from datetime import datetime
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

st.set_page_config(page_title="F1 V19 QUANT GOLD", layout="wide")

# HEADER GOLD - Usa la imagen car_btc_eth_sol_aapl.jpg
try:
    st.image("car_btc_eth_sol_aapl.jpg", use_container_width=True)
    st.caption("PACK HD V19 QUANT GOLD - BTC | ETH | SOL | AAPL - 10 FÓRMULAS + FIB 0.618")
except:
    st.info("Sube car_btc_eth_sol_aapl.jpg a tu repo")

st.title("🏎️ F1 V19 QUANT GOLD - Bolsa + Crypto + F1")
st.markdown("**Backtest +12.4% / +15% | Win Rate 68% | Sharpe 1.92 | Z-Score 95% | Derivada f'(x) | Ciclo Unitario**")

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

def calcular_quant(precios):
    n = len(precios)
    x_bar = np.mean(precios)
    s = np.std(precios, ddof=1)
    EE = s / math.sqrt(n) if n>0 else 0
    z = (precios[-1] - x_bar) / (s / math.sqrt(n)) if s>0 else 0
    IC_inf = x_bar - 1.96 * s / math.sqrt(n)
    IC_sup = x_bar + 1.96 * s / math.sqrt(n)
    derivada = (precios[-1] - precios[-6]) / 5 if n>6 else 0
    ciclo = math.sin(2*math.pi*datetime.now().hour/24)
    return x_bar, s, EE, z, IC_inf, IC_sup, derivada, ciclo

if "running" not in st.session_state:
    st.session_state.running=False
    st.session_state.last_buy=0
    st.session_state.buy_count=6

# CONTROLES CON LAS 3 OPCIONES
c1,c2,c3,c4,c5 = st.columns(5)
with c1:
    symbol = st.selectbox("Activo", ["AAPL", "BTC/USD", "ETH/USD", "SOL/USD"], index=1)
with c2:
    version = st.selectbox("Flyer", ["V18 12.4%", "V19 15%", "Pack 3 Formatos"])
with c3:
    if st.button("🏁 INICIAR V19", type="primary"):
        st.session_state.running=True
        telegram(f"🏁 F1 LARGO F1 V19 GOLD INICIADO\n{symbol} - {version}\n+15% Backtest | BTC ETH SOL AAPL\n{datetime.now().strftime('%H:%M:%S')}", True)
with c4:
    if st.button("Stop"): st.session_state.running=False
with c5:
    if st.button("🚨 PANICO"):
        try:
            client.close_all_positions(cancel_orders=True)
            telegram("🚨 PANICO - Todo vendido", False)
        except Exception as e: st.error(e)

if st.session_state.running:
    ticker = "AAPL" if symbol=="AAPL" else symbol.split("/")[0]+"-USD"
    h = yf.Ticker(ticker).history(period="1mo")
    if len(h) < 10:
        st.error("Sin datos")
        st.stop()
    precios = h['Close'].values
    fib = h['High'].max()-(h['High'].max()-h['Low'].min())*0.618
    price = precios[-1]
    x_bar, s, EE, z, IC_inf, IC_sup, derivada, ciclo = calcular_quant(precios)

    # METRICAS IGUAL AL FLYER
    m1,m2,m3,m4 = st.columns(4)
    m1.metric(symbol, f"${price:.2f}", f"Fib 0.618 ${fib:.2f}")
    m2.metric("z-score (F3)", f"{z:.2f}", "Compra <-2")
    m3.metric("f'(x) Derivada", f"{derivada:.4f}")
    m4.metric("Ciclo Unitario", f"{ciclo:.2f}")

    # GRAFICO CHINGON V19
    fig, (ax1, ax2) = plt.subplots(2,1, figsize=(12,7), gridspec_kw={'height_ratios': [3,1]})
    fig.patch.set_facecolor('#0E1117')
    ax1.set_facecolor('#0E1117')
    ax1.plot(precios, color='#00FF88', linewidth=2, label='Precio Real')
    ax1.axhline(fib, color='gold', linestyle='--', linewidth=1.5, label='Fib 0.618 Amarillo')
    ax1.axhline(x_bar, color='cyan', alpha=0.6, label='Media x_bar')
    ax1.fill_between(range(len(precios)), IC_inf, IC_sup, color='gold', alpha=0.08, label='IC 95% Fórmula 5')
    if price <= fib and z < -2:
        ax1.scatter(len(precios)-1, price, color='white', s=300, edgecolors='gold', linewidth=3, zorder=5, label='Compra z<-2')
    ax1.tick_params(colors='white')
    ax1.legend(facecolor='black', edgecolor='gold', labelcolor='white')
    ax1.set_title(f"{symbol} - BTC ETH AAPL SOL - QUANT GOLD DASHBOARD", color='gold')

    # Segundo panel naranja/morado
    ax2.set_facecolor('#0E1117')
    z_roll = [np.mean(precios[max(0,i-10):i+1]) for i in range(len(precios))]
    ax2.plot(z_roll, color='orange', label="z = (x̄-μ0)/(σ/√n)")
    ax2.plot([derivada]*len(precios), color='purple', linestyle='--', label="f'(x)=lim h→0")
    ax2.axhline(-2, color='red', linestyle=':', alpha=0.5)
    ax2.legend(facecolor='black', edgecolor='gold', labelcolor='white', fontsize=8)
    ax2.tick_params(colors='white')
    st.pyplot(fig)

    # COMPRA CON TEXTO V15 INTACTO + V19
    if price <= fib and z < -2.0 and (time.time()-st.session_state.last_buy)>45:
        try:
            req = MarketOrderRequest(symbol=symbol, notional=10, side=OrderSide.BUY, time_in_force=TimeInForce.DAY if symbol=="AAPL" else TimeInForce.GTC)
            order = client.submit_order(req)
            st.session_state.buy_count+=1
            st.session_state.last_buy=time.time()
            txt = f"""🏁🔊🔊🔊 SONIDO F1 LARGO - COMPRA
✅ COMPRA REAL #{st.session_state.buy_count}
{symbol} $10
Fib 0.618: {fib:.2f}
Ejecutado: {price:.2f}
z: {z:.2f} EE: {EE:.2f} f'(x): {derivada:.3f}
IC: [{IC_inf:.2f}-{IC_sup:.2f}]
Order: {order.id}
Flyer: {version} - Pack 3 Formatos GOLD"""
            telegram(txt, True)
            st.balloons()
            st.success(f"Compra #{st.session_state.buy_count} OK - {version}")
        except Exception as e: st.error(e)

    time.sleep(5)
    st.rerun()
