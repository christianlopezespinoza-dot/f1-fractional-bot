import streamlit as st
import yfinance as yf
import requests
import time
from datetime import datetime
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

st.set_page_config(page_title="F1 V16 FINAL")
st.title("🏎️ F1 V16 - Ahora con alpaca-py (no falla)")

# Secrets
try:
    A_KEY = st.secrets["alpaca"]["API_KEY"]
    A_SECRET = st.secrets["alpaca"]["SECRET"]
    A_BASE = st.secrets["alpaca"].get("BASE_URL", "https://paper-api.alpaca.markets")
    T_TOKEN = st.secrets["telegram"]["BOT_TOKEN"]
    T_CHAT = st.secrets["telegram"]["CHAT_ID"]
except Exception as e:
    st.error(f"Configura Secrets: {e}"); st.stop()

client = TradingClient(A_KEY, A_SECRET, paper=True)

def telegram(msg, largo=True):
    try:
        url = f"https://api.telegram.org/bot{T_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": T_CHAT, "text": f"{'🏁 F1 LARGO' if largo else '🚨 PANICO'} {msg}\n{datetime.now().strftime('%H:%M:%S')}"}, timeout=10)
        url_a = f"https://api.telegram.org/bot{T_TOKEN}/sendAudio"
        audio = "https://cdn.pixabay.com/audio/2022/03/24/audio_5a70a1157b.mp3" if largo else "https://cdn.pixabay.com/audio/2022/03/10/audio_c8c8a73467.mp3"
        requests.post(url_a, json={"chat_id": T_CHAT, "audio": audio}, timeout=15)
    except: pass

if "running" not in st.session_state:
    st.session_state.running=False
    st.session_state.last_buy=0

c1,c2,c3=st.columns(3)
with c1:
    if st.button("🏁 INICIAR V16", type="primary"):
        st.session_state.running=True
        telegram("F1 V16 INICIADO - ya sin error Oh no", True)
with c2:
    if st.button("Stop"): st.session_state.running=False
with c3:
    if st.button("🚨 PANICO VENDER"):
        try:
            client.close_all_positions(cancel_orders=True)
            telegram("PANICO - Todo vendido", False)
            st.success("Vendido")
        except Exception as e: st.error(e)

def get_fib():
    h=yf.Ticker("AAPL").history(period="1mo")
    price=h['Close'].iloc[-1]
    fib=h['High'].max()-(h['High'].max()-h['Low'].min())*0.618
    return fib, price

if st.session_state.running:
    fib, price = get_fib()
    st.metric("AAPL", f"${price:.2f}", f"Fib 0.618: ${fib:.2f}")
    if price<=fib and (time.time()-st.session_state.last_buy)>45:
        try:
            req = MarketOrderRequest(symbol="AAPL", notional=10, side=OrderSide.BUY, time_in_force=TimeInForce.DAY)
            order = client.submit_order(req)
            st.session_state.last_buy=time.time()
            telegram(f"✅ COMPRA REAL AAPL $10 Fib {fib:.2f} ID {order.id}", True)
            st.success(f"Compra OK {order.id}")
        except Exception as e: st.error(e)
    time.sleep(5)
    st.rerun()
