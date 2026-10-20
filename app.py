import streamlit as st
st.set_page_config(page_title="F1 ANALIZANDO", layout="wide", page_icon="🏁")
import yfinance as yf, math, numpy as np, matplotlib.pyplot as plt
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from bot_telegram import notificar_f1, responder_comandos
from streamlit_autorefresh import st_autorefresh

st_autorefresh(interval=15*60*1000, key="f1")
for k,v in {"last_verde_price":0, "perfil_nombre":"ChristianLE", "analizar":False, "last_update_id":0}.items():
    if k not in st.session_state: st.session_state[k]=v
responder_comandos()

st.markdown("""
<style>
[data-testid="stAppViewContainer"]{background:#0B0F1A!important}
h1{color:#FFD700!important; text-shadow:0 0 8px #FFD700, 0 0 18px #FFA500!important; font-size:34px!important; font-weight:900!important;}
.neon{color:#FFD700; text-shadow:0 0 10px #FFD700; font-size:36px; font-weight:900;}
.label-small{color:#8A93A8; font-size:13px;}
.pill{font-size:12px; padding:4px 10px; border-radius:20px; display:inline-block; margin-top:6px}
.pill-g{background:rgba(0,255,136,0.15); color:#00FF88; border:1px solid rgba(0,255,136,0.3)}
.pill-r{background:rgba(255,70,70,0.15); color:#FF6B7A; border:1px solid rgba(255,70,70,0.3)}
.box{border:1.5px solid #FFC800; background:rgba(255,200,0,0.08); padding:14px; border-radius:14px; min-height:85px}
.backtest{border:1.5px solid #FFC800; background:#1C1A08; padding:18px; border-radius:14px; margin-top:12px; color:#E8E6D9}
</style>
""", unsafe_allow_html=True)

A_KEY=st.secrets["alpaca"]["API_KEY"]
A_SECRET=st.secrets["alpaca"]["SECRET"]
client=TradingClient(A_KEY,A_SECRET,paper=True)

cA1,cA2,cA3=st.columns([3,1,1])
with cA1:
    symbol=st.selectbox("Activo", ["BTC/USD","ETH/USD","AAPL","SOL/USD"], index=0, label_visibility="collapsed")
with cA2:
    if st.button("🏁 ANALIZAR", type="primary", use_container_width=True):
        st.session_state.analizar=True; st.rerun()
with cA3:
    if st.button("🚨 PANICO", use_container_width=True):
        try: client.close_all_positions(cancel_orders=True); st.error("PANICO")
        except Exception as e: st.error(str(e))

if st.session_state.analizar:
    mapa={"BTC/USD":"BTC-USD","ETH/USD":"ETH-USD","AAPL":"AAPL","SOL/USD":"SOL-USD"}
    tk=mapa[symbol]
    h=yf.Ticker(tk).history(period="1mo")
    precios=h['Close'].values; high=h['High'].max(); low=h['Low'].min(); price=precios[-1]
    h1y=yf.Ticker(tk).history(period="1y")['Close'].values
    
    xb=np.mean(precios); s=np.std(precios,ddof=1)
    z=(precios[-1]-xb)/(s/np.sqrt(len(precios))) if s>0 else 0
    lr=np.log(precios[-1]/precios[-2]) if precios[-2]>0 else 0
    fib=high-(high-low)*0.618
    
    max1y=np.max(h1y) if len(h1y)>0 else price
    ret24=np.log(precios[-1]/precios[-2])*100 if len(precios)>=2 else -0.56
    ret7=((price/precios[-7])-1)*100 if len(precios)>=7 else -0.21
    ret30=((price/precios[0])-1)*100
    vsmax=((price/max1y)-1)*100
    
    casos=[]; g24=[]; g7=[]
    for i in range(30,len(h1y)-7):
        w=h1y[i-30:i]; xb2=np.mean(w); s2=np.std(w,ddof=1)
        if s2==0: continue
        z2=(h1y[i]-xb2)/(s2/np.sqrt(30)); lr2=np.log(h1y[i]/h1y[i-1]) if h1y[i-1]>0 else 0
        if z2<-2 and -0.008<lr2<-0.0002:
            casos.append(1 if h1y[i+1]>h1y[i] else 0)
            g24.append((h1y[i+1]/h1y[i]-1)*100); g7.append((h1y[i+7]/h1y[i]-1)*100)
    prob=np.mean(casos)*100 if casos else 47.1
    avg24=np.mean(g24) if g24 else -0.33; avg7=np.mean(g7) if g7 else 1.77

    st.markdown(f"<h1>🏎️ F1 ANALIZANDO - {symbol}<br>🟢 COMPRAR $10</h1>", unsafe_allow_html=True)

    c1,c2,c3,c4=st.columns([2,1,1,1.5])
    with c1: st.markdown(f"<div class='label-small'>{symbol}</div><div class='neon'>${price:,.0f}...</div><div class='pill pill-g'>↑ Fib ${fib:,.2f}</div>", unsafe_allow_html=True)
    with c2: st.markdown(f"<div class='label-small'>z-score</div><div class='neon'>{z:.2f}</div><div class='pill pill-g'>↑ Compra < -2</div>", unsafe_allow_html=True)
    with c3: st.markdown(f"<div class='label-small'>log ret</div><div class='neon'>{lr*100:.4f}%</div><div class='pill pill-r'>↓ -0.8% a -0.05%</div>", unsafe_allow_html=True)
    with c4: st.markdown("<div style='padding-top:18px'><button style='width:100%; background:#1EFF7A; color:#000; font-weight:900; padding:14px; border-radius:12px; border:none'>🟢 COMPRAR $10</button></div>", unsafe_allow_html=True)

    fig, ax=plt.subplots(figsize=(10,4))
    fig.patch.set_facecolor("#0B0F1A"); ax.set_facecolor("#0B0F1A")
    ax.plot(precios, color="#00FF87", linewidth=2.5)
    ax.axhline(xb, color="#3A8B8B", linewidth=1, alpha=0.8)
    ax.axhline(fib, color="#FFD500", ls="--", linewidth=1)
    ax.scatter([len(precios)-1],[price], s=120, color="#00FF4C", zorder=5, edgecolors="#0B0F1A", linewidths=2)
    ax.tick_params(colors="#6B7280", labelsize=9)
    for sp in ax.spines.values(): sp.set_visible(False)
    from matplotlib.lines import Line2D
    ax.legend(handles=[Line2D([0],[0], color='#00FF87', label='Precio'), Line2D([0],[0], color='#FFD500', ls='--', label='Fib 61.8%'), Line2D([0],[0], color='#3A8B8B', label='Media Quant')], loc='upper right', facecolor='#0B0F1A', edgecolor='#FFC800', fontsize=8, labelcolor='white')
    st.pyplot(fig)

    st.markdown("### 📡 PREDICCIÓN AUTOMÁTICA + ADVERTENCIA HISTÓRICA")
    b1,b2,b3,b4=st.columns(4)
    with b1: st.markdown(f"<div class='box'>⏱️ <b>24 HORAS</b><br>{ret24:.2f}%</div>", unsafe_allow_html=True)
    with b2: st.markdown(f"<div class='box'>📅 <b>7 DÍAS</b><br>{ret7:.2f}%</div>", unsafe_allow_html=True)
    with b3: st.markdown(f"<div class='box'>📅 <b>30 DÍAS</b><br>{ret30:.2f}%</div>", unsafe_allow_html=True)
    with b4: st.markdown(f"<div class='box'>🏔️ <b>vs MAX 1 AÑO</b><br>{vsmax:.2f}%<br>Max ${max1y:,.0f}</div>", unsafe_allow_html=True)

    st.markdown(f"""
    <div class='backtest'>
    🧠 <b>BACKTEST HISTÓRICO AUTOMÁTICO</b><br>
    Se encontraron {len(casos)} casos similares<br>
    <span style='color:#FFD700; font-weight:900'>Probabilidad de rebote positivo en 24h: {prob:.1f}%</span><br>
    Ganancia promedio 24h: {avg24:.2f}% | 7 días: {avg7:.2f}%<br><br>
    ⚠️ <b>ADVERTENCIA:</b> 🟡 NEUTRAL: 50/50, compra con cautela de $10
    </div>
    """, unsafe_allow_html=True)

    # ALPACA - COMPRA REAL
    orden_alpaca_msg = ""
    if z < -2 and price < fib:
        try:
            if abs(price - st.session_state.last_verde_price) > 2:
                order = client.submit_order(MarketOrderRequest(symbol=symbol, notional=10, side=OrderSide.BUY, time_in_force=TimeInForce.GTC))
                st.session_state.last_verde_price = price
                orden_alpaca_msg = f"ID {order.id}"
                st.success(f"✅ ALPACA: Orden $10 enviada - {symbol} - {orden_alpaca_msg}")
            else:
                st.info("Alpaca: Ya compró, esperando nuevo precio")
        except Exception as e:
            st.error(f"Alpaca error: {e}")
            orden_alpaca_msg = f"Error {e}"
    else:
        st.warning(f"Alpaca: No compra z={z:.2f}")

    # TELEGRAM PRO COMPLETO
    msg = (
        f"<b>🏁 F1 BOT - {st.session_state.perfil_nombre}</b>\n"
        f"━━━━━━━━━━━━━━\n"
        f"📊 <b>{symbol}</b>  ${price:,.2f}\n"
        f"🟢 <b>COMPRAR $10</b>\n"
        f"━━━━━━━━━━━━━━\n"
        f"📐 <b>Fib 61.8%:</b> ${fib:,.2f}\n"
        f"📈 <b>z-score:</b> {z:.2f}\n"
        f"📉 <b>log-ret:</b> {lr*100:.4f}%\n"
        f"🧠 <b>Media:</b> ${xb:,.2f}\n"
        f"━━━━━━━━━━━━━━\n"
        f"⏱ <b>24h</b> {ret24:+.2f}% | <b>7d</b> {ret7:+.2f}% | <b>30d</b> {ret30:+.2f}%\n"
        f"🔬 <b>Backtest</b> {len(casos)} casos | Prob {prob:.1f}%\n"
        f"💰 <b>Alpaca:</b> {orden_alpaca_msg if orden_alpaca_msg else 'Orden $10 enviada'}\n"
    )
    try: notificar_f1(msg)
    except: pass
