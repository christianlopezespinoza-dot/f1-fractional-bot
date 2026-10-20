import streamlit as st
st.set_page_config(page_title="F1 V30 ULTIMATE DIAMANTE", layout="wide", page_icon="💎")
import yfinance as yf, numpy as np, matplotlib.pyplot as plt
from datetime import datetime, timedelta
import os, json, pandas as pd
from matplotlib.patches import Rectangle
from matplotlib.colors import LinearSegmentedColormap
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
[data-testid="stAppViewContainer"]{background:#0A0C14!important}
.semaforo-box{border:2px solid #FFD700; border-radius:16px; padding:16px; background:linear-gradient(135deg, #181B27 0%, #1E2233 100%); box-shadow:0 0 25px rgba(255,215,0,0.3); margin-bottom:14px}
.semaforo-title{color:#FFD700; font-weight:900; font-size:18px; text-shadow:0 0 10px rgba(255,215,0,0.5)}
.diamond-card{border:2px solid #00FFFF; background:linear-gradient(135deg, #0B1A1A 0%, #0F2A2A 100%); border-radius:14px; padding:14px; box-shadow:0 0 15px rgba(0,255,255,0.2); margin-bottom:10px}
.leaderboard{border:2px solid #FFD700; background:#0B0F1A; border-radius:14px; padding:16px; margin-top:12px}
.leader-row{display:flex; justify-content:space-between; padding:8px 0; border-bottom:1px solid rgba(255,215,0,0.15); font-size:13px}
.leader-header{color:#FFD700; font-weight:900; font-size:11px; letter-spacing:1px; margin-bottom:8px}
.pos-1{color:#FFD700; font-weight:900}.pos-2{color:#C0C0C0; font-weight:800}.pos-3{color:#CD7F32; font-weight:700}
.heatmap-legend{display:flex; gap:6px; align-items:center; font-size:10px; color:#8A93A8; margin-top:6px}
.neon-yellow{color:#FFD700!important; font-weight:900; font-size:38px}
.box{border:1.5px solid #FFC800; background:rgba(255,200,0,0.08); padding:14px; border-radius:14px; color:#E8E6D9}
@keyframes drive { 0% { transform: translateX(0); } 100% { transform: translateX(calc(-100vw - 650px)); } }
@keyframes diamondShine { 0% { filter: hue-rotate(0deg) brightness(1.2) drop-shadow(0 0 8px gold); } 50% { filter: hue-rotate(30deg) brightness(1.6) drop-shadow(0 0 15px cyan); } 100% { filter: hue-rotate(0deg) brightness(1.2) drop-shadow(0 0 8px gold); } }
@keyframes sparkle { 0% { transform: scale(0) rotate(0); opacity:0; } 50% { opacity:1; transform: scale(1) rotate(180deg); } 100% { transform: scale(0) rotate(360deg); opacity:0; } }
@keyframes coinFloat { 0% { transform: translateY(0) rotateY(0); } 50% { transform: translateY(-6px) rotateY(180deg); } 100% { transform: translateY(0) rotateY(360deg); } }
@keyframes coinCollect { 0%, 18% { opacity:1; transform: scale(1); } 20% { opacity:1; transform: scale(1.8); filter: brightness(2); } 22% { opacity:0; transform: scale(0) translateY(-40px); } 100% { opacity:0; } }
</style>
""", unsafe_allow_html=True)

# 💎 V30 ULTIMATE BANNER - TODO
modo = "💎 DIAMANTE DORADO" if st.session_state.modo_diamante else "🏁 NORMAL"
car_emoji = "🏎️" if not st.session_state.modo_diamante else "🏎️"
car_filter = "animation: drive 5.5s linear infinite, diamondShine 1.2s ease-in-out infinite;" if st.session_state.modo_diamante else "animation: drive 5.5s linear infinite; filter: drop-shadow(0 0 8px rgba(255,215,0,0.8));"

car_html = f"""
<div style="position:relative; width:100%; height:132px; background: linear-gradient(90deg, #0A0A0F 0%, #1A1A2E 25%, #2A2A0A 50%, #1A1A2E 75%, #0A0A0F 100%); border:2px solid #FFD700; border-radius:16px; overflow:hidden; margin-bottom:14px; box-shadow:0 0 30px rgba(255,215,0,0.4), inset 0 0 20px rgba(0,255,255,0.1)">
  <div style="position:absolute; top:8px; left:16px; color:#FFD700; font-weight:900; font-size:11px; letter-spacing:1px; z-index:10">💎 ESCUDERIA CHRISTIANLE • V30 ULTIMATE • {modo} • COINS: <span id="coinCounter">0</span> 🪙 • HEATMAP ON 🔥</div>
  <div style="position:absolute; top:8px; right:16px; color:#00FFFF; font-weight:800; font-size:10px; z-index:10">💎🏆🔥 TODO ACTIVADO</div>
  <div style="position:absolute; top:34px; right:-350px; {car_filter} font-size:62px; z-index:8;">{car_emoji}</div>
  <!-- Sparkles diamante -->
  <div style="position:absolute; top:36px; right:-340px; animation: drive 5.5s linear infinite, sparkle 0.6s ease-in-out infinite; font-size:14px; z-index:9">💎</div>
  <div style="position:absolute; top:58px; right:-360px; animation: drive 5.5s linear infinite, sparkle 0.6s ease-in-out infinite 0.3s; font-size:10px; z-index:9">✨</div>
  <!-- Monedas -->
  <div style="position:absolute; top:40px; left:70%; animation: coinFloat 0.8s ease-in-out infinite, coinCollect 5.5s linear infinite; font-size:26px; z-index:9; filter: drop-shadow(0 0 6px gold);">🪙</div>
  <div style="position:absolute; top:42px; left:40%; animation: coinFloat 0.8s ease-in-out infinite 0.3s, coinCollect 5.5s linear infinite 1.5s; font-size:24px; z-index:9; filter: drop-shadow(0 0 6px gold);">💎</div>
  <div style="position:absolute; top:38px; left:15%; animation: coinFloat 0.8s ease-in-out infinite 0.6s, coinCollect 5.5s linear infinite 3s; font-size:22px; z-index:9; filter: drop-shadow(0 0 6px cyan);">🏆</div>
  <div style="position:absolute; bottom:12px; left:0; width:100%; height:8px; background: repeating-linear-gradient(90deg, white 0 22px, black 22px 44px); z-index:2"></div>
  <div style="position:absolute; bottom:20px; left:0; width:100%; height:20px; background:#2B2B2B; z-index:1"></div>
</div>
"""
st.markdown(car_html, unsafe_allow_html=True)

c_d1, c_d2 = st.columns([3,1])
with c_d2:
    st.session_state.modo_diamante = st.toggle("💎 Modo Diamante", value=st.session_state.modo_diamante)

A_KEY=st.secrets["alpaca"]["API_KEY"]; A_SECRET=st.secrets["alpaca"]["SECRET"]
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
tk=mapa[symbol]; h=yf.Ticker(tk).history(period="1mo")
precios=h['Close'].values; high=h['High'].max(); low=h['Low'].min(); price=precios[-1]
h1y=yf.Ticker(tk).history(period="1y")['Close'].values
xb=np.mean(precios); s=np.std(precios,ddof=1)
z=(precios[-1]-xb)/(s/np.sqrt(len(precios))) if s>0 else 0
lr=np.log(precios[-1]/precios[-2]) if precios[-2]>0 else 0
fib=high-(high-low)*0.618; max1y=np.max(h1y) if len(h1y)>0 else price

# BACKTEST
casos=[]; 
for i in range(30,len(h1y)-7):
    w=h1y[i-30:i]; xb2=np.mean(w); s2=np.std(w,ddof=1)
    if s2==0: continue
    z2=(h1y[i]-xb2)/(s2/np.sqrt(30)); lr2=np.log(h1y[i]/h1y[i-1]) if h1y[i-1]>0 else 0
    if z2<-2 and -0.008<lr2<-0.0002: casos.append(1)
prob=np.mean(casos)*100 if casos else 47.1
if z < -2 and price < fib and -0.008 < lr < -0.0005:
    sema_color="VERDE"; sema_txt="🟢 COMPRAR $10"; puede_comprar=True
else:
    if z>0 or lr<-0.05: sema_color="ROJO"; sema_txt="🔴 Freno total"; puede_comprar=False
    else: sema_color="AMARILLO"; sema_txt="🟡 Esperas"; puede_comprar=False
orden_msg=""; venta_msg=""; cooldown_ok=True
if st.session_state.last_buy_time: cooldown_ok=datetime.now()-st.session_state.last_buy_time>timedelta(hours=1)

st.markdown(f"""
<div class="semaforo-box">
 <div class="semaforo-title">🏎️ V30 ULTIMATE 💎🔥🏆 {"🤖 AUTO ON" if st.session_state.auto_pilot else ""} • {modo}</div>
 <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:10px; margin-top:10px">
  <div style="border-left:3px solid #FFD700; background:#10131C; border-radius:12px; padding:12px"><div style="color:#F0F0F0; font-weight:700">Fib 0.618</div><div style="color:#8A93A8; font-size:12px">${price:,.0f} vs ${fib:,.0f}</div></div>
  <div style="border-left:3px solid #00FF88; background:#10131C; border-radius:12px; padding:12px"><div style="color:#F0F0F0; font-weight:700">z= {z:.2f}</div><div style="color:#8A93A8; font-size:12px">Compra si < -2</div></div>
  <div style="border-left:3px solid #FF4D4D; background:#10131C; border-radius:12px; padding:12px"><div style="color:#F0F0F0; font-weight:700">log {lr*100:.3f}%</div><div style="color:#8A93A8; font-size:12px">-0.8% a -0.05%</div></div>
 </div>
</div>
""", unsafe_allow_html=True)

try:
    positions=client.get_all_positions(); account=client.get_account()
    total=float(account.equity); pl_total=total-100000
    eq_file="equity_log.json"; tp_file="tp_marks.json"; buy_file="buy_marks.json"
    hist=[]; tp_marks=[]; buy_marks=[]
    for fp, arr in [(eq_file,hist),(tp_file,tp_marks),(buy_file,buy_marks)]:
        if os.path.exists(fp):
            try:
                with open(fp,"r") as f: data=json.load(f)
                arr.extend(data)
            except: pass
    hist.append({"t": datetime.now().strftime("%m-%d %H:%M"), "eq": total}); hist=hist[-200:]
    with open(eq_file,"w") as f: json.dump(hist,f)

    # AUTO BUY
    if puede_comprar and cooldown_ok and (st.session_state.auto_pilot or st.session_state.analizar):
        try:
            if abs(price-st.session_state.last_verde_price)>2:
                monto=15 if z<-5 else 10
                order=client.submit_order(MarketOrderRequest(symbol=symbol, notional=monto, side=OrderSide.BUY, time_in_force=TimeInForce.GTC))
                st.session_state.last_verde_price=price; st.session_state.last_buy_time=datetime.now(); st.session_state.coins+=100
                orden_msg=f"ID {str(order.id)[:8]} • ${monto} • +100 🪙💎"
                buy_marks.append({"idx":len(hist)-1, "symbol":symbol, "price":float(price), "t":datetime.now().strftime("%H:%M"), "eq":total})
                buy_marks=buy_marks[-50:]
                with open(buy_file,"w") as f: json.dump(buy_marks,f)
        except Exception as e: orden_msg=f"Error {e}"

    # AUTO TP
    leaderboard_data=[]
    for p in positions:
        try:
            pct=float(p.unrealized_plpc)*100 if hasattr(p,'unrealized_plpc') else (float(p.unrealized_pl)/float(p.cost_basis)*100 if float(p.cost_basis)!=0 else 0)
            leaderboard_data.append({"symbol":p.symbol, "qty":float(p.qty), "value":float(p.market_value), "pl":float(p.unrealized_pl), "pct":pct})
            if pct>=2.0 and st.session_state.auto_pilot:
                qty_vender=float(p.qty)*0.5
                if qty_vender>0:
                    client.submit_order(MarketOrderRequest(symbol=p.symbol, qty=qty_vender, side=OrderSide.SELL, time_in_force=TimeInForce.GTC))
                    venta_msg=f"💰 TP {p.symbol} +{pct:.2f}%"; st.session_state.coins+=200
                    tp_marks.append({"idx":len(hist)-1, "symbol":p.symbol, "pct":pct, "eq":total, "t":datetime.now().strftime("%H:%M")})
                    tp_marks=tp_marks[-30:]; 
                    with open(tp_file,"w") as f: json.dump(tp_marks,f)
                    notificar_f1(f"<b>💰 TP +200 🪙💎</b>\n{p.symbol} +{pct:.2f}%")
        except: pass

    pl_color="#00FF88" if pl_total>=0 else "#FF4D4D"
    st.markdown(f"""<div style="border:2px solid #FFD700; border-radius:14px; padding:10px 16px; background:#0B0F1A;"><span style="color:#FFD700; font-weight:800; font-size:12px">💰 ${total:,.2f} • P/L <span style='color:{pl_color}'>{pl_total:+.2f}</span> • 🪙 {st.session_state.coins} • 💎 {modo} • {orden_msg} {venta_msg}</span></div>""", unsafe_allow_html=True)

    # INTERLAGOS CON HEATMAP + DIAMANTE
    if len(hist)>1:
        st.markdown("<div style='border:1.5px solid #00FF88; background:#0B1A13; padding:12px; border-radius:12px; margin-top:12px'>🏁 <b>INTERLAGOS HD V30 • MAPA DE CALOR 🔥 • DIAMANTE 💎</b> • Rojo = muchas compras</div>", unsafe_allow_html=True)
        eq_vals=np.array([h["eq"] for h in hist]); initial=100000; pnl=eq_vals[-1]-initial; pnl_pct=(eq_vals[-1]/initial-1)*100
        eq_min, eq_max=np.min(eq_vals), np.max(eq_vals)
        eq_norm=(eq_vals-eq_min)/(eq_max-eq_min+1) if eq_max!=eq_min else np.zeros_like(eq_vals)*0.5+0.5
        x=np.linspace(0,12,len(eq_vals))
        track_center_y=np.sin(x*0.6)*0.5 + np.sin(x*1.8)*0.25 + np.cos(x*0.4)*0.15
        track_width=0.55
        fig2, ax2=plt.subplots(figsize=(14,5.5))
        fig2.patch.set_facecolor("#0F0F0F"); ax2.set_facecolor("#1A1A1A")
        
        # HEATMAP: contar compras por tramo de pista
        heat = np.zeros(len(x))
        for bm in buy_marks:
            if bm["idx"] < len(heat): heat[bm["idx"]] += 1
        # suavizar
        heat_smooth = np.convolve(heat, np.ones(5)/5, mode='same')
        # normalizar para color
        heat_norm = heat_smooth / (np.max(heat_smooth) if np.max(heat_smooth)>0 else 1)
        
        # Dibujar pista con heatmap
        for i in range(len(x)-1):
            alpha = 0.3 + heat_norm[i]*0.7
            color = plt.cm.hot(0.2 + heat_norm[i]*0.8) if heat_norm[i]>0 else "#2B2B2B"
            ax2.fill_between([x[i], x[i+1]], [track_center_y[i]-track_width, track_center_y[i+1]-track_width], [track_center_y[i]+track_width, track_center_y[i+1]+track_width], color=color, alpha=alpha, zorder=1)
        
        ax2.plot(x, track_center_y+track_width, color="white", linewidth=3, zorder=2)
        ax2.plot(x, track_center_y-track_width, color="white", linewidth=3, zorder=2)
        # Meta
        ax2.axvline(x[0], color="white", linewidth=3, zorder=4)
        for y in np.arange(track_center_y[0]-track_width, track_center_y[0]+track_width, 0.06):
            ax2.add_patch(Rectangle((x[0]-0.08,y),0.08,0.03,color="black" if int(y*10)%2==0 else "white",zorder=5))
        # Linea de carrera = equity
        racing_line_y=track_center_y + (eq_norm-0.5)*(track_width*1.2)
        ax2.plot(x, racing_line_y, color="#FFD700" if not st.session_state.modo_diamante else "#00FFFF", linewidth=4.5, zorder=6)
        ax2.plot(x, racing_line_y, color="#FFA500" if not st.session_state.modo_diamante else "#FFD700", linewidth=1.5, alpha=0.7, zorder=7)
        # BUYS
        for mark in buy_marks:
            idx=mark["idx"]
            if idx < len(x):
                ax2.scatter([x[idx]], [racing_line_y[idx]], s=280, color="#00FF88", marker="o", edgecolors="white", linewidths=2, zorder=9)
                ax2.text(x[idx], racing_line_y[idx]-0.32, f"🟢 {mark['symbol']}", color="#00FF88", fontsize=7, fontweight="bold", ha="center", zorder=10, bbox=dict(boxstyle="round,pad=0.2", facecolor="black", edgecolor="#00FF88", alpha=0.85))
        # TPS
        for mark in tp_marks:
            idx=mark["idx"]
            if idx < len(x):
                ax2.scatter([x[idx]], [racing_line_y[idx]], s=420, color="#FFD700", marker="*", edgecolors="white", linewidths=1.8, zorder=11)
                ax2.text(x[idx], racing_line_y[idx]+0.34, f"💎 TP {mark['symbol']}\n+{mark['pct']:.1f}%", color="#FFD700", fontsize=8, fontweight="bold", ha="center", zorder=12, bbox=dict(boxstyle="round,pad=0.3", facecolor="black", edgecolor="#FFD700", alpha=0.9))
        ax2.scatter([x[-1]], [racing_line_y[-1]], s=300, color="#00FFFF" if st.session_state.modo_diamante else "#00FF88", edgecolors="white", linewidths=2.5, zorder=14)
        ax2.text(x[-1]+0.2, racing_line_y[-1], f"🏎️ ${eq_vals[-1]:,.0f}\n{pnl_pct:+.2f}% 💎{st.session_state.coins}", color="#00FFFF" if st.session_state.modo_diamante else "#00FF88", fontsize=11, fontweight="bold", zorder=15, bbox=dict(boxstyle="round,pad=0.4", facecolor="#0F0F0F", edgecolor="#00FFFF" if st.session_state.modo_diamante else "#FFD700", linewidth=1.5))
        ax2.text(0.02,0.96,f"🏁 VUELTA {len(eq_vals)} | P/L ${pnl:+.0f} ({pnl_pct:+.2f}%)\n🔥 HEAT: Rojo=zona de compras ({len(buy_marks)} buys)\n🏆 MAX ${eq_max:,.0f} | 💎 MODE ON", transform=ax2.transAxes, color="white", fontsize=9, family="monospace", bbox=dict(boxstyle="round,pad=0.5", facecolor="black", edgecolor="#00FFFF", linewidth=1.5), verticalalignment='top', zorder=16)
        ax2.set_xlim(-0.6,13); ax2.set_ylim(-1.7,1.7); ax2.axis('off')
        fig2.tight_layout(); st.pyplot(fig2)
        st.markdown("<div class='heatmap-legend'><span style='width:14px; height:10px; background:#2B2B2B; display:inline-block; border-radius:2px'></span> Sin compras <span style='width:14px; height:10px; background:#FF4500; display:inline-block; border-radius:2px; margin-left:10px'></span> Pocas <span style='width:14px; height:10px; background:#FF0000; display:inline-block; border-radius:2px; margin-left:10px'></span> Muchas <span style='width:14px; height:10px; background:#FFFF00; display:inline-block; border-radius:2px; margin-left:10px'></span> Zona caliente 🔥</div>", unsafe_allow_html=True)

    # 🏆 TABLA DE POSICIONES
    st.markdown(f"""
    <div class="leaderboard">
      <div class="leader-header">🏆 TABLA DE POSICIONES • ESCUDERIA CHRISTIANLE • V30 ULTIMATE</div>
      <div class="leader-row" style="color:#8A93A8; font-weight:700; border-bottom:1px solid rgba(255,215,0,0.3)">
        <span>POS • SYMBOL</span><span>QTY</span><span>VALUE</span><span>P/L</span><span>%</span>
      </div>
    </div>
    """, unsafe_allow_html=True)
    leaderboard_data_sorted = sorted(leaderboard_data, key=lambda x: x["pct"], reverse=True)
    for i, row in enumerate(leaderboard_data_sorted[:10]):
        pos_class = "pos-1" if i==0 else "pos-2" if i==1 else "pos-3" if i==2 else ""
        emoji = "🥇" if i==0 else "🥈" if i==1 else "🥉" if i==2 else f"{i+1}."
        color = "#00FF88" if row["pl"]>=0 else "#FF4D4D"
        st.markdown(f"<div class='leader-row'><span class='{pos_class}'>{emoji} {row['symbol']}</span><span>{row['qty']:.4f}</span><span>${row['value']:.2f}</span><span style='color:{color}'>{row['pl']:+.2f}</span><span style='color:{color}; font-weight:800'>{row['pct']:+.2f}%</span></div>", unsafe_allow_html=True)
    
    # STATS DIAMANTE
    c_s1,c_s2,c_s3,c_s4 = st.columns(4)
    with c_s1: st.markdown(f"<div class='diamond-card'>💎 <b>COINS</b><br><span style='font-size:22px; color:#FFD700; font-weight:900'>{st.session_state.coins} 🪙</span></div>", unsafe_allow_html=True)
    with c_s2: st.markdown(f"<div class='diamond-card'>🔥 <b>HEAT ZONES</b><br><span style='font-size:22px; color:#FF4500; font-weight:900'>{len([h for h in heat if h>0])} zonas</span></div>", unsafe_allow_html=True)
    with c_s3: st.markdown(f"<div class='diamond-card'>🏆 <b>MEJOR TRADE</b><br><span style='font-size:14px; color:#FFD700; font-weight:900'>{leaderboard_data_sorted[0]['symbol'] if leaderboard_data_sorted else 'N/A'} {leaderboard_data_sorted[0]['pct']:+.1f}%</span></div>", unsafe_allow_html=True)
    with c_s4: st.markdown(f"<div class='diamond-card'>💎 <b>DIAMANTE</b><br><span style='font-size:22px; color:#00FFFF; font-weight:900'>{'ON ✨' if st.session_state.modo_diamante else 'OFF'}</span></div>", unsafe_allow_html=True)

except Exception as e:
    st.error(f"Alpaca: {e}")

try:
    acc = client.get_account()
    notificar_f1(f"<b>💎 V30 ULTIMATE TODO</b>\n{symbol} ${price:,.2f} • {sema_txt}\n💰 ${float(acc.equity):,.2f} • 🪙 {st.session_state.coins} • 🔥 Heat {len(buy_marks)} buys • 🏆 Leader {leaderboard_data_sorted[0]['symbol'] if 'leaderboard_data_sorted' in locals() and leaderboard_data_sorted else 'N/A'}")
except: pass
