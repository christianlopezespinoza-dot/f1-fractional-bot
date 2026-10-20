import streamlit as st
st.set_page_config(page_title="F1 V25.3 FIX", page_icon="🏁", layout="wide")
import yfinance as yf, math, numpy as np, matplotlib.pyplot as plt
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from bot_telegram import notificar_f1, responder_comandos
from streamlit_autorefresh import st_autorefresh

st_autorefresh(interval=15*60*1000, key="v253")
if "last_update_id" not in st.session_state: st.session_state.last_update_id=0
if "last_verde_price" not in st.session_state: st.session_state.last_verde_price=0
if "perfil_nombre" not in st.session_state: st.session_state.perfil_nombre="ChristianLE"
if "thema" not in st.session_state: st.session_state.thema="Ferrari Rojo/Negro"
if "analizar" not in st.session_state: st.session_state.analizar=False
responder_comandos()

with st.sidebar:
    st.markdown("## 🏁 F1 BOT")
    st.markdown("#### 👨‍✈️ PERFIL")
    nombre_input = st.text_input("Nombre", value=st.session_state.perfil_nombre, label_visibility="collapsed")
    c1,c2=st.columns(2)
    with c1:
        if st.button("💾 Gu...", use_container_width=True):
            st.session_state.perfil_nombre=nombre_input
            st.rerun()
    with c2:
        if st.button("🔄 Reset", use_container_width=True):
            st.session_state.perfil_nombre="Piloto #1"
            st.rerun()
    piloto=st.session_state.perfil_nombre
    st.info(f"🏁 Piloto: {piloto}")
    st.divider()
    with st.expander("⚙️ PITS SETTING", expanded=True):
        st.caption("Elige tu Livery")
        thema_sel = st.radio("Thema", ["Ferrari Rojo/Negro","Dorado Negro Premium","Neon Cyberpunk"], 
            index=["Ferrari Rojo/Negro","Dorado Negro Premium","Neon Cyberpunk"].index(st.session_state.thema),
            label_visibility="collapsed")
        if thema_sel!=st.session_state.thema:
            st.session_state.thema=thema_sel
            st.rerun()
        st.markdown(f"**Activo:** {st.session_state.thema}")

thema=st.session_state.thema

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
<style>
h1{{font-family:Orbitron,monospace!important; color:{title_color}!important; text-shadow:{glow}!important; font-size:32px}}
.card{{border-radius:14px; padding:14px; border:2px solid; background: rgba(255,255,255,0.06); min-height:180px}}
.card-1{{border-color:{border1}}} .card-2{{border-color:{border2}}}
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

st.markdown(f"# {piloto} | {thema}")
col_act,col_btn1,col_btn2=st.columns([2,1,1])
with col_act:
    symbol=st.selectbox("Activo", ["ETH/USD","BTC/USD","AAPL"], index=0)
with col_btn1:
    if st.button("🏁 ANALIZAR", type="primary", use_container_width=True):
        st.session_state.analizar=True
        st.rerun()
with col_btn2:
    if st.button("🚨 PANICO", use_container_width=True):
        try: client.close_all_positions(cancel_orders=True); st.error("PANICO")
        except Exception as e: st.error(str(e))

if st.session_state.analizar:
    try:
        ticker="BTC-USD" if symbol=="BTC/USD" else "ETH-USD" if symbol=="ETH/USD" else "AAPL"
        st.write(f"Analizando {ticker}...")
        h=yf.Ticker(ticker).history(period="1mo")
        if len(h)==0:
            st.error("yfinance no regresó datos, intenta de nuevo")
            st.stop()
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
        ax.plot(precios, color=primary, linewidth=2, label='Precio')
        ax.axhline(fib, color=title_color, linestyle='--', label='Fib 61.8%')
        ax.axhline(xb, color='cyan', alpha=0.4, label='Media')
        if estado=="VERDE": ax.scatter(len(precios)-1, price, color='lime', s=150, edgecolors='white', zorder=5)
        ax.legend(facecolor=bg, edgecolor=title_color, labelcolor="white")
        ax.tick_params(colors='white')
        st.pyplot(fig)

        st.markdown(f"### THE PHYSICS - {thema}")
        r1c1,r1c2,r1c3=st.columns(3)
        with r1c1: st.markdown(f"<div class='card card-1'><b>DOWNFORCE</b><br>z={z:.2f}</div>", unsafe_allow_html=True)
        with r1c2: st.markdown(f"<div class='card card-2'><b>GRIP</b><br>Fib ${fib:,.0f}</div>", unsafe_allow_html=True)
        with r1c3: st.markdown(f"<div class='card card-3'><b>CORNERING</b><br>Volatilidad</div>", unsafe_allow_html=True)

        if estado=="VERDE":
            notificar_f1(f"V25.3 {thema} {piloto} VERDE {symbol} ${price:.2f}")
            try:
                client.submit_order(MarketOrderRequest(symbol=symbol, notional=10, side=OrderSide.BUY, time_in_force=TimeInForce.GTC))
                st.success(f"Orden $10 enviada - {piloto}")
            except Exception as e: st.error(str(e))

    except Exception as e:
        st.error(f"Error analizando: {e}")
