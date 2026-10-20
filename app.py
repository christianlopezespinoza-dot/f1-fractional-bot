import streamlit as st
st.set_page_config(page_title="F1 V35.2 FIX", layout="wide", page_icon="💎")
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
.semaforo-box{border:1.5px solid #FFD700; border-radius:16px; padding:16px; background:#181B27; margin-bottom:14px}
.box{border:1.5px solid #FFC800; background:rgba(255,200,0,0.08); padding:14px; border-radius:14px; min-height:85px; color:#E8E6D9}
.backtest{border:1.5px solid #FFC800; background:#1C1A08; padding:18px; border-radius:14px; margin-top:12px; color:#E8E6D9}
.port-card{border:1.5px solid #00FF88; background:#0B1A13; padding:12px; border-radius:12px; margin-bottom:10px}
.equity-box{border:1.5px solid #00FF88; background:#0B1A13; padding:16px; border-radius:14px; margin-top:12px}
.diamond-card{border:1.5px solid #00FFFF; background:#0B1A1A; border-radius:12px; padding:12px; color:#E8E6D9}
.leaderboard{border:1.5px solid #FFD700; background:#0B0F1A; border-radius:14px; padding:16px; margin-top:14px}
@keyframes driveCorrect { 0% { transform: translateX(0); } 100% { transform: translateX(calc(-100vw - 650px)); } }
@keyframes flagwave { 0% { transform: rotate(-6deg); } 100% { transform: rotate(12deg); } }
@keyframes road { 0% { background-position: 0 0; } 100% { background-position: 80px 0; } }
@keyframes smoke { 0% { transform: scale(0.2); opacity:0; } 15% { transform: scale(1.3); opacity:0.8; } 100% { opacity:0; } }
@keyframes coinFloat { 0% { transform: translateY(0); } 50% { transform: translateY(-6px); } 100% { transform: translateY(0); } }
@keyframes coinCollect { 0%, 18% { opacity:1; } 20% { transform: scale(1.9); } 23% { opacity:0; transform: scale(0); } 100% { opacity:0; } }
@keyframes diamondShine { 0% { filter: brightness(1.2); } 50% { filter: brightness(1.6); } 100% { filter: brightness(1.2); } }
</style>
""", unsafe_allow_html=True)

modo_txt = "DIAMANTE ON" if st.session_state.modo_diamante else "NORMAL"
coins_val = st.session_state.coins
car_extra = "animation: driveCorrect 5.5s linear infinite, diamondShine 1.2s ease-in-out infinite;" if st.session_state.modo_diamante else "animation: driveCorrect 5.5s linear infinite;"

p1 = '<div style="position:relative; width:100%; height:124px; background:#0F0F0F; border:2px solid #FFD700; border-radius:16px; overflow:hidden; margin-bottom:10px">'
p1 += '<div style="position:absolute; top:8px; left:16px; color:#FFD700; font-weight:900; font-size:11px; z-index:10">ESCUDERIA CHRISTIANLE V35.2 ' + modo_txt + ' COINS ' + str(coins_val) + ' HEATMAP</div>'
p1 += '<div style="position:absolute; top:32px; right:-350px; ' + car_extra + ' font-size:60px; z-index:8">🏎️</div>'
p1 += '<div style="position:absolute; top:46px; right:-20px; animation: smoke 5.5s ease-out infinite; font-size:26px; z-index:7">💨</div>'
p1 += '<div style="position:absolute; top:38px; left:72%; animation: coinFloat 0.9s ease-in-out infinite, coinCollect 5.5s linear infinite; font-size:26px; z-index:9">🪙</div>'
p1 += '<div style="position:absolute; top:40px; left:48%; animation: coinFloat 0.9s ease-in-out infinite 0.3s, coinCollect 5.5s linear infinite 1s; font-size:22px; z-index:9">🪙</div>'
p1 += '<div style="position:absolute; top:36px; left:24%; animation: coinFloat 0.9s ease-in-out infinite 0.6s, coinCollect 5.5s linear infinite 2s; font-size:24px; z-index:9">💎</div>'
p1 += '<div style="position:absolute; top:20px; left:22px; animation: flagwave 0.4s ease-in-out infinite alternate; font-size:42px; z-index:6">🏁</div>'
p1 += '<div style="position:absolute; bottom:10px; left:0; width:100%; height:6px; background: repeating-linear-gradient(90deg, white 0 22px, black 22px 44px); animation: road 0.3s linear infinite; z-index:2"></div>'
p1 += '</div>'

p2 = '<audio id="coinSound" preload="auto" src="https://cdn.pixabay.com/audio/2022/03/24/audio_2fba1d43b9.mp3"></audio>'
p2 += '<script>var coins=' + str(coins_val) + '; function playCoin(){ var c=document.getElementById("coinSound"); if(c){ c.volume=0.4; c.currentTime=0; c.play().catch(function(){}); } } setInterval(playCoin,1900); </script>'

st.markdown(p1 + p2, unsafe_allow_html=True)

c_top1, c_top2 = st.columns([3,1])
with c_top2:
    st.session_state.modo_diamante = st.toggle("Modo Diamante", value=st.session_state.modo_diamante)

A_KEY=st.secrets["alpaca"]["API_KEY"]
A_SECRET=st.secrets["alpaca"]["SECRET"]
client=TradingClient(A_KEY,A_SECRET,paper=True)

c0,c1,c2,c3=st.columns([2,1,1,0.8])
with c0: symbol=st.selectbox("Activo", ["BTC/USD","ETH/USD","AAPL","SOL/USD"], index=0, label_visibility="collapsed")
with c1: 
    if st.button("ANALIZAR", type="primary", use_container_width=True):
        st.session_state.analizar=True; st.rerun()
with c2:
    if st.button("PANICO", use_container_width=True):
        try: client.close_all_positions(cancel_orders=True); st.error("PANICO")
        except Exception as e: st.error(str(e))
with c3:
    st.session_state.auto_pilot = st.toggle("Auto", value=st.session_state.auto_pilot)

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
    sema_color = "VERDE"; sema_txt = "COMPRAR $10"; puede_comprar = True
else:
    if z > 0 or lr < -0.05:
        sema_color = "ROJO"; sema_txt = "Freno total"; puede_comprar = False
    else:
        sema_color = "AMARILLO"; sema_txt = "Esperas"; puede_comprar = False
orden_msg = ""; venta_msg = ""; cooldown_ok = True
if st.session_state.last_buy_time:
    cooldown_ok = datetime.now() - st.session_state.last_buy_time > timedelta(hours=1)

st.markdown(f"""
<div class="semaforo-box">
 <div style="color:#FFD700; font-weight:900; font-size:16px">F1 SEMAFORO - 30 seg {"AUTO ON" if st.session_state.auto_pilot else ""}</div>
 <div style="color:#8A93A8; font-size:12px; margin-bottom:10px">Sin formulas. Solo 3 preguntas.</div>
 <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:8px">
  <div style="border-left:3px solid #FFD700; background:#10131C; border-radius:12px; padding:10px"><div style="color:#F0F0F0; font-weight:700; font-size:12px">1. Barato? Fib 0.618</div><div style="color:#8A93A8; font-size:11px">${price:,.0f} vs ${fib:,.0f}</div></div>
  <div style="border-left:3px solid #00FF88; background:#10131C; border-radius:12px; padding:10px"><div style="color:#F0F0F0; font-weight:700; font-size:12px">2. Regalado? z= {z:.2f}</div><div style="color:#8A93A8; font-size:11px">z= {z:.2f}</div></div>
  <div style="border-left:3px solid #FF4D4D; background:#10131C; border-radius:12px; padding:10px"><div style="color:#F0F0F0; font-weight:700; font-size:12px">3. Se cae? log {lr*100:.2f}%</div><div style="color:#8A93A8; font-size:11px">{lr*100:.2f}%</div></div>
 </div>
</div>
""", unsafe_allow_html=True)

try:
    positions = client.get_all_positions()
    account = client.get_account()
    total = float(account.equity)
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
        except Exception:
            pass

    st.markdown(f"<div style='border:1.5px solid #FFD700; border-radius:14px; padding:10px; background:#0B0F1A;'><span style='color:#FFD700; font-weight:800; font-size:12px'>ALPACA ${total:,.2f} P/L {(total-100000):+.2f} {symbol} {orden_msg} COINS {st.session_state.coins}</span></div>", unsafe_allow_html=True)

    if len(hist) > 1:
        st.markdown("<div class='equity-box'><b>CIRCUIT INTERLAGOS HD - HEATMAP ON</b></div>", unsafe_allow_html=True)
        eq_vals=np.array([h["eq"] for h in hist])
        eq_min, eq_max=np.min(eq_vals), np.max(eq_vals)
        eq_norm=(eq_vals-eq_min)/(eq_max-eq_min+1) if eq_max!=eq_min else np.zeros_like(eq_vals)*0.5+0.5
        x=np.linspace(0,12,len(eq_vals))
        track_center_y=np.sin(x*0.6)*0.5 + np.sin(x*1.8)*0.25
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
        racing_line_y=track_center_y + (eq_norm-0.5)*(track_width*1.2)
        ax2.plot(x, racing_line_y, color="#00FFFF" if st.session_state.modo_diamante else "#FFD700", linewidth=4.5, zorder=6)
        for mark in buy_marks:
            idx=mark["idx"]
            if idx < len(x):
                ax2.scatter([x[idx]], [racing_line_y[idx]], s=200, color="#00FF88", marker="o", edgecolors="white", linewidths=2, zorder=9)
        ax2.set_xlim(-0.6,13); ax2.set_ylim(-1.6,1.6); ax2.axis('off')
        fig2.tight_layout(); st.pyplot(fig2)

except Exception as e:
    st.error(f"Alpaca: {e}")

st.markdown(f"""
<div style="display:grid; grid-template-columns: 1.2fr 0.6fr 0.7fr; gap:12px; margin:16px 0">
 <div><div style="color:#FFD700; font-weight:900; font-size:32px">${price:,.0f}...</div><div style="font-size:10px; padding:4px 10px; border-radius:20px; background:rgba(0,255,136,0.15); color:#00FF88; display:inline-block">Fib: ${fib:,.2f}</div></div>
 <div><div style="color:#FFD700; font-weight:900; font-size:32px">{z:.2f}</div><div style="font-size:10px; padding:4px 10px; border-radius:20px; background:rgba(0,255,136,0.15); color:#00FF88; display:inline-block">Compra si -2</div></div>
 <div><div style="color:#FFD700; font-weight:900; font-size:32px">{lr*100:.3f}%</div><div style="font-size:10px; padding:4px 10px; border-radius:20px; background:rgba(255,70,70,0.15); color:#FF6B7A; display:inline-block">-0.8 a -0.05</div></div>
</div>
""", unsafe_allow_html=True)
fig, ax=plt.subplots(figsize=(10,4))
fig.patch.set_facecolor("#10131C"); ax.set_facecolor("#10131C")
ax.plot(precios, color="#00FF87", linewidth=2.5)
ax.axhline(xb, color="#3A8B8B", linewidth=1, alpha=0.8)
ax.axhline(fib, color="#FFD500", ls="--", linewidth=1.2)
ax.tick_params(colors="#6B7280", labelsize=9)
for sp in ax.spines.values(): sp.set_visible(False)
st.pyplot(fig)
b1,b2,b3,b4=st.columns(4)
with b1: st.markdown(f"<div class='box'>24 HORAS<br>{ret24:.2f}%</div>", unsafe_allow_html=True)
with b2: st.markdown(f"<div class='box'>7 DIAS<br>{ret7:.2f}%</div>", unsafe_allow_html=True)
with b3: st.markdown(f"<div class='box'>30 DIAS<br>{ret30:.2f}%</div>", unsafe_allow_html=True)
with b4: st.markdown(f"<div class='box'>vs MAX 1 ANO<br>{vsmax:.2f}%</div>", unsafe_allow_html=True)
st.markdown(f"<div class='backtest'>BACKTEST<br>{len(casos)} casos | Prob {prob:.1f}%<br>{sema_color}: {sema_txt}</div>", unsafe_allow_html=True)

try:
    leaderboard_data=[]
    for p in positions:
        try:
            pct=float(p.unrealized_plpc)*100 if hasattr(p,'unrealized_plpc') else 0
            leaderboard_data.append({"symbol":p.symbol, "value":float(p.market_value), "pl":float(p.unrealized_pl), "pct":pct})
        except Exception:
            pass
    if leaderboard_data:
        st.markdown("<div class='leaderboard'><div style='color:#FFD700; font-weight:900; font-size:12px;'>TABLA DE POSICIONES</div></div>", unsafe_allow_html=True)
        sorted_data = sorted(leaderboard_data, key=lambda x: x["pct"], reverse=True)
        for idx, row in enumerate(sorted_data[:10]):
            if idx==0: emoji="🥇"
            elif idx==1: emoji="🥈"
            elif idx==2: emoji="🥉"
            else: emoji=str(idx+1)+"."
            color = "#00FF88" if row["pl"]>=0 else "#FF4D4D"
            st.markdown(f"<div style='display:flex; justify-content:space-between; padding:6px 0; font-size:12px'><span>{emoji} {row['symbol']}</span><span style='color:{color}'>{row['pl']:+.2f} ({row['pct']:+.2f}%)</span></div>", unsafe_allow_html=True)
except Exception:
    pass
