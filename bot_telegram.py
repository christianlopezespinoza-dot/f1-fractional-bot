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

def responder_comandos():
    try:
        if "last_update_id" not in st.session_state:
            st.session_state.last_update_id = 0

        url = f"https://api.telegram.org/bot{T_TOKEN}/getUpdates"
        params = {"offset": st.session_state.last_update_id + 1, "timeout": 0}
        r = requests.get(url, params=params, timeout=5).json()
        if not r.get("result"): return

        for update in r["result"]:
            st.session_state.last_update_id = update["update_id"]
            msg = update.get("message", {})
            text = msg.get("text", "").lower()
            chat_id = msg.get("chat", {}).get("id")

            if not text or not chat_id: continue

            if "/help" in text:
                txt = "🏎️ MANUAL F1 V21\n🟢 VERDE = COMPRAR $2\n🟡 AMARILLO = ESPERAR\n🔴 ROJO = VENDER\n\n/status /help /start"
                requests.post(f"https://api.telegram.org/bot{T_TOKEN}/sendMessage", data={"chat_id": chat_id, "text": txt}, timeout=10)
            elif "/start" in text:
                requests.post(f"https://api.telegram.org/bot{T_TOKEN}/sendMessage", data={"chat_id": chat_id, "text": "🏁 Motor encendido! Monitoreando cada 15 min."}, timeout=10)
    except: pass
