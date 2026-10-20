import requests
import streamlit as st

T_TOKEN = st.secrets["telegram"]["BOT_TOKEN"]
CHAT_ID = st.secrets["telegram"]["CHAT_ID"]

def notificar_f1(mensaje):
    try:
        url = f"https://api.telegram.org/bot{T_TOKEN}/sendMessage"
        data = {"chat_id": CHAT_ID, "text": mensaje, "parse_mode": "HTML"}
        requests.post(url, data=data, timeout=10)
    except: pass

def responder_comando():
    try:
        url = f"https://api.telegram.org/bot{T_TOKEN}/getUpdates"
        r = requests.get(url, timeout=5).json()
        if not r.get("result"): return
        last = r["result"][-1]
        text = last["message"]["text"].lower()
        chat_id = last["message"]["chat"]["id"]

        if "/help" in text:
            msg = "🏎️ MANUAL F1 FRACTIONAL BYTE\n\n🟢 VERDE = COMPRO $2\n🟡 AMARILLO = No perder es ganar\n🔴 ROJO = Vendo\n\n/status /help /start"
            requests.post(f"https://api.telegram.org/bot{T_TOKEN}/sendMessage", data={"chat_id": chat_id, "text": msg})
        elif "/start" in text:
            requests.post(f"https://api.telegram.org/bot{T_TOKEN}/sendMessage", data={"chat_id": chat_id, "text": "🏁 Motor encendido! Monitoreando cada 15 min."})
    except: pass
