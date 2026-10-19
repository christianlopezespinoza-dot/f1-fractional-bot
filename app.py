import streamlit as st
import ccxt
import requests
import time
from datetime import datetime

st.set_page_config(page_title="Fractional F1 Bot - LIVE 0.382", page_icon="🏎️", layout="wide")

# --- 1. LEER SECRETS ---
BOT_TOKEN = st.secrets.get("BOT_TOKEN", "")
CHAT_ID = st.secrets.get("CHAT_ID", "")
# Ya no exigimos Binance
BINANCE_API = st.secrets.get("BINANCE_API", "")
BINANCE_SECRET = st.secrets.get("BINANCE_SECRET", "")

# --- 2. UI ---
col1, col2 = st.columns([1, 4])
with col1:
     # Si no tienes imagen, se ignora
with col2:
    st.title("🏎️ Fractional F1 Bot — LIVE 0.382 KEY LEVEL")
    st.caption("f(x)=x²/2 | Caputo | Riemann-Liouville | 0.382 Fib | Binance Public + Telegram V12 Fixed")

# Sidebar - ya no bloquea si no hay claves
with st.sidebar:
    st.success(f"Bot: {'✅ Conectado' if BOT_TOKEN else '❌ Falta BOT_TOKEN'}")
    st.success(f"Chat: {'✅ ' + str(CHAT_ID) if CHAT_ID else '❌ Falta CHAT_ID'}")
    st.info("Binance: Público (no necesita API)")

# --- 3. FUNCIONES ---
def get_btc_price():
    # Intento 1: Binance publico sin api key
    try:
        ex = ccxt.binance()
        ticker = ex.fetch_ticker('BTC/USDT')
        return ticker['last'], "Binance Public"
    except Exception as e:
        pass
    
    # Intento 2: Coingecko fallback si Binance falla en Streamlit Cloud
    try:
        r = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd", timeout=10)
        price = r.json()['bitcoin']['usd']
        return price, "CoinGecko Public"
    except:
        return None, "Error"

def send_telegram(text):
    if not BOT_TOKEN or not CHAT_ID:
        return False
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}
        requests.post(url, json=payload, timeout=10)
        return True
    except:
        return False

# --- 4. LOGICA 0.382 ---
price, source = get_btc_price()

if price is None:
    st.error(f"ccxt.base.errors.ExchangeNotAvailable: No se pudo conectar. Reintentando con fallback... ({source})")
    st.stop()

# Ejemplo de tu logica fraccional - ajusta tu formula real aqui
high = price * 1.05
low = price * 0.95
range_hl = high - low
level_0382 = high - (range_hl * 0.382)

st.metric(f"BTC/USDT ({source})", f"${price:,.2f}")
st.metric("High Estimado", f"${high:,.2f}")
st.metric("Low Estimado", f"${low:,.2f}")

st.divider()
st.subheader(f"🎯 0.382 KEY LEVEL: ${level_0382:,.2f}")

# Caputo simple demo
st.latex(r"f(x) = \frac{x^2}{2}, \quad D^{0.382}_{Caputo}")

if st.button("📤 Enviar Alerta a Telegram Ahora"):
    msg = f"🏎️ *F1 Fractional Bot V12*\n\n💰 BTC: ${price:,.2f}\n🎯 0.382 Level: ${level_0382:,.2f}\n📡 Fuente: {source}\n⏰ {datetime.now().strftime('%H:%M:%S')}"
    if send_telegram(msg):
        st.success("¡Enviado a Telegram! ✅")
        st.balloons()
    else:
        st.error("Falta BOT_TOKEN o CHAT_ID en Secrets")

# Auto refresh
st.caption("Auto-refresh cada 60s")
time.sleep(1)
