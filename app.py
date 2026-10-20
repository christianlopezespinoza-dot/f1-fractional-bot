import streamlit as st
st.set_page_config(page_title="F1 V44 ULTIMATE", layout="wide", page_icon="💎")
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
for k,v in {"last_verde_price":0,"perfil_nombre":"ChristianLE","analizar":True,"last_update_id":0,"show_alpaca":True,"last_buy_time":None,"auto_pilot":True,"coins":100}.items():
    if k not in st.session_state: st.session_state[k]=v
responder_comandos()

st.markdown("""
<style>
[data-testid="stAppViewContainer"]{background:#10131C!important}
.semaforo-box{border:1.5px solid #FFD700;border-radius:16px;padding:16px;background:#181B27;box-shadow:0 0 15px rgba(255,215,0,0.2);margin-bottom:14px}
.box{border:1.5px solid #FFC800;background:rgba(255,200,0,0.08);padding:14px;border-radius:14px;min-height:85px;color:#E8E6D9}
.backtest{border:1.5px solid #FFC800;background:#1C1A08;padding:18px;border-radius:14px;margin-top:12px;color:#E8E6D9}
.port-card{border:1.5px solid #00FF88;background:#0B1A13;padding:12px;border-radius:12px;margin-bottom:10px}
.equity-box{border:1.5px solid #00FF88;background:#0B1A13;padding:16px;border-radius:14px;margin-top:12px}
.ultimate-bar{border:2px solid #FFD700;border-radius:14px;padding:12px 18px;background:linear-gradient(90deg,#0B0F1A 0%,#1A1A0B 100%);margin-bottom:12px;box-shadow:0 0 20px rgba(255,215,0,0.3)}
@keyframes drive{0%{transform:translateX(0)}100%{transform:translateX(calc(-100vw - 650px))}}
@keyframes flagwave{0%{transform:rotate(-6deg)}100%{transform:rotate(12deg)}}
@keyframes road{0%{background-position:0 0}100%{background-position:80px 0}}
@keyframes smoke{0%{transform:scale(0.2);opacity:0}15%{transform:scale(1.3);opacity:0.8}100%{opacity:0}}
@keyframes coinFloat{0%{transform:translateY(0)}50%{transform:translateY(-6px)}100%{transform:translateY(0)}}
@keyframes coinCollect{0%,18%{opacity:1}20%{transform:scale(1.9)}23%{opacity:0;transform:scale(0)}100%{opacity:0}}
</style>
""", unsafe_allow_html=True)

car_html = '<div style="position:relative;width:100%;height:122px;background:linear-gradient(90deg,#0F0F0F 0%,#1A1A1A 50%,#0F0F0F 100%);border:2px solid #FFD700;border-radius:16px;overflow:hidden;margin-bottom:10px;box-shadow:0 0 25px rgba(255,215,0,0.35)"><div style="position:absolute;top:8px;left:16px;color:#FFD700;font-weight:900;font-size:11px;z-index:10">💎 V44 ULTIMATE TODO - ESCUDERIA ChristianLE - PA ADELANTE</div><div style="position:absolute;top:32px;right:-350px;animation:drive 5.5s linear infinite;font-size:60px;z-index:8">🏎️</div><div style="position:absolute;top:46px;right:-20px;animation:smoke 5.5s ease-out infinite;font-size:26px;z-index:7">💨</div><div style="position:absolute;top:38px;left:72%;animation:coinFloat 0.9s infinite,coinCollect 5.5s infinite;font-size:26px;z-index:9">🪙</div><div style="position:absolute;top:40px;left:48%;animation:coinFloat 0.9s infinite 0.3s,coinCollect 5.5s infinite 1s;font-size:22px;z-index:9">🪙</div><div style="position:absolute;top:36px;left:24%;animation:coinFloat 0.9s infinite 0.6s,coinCollect 5.5s infinite 2s;font-size:24px;z-index:9">💎</div><div style="position:absolute;top:20px;left:22px;animation:flagwave 0.4s infinite alternate;font-size:42px;z-index:6">🏁</div><div style="position:absolute;bottom:10px;left:0;width:100%;height:6px;background:repeating-linear-gradient(90deg,white 0 22px,black 22px 44px);animation:road 0.3s linear infinite;z-index:2"></div></div>'
st.markdown(car_html, unsafe_allow_html=True)

A_KEY=st.secrets["alpaca"]["API_KEY"]
A_SECRET=st.secrets["alpaca"]["SECRET"]
client=TradingClient(A_KEY,A_SECRET,paper=True)

c0,c1,c2,c3=st.columns([2,1,1,0.8])
with c0: symbol=st.selectbox("Activo",["BTC/USD","ETH/USD","AAPL","SOL/USD"],index=0,label_visibility="collapsed")
with c1:
    if st.button("🏁 ANALIZAR",type="primary",use_container_width=True):
        st.session_state.analizar=True; st.rerun()
with c2:
    if st.button("🚨 PANICO",use_container_width=True):
        try: client.close_all_positions(cancel_orders=True); st.error("PANICO")
        except Exception as e: st.error(str(e))
with c3: st.session_state.auto_pilot=st.toggle("🤖 Auto",value=st.session_state.auto_pilot)

mapa={"BTC/USD":"BTC-USD","ETH/USD":"ETH-USD","AAPL":"AAPL","SOL/USD":"SOL-USD"}
tk=mapa[symbol]
h=yf.Ticker(tk).history(period="1mo")
precios=h['Close'].values; high=h['High'].max(); low=h['Low'].min(); price=precios[-1]
vol=h['Volume'].values if 'Volume' in h.columns else np.ones(len(precios))
h1y=yf.Ticker(tk).history(period="1y")['Close'].values
xb=np.mean(precios); s=np.std(precios,ddof=1)
z=(precios[-1]-xb)/(s/np.sqrt(len(precios))) if s>0 else -7.20
lr=np.log(precios[-1]/precios[-2]) if precios[-2]>0 else -0.005483
fib=high-(high-low)*0.618
max1y=np.max(h1y) if len(h1y)>0 else price
ret24=np.log(precios[-1]/precios[-2])*100 if len(precios)>=2 else -0.55
ret7=((price/precios[-7])-1)*100 if len(precios)>=7 else -0.19
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
    sema_color="VERDE"; sema_txt="🟢 COMPRAR $10"; puede=True
else:
    puede=False
    if z > 0 or lr < -0.05:
        sema_color="ROJO"; sema_txt="🔴 Freno total"
    else:
        sema_color="AMARILLO"; sema_txt="🟡 Esperas"

orden_msg="Cooldown precio"; venta_msg=""; cooldown_ok=True
if st.session_state.last_buy_time:
    cooldown_ok=datetime.now()-st.session_state.last_buy_time>timedelta(hours=1)

try:
    positions=client.get_all_positions(); account=client.get_account(); total=float(account.equity)
    equity_file="equity_log.json"; tp_file="tp_marks.json"; buy_file="buy_marks.json"
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
    hist.append({"t":datetime.now().strftime("%m-%d %H:%M"),"eq":total}); hist=hist[-200:]
    with open(equity_file,"w") as f: json.dump(hist,f)
    
    heat_buys=len(buy_marks)
    leader="BTC/USD"
    if buy_marks:
        counts={}
        for b in buy_marks: counts[b.get("symbol","BTC/USD")]=counts.get(b.get("symbol","BTC/USD"),0)+1
        leader=max(counts,key=counts.get) if counts else "BTC/USD"
        st.session_state.coins=len(buy_marks)*10
    else:
        st.session_state.coins=100
        heat_buys=10

    st.markdown(f"<div class='ultimate-bar'><span style='color:#FFD700;font-weight:900;font-size:13px'>💎 V44 ULTIMATE TODO</span> <span style='color:#00FF88;font-weight:800;margin-left:12px'>{symbol} ${price:,.2f} • {sema_txt}</span> <span style='color:#8A93A8;float:right;font-weight:700;font-size:12px'>💰 ${total:,.2f} • 🪙 {st.session_state.coins} • 🔥 Heat {heat_buys} buys • 🏆 Leader {leader}</span></div>", unsafe_allow_html=True)

    st.markdown(f"""
<div class="semaforo-box">
 <div style="color:#FFD700;font-weight:900;font-size:16px">🏎️ F1 SEMÁFORO - Cómo leer en 30 seg {"🤖 AUTO ON" if st.session_state.auto_pilot else ""}</div>
 <div style="color:#8A93A8;font-size:13px;margin-bottom:12px">Sin fórmulas. Solo 3 preguntas para no perder tu poco dinero.</div>
 <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px">
  <div style="border-left:3px solid #FFD700;background:#10131C;border-radius:12px;padding:12px">
    <div style="color:#F0F0F0;font-weight:700;font-size:13px">1. ¿Está barato? Fib 0.618</div>
    <div style="color:#8A93A8;font-size:12px;margin-top:6px">Si BTC está abajo, es aguacate en oferta.<br>${price:,.0f} vs ${fib:,.0f} normal.</div>
  </div>
  <div style="border-left:3px solid #00FF88;background:#10131C;border-radius:12px;padding:12px">
    <div style="color:#F0F0F0;font-weight:700;font-size:13px">2. ¿Está regalado? z= {z:.2f}</div>
    <div style="color:#8A93A8;font-size:12px;margin-top:6px">z= {z:.2f} súper regalado.</div>
  </div>
  <div style="border-left:3px solid #FF4D4D;background:#10131C;border-radius:12px;padding:12px">
    <div style="color:#F0F0F0;font-weight:700;font-size:13px">3. ¿Se cae a pedazos? log {lr*100:.2f}%</div>
    <div style="color:#8A93A8;font-size:12px;margin-top:6px">{lr*100:.2f}% = normal. -5% = crash.</div>
  </div>
 </div>
 <div style="color:#D4C44A;font-size:11px;margin-top:12px;font-weight:600">🟢 VERDE = Compra $10-$15 | 🟡 AMARILLO = Esperas | 🔴 ROJO = Freno | ⏳ 1h | 💰 Vende 50% si +2%</div>
</div>
""", unsafe_allow_html=True)

    if puede and cooldown_ok and (st.session_state.auto_pilot or st.session_state.analizar):
        try:
            if abs(price-st.session_state.last_verde_price)>2:
                monto=15 if z<-5 else 10
                order=client.submit_order(MarketOrderRequest(symbol=symbol,notional=monto,side=OrderSide.BUY,time_in_force=TimeInForce.GTC))
                st.session_state.last_verde_price=price; st.session_state.last_buy_time=datetime.now()
                orden_msg=f"ID {str(order.id)[:8]} - ${monto}"
                buy_marks.append({"idx":len(hist)-1,"symbol":symbol,"price":float(price),"t":datetime.now().strftime("%H:%M")})
                buy_marks=buy_marks[-100:]
                with open(buy_file,"w") as f: json.dump(buy_marks,f)
                notificar_f1(symbol=symbol,equity=total,cash=float(account.cash),order_id=str(order.id)[:8],monto=monto,auto_on=st.session_state.auto_pilot,cooldown_ok=True)
        except Exception as e: orden_msg=f"Error {e}"

    for p in positions:
        try:
            pct=float(p.unrealized_plpc)*100 if hasattr(p,'unrealized_plpc') else 0
            if pct>=2.0 and st.session_state.auto_pilot:
                qty_vender=float(p.qty)*0.5
                if qty_vender>0:
                    client.submit_order(MarketOrderRequest(symbol=p.symbol,qty=qty_vender,side=OrderSide.SELL,time_in_force=TimeInForce.GTC))
                    tp_marks.append({"idx":len(hist)-1,"symbol":p.symbol,"pct":pct,"eq":total,"t":datetime.now().strftime("%H:%M")})
                    tp_marks=tp_marks[-50:]
                    with open(tp_file,"w") as f: json.dump(tp_marks,f)
        except: pass

    pl_color="#00FF88" if (total-100000)>=0 else "#FF4D4D"
    st.markdown(f"<div style='border:1.5px solid #FFD700;border-radius:14px;padding:10px 16px;background:#0B0F1A;margin-bottom:10px'><span style='color:#FFD700;font-weight:800;font-size:12px'>💰 ALPACA PAPER • Total ${total:,.2f} • P/L <span style='color:{pl_color}'>{(total-100000):+.2f}</span> • {symbol} • {orden_msg} • 🪙 {st.session_state.coins} • 🔥 {heat_buys} buys • 🏆 {leader}</span> <span style='color:#8A93A8;font-size:10px;float:right'>escuderia ChristianLE</span></div>", unsafe_allow_html=True)
    c_alp1,c_alp2=st.columns(2)
    with c_alp1:
        if st.button("💰 Ver en Alpaca →",use_container_width=True): st.session_state.show_alpaca=not st.session_state.show_alpaca
    with c_alp2: st.link_button("🔗 Abrir Dashboard Alpaca","https://app.alpaca.markets/brokerage/dashboard/overview",use_container_width=True)
    if st.session_state.show_alpaca:
        st.markdown(f"<div class='port-card'>🏦 <b>Escudería {st.session_state.perfil_nombre}</b> • Equity ${total:,.2f} • Cash ${float(account.cash):,.2f} • Auto {'ON 🤖' if st.session_state.auto_pilot else 'OFF'}</div>", unsafe_allow_html=True)
        for p in positions:
            pl=float(p.unrealized_pl); pct=float(p.unrealized_plpc)*100 if hasattr(p,'unrealized_plpc') else 0
            st.markdown(f"**{'🟢' if pl>=0 else '🔴'} {p.symbol}** {float(p.qty):.6f} • ${float(p.market_value):.2f} • P/L {pl:+.2f} ({pct:+.2f}%)", unsafe_allow_html=True)

    if len(hist)>1:
        st.markdown("<div class='equity-box'>🏁 <b>CIRCUIT INTERLAGOS HD - V44 ULTIMATE - VUELTA + P/L + BTC/USD TAGS + HEATMAP</b></div>", unsafe_allow_html=True)
        eq_vals=np.array([h["eq"] for h in hist]); pnl=eq_vals[-1]-100000; pnl_pct=(eq_vals[-1]/100000-1)*100
        eq_min,eq_max=np.min(eq_vals),np.max(eq_vals)
        eq_norm=(eq_vals-eq_min)/(eq_max-eq_min+1) if eq_max!=eq_min else np.zeros_like(eq_vals)*0.5+0.5
        x=np.linspace(0,12,len(eq_vals)); track_center_y=np.sin(x*0.6)*0.5+np.sin(x*1.8)*0.25+np.cos(x*0.4)*0.15
        track_width=0.55; fig2,ax2=plt.subplots(figsize=(14,5))
        fig2.patch.set_facecolor("#0A0A0A"); ax2.set_facecolor("#0A0A0A")
        heat=np.zeros(len(x))
        for bm in buy_marks:
            idx=bm["idx"]
            if 0<=idx<len(heat): heat[idx]+=2
        heat_smooth=np.convolve(heat,np.ones(5)/5,mode='same'); heat_max=np.max(heat_smooth) if np.max(heat_smooth)>0 else 1; heat_norm=heat_smooth/heat_max
        for i in range(len(x)-1):
            if heat_norm[i]>0.7: col="#FFFF00"
            elif heat_norm[i]>0.4: col="#FF8C00"
            elif heat_norm[i]>0.15: col="#8B0000"
            else: col="#2B2B2B"
            ax2.fill_between([x[i],x[i+1]],[track_center_y[i]-track_width,track_center_y[i+1]-track_width],[track_center_y[i]+track_width,track_center_y[i+1]+track_width],color=col,alpha=0.95,zorder=1)
        ax2.plot(x,track_center_y+track_width,color="white",linewidth=3,zorder=2); ax2.plot(x,track_center_y-track_width,color="white",linewidth=3,zorder=2)
        ax2.axvline(x[0],color="white",linewidth=3,zorder=4)
        for y in np.arange(track_center_y[0]-track_width,track_center_y[0]+track_width,0.06):
            ax2.add_patch(Rectangle((x[0]-0.08,y),0.08,0.03,color="black" if int(y*10)%2==0 else "white",zorder=5))
        racing_line_y=track_center_y+(eq_norm-0.5)*(track_width*0.8)
        ax2.plot(x,racing_line_y,color="#00FFCC",linewidth=3.5,zorder=6)
        for mark in buy_marks[-10:]:
            idx=mark["idx"]
            if idx<len(x):
                ax2.scatter([x[idx]],[racing_line_y[idx]],s=120,color="#00FFCC",edgecolors="white",linewidths=1.5,zorder=8)
                ax2.text(x[idx],racing_line_y[idx]-0.38,f"{mark['symbol']}",color="#00FFCC",fontsize=6.5,fontweight="bold",ha="center",bbox=dict(boxstyle="round,pad=0.15",facecolor="black",edgecolor="#00FFCC",alpha=0.85),zorder=9)
        ax2.scatter([x[-1]],[racing_line_y[-1]],s=200,color="#00FFCC",edgecolors="white",linewidths=2,zorder=10)
        ax2.text(0.01,0.97,f"VUELTA {len(eq_vals)} | P/L ${pnl:+.0f} ({pnl_pct:+.2f}%)\nHEAT: Rojo=zona de compras ({len(buy_marks)} buys)\nMAX {eq_max:,.0f} | MODE ON • LEADER {leader}",transform=ax2.transAxes,color="#00FFCC",fontsize=8,family="monospace",bbox=dict(boxstyle="round,pad=0.4",facecolor="#001A1A",edgecolor="#00FFCC",linewidth=1.2),verticalalignment='top',zorder=12)
        ax2.text(0.98,0.5,f"${eq_vals[-1]:,.0f}\n{pnl_pct:+.2f}% {len(buy_marks)}",transform=ax2.transAxes,color="#00FFCC",fontsize=9,fontweight="bold",ha="right",bbox=dict(boxstyle="round,pad=0.4",facecolor="#001A1A",edgecolor="#00FFCC"),zorder=12)
        ax2.set_xlim(-0.6,13); ax2.set_ylim(-1.6,1.6); ax2.axis('off'); fig2.tight_layout(); st.pyplot(fig2)
        st.markdown(f"<div style='display:flex;gap:16px;font-size:11px;color:#8A93A8;margin-top:6px'><span style='width:14px;height:10px;background:#2B2B2B;display:inline-block'></span> Sin compras <span style='width:14px;height:10px;background:#FF8C00;display:inline-block;margin-left:8px'></span> Pocas <span style='width:14px;height:10px;background:#8B0000;display:inline-block;margin-left:8px'></span> Muchas <span style='width:14px;height:10px;background:#FFFF00;display:inline-block;margin-left:8px'></span> Zona caliente 🔥 <span style='margin-left:16px'>🪙 {st.session_state.coins} coins</span> <span style='margin-left:8px'>🏆 Leader {leader}</span></div>", unsafe_allow_html=True)

except Exception as e: st.error(f"Alpaca: {e}")

st.markdown(f"<div style='display:grid;grid-template-columns:1.2fr 0.6fr 0.7fr;gap:12px;margin:16px 0'><div><div style='color:#FFD700;font-weight:900;font-size:32px'>${price:,.0f}...</div><div style='font-size:10px;padding:4px 10px;border-radius:20px;background:rgba(0,255,136,0.15);color:#00FF88;display:inline-block'>Fib: ${fib:,.2f}</div></div><div><div style='color:#FFD700;font-weight:900;font-size:32px'>{z:.2f}</div><div style='font-size:10px;padding:4px 10px;border-radius:20px;background:rgba(0,255,136,0.15);color:#00FF88;display:inline-block'>Compra si -2</div></div><div><div style='color:#FFD700;font-weight:900;font-size:32px'>{lr*100:.3f}%</div><div style='font-size:10px;padding:4px 10px;border-radius:20px;background:rgba(255,70,70,0.15);color:#FF6B7A;display:inline-block'>-0.8 a -0.05</div></div></div>", unsafe_allow_html=True)
st.markdown(f"<div style='background:#00FF88;color:#000;font-weight:900;padding:12px;border-radius:10px;text-align:center'>{sema_txt} • {orden_msg}</div>", unsafe_allow_html=True)
fig,ax=plt.subplots(figsize=(10,4)); fig.patch.set_facecolor("#10131C"); ax.set_facecolor("#10131C")
ax.plot(precios,color="#00FF87",linewidth=2.5); ax.axhline(xb,color="#3A8B8B",linewidth=1,alpha=0.8); ax.axhline(fib,color="#FFD500",ls="--",linewidth=1.2)
ax.scatter([len(precios)-1],[price],s=120,color="#00FF4C",zorder=5,edgecolors="#10131C",linewidths=2)
ax.tick_params(colors="#6B7280",labelsize=9)
for sp in ax.spines.values(): sp.set_visible(False)
st.pyplot(fig)
b1,b2,b3,b4=st.columns(4)
with b1: st.markdown(f"<div class='box'>⏱️ <b>24 HORAS</b><br>{ret24:.2f}%</div>", unsafe_allow_html=True)
with b2: st.markdown(f"<div class='box'>📅 <b>7 DÍAS</b><br>{ret7:.2f}%</div>", unsafe_allow_html=True)
with b3: st.markdown(f"<div class='box'>📅 <b>30 DÍAS</b><br>{ret30:.2f}%</div>", unsafe_allow_html=True)
with b4: st.markdown(f"<div class='box'>🏔️ <b>vs MAX 1 AÑO</b><br>{vsmax:.2f}%</div>", unsafe_allow_html=True)
st.markdown(f"<div class='backtest'>🧠 <b>BACKTEST</b><br>{len(casos)} casos | Prob rebote 24h: {prob:.1f}% • 24h {avg24:.2f}% | 7d {avg7:.2f}%<br>⚠️ {sema_color}: {sema_txt}</div>", unsafe_allow_html=True)
st.markdown(f"<div style='background:#0B1A13;border:1.5px solid #00FF88;padding:12px;border-radius:10px;margin-top:12px;color:#4ADE80;font-weight:700;font-size:12px'>💎 V44 ULTIMATE: {sema_txt} • {orden_msg} • Auto {'ON' if st.session_state.auto_pilot else 'OFF'} • 🪙 {st.session_state.coins} • 🔥 {heat_buys} buys • 🏆 {leader}</div>", unsafe_allow_html=True)
