import streamlit as st, ccxt, numpy as np, requests, pandas as pd
from math import gamma

st.set_page_config(page_title="F1 Fractional Bot", page_icon="🏎️", layout="wide")

# --- PWA HEADERS + SPLASH ---
st.markdown("""
<link rel="manifest" href="manifest.json">
<link rel="apple-touch-icon" href="icon_512.png">
<meta name="theme-color" content="#000000">
<meta name="apple-mobile-web-app-capable" content="yes">
<script>
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('sw.js');
}
</script>
<style>
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

st.image("icon_512.png", width=120)
st.title("🏎️ Fractional F1 Bot — LIVE 0.382 KEY LEVEL")
st.caption("f(x)=x²/2 | Caputo | Riemann-Liouville | 0.382 Fib | Binance Testnet + Telegram V12")

# --- SECRETS ---
BOT_TOKEN = st.secrets.get("BOT_TOKEN", st.sidebar.text_input("Telegram BOT_TOKEN", type="password"))
CHAT_ID = st.secrets.get("CHAT_ID", st.sidebar.text_input("Telegram CHAT_ID"))
API_KEY = st.secrets.get("BINANCE_API", st.sidebar.text_input("Binance Testnet API Key", type="password"))
API_SECRET = st.secrets.get("BINANCE_SECRET", st.sidebar.text_input("Binance Testnet Secret", type="password"))

KEY_LEVEL = 0.382

def caputo(prices, alpha=0.5):
    n=len(prices)
    if n<20: return 0.0
    w=np.array([(n-i)**(-alpha) for i in range(n)], dtype=float)
    w/=w.sum()
    ret=np.diff(prices, prepend=prices[0])
    return float(np.sum(ret*w)/gamma(1-alpha+1e-6))

def send_v12_alert(price, fib, score):
    if BOT_TOKEN and CHAT_ID:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        msg = f"🏎️💥 V12 0.382 BREACHED!\n💰 BTC ${price:,.2f}\n📐 FIB 0.382 ${fib:,.2f}\n📊 Alpha Score {score:.3f}\n🎯 Acción: {'BUY' if score>0.3 else 'SELL' if score<-0.3 else 'HOLD'}\nMotor: f(x)=x² Caputo α=0.5"
        try:
            requests.post(url, json={"chat_id": CHAT_ID, "text": msg, "disable_notification": False}, timeout=5)
        except: pass
    # Sonido V12 en la web app
    st.audio("https://cdn.pixabay.com/audio/2023/08/09/audio_2e2c6dbdc6.mp3", autoplay=True)

# --- DATOS REALES ---
if API_KEY and API_SECRET:
    exchange = ccxt.binance({'apiKey': API_KEY, 'secret': API_SECRET, 'enableRateLimit': True})
    exchange.set_sandbox_mode(True)
    ticker = exchange.fetch_ticker('BTC/USDT')
    ohlcv = exchange.fetch_ohlcv('BTC/USDT', '1h', limit=200)
    closes = [c[4] for c in ohlcv]
else:
    # Demo sin claves
    closes = (np.cumsum(np.random.randn(200))*50 + 64500).tolist()
    ticker = {'last': closes[-1], 'percentage': np.random.randn()}

colA, colB, colC = st.columns(3)
colA.metric("BTC/USDT", f"${ticker['last']:,.2f}", f"{ticker.get('percentage',0):.2f}%")
fib_382 = min(closes) + (max(closes)-min(closes))*KEY_LEVEL
colB.metric("0.382 FIB LEVEL", f"${fib_382:,.2f}", f"Dist {ticker['last']-fib_382:+.0f}")
score = caputo(closes, 0.5) + caputo(closes, 1.0)
colC.metric("Alpha Score", f"{score:.3f}", "BUY" if score>0.3 else "SELL" if score<-0.3 else "HOLD")

if abs(ticker['last']-fib_382) < 250:
    st.error(f"🚨 0.382 KEY LEVEL BREACHED en ${fib_382:,.2f} — Alerta V12 activa")
    if st.button("🔔 ENVIAR ALERTA V12 AHORA"):
        send_v12_alert(ticker['last'], fib_382, score)
        st.success("Push V12 enviado a Telegram + sonido")

# Gráfico alphas
alphas = [1.0,0.5,0.0,-0.5,-1.0]
df = pd.DataFrame({f"α={a}": [caputo(closes[:i], abs(a)+0.1) for i in range(20,200)] for a in alphas})
st.subheader("ALPHA SIGNALS — 5 Fractional Derivatives (Real-Time)")
st.line_chart(df)
st.image("splash_1080x1920.png", caption="Splash Screen Negro Oro - PWA", use_container_width=True)

if API_KEY and st.button("🏁 EJECUTAR BUY TESTNET 0.001 BTC"):
    order = exchange.create_market_buy_order('BTC/USDT', 0.001)
    st.success(f"Orden Testnet ejecutada: {order['id']}")