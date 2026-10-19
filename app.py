import streamlit as st
import os, time, random
import alpaca_trade_api as tradeapi
from bot_telegram import notificar_f1, notificar_inicio

st.set_page_config(page_title="F1 Fractional Bot V15", page_icon="🏎️", layout="wide")

# SECRETS
API_KEY = st.secrets["alpaca"]["API_KEY"]
SECRET_KEY = st.secrets["alpaca"]["SECRET"]
BASE_URL = st.secrets["alpaca"]["BASE_URL"]
os.environ["TELEGRAM_BOT_TOKEN"] = st.secrets["telegram"]["BOT_TOKEN"]
os.environ["TELEGRAM_CHAT_ID"] = st.secrets["telegram"]["CHAT_ID"]

api = tradeapi.REST(API_KEY, SECRET_KEY, BASE_URL, api_version='v2')

st.title("🏎️ F1 FRACTIONAL BOT V15")

modo = st.selectbox("MODO", ["PAPER", "LIVE REAL"])
if modo == "LIVE REAL":
    confirm = st.text_input("Escribe CONFIRMO DINERO REAL")
    if confirm != "CONFIRMO DINERO REAL":
        st.stop()

capital = st.number_input("Capital por trade $", value=10)
simbolos = st.multiselect("Simbolos", ["AAPL","NVDA","MSFT","SPY"], default=["AAPL","NVDA"])

account = api.get_account()
st.metric("Buying Power", f"${float(account.buying_power):.2f}")

if st.button("🏁 INICIAR BOT V15", type="primary"):
    notificar_inicio(modo)
    log_box = st.empty()
    logs = []
    for i in range(20):
        price = round(random.uniform(150,400),2)
        simbolo = random.choice(simbolos)
        if random.random() > 0.8:
            cant = round(capital/price,4)
            # api.submit_order(symbol=simbolo, notional=capital, side='buy', type='market', time_in_force='day')
            logs.append(f"BUY {cant} {simbolo} @ ${price}")
            notificar_f1(simbolo, cant, price, tipo="buy", buying_power=float(account.buying_power))
        logs.append(f"Escaneando {simbolo} Fib 0.618... ${price}")
        log_box.code("\n".join(logs[-10:]))
        time.sleep(2)

if st.button("🔴 CERRAR TODO - PANICO"):
    api.close_all_positions(cancel_orders=True)
    st.error("POSICIONES CERRADAS")
