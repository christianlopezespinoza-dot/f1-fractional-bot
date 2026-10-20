import streamlit as st
st.set_page_config(page_title="F1 V35 TODO SIN QUITAR", layout="wide", page_icon="💎")
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
for k,v in {"last_verde_price":0, "perfil_nombre":"ChristianLE", "analizar":True, "last_update_id":0, "show_alpaca":True, "last_buy_time":None, "auto_pilot":True, "coins":0, "modo_diamante":False}.items():
    if k not in st.session_state: st.session_state[k]=v
responder_comandos()

st.markdown("""
<style>
[data-testid="stAppViewContainer"]{background:#10131C!important}
.semaforo-box{border:1.5px solid #FFD700; border-radius:16px; padding:16px; background:#181B27; box-shadow:0 0 15px rgba(255,215,0,0.2); margin-bottom:14px}
.box{border:1.5px solid #FFC800; background:rgba(255,200,0,0.08); padding:14px; border-radius:14px; min-height:85px; color:#E8E6D9}
.backtest{border:1.5px solid #FFC800; background:#1C1A08; padding:18px; border-radius:14px; margin-top:12px; color:#E8E6D9}
.port-card{border:1.5px solid #00FF88; background:#0B1A13; padding:12px; border-radius:12px; margin-bottom:10px}
.equity-box{border:1.5px solid #00FF88; background:#0B1A13; padding:16px; border-radius:14px; margin-top:12px}
.diamond-card{border:1.5px solid #00FFFF; background:linear-gradient(135deg, #0B1A1A 0%, #0F2A2A 100%); border-radius:12px; padding:12px; color:#E8E6D9; box-shadow:0 0 12px rgba(0,255,255,0.15)}
.leaderboard{border:1.5px solid #FFD700; background:#0B0F1A; border-radius:14px; padding:16px; margin-top:14px}
@keyframes driveCorrect { 0% { transform: translateX(0); } 100% { transform: translateX(calc(-100vw - 650px)); } }
@keyframes flagwave { 0% { transform: rotate(-6deg); } 100% { transform: rotate(12deg); } }
@keyframes road { 0% { background-position: 0 0; } 100% { background-position: 80px 0; } }
@keyframes smoke { 0% { transform: scale(0.2); opacity:0; } 15% { transform: scale(1.3); opacity:0.8; } 35% { transform: scale(2) translateX(-90px); opacity:0; } 100% { opacity:0; } }
@keyframes coinFloat { 0% { transform: translateY(0) rotateY(0); } 50% { transform: translateY(-6px) rotateY(180deg); } 100% { transform: translateY(0) rotateY(360deg); } }
@keyframes coinCollect { 0%, 18% { opacity:1; } 20% { transform: scale(1.9); filter: brightness(2.2); } 23% { opacity:0; transform: scale(0) translateY(-35px); } 100% { opacity:0; } }
@keyframes diamondShine { 0% { filter: brightness(1.2) drop-shadow(0 0 8px gold); } 50% { filter: brightness(1.6) drop-shadow(0 0 15px cyan); } 100% { filter: brightness(1.2) drop-shadow(0 0 8px gold); } }
</style>
""", unsafe_allow_html=True)

# ===== AGREGADO ARRIBA: CARRITO + SONIDO + MONEDAS + DIAMANTE =====
modo_txt = "💎 DIAMANTE ON" if st.session_state.modo_diamante else "🏁 NORMAL"
car_extra_style = "animation: driveCorrect 5.5s linear infinite, diamondShine 1.2s ease-in-out infinite;" if st.session_state.modo_diamante else "animation: driveCorrect 5.5s linear infinite;"
car_html = f"""
<div style="position:relative; width:100%; height:124px; background: linear-gradient(90deg, #0F0F0F 0%, #1A1A1A 50%, #0F0F0F 100%); border:2px solid #FFD700; border-radius:16px; overflow:hidden; margin-bottom:10px; box-shadow:0 0 25px rgba(255,215,0,0.35)">
  <div style="position:absolute; top:8px; left:16px; color:#FFD700; font-weight:900; font-size:11px; letter-spacing:1px; z-index:10">🏁 ESCUDERIA CHRISTIANLE • V35 TODO SIN QUITAR • 342 km/h PA' ADELANTE • {modo_txt} • 🪙 <span id="coinCount">{st.session_state.coins}</span> • 🔥 HEATMAP • 🏆 LEADERBOARD</div>
  <div style="position:absolute; top:8px; right:16px; color:#00FF88; font-weight:800; font-size:10px; z-index:10">🏎️💨 PA' ADELANTE + 💎🪙 SONIDO ON</div>
  <div style="position:absolute; top:32px; right:-350px; {car_extra_style} font-size:60px; z-index:8; filter: drop-shadow(0 0 8px rgba(255,215,0,0.8));">🏎️</div>
  <div style="position:absolute; top:46px; right:-20px; animation: smoke 5.5s ease-out infinite; font-size:26px; z-index:7">💨</div>
  <div style="position:absolute; top:38px; left:72%; animation: coinFloat 0.9s ease-in-out infinite, coinCollect 5.5s linear infinite; font-size:26px; z-index:9; filter: drop-shadow(0 0 6px gold);">🪙</div>
  <div style="position:absolute; top:40px; left:48%; animation: coinFloat 0.9s ease-in-out infinite 0.3s, coinCollect 5.5s linear infinite 1s; font-size:22px; z-index:9; filter: drop-shadow(0 0 6px gold);">🪙</div>
  <div style="position:absolute; top:36px; left:24%; animation: coinFloat 0.9s ease-in-out infinite 0.6s, coinCollect 5.5s linear infinite 2s; font-size:24px; z-index:9">💎</div>
  <div style="position:absolute; top:20px; left:22px; animation: flagwave 0.4s ease-in-out infinite alternate; font-size:42px; z-index:6">🏁</div>
  <div style="position:absolute; bottom:10px; left:0; width:100%; height:6px; background: repeating-linear-gradient(90deg, white 0 22px, black 22px 44px); animation: road 0.3s linear infinite; z-index:2"></div>
</div>
<audio id="coinSound" preload="auto" src="https://cdn.pixabay.com/audio/2022/03/24/audio_2fba1d43b9.mp3"></audio>
<script>
let coins = {st.session_state.coins};
function playCoin(){ const c=document.getElementById('coinSound'); if(c){ c.volume=0.4; c.currentTime=0; c.play().catch(()=>{}); } let e=document.getElementById('coinCount'); if(e){ coins+=10; e.textContent=coins; } }
setInterval(playCoin, 1900);
</script>
"""
st.markdown(car_html, unsafe_allow_html=True)

c_top1, c_top2 = st.columns([3,1])
with c_top2:
    st.session_state.modo_diamante = st.toggle("💎 Modo Diamante Dorado", value=st.session_state.modo_diamante)

# ===== TU BASE ORIGINAL - SIN QUITAR NADA (como en captura) =====
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
ret24=np.log(precios[-1]/precios[-2])*100 if len(precios)>=2 else -0.38
ret7=((price/precios[-7])-1)*100 if len(precios)>=7 else -0.02
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
 <div style="color:#FFD700; font-weight:900; font-size:16px">🏎️ F1 SEMÁFORO - Cómo leer en 30 seg {"🤖 AUTO ON" if st.session_state.auto_pilot else ""}</div>
 <div style="color:#8A93A8; font-size:12px; margin-bottom:10px">Sin fórmulas. Solo 3 preguntas para no perder tu poco dinero.</div>
 <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:8px">
  <div style="border-left:3px solid #FFD700; background:#10131C; border-radius:12px; padding:10px"><div style="color:#F0F0F0; font-weight:700; font-size:12px">1. ¿Está barato? Fib 0.618</div><div style="color:#8A93A8; font-size:11px; margin-top:4px">Si BTC está abajo, es aguacate en oferta.<br>${price:,.0f} vs ${fib:,.0f} normal.</div></div>
  <div style="border-left:3px solid #00FF88; background:#10131C; border-radius:12px; padding:10px"><div style="color:#F0F0F0; font-weight:700; font-size:12px">2. ¿Está regalado? z= {z:.2f}</div><div style="color:#8A93A8; font-size:11px; margin-top:4px">z= {z:.2f} súper regalado.</div></div>
  <div style="border-left:3px solid #FF4D4D; background:#10131C; border-radius:12px; padding:10px"><div style="color:#F0F0F0; font-weight:700; font-size:12px">3. ¿Se cae a pedazos? log {lr*100:.2f}%</div><div style="color:#8A93A8; font-size:11px; margin-top:4px">{lr*100:.2f}% = normal. -5% = crash.</div></div>
 </div>
 <div style="color:#D4C44A; font-size:11px; margin-top:10px">🟢 VERDE = Compra $10-$15 | 🟡 AMARILLO = Esperas | 🔴 ROJO = Freno | ⏳ 1h | 💰 Vende 50% si +2%</div>
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

    if puede_comprar and cooldown_ok and (st.session_state.auto_pilot or st.session_state.analizar):
        try:
            if abs(price - st.session_state.last_verde_price) > 2:
                monto = 15 if z < -5 else 10
                order = client.submit_order(MarketOrderRequest(symbol=symbol, notional=monto, side=OrderSide.BUY, time_in_force=TimeInForce.GTC))
                st.session_state.last_verde_price = price
                st.session_state.last_buy_time = datetime.now()
                st.session_state.coins += 100
                orden_msg = f"ID {str(order.id)[:8]} - ${monto}"
                buy_marks.append({"idx": len(hist)-1, "symbol": symbol, "price": float(price), "t": datetime.now().strftime("%H:%M")})
                buy_marks=buy_marks[-100:]
                with open(buy_file,"w") as f: json.dump(buy_marks,f)
        except Exception as e:
            orden_msg = f"Error {e}"

    for p in positions:
        try:
            pct = float(p.unrealized_plpc)*100 if hasattr(p,'unrealized_plpc') else 0
            if pct >= 2.0 and st.session_state.auto_pilot:
                qty_vender = float(p.qty)*0.5
                if qty_vender>0:
                    client.submit_order(MarketOrderRequest(symbol=p.symbol, qty=qty_vender, side=OrderSide.SELL, time_in_force=TimeInForce.GTC))
                    venta_msg = f"TP {p.symbol} +{pct:.2f}%"
                    st.session_state.coins += 200
                    tp_marks.append({"idx": len(hist)-1, "symbol": p.symbol, "pct": pct, "eq": total, "t": datetime.now().strftime("%H:%M")})
                    tp_marks=tp_marks[-50:]
                    with open(tp_file,"w") as f: json.dump(tp_marks,f)
        except: pass

    pl_color="#00FF88" if pl_total>=0 else "#FF4D4D"
    st.markdown(f"""<div style="border:1.5px solid #FFD700; border-radius:14px; padding:10px 16px; background:#0B0F1A; margin-bottom:10px"><span style="color:#FFD700; font-weight:800; font-size:12px">💰 ALPACA PAPER • Total ${total:,.2f} • P/L <span style='color:{pl_color}'>{pl_total:+.2f}</span> • {symbol} • {orden_msg} • 🪙 {st.session_state.coins} • 🔥 HEATMAP • 💎 {modo_txt}</span> <span style="color:#8A93A8; font-size:10px; float:right">escuderia ChristianLE</span></div>""", unsafe_allow_html=True)
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

    # INTERLAGOS CON HEATMAP - AGREGADO
    if len(hist) > 1:
        st.markdown("<div class='equity-box'>🏁 <b>CIRCUIT INTERLAGOS HD - MARCAS DE LLANTA • 🟢 Compra | 💨 Take Profit +2% • 🔥 MAPA DE CALOR ON</b></div>", unsafe_allow_html=True)
        eq_vals=np.array([h["eq"] for h in hist])
        pnl=eq_vals[-1]-100000; pnl_pct=(eq_vals[-1]/100000-1)*100
        eq_min, eq_max=np.min(eq_vals), np.max(eq_vals)
        eq_norm=(eq_vals-eq_min)/(eq_max-eq_min+1) if eq_max!=eq_min else np.zeros_like(eq_vals)*0.5+0.5
        x=np.linspace(0,12,len(eq_vals))
        track_center_y=np.sin(x*0.6)*0.5 + np.sin(x*1.8)*0.25 + np.cos(x*0.4)*0.15
        track_width=0.55
        fig2, ax2=plt.subplots(figsize=(12,5))
        fig2.patch.set_facecolor("#0F0F0F"); ax2.set_facecolor("#1A1A1A")
        heat = np.zeros(len(x))
        for bm in buy_marks:
            idx = bm["idx"]
            if 0 <= idx < len(heat): heat[idx] += 1
        heat_smooth = np.convolve(heat, np.ones(7)/7, mode='same')
        heat_max = np.max(heat_smooth) if np.max(heat_smooth)>0 else 1
        heat_norm = heat_smooth / heat_max
        for i in range(len(x)-1):
            if heat_norm[i] > 0.01:
                color = plt.cm.inferno(0.3 + heat_norm[i]*0.7)
                alpha = 0.35 + heat_norm[i]*0.65
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
        ax2.plot(x, racing_line_y, color="#00FFFF" if st.session_state.modo_diamante else "#FFD700", linewidth=4.5, zorder=6)
        ax2.plot(x, racing_line_y, color="#FFD700" if st.session_state.modo_diamante else "#FFA500", linewidth=1.2, alpha=0.6, zorder=7)
        for mark in buy_marks:
            idx=mark["idx"]
            if idx < len(x):
                ax2.scatter([x[idx]], [racing_line_y[idx]], s=200+heat_norm[idx]*200, color="#00FF88", marker="o", edgecolors="white", linewidths=2, zorder=9)
                ax2.text(x[idx], racing_line_y[idx]-0.32, f"BUY {mark['symbol']}", color="#00FF88", fontsize=7, fontweight="bold", ha="center", bbox=dict(boxstyle="round,pad=0.2", facecolor="black", edgecolor="#00FF88", alpha=0.85), zorder=10)
        for mark in tp_marks:
            idx=mark["idx"]
            if idx < len(x):
                ax2.scatter([x[idx]], [racing_line_y[idx]], s=380, color="#FFD700", marker="*", edgecolors="white", linewidths=1.8, zorder=11)
        ax2.scatter([x[-1]], [racing_line_y[-1]], s=260, color="#00FFFF" if st.session_state.modo_diamante else "#00FF88", edgecolors="white", linewidths=2.5, zorder=14)
        ax2.text(0.02,0.97,f"VUELTA {len(eq_vals)} | P/L ${pnl:+.0f} ({pnl_pct:+.2f}%)\nBUYS: {len(buy_marks)} | TPs: {len(tp_marks)} | HEAT MAX {heat_max:.0f}\nMAX {eq_max:,.0f}", transform=ax2.transAxes, color="white", fontsize=9, family="monospace", bbox=dict(boxstyle="round,pad=0.5", facecolor="black", edgecolor="#FF4500" if np.max(heat)>2 else "#00FF88", linewidth=1.5), verticalalignment='top', zorder=16)
        ax2.set_xlim(-0.6,13); ax2.set_ylim(-1.6,1.6); ax2.axis('off')
        fig2.tight_layout(); st.pyplot(fig2)
        st.markdown("<div style='display:flex; gap:8px; align-items:center; font-size:10px; color:#8A93A8; margin-top:6px'><span style='width:14px; height:10px; background:#2B2B2B; display:inline-block; border-radius:2px'></span> Sin compras <span style='width:14px; height:10px; background:#FF4500; display:inline-block; border-radius:2px; margin-left:8px'></span> Pocas <span style='width:14px; height:10px; background:#FF0000; display:inline-block; border-radius:2px; margin-left:8px'></span> Muchas <span style='width:14px; height:10px; background:#FFFF00; display:inline-block; border-radius:2px; margin-left:8px'></span> Zona caliente 🔥</div>", unsafe_allow_html=True)
        if buy_marks:
            ultimos = " | ".join([f"BUY {b['symbol']} {b['t']}" for b in buy_marks[-2:]])
            st.markdown(f"<div style='color:#8A93A8; font-size:11px; margin-top:4px'>Últimos: {ultimos}</div>", unsafe_allow_html=True)

except Exception as e:
    st.error(f"Alpaca: {e}")

# ===== TODO ESTO DE ABAJO ES TU CAPTURA ORIGINAL - SIN QUITAR NADA =====
st.markdown(f"""
<div style="display:grid; grid-template-columns: 1.2fr 0.6fr 0.7fr; gap:12px; margin:16px 0">
 <div><div style="color:#FFD700; font-weight:900; font-size:32px">${price:,.0f}...</div><div style="font-size:10px; padding:4px 10px; border-radius:20px; background:rgba(0,255,136,0.15); color:#00FF88; display:inline-block">↑ Fib: ${fib:,.2f}</div></div>
 <div><div style="color:#FFD700; font-weight:900; font-size:32px">{z:.2f}</div><div style="font-size:10px; padding:4px 10px; border-radius:20px; background:rgba(0,255,136,0.15); color:#0
