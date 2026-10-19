import streamlit as st
import yfinance as yf
import requests
import os
import time
from datetime import datetime
import alpaca_trade_api as tradeapi

st.set_page_config(page_title="F1 V15 FINAL", layout="wide")
st.title("🏎️ F1 V15 FINAL - Fib 0.618 + Telegram F1 Real")

# --- SECRETS ---
try:
    A_KEY = st.secrets["alpaca"]["API_KEY"]
    A_SECRET = st.secrets["alpaca"]["SECRET"]
    A_BASE = st.secrets["alpaca"].get("BASE_URL", "https://paper-api.alpaca.markets")
    HAS_ALPACA = True
except:
    st.error("Falta [alpaca] en Secrets")
    HAS_ALPACA = False
    st.stop()

try:
    T_TOKEN = st.secrets["telegram"]["BOT_TOKEN"]
    T_CHAT = st.secrets["telegram"]["CHAT_ID"]
    HAS_TELE = True
except:
    HAS_TELE = False
    st.warning("Falta [telegram] en Secrets - Telegram no sonará")

# --- TELEGRAM CON AUDIO REAL ---
def telegram(msg, largo=True):
    if not HAS_TELE:
        return
    try:
        icono = "🏁🔊🔊🔊 SONIDO F1 LARGO - COMPRA" if largo else "⚠️🔇 SONIDO CORTO - PANICO / VENTA"
        url = f"https://api.telegram.org/bot{T_TOKEN}/sendMessage"
        payload = {
            "chat_id": T_CHAT,
            "text": f"{icono}\n{msg}\n⏰ {datetime.now().strftime('%H:%M:%S %d/%m')}",
            "disable_notification": False
        }
        requests.post(url, json=payload, timeout=10)

        # Enviar audio REAL si existe en tu repo
        nombre_audio = "f1_largo.mp3" if largo else "f1_corto.mp3"
        if os.path.exists(nombre_audio):
            url_audio = f"https://api.telegram.org/bot{T_TOKEN}/sendAudio"
            with open(nombre_audio, 'rb') as audio_file:
                files = {'audio': audio_file}
                data = {'chat_id': T_CHAT, 'caption': '🏎️ F1 LARGO - COMPRA' if largo else '🚨 F1 CORTO - PANICO'}
                requests.post(url_audio, data=data, files=files, timeout=20)
    except Exception as e:
        print(f"Error telegram: {e}")

# --- ALPACA CLIENT ---
api = tradeapi.REST(A_KEY, A_SECRET, A_BASE, api_version='v2')

SYMBOL = "AAPL"
NOTIONAL = 10  # $10 fraccional
COOLDOWN_SEC = 45

if "running" not in st.session_state:
    st.session_state.running = False
if "logs" not in st.session_state:
    st.session_state.logs = []
if "buy_count" not in st.session_state:
    st.session_state.buy_count = 0
if "last_buy_time" not in st.session_state:
    st.session_state.last_buy_time = 0

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("🏁 INICIAR V15", type="primary"):
        st.session_state.running = True
        telegram("F1 V15 FINAL INICIADO - Bot corriendo... cooldown 45s entre compras", largo=True)
        st.session_state.logs.append(f"{datetime.now().strftime('%H:%M:%S')} - F1 V15 FINAL INICIADO")
with col2:
    if st.button("⏹️ Stop"):
        st.session_state.running = False
        st.session_state.logs.append(f"{datetime.now().strftime('%H:%M:%S')} - Bot detenido")
with col3:
    if st.button("🚨 BOTÓN PÁNICO - VENDER TODO", type="secondary"):
        try:
            api.close_all_positions(cancel_orders=True)
            st.session_state.running = False
            msg = "🚨 PANICO ACTIVADO - Vendiendo todo AAPL y cerrando posiciones"
            st.session_state.logs.append(f"{datetime.now().strftime('%H:%M:%S')} - {msg}")
            telegram(msg, largo=False)
            st.success("Pánico ejecutado - Todo vendido")
        except Exception as e:
            st.error(f"Error pánico: {e}")

st.divider()

# --- LOGICA FIB 0.618 REAL ---
def get_fib_level():
    try:
        ticker = yf.Ticker(SYMBOL)
        hist
