import streamlit as st
st.set_page_config(page_title="F1 SEMAFORO", layout="wide", page_icon="🏁")
import yfinance as yf, numpy as np, matplotlib.pyplot as plt
from datetime import datetime, timedelta
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from bot_telegram import notificar_f1, responder_comandos
from streamlit_autorefresh import st_autorefresh

st_autorefresh(interval=15*60*1000, key="f1")
for k,v in {"last_verde_price":0, "perfil_nombre":"ChristianLE", "analizar":True, "last_update_id":0, "show_alpaca":True, "last_buy_time":None, "auto_pilot":True}.items():
    if k not in st.session_state: st.session_state[k]=v
responder_comandos()

st.markdown("""
<style>
[data-testid="stAppViewContainer"]{background:#10131C!important}
.semaforo-box{border:1.5px solid #FFD700; border-radius:16px; padding:16px; background:#181B27; box-shadow:0 0 15px rgba(255,215,0,0.2); margin-bottom:14px}
.semaforo-title{color:#FFD700; font-weight:900; font-size:18px}
.semaforo-sub{color:#8A93A8; font-size:13px; margin-bottom:12px}
.sema-card{border-radius:12px; padding:12px; background:#10131C; min-height:110px}
.card-yellow{border-left:3px solid #FFD700}.card-green{border-left:3px solid #00FF88}.card-red{border-left:3px solid #FF4D4D}
.sema-label{color:#F0F0F0; font-weight:700; font-size:14px}.sema-text{color:#8A93A8; font-size:12px; margin-top:6px}.sema-footer{color:#D4C44A; font-size:12px; margin-top:12px}
/* NUMEROS EXACTOS COMO TU FOTO */
.neon-yellow{color:#FFD700!important; text-shadow:0 0 10px #FFD700, 0 0 20px #FFA500!important; font-weight:900; font-size:38px; line-height:1; letter-spacing:-1px}
.neon-small{font-size:12px; padding:4px 12px; border-radius:20px; display:inline-block; margin-top:6px; font-weight:700}
.neon-green{background:rgba(0,255,136,0.15); color:#00FF88; border:1px solid rgba(0,255,136,0.35)}
.neon-red{background:rgba(255,70,70,0.15); color:#FF6B7A; border:1px solid rgba(255,70,70,0.35)}
.box{border:1.5px solid #FFC800; background:rgba(255,200,0,0.08); padding:14px; border-radius:14px; min-height:85px; color:#E8E6D9}
.backtest{border:1.5px solid #FFC800; background:#1C1A08; padding:18px; border-radius:14px; margin-top:12px; color:#E8E6D9}
.verde-banner{background:rgba(0,255,136,0.15); border:1px solid rgba(0,255,136,0.3); color:#4ADE80; padding:12px; border-radius:10px; font-weight:700; margin-top:12px}
.port-card{border:1.5px solid #00FF88; background:#0B1A13; padding:12px; border-radius:12px; margin-bottom:10px}
</style>
""", unsafe_allow_html=True)

A_KEY=st.secrets["alpaca"]["API_KEY"]
A_SECRET=st.secrets["alpaca"]["SECRET"]
client=TradingClient(A_KEY,A_SECRET,paper=True)

c0,c1,c2,c3=st.columns([2,1,1,0.8])
with c0: symbol=st.selectbox("Activo", ["BTC/USD","ETH/USD","AAPL","SOL/USD"], index=0, label_visibility="collapsed")
with c1: 
    if st.button("🏁 ANALIZAR", type="primary", use_container_width=True):
        st.session_state.analizar=True; st.rerun()
with c2:
    if st.button("🚨 PANICO", use_container_width=True):
        try: client.close_all_positions(cancel_orders=True); st.error("PANICO")
        except Exception as e: st.error(str(e))
with c3:
    st.session_state.auto_pilot = st.toggle("🤖 Auto", value=st.session_state.auto_pilot)

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
ret30=((price/precios[0])-1)*100; vsmax=((price/max1y)-1)*100

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
    sema_color = "VERDE"; sema_txt = "🟢 COMPRAR $10"; puede_comprar = True
else:
    if z > 0 or lr < -0.05:
        sema_color = "ROJO"; sema_txt = "🔴 Freno total"; puede_comprar = False
    else:
        sema_color = "AMARILLO"; sema_txt = "🟡 Esperas, no perder es ganar"; puede_comprar = False

orden_msg = ""
cooldown_ok = True
if st.session_state.last_buy_time:
    cooldown_ok = datetime.now() - st.session_state.last_buy_time > timedelta(hours=1)

if (puede_comprar and cooldown_ok) or (puede_comprar and st.session_state.auto_pilot):
    if st.session_state.auto_pilot or st.session_state.analizar:
        try:
            if abs(price - st.session_state.last_verde_price) > 2:
                monto = 15 if z < -5 else 10
                order = client.submit_order(MarketOrderRequest(symbol=symbol, notional=monto, side=OrderSide.BUY, time_in_force=TimeInForce.GTC))
                st.session_state.last_verde_price = price
                st.session_state.last_buy_time = datetime.now()
                orden_msg = f"ID {str(order.id)[:8]} • ${monto}"
            else:
                orden_msg = "Cooldown precio"
        except Exception as e:
            orden_msg = f"Error {e}"
else:
    if not cooldown_ok and puede_comprar:
        orden_msg = f"⏳ Cooldown 1h - {st.session_state.last_buy_time.strftime('%H:%M')}"

st.markdown(f"""
<div class="semaforo-box">
 <div class="semaforo-title">🏎️ F1 SEMÁFORO - Cómo leer en 30 seg {"🤖 AUTO ON" if st.session_state.auto_pilot else ""}</div>
 <div class="semaforo-sub">Sin fórmulas. Solo 3 preguntas para no perder tu poco dinero.</div>
 <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:10px">
  <div class="sema-card card-yellow"><div class="sema-label">1. ¿Está barato? Fib 0.618</div><div class="sema-text">Línea dorada. Si BTC está abajo de ella, es como aguacate en oferta. ${price:,.0f} vs ${fib:,.0f} normal.</div></div>
  <div class="sema-card card-green"><div class="sema-label">2. ¿Está regalado? z= {z:.2f}</div><div class="sema-text">z -2 a -7 = pánico. La gente lo remata. Tu ejemplo: {z:.2f} = súper regalado.</div></div>
  <div class="sema-card card-red"><div class="sema-label">3. ¿Se cae a pedazos? log {lr*100:.2f}%</div><div class="sema-text">{lr*100:.2f}% = bajó {abs(lr*100):.0f} centavos = normal. -5% = crash = no tocar.</div></div>
 </div>
 <div class="sema-footer">🟢 VERDE = Barato + Regalado + Bajadita chiquita → Compras $10 | 🟡 AMARILLO = Esperas | 🔴 ROJO = Freno total | ⏳ 1h entre compras</div>
</div>
""", unsafe_allow_html=True)

try:
    positions = client.get_all_positions()
    account = client.get_account()
    total = float(account.equity)
    pl_total = float(account.equity) - float(account.last_equity) if hasattr(account,'last_equity') else 0
    pl_color = "#00FF88" if pl_total >=0 else "#FF4D4D"
    barra_txt = f"💰 ALPACA PAPER • Total ${total:,.2f} • P/L <span style='color:{pl_color}'>{pl_total:+.2f}</span> • {symbol} • {orden_msg if orden_msg else 'Listo'}"
    st.markdown(f"""<div style="border:1.5px solid #FFD700; border-radius:14px; padding:10px 16px; background:#0B0F1A; box-shadow:0 0 12px rgba(255,215,0,0.3); margin-bottom:10px"><span style="color:#FFD700; font-weight:800; font-size:12px">{barra_txt}</span> <span style="color:#8A93A8; font-size:10px; float:right">escudería {st.session_state.perfil_nombre}</span></div>""", unsafe_allow_html=True)
    c_alp1, c_alp2 = st.columns(2)
    with c_alp1:
        if st.button("💰 Ver en Alpaca →", use_container_width=True):
            st.session_state.show_alpaca = not st.session_state.show_alpaca
    with c_alp2:
        st.link_button("🔗 Abrir Dashboard Alpaca", "https://app.alpaca.markets/brokerage/dashboard/overview", use_container_width=True)
    if st.session_state.show_alpaca:
        st.markdown(f"<div class='port-card'>🏦 <b>Escudería {st.session_state.perfil_nombre}</b> • Equity ${total:,.2f} • Cash ${float(account.cash):,.2f} • Auto {'ON 🤖' if st.session_state.auto_pilot else 'OFF'}</div>", unsafe_allow_html=True)
        for p in positions:
            pl = float(p.unrealized_pl)
            st.markdown(f"**{'🟢' if pl>=0 else '🔴'} {p.symbol}** {float(p.qty):.8f} • ${float(p.market_value):.2f} • P/L <span style='color:{'#00FF88' if pl>=0 else '#FF4D4D'}'>{pl:+.2f}</span>", unsafe_allow_html=True)

except Exception as e:
    st.error(f"Alpaca: {e}")

# === NUMEROS EXACTOS COMO TU FOTO ===
st.markdown(f"""
<div style="display:grid; grid-template-columns: 1.2fr 0.6fr 0.7fr; gap:12px; margin:16px 0; align-items:start">
 <div><div class="neon-yellow">${price:,.0f}...</div><div class="neon-small neon-green">↑ Fib: ${fib:,.2f}</div></div>
 <div><div class="neon-yellow">{z:.2f}</div><div class="neon-small neon-green">↑ Compra si < -2</div></div>
 <div><div class="neon-yellow">{lr*100:.3f}%</div><div class="neon-small neon-red">↓ -0.8% a -0.05%</div></div>
</div>
""", unsafe_allow_html=True)

st.markdown(f"<div style='background:{'#00FF88' if puede_comprar else '#2A2A2A'}; color:{'#000' if puede_comprar else '#888'}; font-weight:900; padding:12px; border-radius:10px; text-align:center; margin-bottom:12px'>{sema_txt} • {orden_msg}</div>", unsafe_allow_html=True)

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

b1,b2,b3,b4=st.columns(4)
with b1: st.markdown(f"<div class='box'>⏱️ <b>24 HORAS</b><br>{ret24:.2f}%</div>", unsafe_allow_html=True)
with b2: st.markdown(f"<div class='box'>📅 <b>7 DÍAS</b><br>{ret7:.2f}%</div>", unsafe_allow_html=True)
with b3: st.markdown(f"<div class='box'>📅 <b>30 DÍAS</b><br>{ret30:.2f}%</div>", unsafe_allow_html=True)
with b4: st.markdown(f"<div class='box'>🏔️ <b>vs MAX 1 AÑO</b><br>{vsmax:.2f}%</div>", unsafe_allow_html=True)

st.markdown(f"<div class='backtest'>🧠 <b>BACKTEST</b><br>{len(casos)} casos similares<br><span style='color:#FFD700; font-weight:900'>Prob rebote 24h: {prob:.1f}%</span> • 24h {avg24:.2f}% | 7d {avg7:.2f}%<br><br>⚠️ {sema_color}: {sema_txt} • {orden_msg}</div>", unsafe_allow_html=True)
st.markdown(f"<div class='verde-banner'>🟢 {sema_color}: {sema_txt} • {orden_msg} • Auto {'🤖 ON' if st.session_state.auto_pilot else 'OFF'}</div>", unsafe_allow_html=True)

try:
    acc = client.get_account()
    msg = (f"<b>🏁 F1 ESCUDERIA {st.session_state.perfil_nombre}</b>\n📊 <b>{symbol}</b> ${price:,.2f} • {sema_txt}\n🏦 Equity ${float(acc.equity):,.2f} • Cash ${float(acc.cash):,.2f}\n📐 Fib ${fib:,.2f} | z {z:.2f} | log {lr*100:.3f}%\n⏱ 24h {ret24:+.2f}% | 7d {ret7:+.2f}% | 30d {ret30:+.2f}%\n🔬 Backtest {len(casos)} Prob {prob:.1f}%\n🚦 {sema_color} | {orden_msg} | Auto {'ON' if st.session_state.auto_pilot else 'OFF'}\n")
    notificar_f1(msg)
except: pass
