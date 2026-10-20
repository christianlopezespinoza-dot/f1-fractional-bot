import requests
import streamlit as st

def notificar_f1(*args, **kwargs):
    # Acepta cualquier forma para no tronar nunca
    try:
        BOT_TOKEN = st.secrets["telegram"]["BOT_TOKEN"]
        CHAT_ID = st.secrets["telegram"]["CHAT_ID"]
    except:
        return False

    symbol = kwargs.get("symbol") or (args[0] if len(args)>0 else "BTC/USD")
    price = kwargs.get("price") or kwargs.get("precio") or (args[2] if len(args)>2 else 0)
    fib = kwargs.get("fib", 0)
    z = kwargs.get("z", 0)
    log = kwargs.get("log", 0)
    tipo = kwargs.get("tipo", "verde")

    if tipo == "verde":
        texto = f"🏁 VERDE {symbol} COMPRAR $2\nPrecio ${price:.2f}\nFib ${fib:.2f}\nZ {z:.2f}\nLog {log*100:.3f}%"
    else:
        texto = f"🔴 ROJO {symbol} NO COMPRAR"

    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        r = requests.post(url, json={"chat_id": CHAT_ID, "text": texto}, timeout=10)
        return r.ok
    except:
        return False
