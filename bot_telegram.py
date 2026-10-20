import requests, streamlit as st, os, time, json

T_TOKEN = st.secrets["telegram"]["BOT_TOKEN"]
CHAT_ID = st.secrets["telegram"]["CHAT_ID"]
OFFSET_FILE = "/tmp/telegram_offset.txt"
LOCK_FILE = "/tmp/last_msg.json"

def notificar_f1(mensaje):
    try:
        # candado para no mandar 4 VERDE al mismo minuto
        now = time.time()
        last = 0
        if os.path.exists(LOCK_FILE):
            try:
                with open(LOCK_FILE) as f:
                    data = json.load(f)
                    last = data.get("time", 0)
            except: pass
        
        if now - last < 1800: # 1800 = 30 min / 3600 = 60 min
            if "VERDE" in mensaje:
                return
        
        url = f"https://api.telegram.org/bot{T_TOKEN}/sendMessage"
        data = {"chat_id": CHAT_ID, "text": mensaje, "parse_mode": "HTML"}
        requests.post(url, data=data, timeout=10)
        
        with open(LOCK_FILE, "w") as f:
            json.dump({"time": now}, f)
    except: pass

def responder_comandos():
    try:
        # leer offset guardado en disco, no en memoria
        last_id = 0
        if os.path.exists(OFFSET_FILE):
            try:
                last_id = int(open(OFFSET_FILE).read())
            except: pass

        url = f"https://api.telegram.org/bot{T_TOKEN}/getUpdates"
        params = {"offset": last_id + 1, "timeout": 0}
        r = requests.get(url, params=params, timeout=5).json()
        
        if not r.get("result"): return

        for update in r["result"]:
            update_id = update["update_id"]
            msg = update.get("message", {})
            text = msg.get("text", "").lower()
            chat_id = msg.get("chat", {}).get("id")
            msg_date = msg.get("date", 0)
            
            # IGNORAR mensajes viejos de mas de 90 seg (esto mata los 4 Motor)
            if time.time() - msg_date > 90:
                last_id = update_id
                continue

            if not text or not chat_id: 
                last_id = update_id
                continue

            if "/help" in text:
                txt = "🏎️ MANUAL F1\n🟢 VERDE = COMPRAR $2\n🟡 AMARILLO = ESPERAR\n🔴 ROJO = VENDER"
                requests.post(f"https://api.telegram.org/bot{T_TOKEN}/sendMessage", data={"chat_id": chat_id, "text": txt}, timeout=10)
            elif "/start" in text:
                requests.post(f"https://api.telegram.org/bot{T_TOKEN}/sendMessage", data={"chat_id": chat_id, "text": "🏁 Motor encendido! Monitoreando cada 15 min."}, timeout=10)
            
            last_id = update_id
        
        # guardar offset para que los otros 3 workers no lo re-lean
        with open(OFFSET_FILE, "w") as f:
            f.write(str(last_id))
            
    except: pass
