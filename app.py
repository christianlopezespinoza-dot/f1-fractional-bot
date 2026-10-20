import streamlit as st
st.set_page_config(page_title="F1 ANALIZANDO", page_icon="🏁", layout="wide")
import yfinance as yf, math, numpy as np, matplotlib.pyplot as plt
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from bot_telegram import notificar_f1, responder_comandos
from streamlit_autorefresh import st_autorefresh

st_autorefresh(interval=15*60*1000, key="f1")
if "last_update_id" not in st.session_state: st.session_state.last_update_id=0
if "last_verde_price" not in st.session_state: st.session_state.last_verde_price=0
if "perfil_nombre" not in st.session_state: st.session_state.perfil_nombre="ChristianLE"
if "analizar" not in st.session_state: st.session_state.analizar=False
responder_comandos()

primary="#FFD700"; bg="#070B12"

st.markdown(f"<style>h1{{color:#FFD700!important; text-shadow:0 0 15px #FFD700}} [data-testid='stSidebar']{{background:{bg}}}</style>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## 🏁 F1 BOT")
    nombre_input = st.text_input("Piloto", value=st.session_state.perfil_nombre)
    if st.button("Guardar"): 
        st.session_state.perfil_nombre=nombre_input
        st.rerun()
    piloto=st.session_state.perfil_nombre

A_KEY=st.secrets["alpaca"]["API_KEY"]
A_SECRET=st.secrets["alpaca"]["SECRET"]
client=TradingClient(A_KEY,A_SECRET,paper=True)

def calcular(precios, high, low):
    n=len(precios); xb=np.mean(precios); s=np.std(precios,ddof=1)
    z=(precios[-1]-xb)/(s/math.sqrt(n)) if s>0 else 0
    lr=math.log(precios[-1]/precios[-2]) if precios[-2]>0 else 0
    fib=high-(high-low)*0.618
    return xb,s,z,lr,fib

def get_semaforo(price,fib,z,lr):
    if price<fib and z<-2.0 and -0.008<lr<-0.0002: return "VERDE","COMPRAR $10","#00FF88"
    elif lr<-0.05 or z>1.0: return "ROJO","NO COMPRAR","#FF3B3B"
    else: return "AMARILLO","ESPERAR","#FFD60A"

def historico(ticker, precios):
    h1y=yf.Ticker(ticker).history(period="1y")['Close'].values
    price=precios[-1]
    ret24=math.log(precios[-1]/precios[-2])*100 if len(precios)>=2 else 0
    ret7=((price/precios[-7])-1)*100 if len(precios)>=7 else 0
    ret30=((price/precios[0])-1)*100
    max1y=np.max(h1y) if len(h1y)>0 else price
    # backtest
    casos=[]
    for i in range(30, len(h1y)-7):
        w=h1y[i-30:i]; xb=np.mean(w); s=np.std(w,ddof=1)
        if s==0: continue
        z=(h1y[i]-xb)/(s/math.sqrt(30)); lr=math.log(h1y[i]/h1y[i-1]) if h1y[i-1]>0 else 0
        if z<-2 and -0.008<lr<-0.0002:
            casos.append(1 if h1y[i+1]>h1y[i] else 0)
    prob=np.mean(casos)*100 if casos else 0
    return ret24,ret7,ret30,len(casos),prob

st.markdown(f"# 🏁 F1 ANALIZANDO - {piloto}")
col1,col2,col3=st.columns([2,1,1])
with col1: symbol=st.selectbox("Activo", ["BTC/USD","ETH/USD","AAPL","SOL/USD"], index=0)
with col2:
    if st.button("🏁 ANALIZAR", type="primary", use_container_width=True):
        st.session_state.analizar=True; st.rerun()
with col3:
    if st.button("PANICO", use_container_width=True):
        try: client.close_all_positions(cancel_orders=True); st.error("PANICO")
        except Exception as e: st.error(str(e))

if st.session_state.analizar:
    mapa={"BTC/USD":"BTC-USD","ETH/USD":"ETH-USD","AAPL":"AAPL","SOL/USD":"SOL-USD"}
    ticker=mapa[symbol]
    h=yf.Ticker(ticker).history(period="1mo")
    precios=h['Close'].values; high=h['High'].max(); low=h['Low'].min(); price=precios[-1]
    xb,s,z,lr,fib=calcular(precios,high,low)
    estado,texto,color=get_semaforo(price,fib,z,lr)
    ret24,ret7,ret30,ncasos,prob=historico(ticker, precios)
    emj="🟢" if estado=="VERDE" else "🔴" if estado=="ROJO" else "🟡"

    st.markdown(f"### {emj} {texto} - {symbol} ${price:,.2f}")
    c1,c2,c3=st.columns(3)
    with c1: st.metric("z-score", f"{z:.2f}")
    with c2: st.metric("log-ret", f"{lr*100:.4f}%")
    with c3: st.metric("Fib 61.8%", f"${fib:,.2f}")

    fig, ax=plt.subplots(figsize=(10,4))
    fig.patch.set_facecolor(bg); ax.set_facecolor(bg)
    ax.plot(precios, color=primary); ax.axhline(fib, color="gold", ls="--"); ax.axhline(xb, color="cyan", alpha=0.5)
    st.pyplot(fig)

    # MENSAJE PRO - EL QUE SI LLEGA
    mensaje_telegram = (
        f"<b>🏁 F1 BOT - {piloto}</b>\n"
        f"━━━━━━━━━━━━━━\n"
        f"📊 <b>{symbol}</b>  ${price:,.2f}\n"
        f"{emj} <b>{texto}</b>\n"
        f"━━━━━━━━━━━━━━\n"
        f"📐 <b>Fib 61.8%:</b> ${fib:,.2f}\n"
        f"📈 <b>z-score:</b> {z:.2f}\n"
        f"📉 <b>log-ret:</b> {lr*100:.4f}%\n"
        f"🧠 <b>Media:</b> ${xb:,.2f}\n"
        f"━━━━━━━━━━━━━━\n"
        f"⏱ <b>24h</b> {ret24:+.2f}% | <b>7d</b> {ret7:+.2f}% | <b>30d</b> {ret30:+.2f}%\n"
        f"🔬 <b>Backtest</b> {ncasos} casos | Prob {prob:.1f}%\n"
    )
    
    try:
        notificar_f1(mensaje_telegram)
        st.toast("Telegram PRO enviado")
    except Exception as e:
        st.warning(str(e))

    if estado=="VERDE" and abs(price-st.session_state.last_verde_price)>10:
        try:
            client.submit_order(MarketOrderRequest(symbol=symbol, notional=10, side=OrderSide.BUY, time_in_force=TimeInForce.GTC))
            st.success("Orden $10 enviada")
            st.session_state.last_verde_price=price
        except Exception as e:
            st.error(str(e))
