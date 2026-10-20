import requests
import os

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def notificar_f1(simbolo, cantidad, precio, tipo="verde", fib=0, z=0, log=0):
    if not BOT_TOKEN or not CHAT_ID:
        print("FALTA BOT_TOKEN o CHAT_ID en secrets")
        return False
    try:
        if tipo == "verde":
            msg = f"🏁🔊 F1 LARGO - VERDE DETECTADO\n\n🟢 {simbolo} COMPRAR $2\nPrecio: ${precio}\nFib: ${fib:.2f}\nZ: {z:.2f} (regalado)\nLog: {log*100:.3f}% (bajadita)\n\n💰 Si fuera real, $2"
            emoji = "🏁"
        else:
            msg = f"🔴 F1 V21 {tipo.upper()} - {simbolo}"
            emoji = "🔴"

        url_msg = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        r = requests.post(url_msg, json={"chat_id": CHAT_ID, "text": msg}, timeout=10)
        print("Telegram msg:", r.text)

        # Sonido: manda link de audio F1
        url_audio = f"https://api.telegram.org/bot{BOT_TOKEN}/sendAudio"
        audio_url = "https://cdn.pixabay.com/audio/2022/03/24/audio_5a70a1157b.mp3"  # largo
        if tipo != "verde":
            audio_url = "https://cdn.pixabay.com/audio/2022/03/10/audio_c8c8a73467.mp3" # corto
        requests.post(url_audio, json={"chat_id": CHAT_ID, "audio": audio_url, "caption": f"{emoji} F1 {tipo}"}, timeout=10)

        return r.ok
    except Exception as e:
        print(f"Error Telegram: {e}")
        return False
