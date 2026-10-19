import telegram
import os

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or "TU_TOKEN_AQUI"
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID") or "TU_CHAT_ID_AQUI"
bot = telegram.Bot(token=BOT_TOKEN)

def notificar_f1(simbolo, cantidad, precio, tipo="buy", buying_power=0):
    try:
        # Elige sonido
        if tipo == "take_profit":
            sonido_path = "assets/f1_opcion1_aceleron_largo.wav"
            emoji = "🏁💰 TAKE PROFIT!"
        else:
            sonido_path = "assets/f1_opcion2_braaap_corto.wav"
            emoji = "🏎️💨 F1 BREAK"

        if os.path.exists(sonido_path):
            with open(sonido_path, 'rb') as audio:
                bot.send_audio(chat_id=CHAT_ID, audio=audio, title=f"F1 {tipo}")

        if tipo == "buy":
            msg = f"""
{emoji} V15 DETECTADO!

📊 {simbolo}
BUY {cantidad} @ ${precio}
Motivo: F1 Break + Fib 0.618

💵 Power: ${buying_power}
Stop: 2% | Take: 3.5%
            """
        else:
            msg = f"{emoji} SELL {cantidad} {simbolo} @ ${precio}"

        bot.send_message(chat_id=CHAT_ID, text=msg)
        return True
    except Exception as e:
        print(f"Error Telegram: {e}")
        return False

def notificar_inicio(modo):
    bot.send_message(chat_id=CHAT_ID, text=f"🏎️ F1 BOT V15 INICIADO - MODO {modo}")
