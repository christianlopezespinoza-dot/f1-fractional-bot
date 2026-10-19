import streamlit as st
st.write("Cargando...") # Para que no salga Oh no de golpe

try:
    import yfinance as yf
    import requests
    import time
    from datetime import datetime
    import alpaca_trade_api as tradeapi
except Exception as e:
    st.error(f"Error importando librerias: {e}")
    st.stop()

st.set_page_config(page_title="F1 V15.1")
st.title("🏎️ F1 V15.1 - Blindado")

# Secrets con proteccion para no crashear
try:
    A_KEY = st.secrets["alpaca"]["API_KEY"]
    A_SECRET = st.secrets["alpaca"]["SECRET"]
    A_BASE = st.secrets["alpaca"].get("BASE_URL", "https://paper-api.alpaca.markets")
    T_TOKEN = st.secrets["telegram"]["BOT_TOKEN"]
    T_CHAT = st.secrets["telegram"]["CHAT_ID"]
    st.success("✅ Secrets OK")
except Exception as e:
    st.error(f"❌ Falta configurar Secrets: {e}")
    st.code("""
[alpaca]
API_KEY="TU_KEY"
SECRET="TU_SECRET"
BASE_URL="https://paper-api.alpaca.markets"

[telegram]
BOT_TOKEN="TU_BOT_TOKEN"
CHAT_ID="TU_CHAT_ID"
    """)
    st.stop()

F1_LARGO = "https://cdn.pixabay.com/audio/2022/03/24/audio_5a70a1157b.mp3"
F1_CORTO = "https://cdn.pixabay.com/audio/2022/03/10/audio_c8c8a73467.mp3"

def telegram(msg, largo=True):
    try:
        url = f"https://api.telegram.org/bot{T_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": T_CHAT, "text": f"{'F1 LARGO' if largo else 'PANICO'} {msg}"}, timeout=10)
        url_a = f"https://api.telegram.org/bot{T_TOKEN}/sendAudio"
        requests.post(url_a, json={"chat_id": T_CHAT, "audio": F1_LARGO if largo else F1_CORTO}, timeout=15)
    except: pass

try:
    api = tradeapi.REST(A_KEY, A_SECRET, A_BASE, api_version='v2')
    st.write(f"Cuenta: {api.get_account().status}")
except Exception as e:
    st.error(f"Error Alpaca: {e}")
    st.stop()

if "running" not in st.session_state:
    st.session_state.running=False
    st.session_state.last_buy=0

c1,c2,c3 = st.columns(3)
with c1:
    if st.button("🏁 INICIAR", type="primary"):
        st.session_state.running=True
        telegram("F1 INICIADO", True)
with c2:
    if st.button("Stop"):
        st.session_state.running=False
with c3:
    if st.button("🚨 PANICO"):
        try:
            api.close_all_positions(cancel_orders=True)
            telegram("PANICO VENDIDO", False)
            st.success("Vendido")
        except Exception as e:
            st.error(e)

if st.session_state.running:
    try:
        h = yf.Ticker("AAPL").history(period="1mo")
        price = h['Close'].iloc[-1]
        fib = h['High'].max() - (h['High'].max()-h['Low'].min())*0.618
        st.metric("AAPL", f"${price:.2f}", f"Fib ${fib:.2f}")
        
        if price <= fib and (time.time()-st.session_state.last_buy)>45:
            order = api.submit_order(symbol="AAPL", notional=10, side='buy', type='market', time_in_force='day')
            st.session_state.last_buy=time.time()
            telegram(f"COMPRA AAPL $10 Fib {fib:.2f} ID {order.id}", True)
            st.success(f"Compra {order.id}")
        time.sleep(5)
        st.rerun()
    except Exception as e:
        st.error(f"Error en loop: {e}")
        time.sleep(5)
        st.rerun()
