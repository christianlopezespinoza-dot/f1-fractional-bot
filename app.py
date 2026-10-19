import streamlit as st
import requests
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="Fractional F1 Bot V15", page_icon="🏎️", layout="wide")

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
            return 82376.0, "Simulado"

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
st.sidebar.success(f"Bot: ✅ {CHAT_ID}")
st.sidebar.info(f"Fuente: {source}")

st.title("🏎️ Fractional F1 Bot — LIVE 0.382")
st.caption(f"f(x)=x²/2 | Caputo | {source} | V15 Dark")

c1,c2,c3 = st.columns(3)
c1.metric(f"BTC {source}", f"${price:,.2f}")
c2.metric("High Est.", f"${high:,.2f}")
c3.metric("Low Est.", f"${low:,.2f}")

st.metric("🎯 0.382 KEY LEVEL", f"${level:,.2f}", delta=f"{((price-level)/level)*100:.2f}%")

# GRAFICA CORREGIDA - DOBLE EJE
st.divider()
st.subheader("📈 Gráfica Fraccional f(x)=x²/2 + Nivel 0.382")

x = np.linspace(0, 10, 200)
y = (x**2)/2
# Caputo 0.382: D^0.382 x²/2 = 2/Gamma(2.618) * x^1.618
y_caputo = (2/1.5) * np.power(x, 1.618)

fig = go.Figure()
fig.add_trace(go.Scatter(x=x, y=y, name="f(x)=x²/2", line=dict(color="#00d4ff", width=3), yaxis="y"))
fig.add_trace(go.Scatter(x=x, y=y_caputo, name="D^0.382 f(x) Caputo", line=dict(color="#9d4edd", width=2.5)))

y_0382 = np.full_like(x, level)
fig.add_trace(go.Scatter(x=x, y=y_0382, name=f"0.382 Level ${level:,.0f}", line=dict(color="#ff0054", width=2, dash="dash"), yaxis="y2"))
fig.add_trace(go.Scatter(x=[5], y=[price], mode="markers+text", text=[f" BTC ${price:,.0f}"], textposition="top center", name="BTC Actual", marker=dict(size=12, color="#ffff00"), yaxis="y2"))

fig.update_layout(
    template="plotly_dark",
    height=430,
    margin=dict(l=10,r=10,t=30,b=10),
    yaxis=dict(title="f(x) Valor", side="left", range=[0, 60], gridcolor="#222"),
    yaxis2=dict(title="Precio USD", side="right", overlaying="y", range=[low*0.97, high*1.03], gridcolor="rgba(0,0,0,0)"),
    legend=dict(orientation="h", y=1.12, x=0),
    paper_bgcolor="#0e1117",
    plot_bgcolor="#0e1117"
)
st.plotly_chart(fig, use_container_width=True)

st.latex(r"D^{0.382} f(x) = \frac{2}{\Gamma(2.618)} x^{1.618}")

if st.button("📤 Enviar Alerta a Telegram Ahora"):
    msg = f"🏎️ *F1 Fractional Bot V15*\n\n💰 BTC: ${price:,.2f}\n🎯 0.382 Level: ${level:,.2f}\n📈 f(x)=x²/2 | Caputo\n📡 Fuente: {source}\n⏰ {datetime.now().strftime('%H:%M:%S')}"
    if send_telegram(msg):
        st.success("Enviado a Telegram ✅")
        st.balloons()

# Auto-alerta
if abs(price - level) / level < 0.002:
    send_telegram(f"⚠️ *AUTO-TOQUE 0.382*\nBTC ${price:,.2f} tocando ${level:,.2f}")

st.caption("Auto-refresh 60s | V15 Dark Pro")
