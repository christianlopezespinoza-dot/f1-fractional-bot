import streamlit as st
st.set_page_config(page_title="F1 SEMAFORO", layout="wide", page_icon="🏁")
import yfinance as yf, numpy as np, matplotlib.pyplot as plt
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from bot_telegram import notificar_f1, responder_comandos
from streamlit_autorefresh import st_autorefresh

st_autorefresh(interval=15*60*1000, key="f1")
for k,v in {"last_verde_price":0, "perfil_nombre":"ChristianLE", "analizar":True, "last_update_id":0, "show_alpaca":False}.items():
    if k not in st.session_state: st.session_state[k]=v
responder_comandos()

st.markdown("""
<style>
[data-testid="stAppViewContainer"]{background:#10131C!important}
.semaforo-box{border:1.5px solid #FFD700; border-radius:16px; padding:16px; background:#181B27; box-shadow:0 0 15px rgba(255,215,0,0.2); margin-bottom:14px}
.semaforo-title{color:#FFD700; font-weight:900; font-size:18px; margin-bottom:4px}
.semaforo-sub{color:#8A93A8; font-size:13px; margin-bottom:12px}
.sema-card{border-radius:12px; padding:12px; background:#10131C; min-height:110px}
.card-yellow{border-left:3px solid #FFD700}
.card-green{border-left:3px solid #00FF88}
.card-red{border-left:3px solid #FF4D4D}
.sema-label{color:#F0F0F0; font-weight:700; font-size:14px}
.sema-text{color:#8A93A8; font-size:12px; line-height:1.4; margin-top:6px}
.sema-footer{color:#D4C44A; font-size:12px; margin-top:12px}
.neon-yellow{color:#FFD700!important; text-shadow:0 0 8px #FFD700, 0 0 15px #FFA500!important; font-weight:900; font-size:32px; line-height:1.1}
.neon-small{font-size:12px; padding:3px 10px; border-radius:20px; display:inline-block; margin-top:4px; font-weight:700}
.neon-green{background:rgba(0,255,136,0.15); color:#00FF88; border:1px solid rgba(0,255,136,0.3)}
.neon-red{background:rgba(255,70,70,0.15); color:#FF6B7A; border:1px solid rgba(255,70,70,0.3)}
.box{border:1.5px solid #FFC800; background:rgba(255,200,0,0.08); padding:14px; border-radius:14px; min-height:85px; color:#E8E6D9}
.backtest{border:1.5px solid #FFC800; background:#1C1A08; padding:18px; border-radius:14px; margin-top:12px; color:#E8E6D9}
.verde-banner{background:rgba(0,255,136,0.15); border:1px solid rgba(0,255,136,0.3); color:#4ADE80; padding:12px; border-radius:10px; font-weight:700; margin-top:12px}
</style>
""", unsafe_allow_html=True)

A_KEY=st.secrets["alpaca"]["API_KEY"]
A_SECRET=st.secrets["alpaca"]["SECRET"]
client=TradingClient(A_KEY,A_SECRET,paper=True)

c0,c1,c2=st.columns([2.5,1,1])
with c0: symbol=st.selectbox("Activo", ["BTC/USD","ETH/USD","AAPL","SOL/USD"], index=0, label_visibility="collapsed")
with c1: 
    if st.button("🏁 ANALIZAR", type="primary", use_container_width=True):
        st.session_state.analizar=True; st.rerun()
with c2:
    if st.button("🚨 PANICO", use_container_width=True):
        try: client.close_all_positions(cancel_orders=True); st.error("PANICO")
        except Exception as e: st.error(str(e))

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

if z < -2 and price < fib and -0.008 < lr < -0.0005:
    sema_color = "VERDE"; sema_txt = "🟢 COMPRAR $10"
else:
    if z > 0 or lr < -0.05:
        sema_color = "ROJO"; sema_txt = "🔴 Freno total"
    else:
        sema_color = "AMARILLO"; sema_txt = "🟡 Esperas, no perder es ganar"

# ALPACA COMPRA REAL ANTES PARA QUE LA BARRA LO MUESTRE
orden_msg=""
if z < -2 and price < fib:
    try:
        if abs(price - st.session_state.last_verde_price) > 2:
            order = client.submit_order(MarketOrderRequest(symbol=symbol, notional=10, side=OrderSide.BUY, time_in_force=TimeInForce.GTC))
            st.session_state.last_verde_price = price
            orden_msg = f"ID {str(order.id)[:8]}"
    except Exception as e:
        orden_msg = f"Error {e}"

# SEMAFORO
st.markdown(f"""
<div class="semaforo-box">
 <div class="semaforo-title">🏎️ F1 SEMÁFORO - Cómo leer en 30 seg</div>
 <div class="semaforo-sub">Sin fórmulas. Solo 3 preguntas para no perder tu poco dinero.</div>
 <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:10px">
  <div class="sema-card card-yellow">
   <div class="sema-label">1. ¿Está barato? Fib 0.618</div>
   <div class="sema-text">Línea dorada. Si BTC está abajo de ella, es como aguacate en oferta. ${price:,.0f} vs ${fib:,.0f} normal.</div>
  </div>
  <div class="sema-card card-green">
   <div class="sema-label">2. ¿Está regalado? z= {z:.2f}</div>
   <div class="sema-text">z -2 a -7 = pánico. La gente lo remata. Mientras más negativo, más oportunidad. Tu ejemplo: {z:.2f} = súper regalado.</div>
  </div>
  <div class="sema-card card-red">
   <div class="sema-label">3. ¿Se cae a pedazos? log {lr*100:.2f}%</div>
   <div class="sema-text">{lr*100:.2f}% = bajó {abs(lr*100):.0f} centavos de $100 = normal. -5% = crash = no tocar. Solo compramos bajaditas chiquitas.</div>
  </div>
 </div>
 <div class="sema-footer">🟢 VERDE = Barato + Regalado + Bajadita chiquita → Compras $10 | 🟡 AMARILLO = Esperas | 🔴 ROJO = Freno total</div>
</div>
""", unsafe_allow_html=True)

# === BARRA AMARILLA AHORA ES BOTON ALPACA DISCRETO ===
barra_txt = f"💰 ALPACA PAPER • {symbol} • Última compra ${st.session_state.last_verde_price:,.0f} • {orden_msg if orden_msg else 'Listo para comprar'}"
st.markdown(f"""
<div style="border:1.5px solid #FFD700; border-radius:14px; padding:10px 16px; background:#0B0F1A; box-shadow:0 0 12px rgba(255,215,0,0.3); margin-bottom:10px; display:flex; justify-content:space-between">
  <span style="color:#FFD700; font-weight:800; font-size:12px">{barra_txt}</span>
  <span style="color:#8A93A8; font-size:10px">discreto</span>
</div>
""", unsafe_allow_html=True)

c_alp1, c_alp2 = st.columns(2)
with c_alp1:
    if st.button("💰 Ver en Alpaca →", use_container_width=True):
        st.session_state.show_alpaca = not st.session_state.show_alpaca
with c_alp2:
    st.link_button("🔗 Abrir Dashboard Alpaca", "https://app.alpaca.markets/brokerage/dashboard/overview", use_container_width=True)

if st.session_state.show_alpaca:
    try:
        positions = client.get_all_positions()
        orders = client.get_orders()
        st.markdown("### 📦 Posiciones Alpaca")
        if positions:
            for p in positions:
                st.write(f"**{p.symbol}** {p.qty} • ${float(p.market_value):.2f} • P/L ${float(p.unrealized_pl):.2f}")
        else:
            st.info("Sin posiciones aún - en cuanto compre aparecerá aquí")
        st.markdown("### 🧾 Últimas órdenes $10")
        for o in list(orders)[:5]:
            st.caption(f"{o.symbol} {o.side} ${o.notional} - {o.status}")
    except Exception as e:
        st.error(f"Alpaca: {e}")

# NUMEROS NEON
cA,cB,cC,cD=st.columns([1.2,0.8,0.8,1])
with cA: st.markdown(f"<div style='color:#8A93A8; font-size:13px'>BTC/USD</div><div class='neon-yellow'>${price:,.0f}...</div><div class='neon-small neon-green'>↑ Fib: ${fib:,.2f}</div>", unsafe_allow_html=True)
with cB: st.markdown(f"<div style='color:#8A93A8; font-size:13px'>z-score</div><div class='neon-yellow'>{z:.2f}</div><div class='neon-small neon-green'>↑ Compra si < -2</div>", unsafe_allow_html=True)
with cC: st.markdown(f"<div style='color:#8A93A8; font-size:13px'>log ret</div><div class='neon-yellow'>{lr*100:.3f}%</div><div class='neon-small neon-red'>↓ -0.8% a -0.05%</div>", unsafe_allow_html=True)
with cD: st.markdown(f"<div style='padding-top:10px'><div style='background:#00FF88; color:#000; font-weight:900; padding:12px; border-radius:10px; text-align:center'>🟢 {sema_txt}</div></div>", unsafe_allow_html=True)

fig, ax=plt.subplots(figsize=(10,4))
fig.patch.set_facecolor("#10131C"); ax.set_facecolor("#10131C")
ax.plot(precios, color="#00FF87", linewidth=2.5)
ax.axhline(xb, color="#3A8B8B", linewidth=1, alpha=0.8)
ax.axhline(fib, color="#FFD500", ls="--", linewidth=1.2)
ax.scatter([len(precios)-1],[price], s=120, color="#00FF4C", zorder=5, edgecolors="#10131C", linewidths=2)
ax.tick_params(colors="#6B7280", labelsize=9)
for sp in ax.spines.values(): sp.set_visible(False)
from matplotlib.lines import Line2D
ax.legend(handles=[Line2D([0],[0], color='#00FF87', label='Precio'), Line2D([0],[0], color='#FFD500', ls='--', label='Fib'), Line2D([0],[0], color='#3A8B8B', label='Media')], loc='upper right', facecolor='#10131C', edgecolor='#FFC800', fontsize=8, labelcolor='white')
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
⚠️ <b>ADVERTENCIA:</b> {sema_color}: {sema_txt}
</div>
""", unsafe_allow_html=True)

st.markdown(f"<div class='verde-banner'>🟢 {sema_color}: {sema_txt} • Alpaca {orden_msg}</div>", unsafe_allow_html=True)
if orden_msg and "ID" in orden_msg:
    st.success(f"✅ ALPACA: Orden $10 enviada - {symbol} - {orden_msg}")

msg = (
    f"<b>🏁 F1 BOT - {st.session_state.perfil_nombre}</b>\n"
    f"━━━━━━━━━━━━━━\n"
    f"📊 <b>{symbol}</b>  ${price:,.2f}\n"
    f"{sema_txt}\n"
    f"━━━━━━━━━━━━━━\n"
    f"📐 <b>Fib 61.8%:</b> ${fib:,.2f}\n"
    f"📈 <b>z-score:</b> {z:.2f}\n"
    f"📉 <b>log-ret:</b> {lr*100:.4f}%\n"
    f"🧠 <b>Media:</b> ${xb:,.2f}\n"
    f"━━━━━━━━━━━━━━\n"
    f"⏱ <b>24h</b> {ret24:+.2f}% | <b>7d</b> {ret7:+.2f}% | <b>30d</b> {ret30:+.2f}%\n"
    f"🔬 <b>Backtest</b> {len(casos)} casos | Prob {prob:.1f}%\n"
    f"🚦 <b>Semaforo:</b> {sema_color} {sema_txt}\n"
    f"💰 <b>Alpaca:</b> {orden_msg}\n"
)
try: notificar_f1(msg)
except: pass
