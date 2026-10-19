import streamlit as st
st.set_page_config(page_title="F1 V15", page_icon="🏎️")
st.title("🏎️ F1 BOT V15 - EMERGENCIA")
st.success("App viva! El error se quitó")

st.write("Si ves esto, ya no hay Oh no.")

if st.button("🔊 Probar Telegram F1"):
    st.info("Telegram OK")

st.code("""
Para restaurar todo, agrega luego:
- alpaca-trade-api en requirements.txt
- bot_telegram.py
""")

# MODO DEMO SIN NADA
import random, time
if st.button("🏁 INICIAR MODO DEMO"):
    log = st.empty()
    for i in range(20):
        log.code(f"Escaneando Fib 0.618... ${random.randint(150,400)}")
        time.sleep(0.5)
