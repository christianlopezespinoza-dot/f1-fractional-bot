import streamlit as st
st.set_page_config(page_title="F1 BOT", page_icon="🏁", layout="wide")
import yfinance as yf, math, numpy as np, matplotlib.pyplot as plt
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from bot_telegram import notificar_f1, responder_comandos
from streamlit_autorefresh import st_autorefresh

st_autorefresh(interval=15*60*1000, key="f1final")
if "last_update_id" not in st.session_state: st.session_state.last_update_id=0
if "last_verde_price" not in st.session_state: st.session_state.last_verde_price=0
if "perfil_nombre" not in st.session_state: st.session_state.perfil_nombre="ChristianLE"
if "analizar" not in st.session_state: st.session_state.analizar=False
responder_comandos()

# THEMA FIJO FERRARI - SIN SELECTOR
primary="#FF0000"; bg="#0A0000"; title_color="#FF0000"; glow="0 0 20px #FF0000"

with st.sidebar:
    st.markdown("## 🏁 F1 BOT")
    st.markdown("#### 👨‍✈️ PERFIL")
    nombre_input = st.text_input("Nombre", value=st.session_state.perfil_nombre, label_visibility="collapsed")
    c1,c2=st.columns(2)
    with c1:
        if st.button("💾 Guardar", use_container_width=True):
            st.session_state.perfil_nombre=nombre_input
            st.rerun()
    with c2:
        if st.button("🔄 Reset", use_container_width=True):
            st.session_state.perfil_nombre="Piloto #1"
            st.rerun()
    piloto=st.session_state.perfil_nombre
    st.info(f"🏁 Piloto: {piloto}")

st.markdown(f"""
<style>
h1{{color:{title_color}!important; text-shadow:{glow}!important}}
[data-testid="stSidebar"]{{background:{bg}; border-right:2px solid {title_color}}}
</style>
""", unsafe_allow_html=True)

A_KEY=st.secrets["alpaca"]["API_KEY"]; A_SECRET=st.secrets["alpaca"]["SECRET"]
client=TradingClient(A_KEY,A_SECRET,paper=True)

def calcular_quant(precios):
    n=len(precios); xb=np.mean(precios); s=np.std(precios,ddof=1)
    z=(precios[-1]-xb)/(s/math.sqrt(n)) if s>0 else 0
    lr=math.log(precios[-1]/precios[-2]) if precios[-2]>0 else 0
    return xb,s,z,lr

def get_semaforo(price,fib,z,lr):
    if price<fib and z<-2.0 and -0.008<lr<-0.0002: return "VERDE","🟢 COMPRAR","#00FF88"
    elif lr<-0.05 or z>1.0: return "ROJO","🔴 NO COMPRAR","#FF3B3B"
    else: return "AMARILLO","🟡 ESPERAR","#FFD60A"

st.markdown(f"# {piloto} | F1 BOT")
col_act,col_btn1,col_btn2=st.columns([2,1,1])
with col_act: symbol=st.selectbox("Activo", ["ETH/USD","BTC/USD","AAPL"], index=0)
with col_btn1:
    if st.button("🏁 ANALIZAR", type="primary", use_container_width=True):
        st.session_state.analizar=True
        st.rerun()
with col_btn2:
    if st.button("🚨 PANICO", use_container_width=True):
        try: client.close_all_positions(cancel_orders=True); st.error("PANICO EJECUTADO")
        except Exception as e: st.error(str(e))

if st.session_state.analizar:
    try:
        ticker="BTC-USD" if symbol=="BTC/USD" else "ETH-USD" if symbol=="ETH/USD" else "AAPL"
        h=yf.Ticker(ticker).history(period="1mo")
        precios=h['Close'].values
        fib=h['High'].max()-(h['High'].max()-h['Low'].min())*0.618
        price=precios[-1]; xb,s,z,lr=calcular_quant(precios)
        estado,texto,color=get_semaforo(price,fib,z,lr)

        st.markdown(f"### {texto} - {symbol} ${price:,.2f}")
        m1,m2,m3,m4=st.columns(4)
        m1.metric(symbol, f"${price:,.2f}", f"Fib ${fib:,.2f}")
        m2.metric("z-score", f"{z:.2f}"); m3.metric("log ret", f"{lr*100:.3f}%")
        m4.markdown(f"<div style='background:{color};color:black;padding:12px;border-radius:10px;text-align:center'><b>{texto}</b></div>", unsafe_allow_html=True)

        fig, ax = plt.subplots(figsize=(11,4.5))
        fig.patch.set_facecolor(bg); ax.set_facecolor(bg)
        ax.plot(precios, color=primary, linewidth=2)
        ax.axhline(fib, color=title_color, linestyle='--')
        ax.axhline(xb, color='cyan', alpha=0.4)
        ax.tick_params(colors='white')
        st.pyplot(fig)

        # ============ TELEGRAM FINAL LIMPIO - SIN THEMA Y SIN VERSION ============
        mensaje_telegram = (
            f"🏁 F1 BOT - {piloto}\n"
            f"📊 Activo: {symbol} ${price:,.2f}\n"
            f"{texto}\n"
            f"Fib 61.8%: ${fib:,.2f}\n"
            f"z-score: {z:.2f}\n"
            f"log-ret: {lr*100:.4f}%\n"
            f"Media: ${xb:,.2f}\n"
            f"Estado: {estado}"
        )
        
        try:
            notificar_f1(mensaje_telegram)
            st.toast(f"📲 Telegram enviado", icon="📡")
        except Exception as e:
            st.warning(f"Telegram error: {e}")

        if estado=="VERDE" and abs(price-st.session_state.last_verde_price)>10:
            try:
                client.submit_order(MarketOrderRequest(symbol=symbol, notional=10, side=OrderSide.BUY, time_in_force=TimeInForce.GTC))
                st.success(f"Orden $10 enviada - {piloto}")
                notificar_f1(f"✅ ORDEN EJECUTADA {symbol} ${price:.2f} - {piloto}")
            except Exception as e: st.error(str(e))
            st.session_state.last_verde_price=price

    except Exception as e: st.error(f"Error: {e}")
