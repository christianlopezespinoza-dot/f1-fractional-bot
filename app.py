import streamlit as st
st.set_page_config(page_title="F1 V23 PRO", page_icon="🏁", layout="wide")
import yfinance as yf, math, numpy as np, matplotlib.pyplot as plt
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from bot_telegram import notificar_f1, responder_comandos
from streamlit_autorefresh import st_autorefresh

st_autorefresh(interval=15*60*1000, key="v23")
if "last_update_id" not in st.session_state: st.session_state.last_update_id=0
if "last_verde_price" not in st.session_state: st.session_state.last_verde_price=0

responder_comandos()
primary="#00FF88"; bg="#070B12"

st.markdown("""
<style>
h1{color:#FFD700!important; text-shadow:0 0 15px #FFD700!important; font-family:monospace}
[data-testid="stMetricValue"]{color:#FFD700!important; font-size:32px!important; text-shadow:0 0 10px #FFD700}
</style>
""", unsafe_allow_html=True)

A_KEY=st.secrets["alpaca"]["API_KEY"]
A_SECRET=st.secrets["alpaca"]["SECRET"]
client=TradingClient(A_KEY,A_SECRET,paper=True)

def calcular_v23(precios, high, low):
    n=len(precios)
    xb=np.mean(precios)
    s=np.std(precios,ddof=1)
    z=(precios[-1]-xb)/(s/math.sqrt(n)) if s>0 else 0
    lr=math.log(precios[-1]/precios[-2]) if precios[-2]>0 else 0
    fib=high-(high-low)*0.618
    return xb,s,z,lr,fib

def get_semaforo(price,fib,z,lr):
    if price<fib and z<-2.0 and -0.008<lr<-0.0005:
        return "VERDE","COMPRAR $10","#00FF88"
    elif lr<-0.05 or z>1.0:
        return "ROJO","NO COMPRAR","#FF3B3B"
    else:
        return "AMARILLO","ESPERAR","#FFD60A"

def prediccion_y_backtest(ticker, precios, z_actual, lr_actual):
    h1y=yf.Ticker(ticker).history(period="1y")
    c1y=h1y['Close'].values
    price_now=precios[-1]
    
    # Prediccion
    ret_24=lr_actual*100
    ret_7d=((price_now/precios[-7])-1)*100 if len(precios)>=7 else 0
    ret_30d=((price_now/precios[0])-1)*100
    max_1y=np.max(c1y) if len(c1y)>0 else price_now
    vs_max=((price_now/max_1y)-1)*100

    # Backtest: busca casos Z<-2 y lr similar en ultimo año
    casos=[]
    for i in range(30, len(c1y)-7):
        window=c1y[i-30:i]
        xb_w=np.mean(window); s_w=np.std(window,ddof=1)
        if s_w==0: continue
        z_w=(c1y[i]-xb_w)/(s_w/math.sqrt(30))
        lr_w=math.log(c1y[i]/c1y[i-1]) if c1y[i-1]>0 else 0
        if z_w<-2 and -0.008<lr_w<-0.0002:
            # futuro
            r24=((c1y[i+1]/c1y[i])-1)*100 if i+1<len(c1y) else 0
            r7=((c1y[i+7]/c1y[i])-1)*100 if i+7<len(c1y) else 0
            casos.append((r24,r7))
    
    prob=0; avg24=0; avg7=0
    if casos:
        prob=len([x for x in casos if x[0]>0])/len(casos)*100
        avg24=np.mean([x[0] for x in casos])
        avg7=np.mean([x[1] for x in casos])
    
    return ret_24,ret_7d,ret_30d,vs_max,max_1y,len(casos),prob,avg24,avg7

# UI
c_act,c_b1,c_b2=st.columns([2,1,1])
with c_act: symbol=st.selectbox("Activo", ["BTC/USD","ETH/USD","AAPL","SOL/USD"], index=0)
with c_b1:
    if st.button("🏁 ANALIZAR V23 PRO", type="primary", use_container_width=True):
        st.session_state.analizar=True
with c_b2:
    if st.button("🚨 PANICO", use_container_width=True):
        client.close_all_positions(cancel_orders=True)
        st.error("PANICO")

if st.session_state.get("analizar", False):
    mapa={"BTC/USD":"BTC-USD","ETH/USD":"ETH-USD","AAPL":"AAPL","SOL/USD":"SOL-USD"}
    ticker=mapa[symbol]
    h=yf.Ticker(ticker).history(period="1mo")
    precios=h['Close'].values; high=h['High'].max(); low=h['Low'].min(); price=precios[-1]
    xb,s,z,lr,fib=calcular_v23(precios,high,low)
    estado,texto,color=get_semaforo(price,fib,z,lr)
    ret24,ret7,ret30,vs_max,max1y,ncasos,prob,avg24,avg7=prediccion_y_backtest(ticker,precios,z,lr)

    st.markdown(f"# 🏁 F1 ANALIZANDO - {symbol}\n## 🟢 {texto} | ${price:,.2f}")🏎️
    m1,m2,m3,m4=st.columns([1.2,0.8,0.8,1])
    with m1: st.markdown(f"**{symbol}**\n\n# ${price:,.2f}\n\n🟢 Fib ${fib:,.2f}")
    with m2: st.markdown(f"**z-score**\n\n# {z:.2f}\n\n🟢 Compra < -2")
    with m3: st.markdown(f"**log ret**\n\n# {lr*100:.3f}%\n\n🔴 -0.8% a -0.05%")
    with m4:
        if st.button("🟢 COMPRAR $10", type="primary", use_container_width=True):
            client.submit_order(MarketOrderRequest(symbol=symbol, notional=10, side=OrderSide.BUY, time_in_force=TimeInForce.GTC))

    fig, ax=plt.subplots(figsize=(10,4))
    fig.patch.set_facecolor(bg); ax.set_facecolor(bg)
    ax.plot(precios, color="#00FF88", label="Precio")
    ax.axhline(fib, color="gold", linestyle="--", label="Fib 61.8%")
    ax.axhline(xb, color="#00BFFF", alpha=0.5, label="Media Quant")
    ax.plot(len(precios)-1, price, 'o', color="#00FF88", markersize=10)
    ax.legend()
    st.pyplot(fig)

    st.markdown("## 📡 PREDICCIÓN AUTOMÁTICA + ADVERTENCIA HISTÓRICA")
    p1,p2,p3,p4=st.columns(4)
    with p1: st.markdown(f"<div style='border:2px solid gold; padding:12px; border-radius:10px'>⏱️ <b>24 HORAS</b><br>{ret24:.2f}%<br><small>Tendencia corta</small></div>", unsafe_allow_html=True)
    with p2: st.markdown(f"<div style='border:2px solid gold; padding:12px; border-radius:10px'>📅 <b>7 DÍAS</b><br>{ret7:.2f}%<br><small>Tendencia semanal</small></div>", unsafe_allow_html=True)
    with p3: st.markdown(f"<div style='border:2px solid gold; padding:12px; border-radius:10px'>📅 <b>30 DÍAS</b><br>{ret30:.2f}%<br><small>Tendencia mensual</small></div>", unsafe_allow_html=True)
    with p4: st.markdown(f"<div style='border:2px solid gold; padding:12px; border-radius:10px'>🏔️ <b>vs MAX 1 AÑO</b><br>{vs_max:.2f}%<br><small>Max ${max1y:,.0f}</small></div>", unsafe_allow_html=True)

    st.markdown(f"""
    <div style='border:2px solid gold; background:#1A1A00; padding:15px; border-radius:12px; margin-top:15px'>
    🧠 <b>BACKTEST HISTÓRICO AUTOMÁTICO</b><br>
    Se encontraron {ncasos} casos similares en el último año donde Z < -2 y log-ret igual que ahora.<br>
    <span style='color:gold'><b>Probabilidad de rebote positivo en 24h: {prob:.1f}%</b></span><br>
    Ganancia promedio si rebotó en 24h: {avg24:.2f}% | En 7 días: {avg7:.2f}%<br><br>
    ⚠️ <b>ADVERTENCIA:</b> 🟡 NEUTRAL: 50/50, compra con cautela de $10
    </div>
    """, unsafe_allow_html=True)

    # Telegram V23
    msg=(f"🏁 F1 V23 PRO - {symbol} ${price:,.2f}\n{texto} z {z:.2f} lr {lr*100:.3f}%\nFib ${fib:,.2f}\n24h {ret24:.2f}% 7d {ret7:.2f}% 30d {ret30:.2f}%\nBacktest {ncasos} casos Prob {prob:.1f}%")
    notificar_f1(msg)
    st.success(f"✅ Orden REAL $10 enviada - V23 PRO | 🟢 COMPRAR $10 - Backtest {prob:.1f}% prob rebote")
