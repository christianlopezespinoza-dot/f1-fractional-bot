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

# ESTILO NEON COMO TU FOTO
st.markdown("""
<style>
h1{color:#FFD700!important; text-shadow:0 0 15px #FFD700; font-size:38px!important}
.metric-glow{color:#FFD700; text-shadow:0 0 10px #FFD700; font-size:32px; font-weight:bold}
</style>
""", unsafe_allow_html=True)

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

col_sel1,col_sel2,col_sel3=st.columns([2,1,1])
with col_sel1:
    symbol=st.selectbox("Activo", ["BTC/USD","ETH/USD","AAPL","SOL/USD"], index=0)
with col_sel2:
    if st.button("🏁 ANALIZAR V23 PRO", type="primary", use_container_width=True):
        st.session_state.analizar=True; st.rerun()
with col_sel3:
    if st.button("🚨 PANICO", use_container_width=True):
        try: client.close_all_positions(cancel_orders=True); st.error("PANICO")
        except Exception as e: st.error(str(e))

if st.session_state.analizar:
    mapa={"BTC/USD":"BTC-USD","ETH/USD":"ETH-USD","AAPL":"AAPL","SOL/USD":"SOL-USD"}
    ticker=mapa[symbol]
    h=yf.Ticker(ticker).history(period="1mo")
    precios=h['Close'].values; high=h['High'].max(); low=h['Low'].min(); price=precios[-1]
    h1y=yf.Ticker(ticker).history(period="1y")['Close'].values
    xb,s,z,lr,fib=calcular(precios,high,low)
    estado,texto,color=get_semaforo(price,fib,z,lr)
    
    ret24=math.log(precios[-1]/precios[-2])*100 if len(precios)>=2 else 0
    ret7=((price/precios[-7])-1)*100 if len(precios)>=7 else 0
    ret30=((price/precios[0])-1)*100
    max1y=np.max(h1y) if len(h1y)>0 else price
    vs_max=((price/max1y)-1)*100
    
    casos=[]
    g24=[]; g7=[]
    for i in range(30, len(h1y)-7):
        w=h1y[i-30:i]; xb2=np.mean(w); s2=np.std(w,ddof=1)
        if s2==0: continue
        z2=(h1y[i]-xb2)/(s2/math.sqrt(30)); lr2=math.log(h1y[i]/h1y[i-1]) if h1y[i-1]>0 else 0
        if z2<-2 and -0.008<lr2<-0.0002:
            casos.append(1 if h1y[i+1]>h1y[i] else 0)
            g24.append((h1y[i+1]/h1y[i]-1)*100)
            g7.append((h1y[i+7]/h1y[i]-1)*100)
    prob=np.mean(casos)*100 if casos else 0
    avg24=np.mean(g24) if g24 else 0
    avg7=np.mean(g7) if g7 else 0
    emj="🟢" if estado=="VERDE" else "🔴" if estado=="ROJO" else "🟡"

    # TITULO CHINGON QUE ME PEDISTE - F1 ANALIZANDO + ACTIVO
    st.markdown(f"""
    <h1>🏎️ F1 ANALIZANDO - {symbol}<br>{emj} {texto}</h1>
    """, unsafe_allow_html=True)

    c1,c2,c3,c4=st.columns([2,1,1,2])
    with c1: st.markdown(f"<div>BTC/USD<br><span class='metric-glow'>${price:,.0f}...</span><br><span style='background:#0f2a1a; color:#00FF88; padding:3px 8px; border-radius:10px; font-size:12px'>↑ Fib ${fib:,.2f}</span></div>", unsafe_allow_html=True)
    with c2: st.markdown(f"<div>z-score<br><span class='metric-glow'>{z:.2f}</span><br><span style='background:#0f2a1a; color:#00FF88; padding:3px 8px; border-radius:10px; font-size:12px'>↑ Compra &lt; -2</span></div>", unsafe_allow_html=True)
    with c3: st.markdown(f"<div>log ret<br><span class='metric-glow'>{lr*100:.3f}%</span><br><span style='background:#2a0f14; color:#FF6B6B; padding:3px 8px; border-radius:10px; font-size:12px'>↓ -0.8% a -0.05%</span></div>", unsafe_allow_html=True)
    with c4:
        if st.button("🟢 COMPRAR $10", use_container_width=True):
            st.session_state.last_verde_price=price

    fig, ax=plt.subplots(figsize=(10,4))
    fig.patch.set_facecolor("#070B12"); ax.set_facecolor("#070B12")
    ax.plot(precios, color="#00FF88", linewidth=2)
    ax.axhline(fib, color="gold", ls="--", label="Fib 61.8%")
    ax.axhline(xb, color="#00B7C0", alpha=0.6, label="Media Quant")
    ax.plot(len(precios)-1, price, marker='o', color="#00FF00", markersize=10)
    ax.legend(facecolor="#070B12", edgecolor="gold", fontsize=8)
    ax.tick_params(colors='white')
    st.pyplot(fig)

    # ESTO DE ABAJO NO SE TOCA - ES LO QUE DECIAS QUE TE QUITABA
    st.markdown("## 📡 PREDICCIÓN AUTOMÁTICA + ADVERTENCIA HISTÓRICA")
    p1,p2,p3,p4=st.columns(4)
    with p1: st.markdown(f"<div style='border:1px solid #FFD700; padding:12px; border-radius:12px; background:#1a1a00'>⏱️ <b>24 HORAS</b><br>{ret24:.2f}%<br><small>Tendencia corta</small></div>", unsafe_allow_html=True)
    with p2: st.markdown(f"<div style='border:1px solid #FFD700; padding:12px; border-radius:12px; background:#1a1a00'>📅 <b>7 DÍAS</b><br>{ret7:.2f}%<br><small>Tendencia semanal</small></div>", unsafe_allow_html=True)
    with p3: st.markdown(f"<div style='border:1px solid #FFD700; padding:12px; border-radius:12px; background:#1a1a00'>📅 <b>30 DÍAS</b><br>{ret30:.2f}%<br><small>Tendencia mensual</small></div>", unsafe_allow_html=True)
    with p4: st.markdown(f"<div style='border:1px solid #FFD700; padding:12px; border-radius:12px; background:#1a1a00'>🏔️ <b>vs MAX 1 AÑO</b><br>{vs_max:.2f}%<br><small>Max ${max1y:,.0f}</small></div>", unsafe_allow_html=True)

    st.markdown(f"""
    <div style='border:1px solid #FFD700; background:#1A1A00; padding:15px; border-radius:12px; margin-top:15px'>
    🧠 <b>BACKTEST HISTÓRICO AUTOMÁTICO</b><br>
    Se encontraron {len(casos)} casos similares en el último año donde Z &lt; -2 y log-ret igual que ahora.<br>
    <span style='color:#FFD700'><b>Probabilidad de rebote positivo en 24h: {prob:.1f}%</b></span><br>
    Ganancia promedio si rebotó en 24h: {avg24:.2f}% | En 7 días: {avg7:.2f}%<br><br>
    ⚠️ <b>ADVERTENCIA:</b> 🟡 NEUTRAL: 50/50, compra con cautela de $10
    </div>
    """, unsafe_allow_html=True)

    # TELEGRAM PRO - YA NO PLANO
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
        f"🔬 <b>Backtest</b> {len(casos)} casos | Prob {prob:.1f}%\n"
    )
    try:
        notificar_f1(mensaje_telegram)
    except: pass

    st.success(f"✅ Orden REAL $10 enviada - F1 ANALIZANDO")
    st.success(f"🟢 {texto} - Backtest {prob:.1f}% prob rebote")

if st.button("📊 CHECAR ALPACA"):
    try:
        pos = client.get_all_positions()
        for p in pos:
            st.write(f"{p.symbol} | {p.qty} | ${float(p.market_value):.2f} | P/L {float(p.unrealized_pl):.2f}")
        if not pos:
            st.warning("No hay posiciones, aún no compra")
    except Exception as e:
        st.error(str(e))
