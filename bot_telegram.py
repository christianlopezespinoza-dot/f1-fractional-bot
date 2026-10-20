import requests
import streamlit as st

T_TOKEN = st.secrets["telegram"]["BOT_TOKEN"]

def notificar_f1(mensaje, foto=None):
    url = f"https://api.telegram.org/bot{T_TOKEN}/sendMessage"
    chat_id = st.secrets["telegram"]["CHAT_ID"]
    data = {"chat_id": chat_id, "text": mensaje, "parse_mode": "HTML"}
    requests.post(url, data=data)

def responder_comandos():
    # Esto lee si alguien le puso /help a tu bot
    try:
        url = f"https://api.telegram.org/bot{T_TOKEN}/getUpdates"
        resp = requests.get(url, timeout=5).json()
        if not resp["result"]: return
        last = resp["result"][-1]
        text = last["message"]["text"].lower()
        chat_id = last["message"]["chat"]["id"]

        if "/help" in text:
            msg = """🏎️ MANUAL F1 FRACTIONAL BYTE - Golden Edition

f(x)=x²/2 | Caputo 0.382 | Fibonacci Golden Level

🟢 VERDE = COMPRO $2 automático
   Barato + Regalado + Bajadita -0.8% a -0.05%
🟡 AMARILLO = ESPERAR
   No perder es ganar
🔴 ROJO = VENDER

Comandos:
/status - ver BTC ahora
/help - este manual
/start - arrancar motor
"""
            requests.post(f"https://api.telegram.org/bot{T_TOKEN}/sendMessage", data={"chat_id": chat_id, "text": msg})
            
        elif "/start" in text:
            requests.post(f"https://api.telegram.org/bot{T_TOKEN}/sendMessage", data={"chat_id": chat_id, "text": "🏁 Motor encendido en pits! Monitoreando BTC cada 15 min. Si veo VERDE te aviso solo."})
    except: pass
