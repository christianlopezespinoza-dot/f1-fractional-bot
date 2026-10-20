import streamlit as st
st.set_page_config(page_title="F1 V25.2 PITS", page_icon="🏁", layout="wide")
import yfinance as yf, math, numpy as np, matplotlib.pyplot as plt
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from bot_telegram import notificar_f1, responder_comandos
from streamlit_autorefresh import st_autorefresh

st_autorefresh(interval=15*60*1000, key="v252")
if "last_update_id" not in st.session_state: st.session_state.last_update_id=0
if "last_verde_price" not in st.session_state: st.session_state.last_verde_price=0
if "perfil_nombre" not in st.session_state: st.session_state.perfil_nombre="Piloto #1"
responder_comandos()

# ============ SIDEBAR - PITS SETTING + PERFIL ============
with st.sidebar:
    st.markdown("## 🏁 F1 BOT")
    
    # PERFIL QUE EL USUARIO ESCRIBE Y GUARDA
    st.markdown("#### 👨‍✈️ PERFIL")
    nombre_input = st.text_input("Nombre Perfil", value=st.session_state.perfil_nombre, label_visibility="collapsed", placeholder="Escribe tu nombre")
    
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        if st.button("💾 Guardar", use_container_width=True):
            st.session_state.perfil_nombre = nombre_input
            st.success(f"Guardado: {nombre_input}")
            st.rerun()
    with col_g2:
        if st.button("🔄 Reset", use_container_width=True):
            st.session_state.perfil_nombre = "Piloto #1"
            st.rerun()
    
    piloto = st.session_state.perfil_nombre
    st.info(f"🏁 Piloto: {piloto}")
    
    st.divider()
    
    # PITS SETTING - CLICK PARA THEMA
    with st.expander("⚙️ PITS SETTING", expanded=False):
        st.caption("Elige tu Livery")
        thema = st.radio("Thema", 
            ["Ferrari Rojo/Negro", "Dorado Negro Premium", "Neon Cyberpunk"],
            index=0,
            label_visibility="collapsed",
            format_func=lambda x: f"🛞 {x}" if "Ferrari" in x else f"🏆 {x}" if "Dorado" in x else f"🌃 {x}"
        )
        st.markdown(f"**Activo:** {thema}")

# Colores por thema
if "Ferrari" in thema:
    primary="#FF0000"; bg="#0A0000"; border1="#FF0000"; border2="#333333"; border3="#FF0000"
    title_color="#FF0000"; glow="0 0 20px #FF0000"
elif "Dorado" in thema:
    primary="#FFD700"; bg="#0A0800"; border1="#FFD700"; border2="#FFD700"; border3="#FFD700"
    title_color="#FFD700"; glow="0 0 25px #FFD700"
else:
    primary="#00FFFF"; bg="#080A14"; border1="#00FFFF"; border2="#FF00FF"; border3="#FF00FF"
    title_color="#00FFFF"; glow="0 0 20px #00FFFF, 0 0 40px #FF00FF"

st.markdown(f"""
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@700&display=swap" rel="stylesheet">
<style>
h1,h2,h3{{font-family:'Orbitron',monospace!important; color:{title_color}!important; text-shadow:{glow}!important}}
.card{{border-radius:14px; padding:14px; border:2px solid; background: rgba(255,255,255,0.06); min-height:230px}}
.card-1{{border-color:{border1}}} .card-2{{border-color:{border2}}} .card-3{{border-color:{border3}}}
.formula{{font-family:Orbitron; font-size:22px; color:{title_color}; text-align:center; text-shadow:{glow}}}
[data-testid="stSidebar"]{{background:{bg}; border-right:2px solid {title_color}}}
</style>
""", unsafe_allow_html=True)

A_KEY=st.secrets["alpaca"]["API_KEY"]
A_SECRET=st.secrets["alpaca"]["SECRET"]
client=TradingClient(A_KEY,A_SECRET,paper=True)

def calcular_quant(precios):
    n=len(precios)
    xb=np.mean(precios)
    s=np.std(precios,ddof=1)
    z=(precios[-1]-xb)/(s/math.sqrt(n)) if s>0 else 0
    lr=math.log(precios[-1]/precios[-2]) if precios[-2]>0 else 0
    return xb,s,z,lr

def get_semaforo(price,fib,z,lr):
    if price<fib and z<-2.0 and -0.008<lr<-0.0002:
        return "VERDE","🟢 COMPRAR","#00FF88"
    elif lr<-0.05 or z>1.0:
        return "ROJO","🔴 NO COMPRAR","#FF3B3B"
    else:
        return "AMARILLO","🟡 ESPERAR","#FFD60A"

def analisis_historico(ticker):
    hist=yf.Ticker(ticker).history(period="1y")
    close=hist['Close'].values
    def ret(n):
        return (close[-1]/close[-n]-1)*100 if len(close)>n else 0
    casos=[]
    for i in range(30,len(close)-7):
        w=close[i-30:i]
        s=np.std(w,ddof=1)
        if s==0:
            continue
        z=(w[-1]-np.mean(w))/(s/math.sqrt(len(w)))
        lr=math.log(close[i]/close[i-1]) if close[i-1]>0 else 0
        if z<-2 and -0.008<lr<-0.0002:
            casos.append((close[i+1]/close[i]-1)*100)
    prob=sum(x>0 for x in casos)/len(casos)*100 if casos else 0
    avg=np.mean(casos) if casos else 0
    return {"24h":ret(2),"7d":ret(6),"30d":ret(21),"vsMax":(close[-1]/hist['High'].max()-1)*100,"max":hist['High'].max(),"prob":prob,"avg":avg,"casos":len(casos)}

st.markdown(f"# {piloto} | {thema}")

col0,col1,col2=st.columns([2,1,1])
with col0:
    symbol=st.selectbox("Activo", ["BTC/USD","AAPL","ETH/USD"])
with col1:
    iniciar=st.button("🏁 ANALIZAR", type="primary", use_container_width=True)
with col2:
    if st.button("🚨 PANICO", use_container_width=True):
        try:
            client.close_all_positions(cancel_orders=True)
            st.error("PANICO - Todo vendido")
        except Exception as e:
            st.error(str(e))

if iniciar:
    ticker="BTC-USD" if symbol=="BTC/USD" else "ETH-USD" if symbol=="ETH/USD" else "AAPL"
    h=yf.Ticker(ticker).history(period="1mo")
    precios=h['Close'].values
    fib=h
