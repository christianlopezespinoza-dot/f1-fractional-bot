import streamlit as st
import requests
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="Fractional F1 Bot V14", page_icon="🏎️", layout="wide")

st.markdown("""
<style>
.stApp {background:#0e1117;}
</style>
""", unsafe_allow_html=True)

BOT_TOKEN = st.secrets.get("BOT_TOKEN", "")
CHAT_ID = st.secrets.get("CHAT_ID", "")

def get_btc_price():
    try:
        import ccxt
        ex = ccxt.binance()
        t = ex.fetch_ticker('BTC/USDT')
        return float(t['last']), "Binance"
    except:
        try:
            r = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd", timeout=10).json()
            return float(r['bitcoin']['usd']), "CoinGecko"
        except:
            return 82919.0, "Simulado"

def send_telegram(text):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}, timeout=10)
        return True
    except:
        return False

price, source = get_btc_price()
high = price * 1.05
low = price * 0.95
level = high - ((high - low) * 0.382)

# HEADER
st.sidebar.success(f"Bot: {'✅' if BOT_TOKEN else '❌'} {CHAT_ID}")
st.title("🏎️ Fractional F1 Bot — LIVE 0.382")
st.caption(f"f(x)=x²/2 | Caputo | {source} | V14")

c1,c2,c3 = st.columns(3)
c1.metric(f"BTC {source}", f"${price:,.2f}")
c2.metric("High", f"${high:,.2f}")
c3.metric("Low", f"${low:,.2f}")
st.metric("🎯 0.382 KEY LEVEL", f"${level:,.2f}", delta=f"{((price-level)/level)*100:.2f}%")

# GRAFICA
st.divider()
st.subheader("📈 Gráfica Fraccional f(x)=x²/2 + Nivel 0.382")
x = np.linspace(0, 10, 200)
y = (x**2)/2
y_0382 = np.full_like(x, level)

fig = go.Figure()
fig.add_trace(go.Scatter(x=x, y=y, name="f(x)=x²/2", line=dict(color="#00d4ff", width=3)))
fig.add_trace(go.Scatter(x=x, y=y_0382, name=f"0.382 Level ${level:,.0f}", line=dict(color="#ff004c", width=2, dash="dash")))
fig.add_trace(go.Scatter(x=[5], y=[price], mode="markers", name=f"BTC Actual ${price:,.0f}", marker=dict(size=12, color="yellow")))
fig.update_layout(template="plotly_dark", height=400, margin=dict(l=0,r=0,t=20,b=0))
st.plotly_chart(fig, use_container_width=True)

st.latex(r"D^{0.382} f(x) = \frac{2}{\Gamma(2.618)} x^{1.618}")

if st.button("📤 Enviar Alerta a Telegram"):
    msg = f"🏎️ *F1 Bot V14*\n💰 BTC: ${price:,.2f}\n🎯 0.382: ${level:,.2f}\n📊 f(x)=x²/2\n⏰ {datetime.now().strftime('%H:%M:%S')}"
    if send_telegram(msg):
        st.success("Enviado ✅")
        st.balloons()

# Auto alerta
if abs(price - level)/level < 0.002:
    send_telegram(f"⚠️ TOQUE 0.382\nBTC ${price:,.2f} -> ${level:,.2f}")
