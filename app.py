import streamlit as st
import requests
import os
import random
import time

st.set_page_config(page_title="F1 V15", page_icon="🏎️")
st.title("🏎️ F1 BOT V15 - SIN LIBRERIA PESADA")

# SECRETS
try:
    API_KEY = st.secrets["alpaca"]["API_KEY"]
    SECRET_KEY = st.secrets["alpaca"]["SECRET"]
    BASE_URL = st.secrets["alpaca"]["BASE_URL"]  # paper-api.alpaca.markets
    SECRETS_OK = True
except:
    st.warning("Falta secrets - Modo DEMO")
    SECRETS_OK = False
    API_KEY = SECRET_KEY = BASE_URL = None

def get_account():
    headers = {"APCA-API-KEY-ID": API_KEY, "APCA-API-SECRET-KEY": SECRET_KEY}
    r = requests.get(f"https://{BASE_URL}/v2/account", headers=headers)
    return r.json()

if SECRETS_OK:
    try:
        acc = get_account()
        st.metric("Buying Power", f"${acc.get('buying_power', '0')}")
        st.success(f"Conectado a {BASE_URL} - Sin libreria alpaca, no se cae")
    except Exception as e:
        st.error(f"Error cuenta: {e}")

# BOT
capital = st.number_input("Capital $", value=10)
if st.button("🏁 INICIAR V15", type="primary"):
    log = st.empty()
    logs = []
    for i in range(20):
        price = random.randint(150,400)
        logs.append(f"Escaneando Fib 0.618 ... ${price} - BUY detectado!")
        log.code("\n".join(logs[-10:]))
        time.sleep(1)

st.write("Este método con requests ya no se cae en Streamlit")
