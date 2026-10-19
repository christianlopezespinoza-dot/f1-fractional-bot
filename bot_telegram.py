# En tu función de notificación V15

def notificar_compra_f1(simbolo, cantidad, precio):
    # 1. Manda el audio F1
    with open('f1_sound.mp3', 'rb') as audio:
        bot.send_audio(
            chat_id=CHAT_ID,
            audio=audio,
            title="F1 ENTRY V15"
        )
    
    # 2. Luego el mensaje mamalón
    mensaje = f"""
🏎️💨 F1 BREAK DETECTADO!

BUY {cantidad} {simbolo} @ ${precio}
Motivo: F1 Break + Fib 0.618
Stop: 2% | Take: 3.5%

Power: {buying_power}
    """
    bot.send_message(chat_id=CHAT_ID, text=mensaje)
