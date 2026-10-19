import streamlit as st
import yfinance as yf
import requests
import time
from datetime import datetime
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

st.set_page_config(page_title="F1 V15 Textos - V16 Motor", layout="wide")
st.title("🏎️ F1 V16 - Ahora con alpaca-py (no falla)")

A_KEY = st.secrets["alpaca"]["API_KEY"]
A_SECRET = st.secrets["alpaca"]["SECRET"]
T_TOKEN = st.secrets["telegram"]["BOT_TOKEN"]
T_CHAT = st.secrets["telegram"]["CHAT_ID"]

client = TradingClient(A_KEY, A_SECRET, paper=True)

# Audios sin subir nada - para que suene igual que V15
F1_LARGO_URL = "https://cdn.pixabay.com/audio/2022/03/24/audio_5a70a1157b.mp3"
F1_CORTO_URL = "https://cdn.pixabay.com/audio/2022/03/10/audio_c8c8a73467.mp3"

def telegram(msg, largo=True):
    try:
        # Texto igual que V15 del flyer/PDF
        url = f"https://api.telegram.org/bot{T_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": T_CHAT, "text": msg, "disable_notification": False}, timeout=10)
        
        # Audio real
        url_audio = f"https://api.telegram.org/bot{T_TOKEN}/sendAudio"
        requests.post(url_audio, json={"chat_id": T_CHAT, "audio": F1_LARGO_URL if largo else F1_CORTO_URL}, timeout=15)
    except: pass

if "running" not in st.session_state:
    st.session_state.running=False
    st.session_state.last_buy=0
    st.session_state.buy_count=6

c1,c2,c3=st.columns(3)
with c1:
    if st.button("🏁 INICIAR V16", type="primary"):
        st.session_state.running=True
        msg = f"🏁 F1 LARGO F1 V16 INICIADO\n- ya sin error Oh no\n{datetime.now().strftime('%H:%M:%S')}"
        telegram(msg, largo=True)
with c2:
    if st.button("Stop"):
        st.session_state.running=False
with c3:
    if st.button("🚨 PANICO VENDER"):
        try:
            client.close_all_positions(cancel_orders=True)
            st.session_state.running=False
            msg = f"🚨 PANICO PANICO - Todo vendido\n{datetime.now().strftime('%H:%M:%S')}"
            telegram(msg, largo=False)
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
    
    # LOGICA COMPRA - TEXTO IDENTICO A PDF V15
    if price <= fib and (time.time()-st.session_state.last_buy)>45:
        try:
            req = MarketOrderRequest(symbol="AAPL", notional=10, side=OrderSide.BUY, time_in_force=TimeInForce.DAY)
            order = client.submit_order(req)
            st.session_state.buy_count+=1
            st.session_state.last_buy=time.time()
            
            # TEXTO IGUAL QUE EN TU SCREENSHOT V15
            texto_v15 = f"""🏁🔊🔊🔊 SONIDO F1 LARGO - COMPRA
✅ COMPRA REAL #{st.session_state.buy_count}
AAPL $10
Fib 0.618: {fib:.2f}
Ejecutado: {price:.2f}
Order: {order.id}
⏰ {datetime.now().strftime('%H:%M:%S')}"""
            
            telegram(texto_v15, largo=True)
            st.success(f"Compra #{st.session_state.buy_count} OK")
        except Exception as e: st.error(e)
    
    time.sleep(5)
    st.rerun()
