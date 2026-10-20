import streamlit as st
st.set_page_config(page_title="F1 SEMAFORO V31 TODO", layout="wide", page_icon="💎")
import yfinance as yf, numpy as np, matplotlib.pyplot as plt
from datetime import datetime, timedelta
import os, json, pandas as pd
from matplotlib.patches import Rectangle
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from bot_telegram import notificar_f1, responder_comandos
from streamlit_autorefresh import st_autorefresh

st_autorefresh(interval=15*60*1000, key="f1")
for k,v in {"last_verde_price":0, "perfil_nombre":"ChristianLE", "analizar":True, "last_update_id":0, "show_alpaca":True, "last_buy_time":None, "auto_pilot":True, "coins":0, "modo_diamante":True}.items():
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
.neon-yellow{color:#FFD700!important; font-weight:900; font-size:38px; line-height:1; letter-spacing:-1px}
.neon-small{font-size:12px; padding:4px 12px; border-radius:20px; display:inline-block; margin-top:6px; font-weight:700}
.neon-green{background:rgba(0,255,136,0.15); color:#00FF88; border:1px solid rgba(0,255,136,0.35)}
.neon-red{background:rgba(255,70,70,0.15); color:#FF6B7A; border:1px solid rgba(255,70,70,0.35)}
.box{border:1.5px solid #FFC800; background:rgba(255,200,0,0.08); padding:14px; border-radius:14px; min-height:85px; color:#E8E6D9}
.backtest{border:1.5px solid #FFC800; background:#1C1A08; padding:18px; border-radius:14px; margin-top:12px; color:#E8E6D9}
.verde-banner{background:rgba(0,255,136,0.15); border:1px solid rgba(0,255,136,0.3); color:#4ADE80; padding:12px; border-radius:10px; font-weight:700; margin-top:12px}
.port-card{border:1.5px solid #00FF88; background:#0B1A13; padding:12px; border-radius:12px; margin-bottom:10px}
.equity-box{border:1.5px solid #00FF88; background:#0B1A13; padding:16px; border-radius:14px; margin-top:12px}
.diamond-card{border:2px solid #00FFFF; background:linear-gradient(135deg, #0B1A1A 0%, #0F2A2A 100%); border-radius:14px; padding:14px; box-shadow:0 0 15px rgba(0,255,255,0.2); margin-bottom:10px; color:#E8E6D9}
.leaderboard{border:2px solid #FFD700; background:#0B0F1A; border-radius:14px; padding:16px; margin-top:12px}
@keyframes driveCorrect { 0% { transform: translateX(0); } 100% { transform: translateX(calc(-100vw - 600px)); } }
@keyframes flagwave { 0% { transform: rotate(-6deg); } 100% { transform: rotate(12deg); } }
@keyframes road { 0% { background-position: 0 0; } 100% { background-position: 80px 0; } }
@keyframes smokeTrail { 0% { transform: translateX(0); opacity:0; } 15% { opacity:0.7; } 100% { transform: translateX(calc(-100vw - 600px)); opacity:0; } }
@keyframes diamondShine { 0% { filter: hue-rotate(0deg) brightness(1.2) drop-shadow(0 0 8px gold); } 50% { filter: hue-rotate(30deg) brightness(1.6) drop-shadow(0 0 15px cyan); } 100% { filter: hue-rotate(0deg) brightness(1.2) drop-shadow(0 0 8px gold); } }
@keyframes coinFloat { 0% { transform: translateY(0); } 50% { transform: translateY(-5px); } 100% { transform: translateY(0); } }
</style>
""", unsafe_allow_html=True)

# CARRITO V28.1 ORIGINAL + AGREGADOS DIAMANTE Y COINS (NO QUITA NADA)
modo_txt = "💎 DIAMANTE" if st.session_state.modo_diamante else "🏁 NORMAL"
car_filter = "filter: drop-shadow(0 0 8px rgba(255,215,0,0.8)); animation: driveCorrect 5.5s linear infinite, diamondShine 1.2s ease-in-out infinite;" if st.session_state.modo_diamante else "filter: drop-shadow(0 0 8px rgba(255,215,0,0.8));"
car_html = f"""
<div style="position:relative; width:100%; height:118px; background: linear-gradient(90deg, #0F0F0F 0%, #1A1A1A 50%, #0F0F0F 100%); border:2px solid #FFD700; border-radius:16px; overflow:hidden; margin-bottom:14px; box-shadow:0 0 25px rgba(255,215,0,0.35)">
  <div style="position:absolute; top:8px; left:16px; color:#FFD700; font-weight:900; font-size:11px; letter-spacing:2px; z-index:10">🏁 ESCUDERIA CHRISTIANLE • V31 • {modo_txt} • 342 km/h • 🪙 {st.session_state.coins}</div>
  <div style="position:absolute; top:8px; right:16px; color:#00FF88; font-weight:800; font-size:10px; z-index:10">🏎️ PA' ADELANTE + 💎 + 🪙</div>
  <div style="position:absolute; top:30px; right:-350px; animation: driveCorrect 5.5s linear infinite; {car_filter} font-size:62px; z-index:5;">🏎️</div>
  <div style="position:absolute; top:20px; left:22px; animation: flagwave 0.4s ease-in-out infinite alternate; font-size:44px; z-index:6">🏁</div>
  <div style="position:absolute; bottom:10px; left:0; width:100%; height:6px; background: repeating-linear-gradient(90deg, white 0 22px, black 22px 44px); animation: road 0.3s linear infinite; z-index:2"></div>
  <div style="position:absolute; bottom:18px; right:-120px; width:90px; height:5px; background:radial-gradient(rgba(255,255,255,0.5), transparent); filter:blur(2px); animation: smokeTrail 5.5s linear infinite; z-index:4"></div>
  <!-- AGREGADO: monedas flotando -->
  <div style="position:absolute; top:38px; left:65%; animation: coinFloat 0.8s ease-in-out infinite; font-size:22px; z-index:6">🪙</div>
  <div style="position:absolute; top:40px; left:30%; animation: coinFloat 0.8s ease-in-out infinite 0.4s; font-size:20px; z-index:6">💎</div>
</div>
"""
st.markdown(car_html, unsafe_allow_html=True)

c_d1, c_d2 = st.columns([3,1])
with c_d2:
    st.session_state.modo_diamante = st.toggle("💎 Modo Diamante", value=st.session_state.modo_diamante)

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
 <div class="semaforo-title">🏎️ F1 SEMÁFORO V31 PA' ADELANTE 💎 {"🤖 AUTO ON" if st.session_state.auto_pilot else ""} • 🪙 {st.session_state.coins}</div>
 <div class="semaforo-sub">Sin fórmulas. Solo 3 preguntas. Carrito pa' adelante + diamante + coins</div>
 <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:10px">
  <div class="sema-card card-yellow"><div class="sema-label">1. ¿Está barato? Fib 0.618</div><div class="sema-text">${price:,.0f} vs ${fib:,.0f}</div></div>
  <div class="sema-card card-green"><div class="sema-label">2. ¿Está regalado? z= {z:.2f}</div><div class="sema-text">z {z:.2f}</div></div>
  <div class="sema-card card-red"><div class="sema-label">3. ¿Se cae? log {lr*100:.2f}%</div><div class="sema-text">{lr*100:.2f}%</div></div>
 </div>
 <div class="sema-footer">🟢 VERDE = Compra $10-$15 | 💰 Vende 50% si +2% | ⏳ 1h | 💎 +100 coins por BUY</div>
</div>
""", unsafe_allow_html=True)

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

    if (puede_comprar and cooldown_ok) or (puede_comprar and st.session_state.auto_pilot):
        if st.session_state.auto_pilot or st.session_state.analizar:
            try:
                if abs(price - st.session_state.last_verde_price) > 2:
                    monto = 15 if z < -5 else 10
                    order = client.submit_order(MarketOrderRequest(symbol=symbol, notional=monto, side=OrderSide.BUY, time_in_force=TimeInForce.GTC))
                    st.session_state.last_verde_price = price
                    st.session_state.last_buy_time = datetime.now()
                    st.session_state.coins += 100
                    orden_msg = f"ID {str(order.id)[:8]} • ${monto} • +100 🪙"
                    buy_marks.append({"idx": len(hist)-1, "symbol": symbol, "price": float(price), "t": datetime.now().strftime("%H:%M")})
                    buy_marks=buy_marks[-50:]
                    with open(buy_file,"w") as f: json.dump(buy_marks,f)
                else:
                    orden_msg = "Cooldown precio"
            except Exception as e:
                orden_msg = f"Error {e}"
    else:
        if not cooldown_ok and puede_comprar:
            orden_msg = f"⏳ Cooldown 1h - {st.session_state.last_buy_time.strftime('%H:%M')}"

    for p in positions:
        try:
            pct = float(p.unrealized_plpc)*100 if hasattr(p,'unrealized_plpc') else (float(p.unrealized_pl)/float(p.cost_basis)*100 if float(p.cost_basis)!=0 else 0)
            if pct >= 2.0 and st.session_state.auto_pilot:
                qty_vender = float(p.qty)*0.5
                if qty_vender>0:
                    client.submit_order(MarketOrderRequest(symbol=p.symbol, qty=qty_vender, side=OrderSide.SELL, time_in_force=TimeInForce.GTC))
                    venta_msg = f"💰 TP {p.symbol} +{pct:.2f}%"
                    st.session_state.coins += 200
                    tp_marks.append({"idx": len(hist)-1, "symbol": p.symbol, "pct": pct, "eq": total, "t": datetime.now().strftime("%H:%M")})
                    tp_marks=tp_marks[-30:]
                    with open(tp_file,"w") as f: json.dump(tp_marks,f)
                    notificar_f1(f"<b>💰 TAKE PROFIT +200 🪙💎</b>\n{p.symbol} +{pct:.2f}%")
        except: pass

    pl_color="#00FF88" if pl_total>=0 else "#FF4D4D"
    barra_txt=f"💰 ALPACA PAPER • Total ${total:,.2f} • P/L <span style='color:{pl_color}'>{pl_total:+.2f}</span> • {symbol} • 🪙 {st.session_state.coins} • {orden_msg} {venta_msg}"
    st.markdown(f"""<div style="border:1.5px solid #FFD700; border-radius:14px; padding:10px 16px; background:#0B0F1A; box-shadow:0 0 12px rgba(255,215,0,0.3); margin-bottom:10px"><span style="color:#FFD700; font-weight:800; font-size:12px">{barra_txt}</span> <span style="color:#8A93A8; font-size:10px; float:right">escudería {st.session_state.perfil_nombre} 💎</span></div>""", unsafe_allow_html=True)
    c_alp1, c_alp2 = st.columns(2)
    with c_alp1:
        if st.button("💰 Ver en Alpaca →", use_container_width=True):
            st.session_state.show_alpaca = not st.session_state.show_alpaca
    with c_alp2:
        st.link_button("🔗 Abrir Dashboard Alpaca", "https://app.alpaca.markets/brokerage/dashboard/overview", use_container_width=True)
    if st.session_state.show_alpaca:
        st.markdown(f"<div class='port-card'>🏦 <b>Escudería {st.session_state.perfil_nombre}</b> • Equity ${total:,.2f} • Cash ${float(account.cash):,.2f} • Auto {'ON 🤖' if st.session_state.auto_pilot else 'OFF'} • 🪙 {st.session_state.coins}</div>", unsafe_allow_html=True)
        for p in positions:
            pl=float(p.unrealized_pl); pct=float(p.unrealized_plpc)*100 if hasattr(p,'unrealized_plpc') else 0
            st.markdown(f"**{'🟢' if pl>=0 else '🔴'} {p.symbol}** {float(p.qty):.6f} • ${float(p.market_value):.2f} • P/L {pl:+.2f} ({pct:+.2f}%)", unsafe_allow_html=True)

    if len(hist) > 1:
        # INTERLAGOS ORIGINAL + HEATMAP AGREGADO (no quita nada)
        st.markdown("<div class='equity-box'>🏁 <b>CIRCUIT INTERLAGOS HD V31 + HEATMAP 🔥 + DIAMANTE 💎</b> • 🟢 BUY | 💨 TP +2% | Rojo=zona compras</div>", unsafe_allow_html=True)
        eq_vals=np.array([h["eq"] for h in hist])
        initial=100000; pnl=eq_vals[-1]-initial; pnl_pct=(eq_vals[-1]/initial-1)*100
        eq_min, eq_max=np.min(eq_vals), np.max(eq_vals)
        eq_norm=(eq_vals-eq_min)/(eq_max-eq_min+1) if eq_max!=eq_min else np.zeros_like(eq_vals)*0.5+0.5
        x=np.linspace(0,12,len(eq_vals))
        track_center_y=np.sin(x*0.6)*0.5 + np.sin(x*1.8)*0.25 + np.cos(x*0.4)*0.15
        track_width=0.55
        fig2, ax2=plt.subplots(figsize=(12,5))
        fig2.patch.set_facecolor("#0F0F0F"); ax2.set_facecolor("#2B2B2B")
        # HEATMAP CALC - agregado sin quitar pista original
        heat = np.zeros(len(x))
        for bm in buy_marks:
            if bm["idx"] < len(heat): heat[bm["idx"]] += 1
        heat_smooth = np.convolve(heat, np.ones(5)/5, mode='same')
        heat_norm = heat_smooth / (np.max(heat_smooth) if np.max(heat_smooth)>0 else 1)
        # Pista con heatmap leve
        for i in range(len(x)-1):
            if heat_norm[i]>0:
                alpha = 0.25 + heat_norm[i]*0.5
                color = plt.cm.hot(0.3 + heat_norm[i]*0.7)
                ax2.fill_between([x[i], x[i+1]], [track_center_y[i]-track_width, track_center_y[i+1]-track_width], [track_center_y[i]+track_width, track_center_y[i+1]+track_width], color=color, alpha=alpha, zorder=1)
            else:
                ax2.fill_between([x[i], x[i+1]], [track_center_y[i]-track_width, track_center_y[i+1]-track_width], [track_center_y[i]+track_width, track_center_y[i+1]+track_width], color="#2B2B2B", zorder=1)
        ax2.plot(x, track_center_y+track_width, color="white", linewidth=3, zorder=2)
        ax2.plot(x, track_center_y-track_width, color="white", linewidth=3, zorder=2)
        for i in range(0,len(x),3):
            ax2.plot([x[i],x[i]], [track_center_y[i]+track_width, track_center_y[i]+track_width+0.08], color="#FF0000" if i%2==0 else "white", linewidth=4, zorder=3)
            ax2.plot([x[i],x[i]], [track_center_y[i]-track_width, track_center_y[i]-track_width-0.08], color="#FF0000" if i%2==0 else "white", linewidth=4, zorder=3)
        ax2.axvline(x[0], color="white", linewidth=3, zorder=4)
        for y in np.arange(track_center_y[0]-track_width, track_center_y[0]+track_width, 0.06):
            ax2.add_patch(Rectangle((x[0]-0.08,y),0.08,0.03,color="black" if int(y*10)%2==0 else "white",zorder=5))
        racing_line_y=track_center_y + (eq_norm-0.5)*(track_width*1.2)
        ax2.plot(x, racing_line_y, color="#00FFFF" if st.session_state.modo_diamante else "#FFD700", linewidth=4, zorder=6)
        ax2.plot(x, racing_line_y, color="#FFD700" if st.session_state.modo_diamante else "#FFA500", linewidth=1.5, alpha=0.6, zorder=7)
        for mark in buy_marks:
            idx=mark["idx"]
            if idx < len(x):
                ax2.scatter([x[idx]], [racing_line_y[idx]], s=320, color="#00FF88", marker="o", edgecolors="white", linewidths=2, zorder=9)
                ax2.scatter([x[idx]], [racing_line_y[idx]], s=600, color="#00FF88", alpha=0.15, zorder=8)
                ax2.text(x[idx], racing_line_y[idx]-0.28, f"🟢 BUY {mark['symbol']}", color="#00FF88", fontsize=7.5, fontweight="bold", ha="center", zorder=10, bbox=dict(boxstyle="round,pad=0.2", facecolor="black", edgecolor="#00FF88", alpha=0.9))
        for mark in tp_marks:
            idx=mark["idx"]
            if idx < len(x):
                ax2.scatter([x[idx]], [racing_line_y[idx]], s=400, color="#00FF88", marker="*", edgecolors="white", linewidths=1.8, zorder=11)
                ax2.text(x[idx], racing_line_y[idx]+0.30, f"💨 TP {mark['symbol']}\n+{mark['pct']:.1f}%", color="#FFD700", fontsize=8, fontweight="bold", ha="center", zorder=12, bbox=dict(boxstyle="round,pad=0.3", facecolor="black", edgecolor="#FFD700", alpha=0.9))
        ax2.scatter([x[-1]], [racing_line_y[-1]], s=260, color="#00FFFF" if st.session_state.modo_diamante else "#00FF88", edgecolors="white", linewidths=2.5, zorder=14)
        ax2.text(x[-1]+0.2, racing_line_y[-1], f"🏎️ ${eq_vals[-1]:,.0f}\n{pnl_pct:+.2f}% 🪙{st.session_state.coins}", color="#00FF88" if pnl>=0 else "#FF4D4D", fontsize=10, fontweight="bold", zorder=15, bbox=dict(boxstyle="round,pad=0.4", facecolor="#0F0F0F", edgecolor="#FFD700", linewidth=1.2))
        ax2.text(0.02,0.96,f"🏁 VUELTA {len(eq_vals)} | P/L ${pnl:+.0f} ({pnl_pct:+.2f}%)\n🟢 BUYS: {len(buy_marks)} | 💨 TPs: {len(tp_marks)}\n🏆 MAX ${eq_max:,.0f} | 🔥 Heatmap ON", transform=ax2.transAxes, color="white", fontsize=9, family="monospace", bbox=dict(boxstyle="round,pad=0.5", facecolor="black", edgecolor="#00FF88" if pnl>=0 else "#FF4D4D", linewidth=1.5), verticalalignment='top', zorder=16)
        ax2.set_xlim(-0.6,13); ax2.set_ylim(-1.6,1.6); ax2.axis('off')
        fig2.tight_layout(); st.pyplot(fig2)

    # TABLA POSICIONES AGREGADA - ABAJO DE TODO, NO QUITA NADA
    leaderboard_data=[]
    for p in positions:
        try:
            pct=float(p.unrealized_plpc)*100 if hasattr(p,'unrealized_plpc') else 0
            leaderboard_data.append({"symbol":p.symbol, "qty":float(p.qty), "value":float(p.market_value), "pl":float(p.unrealized_pl), "pct":pct})
        except: pass
    if leaderboard_data:
        st.markdown(f"""<div class="leaderboard"><div style="color:#FFD700; font-weight:900; font-size:12px; margin-bottom:8px">🏆 TABLA DE POSICIONES • V31 ULTIMATE • NO QUITA NADA, SOLO AGREGA</div></div>""", unsafe_allow_html=True)
        for i, row in e
