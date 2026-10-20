import streamlit as st
st.set_page_config(page_title="F1 BOT PRO", page_icon="🏁", layout="wide")
import yfinance as yf, math, numpy as np, matplotlib.pyplot as plt
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from bot_telegram import notificar_f1, responder_comandos
from streamlit_autorefresh import st_autorefresh

st_autorefresh(interval=15*60*1000, key="f1pro")
if "last_update_id" not in st.session_state: st.session_state.last_update_id=0
if "last_verde_price" not in st.session_state: st.session_state.last_verde_price=0
if "perfil_nombre" not in st.session_state: st.session_state.perfil_nombre="ChristianLE"
if "analizar" not in st.session_state: st.session_state.analizar=False
responder_comandos()

primary="#FF0000"; bg="#0A0000"; title_color="#FF0000"; glow="0 0 20px #FF0000"

with st.sidebar:
    st.markdown("## 🏁 F1 BOT PRO")
    st.markdown("#### PILOTO")
    nombre_input = st.text_input("Nombre", value=st.session_state.perfil_nombre, label_visibility="collapsed")
    c1,c2=st.columns(2)
    with c1:
        if st.button("Guardar", use_container_width=True):
            st.session_state.perfil_nombre=nombre_input
            st.rerun()
    with c2:
        if st.button("Reset", use_container_width=True):
            st.session_state.perfil_nombre="Piloto #1"
            st.rerun()
    piloto=st.session_state.perfil_nombre
    st.info(f"Piloto: {piloto}")

st.markdown(f"<style>h1{{color:{title_color}!important; text-shadow:{glow}!important}} [data-testid='stSidebar']{{background:{bg}; border-right:2px solid {title_color}}}</style>", unsafe_allow_html=True)

A_KEY=st.secrets["alpaca"]["API_KEY"]
A_SECRET=st.secrets["alpaca"]["SECRET"]
client=TradingClient(A_KEY,A_SECRET,paper=True)

def calcular_baldor_pro(precios, high, low):
    n=len(precios)
    xb=np.mean(precios)
    s=np.std(precios,ddof=1)
    z=(precios[-1]-xb)/(s/math.sqrt(n)) if s>0 else 0
    lr=math.log(precios[-1]/precios[-2]) if precios[-2]>0 else 0
    fib=high-(high-low)*0.618
    atr=np.mean([abs(precios[i]-precios[i-1]) for i in range(1,len(precios))])
    risk_2pct=10000*0.02
    pos_size=risk_2pct/atr if atr>0 else 0
    tp=xb+2*s
    sl=xb-s
    rr=(tp-precios[-1])/(precios[-1]-sl) if (precios[-1]-sl)!=0 else 0
    win_rate=len([x for x in precios if x>xb])/n
    return xb,s,z,lr,fib,atr,pos_size,rr,win_rate,tp,sl

def get_semaforo(price,fib,z,lr,rr):
    if price<fib and z<-2.0 and -0.008<lr<-0.0002 and rr>=1.5:
        return "VERDE","COMPRAR","#00FF88"
    elif lr<-0.05 or z>1.0 or rr<0:
        return "ROJO","NO COMPRAR","#FF3B3B"
    else:
        return "AMARILLO","ESPERAR","#FFD60A"

st.markdown(f"# {piloto} | F1 BOT PRO Baldor")

col_act,col_btn1,col_btn2=st.columns([2,1,1])
with col_act:
    symbol=st.selectbox("Activo", ["ETH/USD","BTC/USD","AAPL","SOL/USD"], index=0)
with col_btn1:
    if st.button("ANALIZAR", type="primary", use_container_width=True):
        st.session_state.analizar=True
        st.rerun()
with col_btn2:
    if st.button("PANICO", use_container_width=True):
        try:
            client.close_all_positions(cancel_orders=True)
            st.error("PANICO EJECUTADO")
        except Exception as e:
            st.error(str(e))

if st.session_state.analizar:
    try:
        mapa={"ETH/USD":"ETH-USD","BTC/USD":"BTC-USD","AAPL":"AAPL","SOL/USD":"SOL-USD"}
        ticker=mapa[symbol]
        h=yf.Ticker(ticker).history(period="1mo")
        if len(h)<20:
            st.warning("Pocos datos")
            st.stop()
        precios=h['Close'].values
        high=h['High'].max()
        low=h['Low'].min()
        price=precios[-1]
        xb,s,z,lr,fib,atr,pos_size,rr,win_rate,tp,sl=calcular_baldor_pro(precios,high,low)
        estado,texto,color=get_semaforo(price,fib,z,lr,rr)
        st.markdown(f"### {texto} - {symbol} ${price:,.2f}")
        c1,c2,c3=st.columns(3)
        with c1:
            st.markdown("**1. TREND MOMENTUM**")
            st.metric("z-score", f"{z:.2f}")
            st.metric("log-ret", f"{lr*100:.4f}%")
        with c2:
            st.markdown("**2. RISK MGMT**")
            st.metric("ATR", f"${atr:.2f}")
            st.metric("Pos Size", f"{pos_size:.1f}")
        with c3:
            st.markdown("**3. ORDER FLOW**")
            st.metric("Fib 61.8%", f"${fib:,.2f}")
            st.metric("Dist Fib", f"{((price/fib)-1)*100:+.2f}%")
        c4,c5,c6=st.columns(3)
        with c4:
            st.markdown("**4. VOLATILITY**")
            st.metric("sigma", f"${s:.2f}")
        with c5:
            st.markdown("**5. ENTRY VS EXIT**")
            st.metric("R:R", f"{rr:.2f}:1")
            st.caption(f"TP ${tp:.2f} SL ${sl:.2f}")
        with c6:
            st.markdown("**6. P&L**")
            st.metric("WinRate", f"{win_rate*100:.1f}%")
            st.metric("Media", f"${xb:.2f}")
        st.markdown(f"<div style='background:{color};color:black;padding:14px;border-radius:10px;text-align:center;font-size:18px'><b>{texto} - {estado}</b></div>", unsafe_allow_html=True)
        fig, ax = plt.subplots(figsize=(12,4))
        fig.patch.set_facecolor(bg)
        ax.set_facecolor(bg)
        ax.plot(precios, color=primary, linewidth=2, label='Price')
        ax.axhline(fib, color='yellow', linestyle='--', label='Fib 61.8%')
        ax.axhline(xb, color='cyan', alpha=0.5, label='Media Baldor')
        ax.axhline(tp, color='#00FF88', linestyle=':', alpha=0.6, label='TP')
        ax.axhline(sl, color='#FF3B3B', linestyle=':', alpha=0.6, label='SL')
        ax.legend(facecolor=bg, labelcolor='white')
        ax.tick_params(colors='white')
        st.pyplot(fig)
        mensaje_telegram = (
            f"🏁 F1 BOT PRO - {piloto}\n"
            f"Activo: {symbol} ${price:,.2f}\n"
            f"{texto} | Estado: {estado}\n"
            f"1.Momentum z {z:.2f} lr {lr*100:.3f}%\n"
            f"2.Risk ATR ${atr:.2f} Pos {pos_size:.1f}\n"
            f"3.Flow Fib ${fib:,.2f}\n"
            f"4.Vol sigma ${s:.2f}\n"
            f"5.R:R {rr:.2f}:1 TP ${tp:.2f} SL ${sl:.2f}\n"
            f"6.P&L Media ${xb:.2f} WR {win_rate*100:.0f}%"
        )
        try:
            notificar_f1(mensaje_telegram)
            st.toast("Telegram PRO enviado", icon="🏁")
        except Exception as e:
            st.warning(f"Telegram error: {e}")
        if estado=="VERDE" and abs(price-st.session_state.last_verde_price)>10:
            try:
                client.submit_order(MarketOrderRequest(symbol=symbol, notional=10, side=OrderSide.BUY, time_in_force=TimeInForce.GTC))
                st.success(f"Orden $10 enviada - {piloto}")
                notificar_f1(f"ORDEN {symbol} ${price:.2f} - {piloto} R:R {rr:.2f}")
            except Exception as e:
                st.error(str(e))
            st.session_state.last_verde_price=price
    except Exception as e:
        st.error(f"Error PRO: {e}")
