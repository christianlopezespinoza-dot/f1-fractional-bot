import streamlit as st
st.set_page_config(page_title="F1 BOT PRO", page_icon="🏁", layout="wide")
import yfinance as yf, math, numpy as np, matplotlib.pyplot as plt
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from bot_telegram import notificar_f1, responder_comandos
from streamlit_autorefresh import st_autorefresh

# ============ CONFIG ============
st_autorefresh(interval=15*60*1000, key="f1pro")
if "last_update_id" not in st.session_state: st.session_state.last_update_id=0
if "last_verde_price" not in st.session_state: st.session_state.last_verde_price=0
if "perfil_nombre" not in st.session_state: st.session_state.perfil_nombre="ChristianLE"
if "analizar" not in st.session_state: st.session_state.analizar=False
responder_comandos()

primary="#FF0000"; bg="#0A0000"; title_color="#FF0000"; glow="0 0 20px #FF0000"

# ============ SIDEBAR PERFIL ============
with st.sidebar:
    st.markdown("## 🏁 F1 BOT PRO")
    st.markdown("#### 👨‍✈️ PILOTO")
    nombre_input = st.text_input("Nombre", value=st.session_state.perfil_nombre, label_visibility="collapsed")
    c1,c2=st.columns(2)
    with c1:
        if st.button("💾 Guardar", use_container_width=True):
            st.session_state.perfil_nombre=nombre_input; st.rerun()
    with c2:
        if st.button("🔄 Reset", use_container_width=True):
            st.session_state.perfil_nombre="Piloto #1"; st.rerun()
    piloto=st.session_state.perfil_nombre
    st.info(f"🏁 {piloto}")

st.markdown(f"""<style>
h1{{color:{title_color}!important; text-shadow:{glow}!important}}
[data-testid="stSidebar"]{{background:{bg}; border-right:2px solid {title_color}}}
</style>""", unsafe_allow_html=True)

A_KEY=st.secrets["alpaca"]["API_KEY"]; A_SECRET=st.secrets["alpaca"]["SECRET"]
client=TradingClient(A_KEY,A_SECRET,paper=True)

# ============ FUNCIONES BALDOR + FISICA F1 ============
def calcular_baldor_pro(precios, high, low):
    """
    BALDOR PRO - 6 Principios Física Trading
    """
    n=len(precios)
    # 1. MEDIA - Baldor Cap. Suma
    xb=np.mean(precios)
    # 2. VOLATILIDAD - Baldor (a-b)² + √
    s=np.std(precios,ddof=1)
    # 3. Z-SCORE - Baldor Fracción + Raíz
    z=(precios[-1]-xb)/(s/math.sqrt(n)) if s>0 else 0
    # 4. LOG-RET - Baldor Log Cap.42
    lr=math.log(precios[-1]/precios[-2]) if precios[-2]>0 else 0
    # 5. FIB 61.8% - Baldor Porcentaje Aureo
    fib=high-(high-low)*0.618
    # 6. ATR simplificado - Volatilidad
    atr=np.mean([abs(precios[i]-precios[i-1]) for i in range(1,len(precios))])
    
    # RISK: 2% rule Baldor: R = Capital*0.02
    risk_2pct = 10000*0.02  # ejemplo sobre 10k
    pos_size = risk_2pct / atr if atr>0 else 0
    
    # R:R Entry vs Exit Baldor: (TP-Entry)/(Entry-SL)
    tp = xb + 2*s
    sl = xb - s
    rr = (tp-precios[-1])/(precios[-1]-sl) if (precios[-1]-sl)!=0 else 0
    
    # P&L Expectancy Baldor: Σ
    win_rate = len([x for x in precios if x>xb])/n
    
    return xb,s,z,lr,fib,atr,pos_size,rr,win_rate,tp,sl

def get_semaforo(price,fib,z,lr,rr):
    if price<fib and z<-2.0 and -0.008<lr<-0.0002 and rr>=1.5:
        return "VERDE","🟢 COMPRAR","#00FF88"
    elif lr<-0.05 or z>1.0 or rr<0:
        return "ROJO","🔴 NO COMPRAR","#FF3B3B"
    else:
        return "AMARILLO","🟡 ESPERAR","#FFD60A"

# ============ UI PRINCIPAL ============
st.markdown(f"# {piloto} | F1 BOT PRO - Baldor Physics")

col_act,col_btn1,col_btn2=st.columns([2,1,1])
with col_act: symbol=st.selectbox("Activo", ["ETH/USD","BTC/USD","AAPL","SOL/USD"], index=0)
with col_btn1:
    if st.button("🏁 ANALIZAR", type="primary", use_container_width=True):
        st.session_state.analizar=True; st.rerun()
with col_btn2:
    if st.button("🚨 PANICO", use_container_width=True):
        try: client.close_all_positions(cancel_orders=True); st.error("PANICO EJECUTADO")
        except Exception as e: st.error(str(e))

if st.session_state.analizar:
    try:
        ticker={"ETH/USD":"ETH-USD","BTC/USD":"BTC-USD","AAPL":"AAPL","SOL/USD":"SOL-USD"}[symbol]
        h=yf.Ticker(ticker).history(period="1mo")
        if len(h)<20: st.warning("Pocos datos"); st.stop()
        precios=h['Close'].values; high=h['High'].max(); low=h['Low'].min()
        price=precios[-1]
        
        xb,s,z,lr,fib,atr,pos_size,rr,win_rate,tp,sl = calcular_baldor_pro(precios,high,low)
        estado,texto,color=get_semaforo(price,fib,z,lr,rr)

        st.markdown(f"### {texto} - {symbol} ${price:,.2f}")

        # ============ 6 PANELES PRO ============
        c1,c2,c3=st.columns(3)
        with c1:
            st.markdown("**1. TREND MOMENTUM** `D≈ΔpA`")
            st.metric("z-score", f"{z:.2f}", f"log-ret
