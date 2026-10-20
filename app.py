import streamlit as st
st.set_page_config(page_title="F1 V24 THEMA", page_icon="🏁", layout="wide")
import yfinance as yf, math, numpy as np, matplotlib.pyplot as plt
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from bot_telegram import notificar_f1, responder_comandos
from streamlit_autorefresh import st_autorefresh

st_autorefresh(interval=15*60*1000, key="v24")
if "last_update_id" not in st.session_state: st.session_state.last_update_id=0
if "last_verde_price" not in st.session_state: st.session_state.last_verde_price=0
responder_comandos()

# THEMA SELECTOR - TUS 3 OPCIONES
thema = st.selectbox("🎨 THEMA F1 - Elige diseño", ["Original Trading", "Dorado Negro Premium", "Neon Cyberpunk"], index=0)

if thema=="Original Trading":
    primary="#00FF88"; bg="#0E1117"; border1="#20C2B0"; border2="#FF7A00"; border3="#8A2BE2"
    title_color="#FFD700"; glow="0 0 20px gold"
elif thema=="Dorado Negro Premium":
    primary="#FFD700"; bg="#0A0800"; border1="#FFD700"; border2="#FFD700"; border3="#FFD700"
    title_color="#FFD700"; glow="0 0 25px #FFD700"
else: # Neon
    primary="#00FFFF"; bg="#080A14"; border1="#00FFFF"; border2="#FF00FF"; border3="#FF00FF"
    title_color="#00FFFF"; glow="0 0 20px #00FFFF, 0 0 40px #FF00FF"

st.markdown(f"""
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@700&display=swap" rel="stylesheet">
<style>
body{{background:{bg}}}
h1,h2,h3{{font-family:'Orbitron',monospace!important; color:{title_color}!important; text-shadow:{glow}!important}}
.card{{border-radius:14px; padding:14px; border:2px solid; background: rgba(255,255,255,0.06); min-height:230px}}
.card-1{{border-color:{border1}}} .card-2{{border-color:{border2}}} .card-3{{border-color:{border3}}}
.card-4{{border-color:{border1}}} .card-5{{border-color:{border2}}} .card-6{{border-color:{border3}}}
.formula{{font-family:Orbitron; font-size:24px; color:{title_color}; text-align:center; text-shadow:{glow}}}
.metric-gold div[data-testid="stMetricValue"]{{color:{title_color}!important; text-shadow:{glow}!important}}
</style>
""", unsafe_allow_html=True)

A_KEY=st.secrets["alpaca"]["API_KEY"]; A_SECRET=st.secrets["alpaca"]["SECRET"]
client=TradingClient(A_KEY,A_SECRET,paper=True)
ORDER_NOTIONAL=10

def calcular_quant(precios):
    n=len(precios); xb=np.mean(precios); s=np.std(precios,ddof=1)
    z=(precios[-1]-xb)/(s/math.sqrt(n)) if s>0 else 0
    lr=math.log(precios[-1]/precios[-2]) if precios[-2]>0 else 0
    return xb,s,z,lr

def get_semaforo(price,fib,z,lr):
    if price<fib and z<-2.0 and -0.008<lr<-0.0002: return "VERDE","🟢 COMPRAR $10","#00FF88"
    elif lr<-0.05 or z>1.0: return "ROJO","🔴 NO COMPRAR","#FF3B3B"
    else: return "AMARILLO","🟡 ESPERAR","#FFD60A"

def analisis_historico(ticker):
    hist=yf.Ticker(ticker).history(period="1y"); close=hist['Close'].values
    ret=lambda n: (close[-1]/close[-n]-1)*100 if len(close)>n else 0
    casos=[]
    for i in range(30,len(close)-7):
        w=close[i-30:i]; s=np.std(w,ddof=1)
        if s==0: continue
        z=(w[-1]-np.mean(w))/(s/math.sqrt(len(w)))
        lr=math.log(close[i]/close[i-1]) if close[i-1]>0 else 0
        if z<-2 and -0.008<lr<-0.0002:
            casos.append((close[i+1]/close[i]-1)*100)
    prob=sum(x>0 for x in casos)/len(casos)*100 if casos else 0
    return {{"24h":ret(2),"7d":ret(6),"30d":ret(21),"vsMax":(close[-1]/hist['High'].max()-1)*100,"max":hist['High'].max(),"prob":prob,"avg":np.mean(casos) if casos else 0,"avg7":np.mean([close[i+7]/close[i]-1 for i in range(len(close)-7)])*100 if casos else 0,"casos":len(casos)}}

col0,col1,col2 = st.columns([2,1,1])
with col0: symbol=st.selectbox("Activo", ["BTC/USD","AAPL","ETH/USD"])
with col1: iniciar=st.button("🏁 ANALIZAR V24", type="primary", use_container_width=True)
with col2: 
    if st.button("🚨 PANICO", use_container_width=True):
        try: client.close_all_positions(cancel_orders=True); st.error("PÁNICO - Todo vendido")
        except Exception as e: st.error(e)

if iniciar:
    ticker="BTC-USD" if symbol=="BTC/USD" else "ETH-USD" if symbol=="ETH/USD" else "AAPL"
    h=yf.Ticker(ticker).history(period="1mo"); precios=h['Close'].values
    fib=h['High'].max()-(h['High'].max()-h['Low'].min())*0.618
    price=precios[-1]; xb,s,z,lr=calcular_quant(precios)
    estado,texto,color=get_semaforo(price,fib,z,lr)
    hist_data=analisis_historico(ticker)

    st.markdown(f"# 🏎️ F1 V24 - {thema.upper()} - {symbol} {texto}")

    m1,m2,m3,m4=st.columns(4)
    m1.metric(symbol, f"${price:,.2f}", f"Fib ${fib:,.2f}")
    m2.metric("z-score", f"{z:.2f}", "Compra < -2")
    m3.metric("log ret", f"{lr*100:.3f}%")
    m4.markdown(f"<div style='background:{color};color:black;padding:12px;border-radius:10px;text-align:center'><b>{texto}</b></div>", unsafe_allow_html=True)

    fig,ax=plt.subplots(figsize=(11,4.5))
    fig.patch.set_facecolor(bg); ax.set_facecolor(bg)
    ax.plot(precios, color=primary, linewidth=2, label='Precio')
    ax.axhline(fib, color=title_color, linestyle='--', label='Fib 61.8%')
    ax.axhline(xb, color='cyan', alpha=0.4, label='Media Quant')
    if estado=="VERDE": ax.scatter(len(precios)-1, price, color='lime', s=150, edgecolors='white', zorder=5)
    ax.legend(facecolor=bg, edgecolor=title_color, labelcolor='white
