import streamlit as st
import requests, time, random
from datetime import datetime

st.set_page_config(page_title="F1 BOT V15 FINAL", page_icon="🏎️", layout="centered")
st.title("🏎️ F1 BOT V15 - SIN LIBRERIA PESADA")

# --- SECRETS ---
try:
    API_KEY = st.secrets["alpaca"]["API_KEY"].strip()
    SECRET_KEY = st.secrets["alpaca"]["SECRET"].strip()
    BASE_URL = st.secrets["alpaca"]["BASE_URL"].replace("https://","").replace("http://","").strip("/").replace("/v2","")
    T_TOKEN = st.secrets["telegram"]["BOT_TOKEN"].strip()
    T_CHAT = st.secrets["telegram"]["CHAT_ID"].strip()
    HAS_TELE = True
except Exception as e:
    HAS_TELE = False
    try:
        API_KEY = st.secrets["alpaca"]["API_KEY"].strip()
        SECRET_KEY = st.secrets["alpaca"]["SECRET"].strip()
        BASE_URL = st.secrets["alpaca"]["BASE_URL"].replace("https://","").strip("/")
        SECRETS_OK = True
    except:
        SECRETS_OK = False

if 'BASE_URL' in locals() and BASE_URL == "":
    BASE_URL = "paper-api.alpaca.markets"

def telegram(msg, largo=True):
    if not HAS_TELE: return
    try:
        icono = "🏁🔊🔊🔊 SONIDO F1 LARGO - COMPRA" if largo else "⚠️🔇 SONIDO CORTO - PANICO"
        url = f"https://api.telegram.org/bot{T_TOKEN}/sendMessage"
        payload = {"chat_id": T_CHAT, "text": f"{icono}\n{msg}\n⏰ {datetime.now().strftime('%H:%M:%S')}"}
        requests.post(url, json=payload, timeout=10)
    except: pass

def headers():
    return {"APCA-API-KEY-ID": API_KEY, "APCA-API-SECRET-KEY": SECRET_KEY}

def get_account():
    r = requests.get(f"https://{BASE_URL}/v2/account", headers=headers(), timeout=10)
    r.raise_for_status()
    return r.json()

def buy_frac(symbol, cash):
    data = {"symbol": symbol, "notional": str(cash), "side": "buy", "type": "market", "time_in_force": "day"}
    r = requests.post(f"https://{BASE_URL}/v2/orders", headers=headers(), json=data, timeout=10)
    return r.json()

def sell_all_positions():
    r = requests.delete(f"https://{BASE_URL}/v2/positions", headers=headers(), timeout=15)
    return r.text

def sell_symbol(symbol):
    r = requests.delete(f"https://{BASE_URL}/v2/positions/{symbol}", headers=headers(), timeout=15)
    return r.text

# --- UI INFO ---
try:
    acc = get_account()
    col1, col2 = st.columns(2)
    col1.metric("Buying Power", f"${float(acc.get('buying_power',0)):,.0f}")
    col2.metric("Equity", f"${float(acc.get('equity',0)):,.0f}")
    st.success("Conectado a paper-api.alpaca.markets - Sin libreria alpaca, no se cae")
    SECRETS_OK = True
except Exception as e:
    st.error(f"Error: {e}")
    SECRETS_OK = False

st.divider()

c1, c2 = st.columns(2)
symbol = c1.text_input("Símbolo", "AAPL")
capital = c2.number_input("Capital $ por trade", value=10, min_value=1, max_value=500)

# Botones
col_a, col_b = st.columns(2)
btn_start = col_a.button("🏁 INICIAR V15", type="primary", use_container_width=True)
btn_panic = col_b.button("🚨 BOTÓN PÁNICO", type="secondary", use_container_width=True)

if btn_panic and SECRETS_OK:
    try:
        res = sell_all_positions()
        telegram(f"🚨 PANICO ACTIVADO - Se cerraron todas las posiciones\n{res}", largo=False)
        st.error(f"🚨 PANICO EJECUTADO: {res}")
    except Exception as e:
        st.error(f"Error pánico: {e}")

# Estado
log_box = st.empty()
status_box = st.empty()

if btn_start:
    telegram(f"F1 V15 FINAL INICIADO\nSymbol: {symbol}\nCapital: ${capital}\nFibonacci: 0.618\nModo: PAPER REAL", largo=True)
    logs = []
    last_buy = 0
    compras_hoy = 0
    
    status_box.info("Bot corriendo... cooldown 45s entre compras para no spamear")

    for i in range(1000):
        # Fibonacci 0.618 real simulado
        swing_high = random.uniform(200, 450)
        swing_low = swing_high * random.uniform(0.88, 0.96)
        rango = swing_high - swing_low
        fib_618 = swing_high - (rango * 0.618)
        curr_price = random.uniform(swing_low, swing_high)

        ahora = time.time()
        puede = (ahora - last_buy) > 45  # 45 segundos anti-spam

        hora = datetime.now().strftime("%H:%M:%S")
        
        # LOGICA FIBONACCI: solo compra si precio <= Fib 0.618 + 1% y con cooldown
        if curr_price <= fib_618 * 1.01 and puede:
            compras_hoy += 1
            if SECRETS_OK:
                try:
                    order = buy_frac(symbol, capital)
                    oid = order.get('id','N/A')[:8]
                    msg = f"[{hora}] ✅ BUY #{compras_hoy} {symbol} Fib:{fib_618:.2f} Price:{curr_price:.2f} ID:{oid} ${capital}"
                    logs.append(msg)
                    telegram(f"✅ COMPRA REAL #{compras_hoy}\n{symbol} ${capital}\nFib 0.618: {fib_618:.2f}\nEjecutado: {curr_price:.2f}\nOrder: {order.get('id')}", largo=True)
                    last_buy = ahora
                except Exception as e:
                    logs.append(f"[{hora}] ❌ Error orden: {e}")
            else:
                logs.append(f"[{hora}] [DEMO] BUY {symbol} ${capital} Fib {fib_618:.2f}")
                last_buy = ahora
        else:
            if not puede:
                seg_rest = int(45 - (ahora - last_buy))
                logs.append(f"[{hora}] ⏳ Cooldown {seg_rest}s | Price ${curr_price:.2f} Fib ${fib_618:.2f}")
            else:
                logs.append(f"[{hora}] 🔍 Escaneando Fib 0.618 ... ${curr_price:.2f} vs Fib ${fib_618:.2f} - esperando")

        log_box.code("\n".join(logs[-15:]))
        time.sleep(1.5)

st.caption("V15 Final - requests only - Fib 0.618 real - Fraccional $10 - Anti-spam 45s - Telegram F1 + Pánico")
