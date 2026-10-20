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
        
        # V21 SEMAFORO EDITION - SONIDOS
        tipo = tipo.lower()
        if tipo in ["verde", "buy", "compra"]:
            sonido = "assets/f1_opcion1_aceleron_largo.wav"  # 🟢 LARGO - COMPRAR
            icono = "🟢"
            titulo = "V21 SEMAFORO VERDE - COMPRAR"
        elif tipo in ["rojo", "crash", "sell"]:
            sonido = "assets/f1_opcion2_braaap_corto.wav"  # 🔴 CORTO - FRENO
            icono = "🔴"
            titulo = "V21 SEMAFORO ROJO - NO COMPRAR"
        elif tipo in ["amarillo", "espera"]:
            sonido = "assets/f1_opcion2_braaap_corto.wav"  # AMARILLO = corto suave
            icono = "🟡"
            titulo = "V21 SEMAFORO AMARILLO - ESPERAR"
        else: # take_profit mantiene tu logica original
            sonido = "assets/f1_opcion1_aceleron_largo.wav" if tipo=="take_profit" else "assets/f1_opcion2_braaap_corto.wav"
            icono = "🏁"
            titulo = f"F1 BREAK {tipo.upper()}"

        if os.path.exists(sonido):
            with open(sonido, 'rb') as audio:
                bot.send_audio(chat_id=chat_id, audio=audio)

        # Mensaje V21 con Baldor
        msg = f"{icono} {titulo}\n📊 {simbolo}\nBUY {cantidad} @ ${precio}\nFib 0.618 | z=(x̄-μ0)/(σ/√n)\nlog=ln(Pt/Pt-1)\nBP: ${buying_power}"
        bot.send_message(chat_id=chat_id, text=msg)
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def notificar_inicio(modo):
    try:
        bot = _get_bot()
        bot.send_message(chat_id=os.getenv("TELEGRAM_CHAT_ID"), text=f"🏎️ BOT V21 SEMAFORO INICIADO {modo}")
    except: pass

def notificar_semaforo(estado, simbolo, precio, z, log_ret):
    # Wrapper facil para tu app.py
    if estado == "VERDE":
        return notificar_f1(simbolo, 0.001, precio, tipo="verde", buying_power=0)
    elif estado == "ROJO":
        return notificar_f1(simbolo, 0, precio, tipo="rojo", buying_power=0)
    else:
        return notificar_f1(simbolo, 0, precio, tipo="amarillo", buying_power=0)
