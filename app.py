import streamlit as st, yfinance as yf, requests, time, os
from datetime import datetime
import alpaca_trade_api as tradeapi

st.set_page_config(page_title="F1 V15 FINAL - Con Sonido Real")
st.title("🏎️ F1 V15 FINAL - Fib 0.618 + Sonido Real sin subir")

A_KEY = st.secrets["alpaca"]["API_KEY"]
A_SECRET = st.secrets["alpaca"]["SECRET"]
A_BASE = st.secrets["alpaca"].get("BASE_URL","https://paper-api.alpaca.markets")
T_TOKEN = st.secrets["telegram"]["BOT_TOKEN"]
T_CHAT = st.secrets["telegram"]["CHAT_ID"]

# AUDIOS F1 PUBLICOS - NO NECESITAS SUBIR NADA
F1_LARGO_URL = "https://cdn.pixabay.com/audio/2022/03/24/audio_5a70a1157b.mp3"  # 12s F1 largo
F1_CORTO_URL = "https://cdn.pixabay.com/audio/2022/03/10/audio_c8c8a73467.mp3"  # 2s beep corto

def telegram(msg, largo=True):
    try:
        # Texto
        icono = "🏁🔊🔊🔊 SONIDO F1 LARGO - COMPRA" if largo else "⚠️ SONIDO CORTO - PANICO"
        url = f"https://api.telegram.org/bot{T_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": T_CHAT, "text": f"{icono}\n{msg}\n{datetime.now().strftime('%H:%M:%S')}", "disable_notification": False}, timeout=10)
        # Audio real desde URL publica
        url_audio = f"https://api.telegram.org/bot{T_TOKEN}/sendAudio"
        audio_url = F1_LARGO_URL if largo else F1_CORTO_URL
        requests.post(url_audio, json={"chat_id": T_CHAT, "audio": audio_url, "caption": "🏎️ F1 LARGO REAL" if largo else "🚨 PANICO CORTO"}, timeout=15)
    except Exception as e:
        print(e)

api = tradeapi.REST(A_KEY, A_SECRET, A_BASE, api_version='v2')
SYMBOL="AAPL"; NOTIONAL=10; COOLDOWN=45

if "running" not in st.session_state:
    st.session_state.running=False; st.session_state.logs=[]; st.session_state.buy_count=0; st.session_state.last_buy_time=0

c1,c2,c3=st.columns(3)
with c1:
    if st.button("🏁 INICIAR V15", type="primary"):
        st.session_state.running=True
        telegram("F1 V15 FINAL INICIADO - Sonido F1 real activado", largo=True)
        st.session_state.logs.append("INICIADO")
with c2:
    if st.button("⏹️ Stop"): st.session_state.running=False
with c3:
    if st.button("🚨 PÁNICO VENDER TODO"):
        try:
            api.close_all_positions(cancel_orders=True)
            st.session_state.running=False
            telegram("🚨 PANICO - Vendiendo todo", largo=False)
        except Exception as e: st.error(e)

def get_fib():
    h=yf.Ticker(SYMBOL).history(period="1mo")
    high=h['High'].max(); low=h['Low'].min(); price=h['Close'].iloc[-1]
    fib=high-(high-low)*0.618
    return high,low,fib,price

if st.session_state.running:
    high,low,fib,price=get_fib()
    st.metric(f"{SYMBOL}", f"${price:.2f}", f"Fib 0.618: ${fib:.2f}")
    now=time.time()
    cd=int(COOLDOWN-(now-st.session_state.last_buy_time)) if st.session_state.last_buy_time else 0
    st.info(f"Bot corriendo... cooldown {cd}s" if cd>0 else "LISTO PARA COMPRAR")
    if price<=fib and (now-st.session_state.last_buy_time)>COOLDOWN:
        try:
            order=api.submit_order(symbol=SYMBOL, notional=NOTIONAL, side='buy', type='market', time_in_force='day')
            st.session_state.buy_count+=1; st.session_state.last_buy_time=now
            msg=f"✅ BUY #{st.session_state.buy_count} {SYMBOL} Fib:{fib:.2f} Price:{price:.2f} ID:{str(order.id)[:8]} $10"
            st.session_state.logs.append(msg)
            telegram(f"✅ COMPRA REAL #{st.session_state.buy_count} {SYMBOL} ${NOTIONAL} Fib:{fib:.2f} Order:{order.id}", largo=True)
        except Exception as e: st.error(e)
    time.sleep(5); st.rerun()

for log in reversed(st.session_state.logs[-15:]): st.text(log)
