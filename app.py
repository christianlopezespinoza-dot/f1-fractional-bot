import streamlit as st
import ccxt
import requests
import time
from datetime import datetime

st.set_page_config(page_title="Fractional F1 Bot V12", page_icon="🏎️", layout="wide")

# CSS correcto (oculto)
st.markdown("""
<style>
.stApp {background: #0e1117; color: white;}
[data-testid="stMetricValue"] {font-size: 28px;}
</style>
""", unsafe_allow_html=True)

BOT_TOKEN = st.secrets.get("BOT_TOKEN", "")
CHAT_ID = st.secrets.get("CHAT_ID", "")

def get_btc_price():
    try:
        ex = ccxt.binance()
        ticker = ex.fetch_ticker('BTC/USDT')
        return float(ticker['last']), "Binance Public"
    except:
        try:
            r = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd", timeout=10).json()
            return float(r['bitcoin']['usd']), "CoinGecko Public"
        except:
            return None, "Error"

def send_telegram(text):
    if not BOT_TOKEN or not CHAT_ID:
        return False
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}, timeout=10)
        return True
    except:
        return False

# --- UI ---
st.sidebar.success(f"Bot: {'✅ Conectado' if BOT_TOKEN else '❌'}")
st.sidebar.success(f"Chat: ✅ {CHAT_ID}")
st.sidebar.info("Binance: Público (no necesita API)")

st.title("🏎️ Fractional F1 Bot — LIVE 0.382 KEY LEVEL")
st.caption("f(x)=x²/2 | Caputo | Riemann-Liouville | 0.382 Fib | V13 Clean")

price, source = get_btc_price()
if not price:
    st.error("No se pudo obtener precio")
    st.stop()

high = price * 1.05
low = price * 0.95
level_0382 = high - ((high - low) * 0.382)

c1, c2, c3 = st.columns(3)
c1.metric(f"BTC/USDT ({source})", f"${price:,.2f}")
c2.metric("High Estimado", f"${high:,.2f}")
c3.metric("Low Estimado", f"${low:,.2f}")

st.divider()
st.subheader(f"🎯 0.382 KEY LEVEL: ${level_0382:,.2f}")
st.latex(r"f(x) = \frac{x^2}{2}, \quad D^{0.382}_{Caputo}")

# Alerta manual
if st.button("📤 Enviar Alerta a Telegram Ahora"):
    msg = f"🏎️ *F1 Fractional Bot V12*\n\n💰 BTC: ${price:,.2f}\n🎯 0.382 Level: ${level_0382:,.2f}\n📡 Fuente: {source}\n⏰ {datetime.now().strftime('%H:%M:%S')}"
    if send_telegram(msg):
        st.success("Enviado a Telegram ✅")
        st.balloons()

# Alerta automática si toca el nivel
if abs(price - level_0382) / level_0382 < 0.002: # 0.2% cerca
    send_telegram(f"⚠️ *AUTO-ALERTA TOQUE 0.382*\nBTC ${price:,.2f} está tocando nivel ${level_0382:,.2f}")

st.caption("Auto-refresh 60s")
