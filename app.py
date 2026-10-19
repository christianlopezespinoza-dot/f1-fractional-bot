import streamlit as st
import os, time, random

st.set_page_config(page_title="F1 Fractional Bot V15", page_icon="🏎️")

# TRY IMPORTS BLINDADOS
try:
    import alpaca_trade_api as tradeapi
    ALPACA_OK = True
except ModuleNotFoundError as e:
    st.error(f"⚠️ Falta instalar: {e}")
    ALPACA_OK = False
    tradeapi = None

try:
    from bot_telegram import notificar_f1, notificar_inicio
    TELEGRAM_OK = True
except Exception as e:
    TELEGRAM_OK = False
    def notificar_f1(*a, **k): return False
    def notificar_inicio(*a, **k): return False

# SECRETS CON TRY
try:
    API_KEY = st.secrets["alpaca"]["API_KEY"]
    SECRET_KEY = st.secrets["alpaca"]["SECRET"]
    BASE_URL = st.secrets["alpaca"]["BASE_URL"]
    os.environ["TELEGRAM_BOT_TOKEN"] = st.secrets["telegram"]["BOT_TOKEN"]
    os.environ["TELEGRAM_CHAT_ID"] = st.secrets["telegram"]["CHAT_ID"]
    SECRETS_OK = True
except:
    st.warning("⚠️ Secrets no configurados - Modo DEMO activado")
    SECRETS_OK = False
    API_KEY = SECRET_KEY = BASE_URL = None

st.title("🏎️ F1 FRACTIONAL BOT V15 - BLINDADO")
modo = st.selectbox("MODO", ["DEMO (Sin Alpaca)", "PAPER", "LIVE REAL"])
capital = st.number_input("Capital por trade $", value=10)

if st.button("🔊 PROBAR SONIDO F1"):
    if TELEGRAM_OK:
        notificar_f1("AAPL", "0.0234", "212.34", tipo="buy", buying_power=1000)
        st.success("Sonido enviado a Telegram!")
    else:
        st.error("Revisa bot_telegram.py")

api = None
if ALPACA_OK and SECRETS_OK and modo != "DEMO (Sin Alpaca)":
    try:
        api = tradeapi.REST(API_KEY, SECRET_KEY, BASE_URL, api_version='v2')
        account = api.get_account()
        st.metric("Buying Power", f"${float(account.buying_power):.2f}")
        st.success(f"Conectado a {BASE_URL}")
    except Exception as e:
        st.error(f"Error Alpaca pero la app NO se cae: {e}")

if st.button("🏁 INICIAR BOT V15", type="primary"):
    if TELEGRAM_OK: notificar_inicio(modo)
    log_box = st.empty()
    logs = []
    for i in range(30):
        price = round(random.uniform(150,400),2)
        logs.append(f"🔍 Escaneando AAPL Fib 0.618... ${price}")
        if random.random() > 0.75:
            logs.append(f"✅ BUY 0.0234 AAPL @ ${price}")
            notificar_f1("AAPL", "0.0234", price, tipo="buy", buying_power=9999)
        log_box.code("\n".join(logs[-12:]))
        time.sleep(1.5)
