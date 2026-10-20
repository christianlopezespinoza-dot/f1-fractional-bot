import streamlit as st
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@700&display=swap" rel="stylesheet">
<style>
h1, h2, h3, .stMetric {font-family: 'Orbitron', monospace !important;}
div[data-testid="stMetricValue"] {color: #FFD700 !important; text-shadow: 0 0 15px #FFD700, 0 0 30px #FFA500;}
.tarjeta-pro {border:2px solid gold; border-radius:15px; padding:12px; background: rgba(255,215,0,0.08);}
.prob-alta {color:#00FF88; font-weight:bold; text-shadow: 0 0 10px #00FF88;}
.prob-media {color:#FFD60A; font-weight:bold;}
.prob-baja {color:#FF3B3B; font-weight:bold;}
</style>
""", unsafe_allow_html=True)

import yfinance as yf
import time, math, numpy as np, pandas as pd, matplotlib.pyplot as plt
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from bot_telegram import notificar_f1, responder_comandos
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="F1 V23 PRO HISTORICO", page_icon="🏎️", layout="wide")
st_autorefresh(interval=15*60*1000, key="v23")
if "last_update_id" not in st.session_state: st.session_state.last_update_id = 0
if "last_verde_price" not in st.session_state: st.session_state.last_verde_price = 0

responder_comandos()

A_KEY = st.secrets["alpaca"]["API_KEY"]
A_SECRET = st.secrets["alpaca"]["SECRET"]
client = TradingClient(A_KEY, A_SECRET, paper=True)
ORDER_NOTIONAL = 10

def calcular_quant(precios):
    n=len(precios); x_bar=np.mean(precios); s=np.std(precios, ddof=1)
    z=(precios[-1]-x_bar)/(s/math.sqrt(n)) if s>0 else 0
    log_ret=math.log(precios[-1]/precios[-2]) if precios[-2]>0 else 0
    return x_bar, s, z, log_ret

def get_semaforo(price, fib, z, log_ret):
    if price < fib and z < -2.0 and -0.008 < log_ret < -0.0002:
        return "VERDE", "🟢 COMPRAR $10", "#00FF88"
    elif log_ret < -0.05 or z > 1.0:
        return "ROJO", "🔴 NO COMPRAR", "#FF3B3B"
    else:
        return "AMARILLO", "🟡 ESPERAR", "#FFD60A"

def analisis_historico(ticker):
    # Descarga 1 año para memoria
    hist_1y = yf.Ticker(ticker).history(period="1y")
    hist_6m = yf.Ticker(ticker).history(period="6mo")
    close = hist_1y['Close'].values
    price_now = close[-1]
    
    # Tendencias
    ret_24h = (close[-1]/close[-2]-1)*100 if len(close)>2 else 0
    ret_7d = (close[-1]/close[-6]-1)*100 if len(close)>6 else 0
    ret_30d = (close[-1]/close[-21]-1)*100 if len(close)>21 else 0
    ret_1y = (close[-1]/close[0]-1)*100 if len(close)>0 else 0
    max_1y = hist_1y['High'].max()
    min_1y = hist_1y['Low'].min()
    dist_max = (price_now/max_1y-1)*100
    
    # Backtest: cada vez que hubo Z < -2 similar, que paso 1d y 7d despues?
    rebotes_1d = []
    rebotes_7d = []
    for i in range(30, len(close)-7):
        ventana = close[i-30:i]
        if len(ventana)<30: continue
        xb = np.mean(ventana); s = np.std(ventana, ddof=1)
        if s==0: continue
        z_i = (ventana[-1]-xb)/(s/math.sqrt(len(ventana)))
        lr_i = math.log(close[i]/close[i-1]) if close[i-1]>0 else 0
        if z_i < -2.0 and -0.008 < lr_i < -0.0002:
            r1 = (close[i+1]/close[i]-1)*100
            r7 = (close[i+7]/close[i]-1)*100
            rebotes_1d.append(r1)
            rebotes_7d.append(r7)
    
    prob_positiva_1d = (np.sum(np.array(rebotes_1d)>0)/len(rebotes_1d)*100) if rebotes_1d else 0
    avg_1d = np.mean(rebotes_1d) if rebotes_1d else 0
    avg_7d = np.mean(rebotes_7d) if rebotes_7d else 0
    casos = len(rebotes_1d)
    
    return {
        "ret_24h": ret_24h, "ret_7d": ret_7d, "ret_30d": ret_30d, "ret_1y": ret_1y,
        "max_1y": max_1y, "min_1y": min_1y, "dist_max": dist_max,
        "prob_1d": prob_positiva_1d, "avg_1d": avg_1d, "avg_7d": avg_7d, "casos": casos
    }

c1,c2,c3 = st.columns([2,1,1])
with c1: symbol = st.selectbox("Activo", ["BTC/USD","AAPL","ETH/USD"], index=0)
with c2: iniciar = st.button("🏁 ANALIZAR V23 PRO", type="primary", use_container_width=True)
with c3:
    if st.button("🚨 PANICO", use_container_width=True):
        try: client.close_all_positions(cancel_orders=True); st.error("PÁNICO ACTIVADO - Todo vendido")
        except Exception as e: st.error(e)

if iniciar:
    ticker = "BTC-USD" if symbol=="BTC/USD" else "ETH-USD" if symbol=="ETH/USD" else "AAPL"
    h = yf.Ticker(ticker).history(period="1mo")
    precios = h['Close'].values
    fib = h['High'].max()-(h['High'].max()-h['Low'].min())*0.618
    price = precios[-1]
    x_bar, s, z, log_ret = calcular_quant(precios)
    estado, texto, color = get_semaforo(price, fib, z, log_ret)
    hist_data = analisis_historico(ticker)

    st.markdown(f"## <span style='color:gold; text-shadow:0 0 20px gold'>🏎️ F1 V23 PRO HISTÓRICO - {symbol} {texto}</span>", unsafe_allow_html=True)

    m1,m2,m3,m4 = st.columns(4)
    m1.metric(symbol, f"${price:,.2f}", f"Fib ${fib:,.2f}")
    m2.metric("z-score", f"{z:.2f}", "Compra < -2")
    m3.metric("log ret", f"{log_ret*100:.3f}%", "-0.8% a -0.05%")
    m4.markdown(f"<div style='background:{color}; color:black; padding:12px; border-radius:10px; text-align:center'><b>{texto}</b></div>", unsafe_allow_html=True)

    # Gráfica
    fig, ax = plt.subplots(figsize=(11,4.5))
    fig.patch.set_facecolor('#0E1117'); ax.set_facecolor('#0E1117')
    ax.plot(precios, color='#00FF88', linewidth=2, label='Precio')
    ax.axhline(fib, color='gold', linestyle='--', label='Fib 61.8%')
    ax.axhline(x_bar, color='cyan', alpha=0.4, label='Media Quant')
    if estado=="VERDE": ax.scatter(len(precios)-1, price, color='lime', s=150, edgecolors='white', zorder=5)
    ax.legend(facecolor='#0E1117', edgecolor='gold', labelcolor='white')
    ax.tick_params(colors='white'); st.pyplot(fig)

    # PANEL PREDICTIVO PRO
    st.markdown("### 📡 PREDICCIÓN AUTOMÁTICA + ADVERTENCIA HISTÓRICA")
    colA, colB, colC, colD = st.columns(4)
    with colA:
        st.markdown(f"<div class='tarjeta-pro'><b>⏱️ 24 HORAS</b><br>{hist_data['ret_24h']:+.2f}%<br><small>Tendencia corta</small></div>", unsafe_allow_html=True)
    with colB:
        st.markdown(f"<div class='tarjeta-pro'><b>📅 7 DÍAS</b><br>{hist_data['ret_7d']:+.2f}%<br><small>Tendencia semanal</small></div>", unsafe_allow_html=True)
    with colC:
        st.markdown(f"<div class='tarjeta-pro'><b>📆 30 DÍAS</b><br>{hist_data['ret_30d']:+.2f}%<br><small>Tendencia mensual</small></div>", unsafe_allow_html=True)
    with colD:
        st.markdown(f"<div class='tarjeta-pro'><b>🏔️ vs MAX 1 AÑO</b><br>{hist_data['dist_max']:+.2f}%<br><small>Max ${hist_data['max_1y']:,.0f}</small></div>", unsafe_allow_html=True)

    prob = hist_data['prob_1d']
    clase_prob = "prob-alta" if prob>=60 else "prob-media" if prob>=45 else "prob-baja"
    st.markdown(f"""
    <div class='tarjeta-pro' style='margin-top:15px'>
    <b>🧠 BACKTEST HISTÓRICO AUTOMÁTICO</b><br>
    Se encontraron <b>{hist_data['casos']} casos</b> similares en el último año donde Z < -2 y log-ret igual que ahora.<br>
    <span class='{clase_prob}'>Probabilidad de rebote positivo en 24h: {prob:.1f}%</span><br>
    Ganancia promedio si rebotó en 24h: <b>{hist_data['avg_1d']:+.2f}%</b> | En 7 días: <b>{hist_data['avg_7d']:+.2f}%</b><br><br>
    <b>⚠️ ADVERTENCIA:</b> {"🟢 OPORTUNIDAD PRO: Históricamente rebota, buen momento para acumular" if prob>=60 else "🟡 NEUTRAL: 50/50, compra con cautela de $10" if prob>=45 else "🔴 CUIDADO: Históricamente sigue cayendo, no cargues mucho"}
    </div>
    """, unsafe_allow_html=True)

    # Orden real
    if estado=="VERDE":
        if abs(price - st.session_state.last_verde_price) > 10:
            mensaje = f"🏁 V23 PRO VERDE {symbol}\nPrecio ${price:.2f} Fib ${fib:.2f}\nZ {z:.2f} Log {log_ret*100:.3f}%\n24h {hist_data['ret_24h']:+.2f}% 7d {hist_data['ret_7d']:+.2f}% vsMax {hist_data['dist_max']:+.2f}%\nBacktest: {prob:.1f}% rebote 24h (casos {hist_data['casos']}) avg {hist_data['avg_1d']:+.2f}%"
            notificar_f1(mensaje)
            try:
                orden = MarketOrderRequest(symbol=symbol, notional=ORDER_NOTIONAL, side=OrderSide.BUY, time_in_force=TimeInForce.GTC)
                client.submit_order(orden)
                st.success(f"✅ Orden REAL ${ORDER_NOTIONAL} enviada - V23 PRO")
            except Exception as e:
                st.error(f"Error Alpaca: {e}")
            st.session_state.last_verde_price = price
        st.success(f"🟢 {texto} - Backtest {prob:.1f}% prob rebote")
    elif estado=="ROJO":
        st.error(f"🔴 {texto} - Advertencia: {hist_data['ret_24h']:+.2f}% en 24h")
    else:
        st.warning(f"🟡 {texto}")
