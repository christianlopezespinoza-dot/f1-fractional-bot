import requests
import streamlit as st

def notificar_f1(symbol, cantidad, price, tipo="verde", fib=0, z=0, log=0):
    try:
        BOT_TOKEN = st.secrets["telegram"]["BOT_TOKEN"]
        CHAT_ID = st.secrets["telegram"]["CHAT_ID"]
    except:
        print("No hay secrets telegram")
        return False

    if tipo == "verde":
        texto = f"🏁🟢 V21 VERDE\n{ symbol} COMPRAR {cantidad}\nPrecio: ${price:.2f}\nFib: ${fib:.2f}\nZ: {z:.2f}\nLog: {log*100:.3f}%\nSonido F1 largo"
    else:
        texto = f"🔴 V21 ROJO\n{ symbol} NO COMPRAR\nPrecio: ${price:.2f}"

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    r = requests.post(url, json={"chat_id": CHAT_ID, "text": texto})
    print(r.text)
    return r.ok
