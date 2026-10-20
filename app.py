import streamlit as st
st.set_page_config(page_title="F1 SEMAFORO V27 PISTA HD", layout="wide", page_icon="🏁")
import yfinance as yf, numpy as np, matplotlib.pyplot as plt
from datetime import datetime, timedelta
import os, json
from matplotlib.patches import Rectangle
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
.neon-yellow{color:#FFD700!important; font-weight:900; font-size:38px; line-height:1; letter-spacing:-1px; text-shadow:none!important}
.neon-small{font-size:12px; padding:4px 12px; border-radius:20px; display:inline-block; margin-top:6px; font-weight:700}
.neon-green{background:rgba(0,255,136,0.15); color:#00FF88; border:1px solid rgba(0,255,136,0.35)}
.neon-red{background:rgba(255,70,70,0.15); color:#FF6B7A; border:1px solid rgba(255,70,70,0.35)}
.box{border:1.5px solid #FFC800; background:rgba(255,200,0,0.08); padding:14px; border-radius:14px; min-height:85px; color:#E8E6D9}
.backtest{border:1.5px solid #FFC800; background:#1C1A08; padding:18px; border-radius:14px; margin-top:12px; color:#E8E6D9}
.verde-banner{background:rgba(0,255,136,0.15); border:1px solid rgba(0,255,136,0.3); color:#4ADE80; padding:12px; border-radius:10px; font-weight:700; margin-top:12px}
.port-card{border:1.5px solid #00FF88; background:#0B1A13; padding:12px; border-radius:12px; margin-bottom:10px}
.equity-box{border:1.5px solid #00FF88; background:#0B1A13; padding:16px; border-radius:14px; margin-top:12px}
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
ret24=np.log(precios[-1]/precios[-2])*100 if len(precios)>=2 else -0.59
ret7=((price/precios[-7])-1)*100 if len(precios)>=7 else -0.23
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
avg24=np.mean(g24) if g24 else -0.36; avg7=np.mean(g7) if g7 else 1.67
if z < -2 and price < fib and -0.008 < lr < -0.0005:
    sema_color = "VERDE"; sema_txt = "🟢 COMPRAR $10"; puede_comprar = True
else:
    if z > 0 or lr < -0.05:
        sema_color = "ROJO"; sema_txt = "🔴 Freno total"; puede_comprar = False
    else:
        sema_color = "AMARILLO"; sema_txt = "🟡 Esperas"; puede_comprar = False

orden_msg = ""; venta_msg = ""; cooldown_ok = True
if st.session_state.last_buy_time:
    cooldown_ok = datetime.now() - st.session_state.last_buy_time > timedelta(hours=1)

st.markdown(f"""
<div class="semaforo-box">
 <div class="semaforo-title">🏎️ F1 SEMÁFORO - Cómo leer en 30 seg {"🤖 AUTO ON" if st.session_state.auto_pilot else ""}</div>
 <div class="semaforo-sub">Sin fórmulas. Solo 3 preguntas para no perder tu poco dinero.</div>
 <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:10px">
  <div class="sema-card card-yellow"><div class="sema-label">1. ¿Está barato? Fib 0.618</div><div class="sema-text">Si BTC está abajo, es aguacate en oferta. ${price:,.0f} vs ${fib:,.0f} normal.</div></div>
  <div class="sema-card card-green"><div class="sema-label">2. ¿Está regalado? z= {z:.2f}</div><div class="sema-text">z {z:.2f}= súper regalado.</div></div>
  <div class="sema-card card-red"><div class="sema-label">3. ¿Se cae a pedazos? log {lr*100:.2f}%</div><div class="sema-text">{lr*100:.2f}% = normal. -5% = crash.</div></div>
 </div>
 <div class="sema-footer">🟢 VERDE = Compra $10-$15 | 🟡 AMARILLO = Esperas | 🔴 ROJO = Freno | ⏳ 1h | 💰 Vende 50% si +2%</div>
</div>
""", unsafe_allow_html=True)

# BARRA + PISTA HD
try:
    positions = client.get_all_positions()
    account = client.get_account()
    total = float(account.equity)
    pl_total = total - 100000

    equity_file = "equity_log.json"; tp_file = "tp_marks.json"; buy_file = "buy_marks.json"
    hist=[]; tp_marks=[]; buy_marks=[]
    if os.path.exists(equity_file):
        try:
            with open(equity_file,"r") as f: hist=json.load(f)
        except: hist=[]
    if os.path.exists(tp_file):
        try:
            with open(tp_file,"r") as f: tp_marks=json.load(f)
        except: tp_marks=[]
    if os.path.exists(buy_file):
        try:
            with open(buy_file,"r") as f: buy_marks=json.load(f)
        except: buy_marks=[]

    hist.append({"t": datetime.now().strftime("%m-%d %H:%M"), "eq": total})
    hist=hist[-200:]
    with open(equity_file,"w") as f: json.dump(hist,f)

    # COMPRA
    if (puede_comprar and cooldown_ok) or (puede_comprar and st.session_state.auto_pilot):
        if st.session_state.auto_pilot or st.session_state.analizar:
            try:
                if abs(price - st.session_state.last_verde_price) > 2:
                    monto = 15 if z < -5 else 10
                    order = client.submit_order(MarketOrderRequest(symbol=symbol, notional=monto, side=OrderSide.BUY, time_in_force=TimeInForce.GTC))
                    st.session_state.last_verde_price = price
                    st.session_state.last_buy_time = datetime.now()
                    orden_msg = f"ID {str(order.id)[:8]} • ${monto}"
                    buy_marks.append({"idx": len(hist)-1, "symbol": symbol, "price": float(price), "t": datetime.now().strftime("%H:%M")})
                    buy_marks=buy_marks[-20:]
                    with open(buy_file,"w") as f: json.dump(buy_marks,f)
                else:
                    orden_msg = "Cooldown precio"
            except Exception as e:
                orden_msg = f"Error {e}"
    else:
        if not cooldown_ok and puede_comprar:
            orden_msg = f"⏳ Cooldown 1h - {st.session_state.last_buy_time.strftime('%H:%M')}"

    # VENTA 50% SI +2%
    for p in positions:
        try:
            pct = float(p.unrealized_plpc)*100 if hasattr(p,'unrealized_plpc') else (float(p.unrealized_pl)/float(p.cost_basis)*100 if float(p.cost_basis)!=0 else 0)
            if pct >= 2.0 and st.session_state.auto_pilot:
                qty_vender = float(p.qty)*0.5
                if qty_vender>0:
                    client.submit_order(MarketOrderRequest(symbol=p.symbol, qty=qty_vender, side=OrderSide.SELL, time_in_force=TimeInForce.GTC))
                    venta_msg = f"💰 TP {p.symbol} +{pct:.2f}%"
                    tp_marks.append({"idx": len(hist)-1, "symbol": p.symbol, "pct": pct, "eq": total, "t": datetime.now().strftime("%H:%M")})
                    tp_marks=tp_marks[-20:]
                    with open(tp_file,"w") as f: json.dump(tp_marks,f)
                    notificar_f1(f"<b>💰 TAKE PROFIT + MARCA LLANTA</b>\n{p.symbol} +{pct:.2f}% vendió 50%\nVuelta {len(hist)} Equity ${total:,.2f}")
        except: pass

    pl_color="#00FF88" if pl_total>=0 else "#FF4D4D"
    barra_txt=f"💰 ALPACA PAPER • Total ${total:,.2f} • P/L <span style='color:{pl_color}'>{pl_total:+.2f}</span> • {symbol} • {orden_msg} {venta_msg}"
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
            pl=float(p.unrealized_pl); pct=float(p.unrealized_plpc)*100 if hasattr(p,'unrealized_plpc') else 0
            st.markdown(f"**{'🟢' if pl>=0 else '🔴'} {p.symbol}** {float(p.qty):.6f} • ${float(p.market_value):.2f} • P/L {pl:+.2f} ({pct:+.2f}%)", unsafe_allow_html=True)

    if len(hist) > 1:
        st.markdown("<div class='equity-box'>🏁 <b>CIRCUIT INTERLAGOS HD - MARCAS DE LLANTA</b> • 🟢 Compra | 💨 Take Profit +2%</div>", unsafe_allow_html=True)
        eq_vals=np.array([h["eq"] for h in hist])
        initial=100000; pnl=eq_vals[-1]-initial; pnl_pct=(eq_vals[-1]/initial-1)*100
        eq_min, eq_max=np.min(eq_vals), np.max(eq_vals)
        eq_norm=(eq_vals-eq_min)/(eq_max-eq_min+1) if eq_max!=eq_min else np.zeros_like(eq_vals)*0.5+0.5
        x=np.linspace(0,12,len(eq_vals))
        # Curva tipo Interlagos S de Senna + curva lenta final
        track_center_y=np.sin(x*0.6)*0.5 + np.sin(x*1.8)*0.25 + np.cos(x*0.4)*0.15
        track_width=0.55
        fig2, ax2=plt.subplots(figsize=(12,5))
        fig2.patch.set_facecolor("#0F0F0F"); ax2.set_facecolor("#2B2B2B")
        # Asfalto
        ax2.fill_between(x, track_center_y-track_width, track_center_y+track_width, color="#2B2B2B", zorder=1)
        # Bordes blancos anchos
        ax2.plot(x, track_center_y+track_width, color="white", linewidth=3, zorder=2)
        ax2.plot(x, track_center_y-track_width, color="white", linewidth=3, zorder=2)
        # Piano rojo/blanco más visible
        for i in range(0,len(x),3):
            ax2.plot([x[i],x[i]], [track_center_y[i]+track_width, track_center_y[i]+track_width+0.08], color="#FF0000" if i%2==0 else "white", linewidth=4, zorder=3)
            ax2.plot([x[i],x[i]], [track_center_y[i]-track_width, track_center_y[i]-track_width-0.08], color="#FF0000" if i%2==0 else "white", linewidth=4, zorder=3)
        # Meta
        ax2.axvline(x[0], color="white", linewidth=3, zorder=4)
        for y in np.arange(track_center_y[0]-track_width, track_center_y[0]+track_width, 0.06):
            ax2.add_patch(Rectangle((x[0]-0.08,y),0.08,0.03,color="black" if int(y*10)%2==0 else "white",zorder=5))
        # Trazada amarilla - tu equity
        racing_line_y=track_center_y + (eq_norm-0.5)*(track_width*1.2)
        ax2.plot(x, racing_line_y, color="#FFD700", linewidth=4, zorder=6, solid_capstyle='round')
        ax2.plot(x, racing_line_y, color="#FFA500", linewidth=1.5, alpha=0.6, zorder=7)
        # MARCAS DE COMPRA - humo verde
        for mark in buy_marks:
            idx=mark["idx"]
            if idx < len(x):
                ax2.scatter([x[idx]], [racing_line_y[idx]], s=320, color="#00FF88", marker="o", edgecolors="white", linewidths=2, zorder=9)
                ax2.scatter([x[idx]], [racing_line_y[idx]], s=600, color="#00FF88", alpha=0.15, zorder=8)
                ax2.text(x[idx], racing_line_y[idx]-0.28, f"🟢 BUY {mark['symbol']}", color="#00FF88", fontsize=7.5, fontweight="bold", ha="center", zorder=10, bbox=dict(boxstyle="round,pad=0.2", facecolor="black", edgecolor="#00FF88", alpha=0.9))
        # MARCAS DE TP - estrella + humo blanco
        for mark in tp_marks:
            idx=mark["idx"]
            if idx < len(x):
                ax2.scatter([x[idx]], [racing_line_y[idx]], s=400, color="#00FF88", marker="*", edgecolors="white", linewidths=1.8, zorder=11)
                ax2.scatter([x[idx]], [racing_line_y[idx]+0.08], s=200, color="white", alpha=0.35, zorder=10)
                ax2.text(x[idx], racing_line_y[idx]+0.30, f"💨 TP {mark['symbol']}\n+{mark['pct']:.1f}%", color="#FFD700", fontsize=8, fontweight="bold", ha="center", zorder=12, bbox=dict(boxstyle="round,pad=0.3", facecolor="black", edgecolor="#FFD700", alpha=0.9))
        # Carrito final
        ax2.scatter([x[-1]], [racing_line_y[-1]], s=260, color="#00FF88", edgecolors="white", linewidths=2.5, zorder=14)
        ax2.text(x[-1]+0.2, racing_line_y[-1], f"🏎️ ${eq_vals[-1]:,.0f}\n{pnl_pct:+.2f}%", color="#00FF88" if pnl>=0 else "#FF4D4D", fontsize=10, fontweight="bold", zorder=15, bbox=dict(boxstyle="round,pad=0.4", facecolor="#0F0F0F", edgecolor="#FFD700", linewidth=1.2))
        # Stats
        ax2.text(0.02,0.96,f"🏁 VUELTA {len(eq_vals)} | P/L ${pnl:+.0f} ({pnl_pct:+.2f}%)\n🟢 BUYS: {len(buy_marks)} | 💨 TPs: {len(tp_marks)}\n🏆 MAX ${eq_max:,.0f} | MIN ${eq_min:,.0f}", transform=ax2.transAxes, color="white", fontsize=9, family="monospace", bbox=dict(boxstyle="round,pad=0.5", facecolor="black", edgecolor="#00FF88" if pnl>=0 else "#FF4D4D", linewidth=1.5), verticalalignment='top', zorder=16)
        ax2.set_xlim(-0.6,13); ax2.set_ylim(-1.6,1.6); ax2.axis('off')
        fig2.tight_layout(); st.pyplot(fig2)
        if buy_marks or tp_marks:
            last_events = sorted(buy_marks[-2:] + tp_marks[-2:], key=lambda x: x["idx"])[-3:]
            st.caption("Últimos: " + " | ".join([f"{'BUY' if 'price' in e else 'TP'} {e['symbol']} {e['t']}" for e in last_events]))
except Exception as e:
    st.error(f"Alpaca: {e}")

# NUMEROS SIN GLOW
st.markdown(f"""
<div style="display:grid; grid-template-columns: 1.2fr 0.6fr 0.7fr; gap:12px; margin:16px 0">
 <div><div class="neon-yellow">${price:,.0f}...</div><div class="neon-small neon-green">↑ Fib: ${fib:,.2f}</div></div>
 <div><div class="neon-yellow">{z:.2f}</div><div class="neon-small neon-green">↑ Compra si < -2</div></div>
 <div><div class="neon-yellow">{lr*100:.3f}%</div><div class="neon-small neon-red">↓ -0.8% a -0.05%</div></div>
</div>
""", unsafe_allow_html=True)
st.markdown(f"<div style='background:{'#00FF88' if puede_comprar else '#2A2A2A'}; color:{'#000' if puede_comprar else '#888'}; font-weight:900; padding:12px; border-radius:10px; text-align:center'>{sema_txt} • {orden_msg} {venta_msg}</div>", unsafe_allow_html=True)
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
st.markdown(f"<div class='backtest'>🧠 <b>BACKTEST</b><br>{len(casos)} casos | Prob rebote 24h: {prob:.1f}% • 24h {avg24:.2f}% | 7d {avg7:.2f}%<br>⚠️ {sema_color}: {sema_txt} • {orden_msg} {venta_msg}</div>", unsafe_allow_html=True)
st.markdown(f"<div class='verde-banner'>🟢 {sema_color}: {sema_txt} • {orden_msg} {venta_msg} • Auto {'🤖 ON' if st.session_state.auto_pilot else 'OFF'}</div>", unsafe_allow_html=True)
try:
    acc = client.get_account()
    msg = (f"<b>🏁 F1 V27 INTERLAGOS HD</b>\n📊 {symbol} ${price:,.2f} • {sema_txt}\n🏦 Equity ${float(acc.equity):,.2f} • P/L ${float(acc.equity)-100000:+.2f}\n🟢 Buys {len(buy_marks) if 'buy_marks' in locals() else 0} | 💨 TPs {len(tp_marks) if 'tp_marks' in locals() else 0}\n🚦 {sema_color} | {orden_msg} {venta_msg}\n")
    notificar_f1(msg)
except: pass
