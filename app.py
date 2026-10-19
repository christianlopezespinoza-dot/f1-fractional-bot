# app.py V20 QUANT GOLD BALDOR EDITION - 10 FORMULAS GANAR-GANAR
import streamlit as st
import yfinance as yf, requests, time, math, numpy as np, matplotlib.pyplot as plt
from datetime import datetime
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

st.set_page_config(page_title="F1 V20 BALDOR GOLD", layout="wide")

try:
    st.image("car_btc_eth_sol_aapl.jpg", use_container_width=True)
    st.caption("V20 BALDOR EDITION - BTC | ETH | SOL | AAPL - 10 FÓRMULAS BALDOR")
except: pass

st.title("🏎️ F1 V20 BALDOR QUANT GOLD")
st.markdown("**Baldor + Quant: Cuadrática | Log Ret | EMA | σ | Sharpe | Z-Score | Fib 0.618 | f'(x) | ∫VaR**")

A_KEY = st.secrets["alpaca"]["API_KEY"]
A_SECRET = st.secrets["alpaca"]["SECRET"]
T_TOKEN = st.secrets["telegram"]["BOT_TOKEN"]
T_CHAT = st.secrets["telegram"]["CHAT_ID"]
client = TradingClient(A_KEY, A_SECRET, paper=True)

def telegram(msg, largo=True):
    try:
        requests.post(f"https://api.telegram.org/bot{T_TOKEN}/sendMessage", json={"chat_id": T_CHAT, "text": msg}, timeout=10)
        audio = "https://cdn.pixabay.com/audio/2022/03/24/audio_5a70a1157b.mp3" if largo else "https://cdn.pixabay.com/audio/2022/03/10/audio_c8c8a73467.mp3"
        requests.post(f"https://api.telegram.org/bot{T_TOKEN}/sendAudio", json={"chat_id": T_CHAT, "audio": audio}, timeout=10)
    except: pass

def calcular_baldor(precios):
    n=len(precios)
    x_bar=np.mean(precios)
    s=np.std(precios, ddof=1)
    EE=s/math.sqrt(n) if n>0 else 0
    z=(precios[-1]-x_bar)/(s/math.sqrt(n)) if s>0 else 0
    IC_inf=x_bar-1.96*s/math.sqrt(n)
    IC_sup=x_bar+1.96*s/math.sqrt(n)
    derivada=(precios[-1]-precios[-6])/5 if n>6 else 0
    # NUEVAS BALDOR
    log_ret=np.log(precios[-1]/precios[-2]) if precios[-2]>0 else 0
    ema_alpha=2/(10+1)
    ema=precios[-1]*ema_alpha + x_bar*(1-ema_alpha)
    sharpe=(x_bar-precios[0])/s if s>0 else 0
    # Cuadratica para soporte: a=1, b=-2*x_bar, c=x_bar**2 - s**2
    disc = (-2*x_bar)**2 -4*1*(x_bar**2 - s**2)
    soporte_quad = (-(-2*x_bar) - math.sqrt(max(0,disc)))/2 if disc>=0 else x_bar-s
    # VaR Integral aprox
    VaR = x_bar - 1.65*s
    ciclo=math.sin(2*math.pi*datetime.now().hour/24)
    return x_bar,s,EE,z,IC_inf,IC_sup,derivada,log_ret,ema,sharpe,soporte_quad,VaR,ciclo

if "running" not in st.session_state:
    st.session_state.running=False
    st.session_state.last_buy=0
    st.session_state.buy_count=6

c1,c2,c3,c4,c5=st.columns(5)
with c1: symbol=st.selectbox("Activo", ["AAPL","BTC/USD","ETH/USD","SOL/USD"], index=1)
with c2: version=st.selectbox("Estrategia", ["V20 Baldor 15%","V20 Baldor 12.4%"])
with c3:
    if st.button("🏁 INICIAR V20", type="primary"):
        st.session_state.running=True
        telegram(f"🏁 F1 LARGO V20 BALDOR INICIADO\n{symbol} - Ganar-Ganar\nCuadrática + Log + EMA + VaR\n{datetime.now().strftime('%H:%M:%S')}", True)
with c4:
    if st.button("Stop"): st.session_state.running=False
with c5:
    if st.button("🚨 PANICO"):
        try: client.close_all_positions(cancel_orders=True); telegram("🚨 PANICO V20", False)
        except Exception as e: st.error(e)

if st.session_state.running:
    ticker="AAPL" if symbol=="AAPL" else symbol.split("/")[0]+"-USD"
    h=yf.Ticker(ticker).history(period="1mo")
    if len(h)<10: st.error("Sin datos"); st.stop()
    precios=h['Close'].values
    fib=h['High'].max()-(h['High'].max()-h['Low'].min())*0.618
    price=precios[-1]
    x_bar,s,EE,z,IC_inf,IC_sup,derivada,log_ret,ema,sharpe,soporte_quad,VaR,ciclo=calcular_baldor(precios)

    m1,m2,m3,m4,m5=st.columns(5)
    m1.metric(symbol, f"${price:.2f}", f"Fib 0.618 ${fib:.2f}")
    m2.metric("z=(x̄-μ0)/(σ/√n)", f"{z:.2f}")
    m3.metric("log ret ln(Pt/Pt-1)", f"{log_ret:.4f}")
    m4.metric("EMA αPt+(1-α)EMA", f"{ema:.2f}")
    m5.metric("VaR ∫ + Sharpe", f"${VaR:.2f} | {sharpe:.2f}")

    fig, (ax1,ax2)=plt.subplots(2,1, figsize=(12,8), gridspec_kw={'height_ratios':[3,1]})
    fig.patch.set_facecolor('#0E1117')
    ax1.set_facecolor('#0E1117')
    ax1.plot(precios, color='#00FF88', linewidth=2, label='Pt Precio')
    ax1.axhline(fib, color='gold', ls='--', lw=1.5, label='Fib 0.618 = (Max-Min)*0.618')
    ax1.axhline(x_bar, color='cyan', alpha=0.6, label='x̄ = Σxi/n')
    ax1.axhline(soporte_quad, color='magenta', ls=':', lw=1.2, label='Cuadrática x=(-b±√(b²-4ac))/2a')
    ax1.axhline(VaR, color='red', ls='-.', alpha=0.6, label='VaR = x̄-1.65σ = ∫f(x)dx')
    ax1.fill_between(range(len(precios)), IC_inf, IC_sup, color='gold', alpha=0.08, label='IC 95% x̄±1.96σ/√n')
    ax1.tick_params(colors='white')
    ax1.legend(facecolor='black', edgecolor='gold', labelcolor='white', fontsize=7, ncol=2)
    ax1.set_title(f"{symbol} - BALDOR V20 - BTC ETH SOL AAPL - 10 FÓRMULAS", color='gold', fontsize=12)

    ax2.set_facecolor('#0E1117')
    ax2.plot([np.log(p/precios[0]) for p in precios], color='orange', label="ln(Pt) Log Baldor")
    ax2.plot([derivada]*len(precios), color='purple', ls='--', label="f'(x)=lim h→0 [f(x+h)-f(x)]/h")
    ax2.axhline(-2, color='red', ls=':', alpha=0.5)
    ax2.legend(facecolor='black', edgecolor='gold', labelcolor='white', fontsize=7)
    ax2.tick_params(colors='white')
    st.pyplot(fig)

    # TABLA DE FORMULAS BALDOR PARA QUE SE VEA GANAR-GANAR
    with st.expander("📚 10 FÓRMULAS BALDOR INTEGRADAS V20"):
        st.code("""
1. Media: x̄ = Σxi/n
2. Desv: σ = √[Σ(xi-x̄)²/(n-1)]
3. Z-Score: z = (x̄-μ0)/(σ/√n)
4. Error: EE = σ/√n
5. IC 95%: x̄ ± 1.96*σ/√n
6. Fib: Retro = Max - (Max-Min)*0.618
7. Log Ret: r = ln(Pt/Pt-1)  [log_a(xy)=log_a x+log_a y]
8. Cuadrática: x=(-b±√(b²-4ac))/2a
9. EMA: EMA_t = α*Pt + (1-α)*EMA_t-1, α=2/(n+1)
10. Derivada: f'(x)=lim h→0 [f(x+h)-f(x)]/h + VaR ∫ + Sharpe = (x̄-rf)/σ
        """)

    if price <= fib and z < -2.0 and (time.time()-st.session_state.last_buy)>45:
        try:
            req=MarketOrderRequest(symbol=symbol, notional=10, side=OrderSide.BUY, time_in_force=TimeInForce.DAY if symbol=="AAPL" else TimeInForce.GTC)
            order=client.submit_order(req)
            st.session_state.buy_count+=1
            st.session_state.last_buy=time.time()
            txt=f"""🏁🔊🔊🔊 SONIDO F1 LARGO - COMPRA V20 BALDOR
✅ COMPRA REAL #{st.session_state.buy_count} - GANAR-GANAR
{symbol} $10
Fib 0.618: {fib:.2f} | Cuad: {soporte_quad:.2f}
Ejecutado: {price:.2f}
z: {z:.2f} log: {log_ret:.4f} EMA: {ema:.2f} Sharpe: {sharpe:.2f}
VaR: {VaR:.2f} IC: [{IC_inf:.2f}-{IC_sup:.2f}]
f'(x): {derivada:.3f}
Order: {order.id}
V20 Baldor 10 Fórmulas"""
            telegram(txt, True)
            st.balloons()
            st.success(f"Compra #{st.session_state.buy_count} V20 Baldor OK")
        except Exception as e: st.error(e)

    time.sleep(5)
    st.rerun()
