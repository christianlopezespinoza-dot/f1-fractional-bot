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

primary="#FF0000"; bg="#0A0000"; title_color="#FF0000"; glow="0 0 20px #FF0000"

with st.sidebar:
    st.markdown("## 🏁 F1 BOT")
    st.markdown("#### 👨‍✈️ PERFIL")
    nombre_input = st.text_input("Nombre", value=st.session_state.perfil_nombre, label_visibility="collapsed")
    c1,c2=st.columns(2)
    with c1:
        if st.button("💾 Guardar", use_container_width=True):
            st.session_state.perfil_nombre=nombre_input; st.rerun()
    with c2:
        if st.button("🔄 Reset", use_container_width=True):
            st.session_state.perfil_nombre="Piloto #1"; st.rerun()
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

def analisis_periodo(ticker, periodo, nombre):
    h=yf.Ticker(ticker).history(period=periodo)
    if len(h)<5: return None
    precios=h['Close'].values
    fib=h['High'].max()-(h['High'].max()-h['Low'].min())*0.618
    price=precios[-1]; xb,s,z,lr=calcular_quant(precios)
    estado,texto,color=get_semaforo(price,fib,z,lr)
    variacion = ((precios[-1]/precios[0])-1)*100
    return {"nombre":nombre, "price":price, "fib":fib, "xb":xb, "z":z, "lr":lr, "estado":estado, "texto":texto, "color":color, "var":variacion, "precios":precios}

st.markdown(f"# {piloto} | F1 BOT V25")
col_act,col_btn1,col_btn2=st.columns([2,1,1])
with col_act: symbol=st.selectbox("Activo", ["ETH/USD","BTC/USD","AAPL"], index=0)
with col_btn1:
    if st.button("🏁 ANALIZAR", type="primary", use_container_width=True):
        st.session_state.analizar=True; st.rerun()
with col_btn2:
    if st.button("🚨 PANICO", use_container_width=True):
        try: client.close_all_positions(cancel_orders=True); st.error("PANICO EJECUTADO")
        except Exception as e: st.error(str(e))

if st.session_state.analizar:
    ticker="BTC-USD" if symbol=="BTC/USD" else "ETH-USD" if symbol=="ETH/USD" else "AAPL"
    
    # ============ ANALISIS MULTI-TEMPORALIDAD ============
    tab1, tab2, tab3, tab4 = st.tabs(["📅 DÍA", "📆 SEMANA", "🗓️ MES", "📈 AÑO"])
    
    periodos = [("1d","DÍA"), ("5d","SEMANA"), ("1mo","MES"), ("1y","AÑO")]
    resultados = []
    
    for per,nom in periodos:
        try:
            r=analisis_periodo(ticker, per, nom)
            if r: resultados.append(r)
        except: pass

    for i, (per,nom) in enumerate(periodos):
        with [tab1,tab2,tab3,tab4][i]:
            if i < len(resultados):
                r=resultados[i]
                st.markdown(f"### {r['texto']} - {symbol} ${r['price']:,.2f}")
                c1,c2,c3,c4=st.columns(4)
                c1.metric(f"Var {nom}", f"{r['var']:+.2f}%")
                c2.metric("Fib 61.8%", f"${r['fib']:,.2f}")
                c3.metric("z-score", f"{r['z']:.2f}")
                c4.markdown(f"<div style='background:{r['color']};color:black;padding:10px;border-radius:8px;text-align:center'><b>{r['estado']}</b></div>", unsafe_allow_html=True)
                
                fig, ax = plt.subplots(figsize=(11,3.5))
                fig.patch.set_facecolor(bg); ax.set_facecolor(bg)
                ax.plot(r['precios'], color=primary, linewidth=2)
                ax.axhline(r['fib'], color=title_color, linestyle='--', alpha=0.7)
                ax.axhline(r['xb'], color='cyan', alpha=0.4)
                ax.tick_params(colors='white')
                st.pyplot(fig)

    # ============ ANALISIS PRINCIPAL PARA TELEGRAM ============
    if resultados:
        r_main = resultados[2] # MES como principal
        price=r_main['price']; fib=r_main['fib']; xb=r_main['xb']; z=r_main['z']; lr=r_main['lr']; estado=r_main['estado']; texto=r_main['texto']

        st.divider()
        st.markdown(f"### RESUMEN: {texto}")

        # TELEGRAM LIMPIO SIN THEMA NI VERSION
        mensaje_telegram = (
            f"🏁 F1 BOT - {piloto}\n"
            f"📊 Activo: {symbol} ${price:,.2f}\n"
            f"{texto}\n"
            f"Fib 61.8%: ${fib:,.2f}\n"
            f"z-score: {z:.2f}\n"
            f"log-ret: {lr*100:.4f}%\n"
            f"Media: ${xb:,.2f}\n"
            f"Estado: {estado}\n"
            f"Día {resultados[0]['var']:+.1f}% | Semana {resultados[1]['var']:+.1f}% | Mes {resultados[2]['var']:+.1f}%"
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
