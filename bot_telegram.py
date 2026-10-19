import os
try:
    import telegram
    TELEGRAM_LIB_OK = True
except:
    TELEGRAM_LIB_OK = False

def _get_bot():
    if not TELEGRAM_LIB_OK: return None
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token: return None
    return telegram.Bot(token=token)

def notificar_f1(simbolo, cantidad, precio, tipo="buy", buying_power=0):
    try:
        bot = _get_bot()
        if not bot: return False
        chat_id = os.getenv("TELEGRAM_CHAT_ID")
        sonido = "assets/f1_opcion1_aceleron_largo.wav" if tipo=="take_profit" else "assets/f1_opcion2_braaap_corto.wav"
        if os.path.exists(sonido):
            with open(sonido, 'rb') as audio:
                bot.send_audio(chat_id=chat_id, audio=audio)
        msg = f"🏎️💨 F1 BREAK V15\n📊 {simbolo}\nBUY {cantidad} @ ${precio}\nFib 0.618"
        bot.send_message(chat_id=chat_id, text=msg)
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def notificar_inicio(modo):
    try:
        bot = _get_bot()
        bot.send_message(chat_id=os.getenv("TELEGRAM_CHAT_ID"), text=f"🏎️ BOT V15 INICIADO {modo}")
    except: pass
