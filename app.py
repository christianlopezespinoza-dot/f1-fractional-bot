import streamlit as st
st.set_page_config(page_title="F1 V45 COMPLETO", layout="wide", page_icon="🛡️")
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
for k,v in {"last_verde_price":0,"perfil_nombre":"ChristianLE","analizar":True,"last_update_id":0,"show_alpaca":True,"last_buy_time":None,"auto_pilot":True,"coins":130,"buys_today":0,"last_day":datetime.now().day}.items():
    if k not in st.session_state: st.session_state[k]=v
responder_comandos()
if st.session_state.last_day != datetime.now().day:
    st.session_state.buys_today=0
    st.session_state.last_day=datetime.now().day

st.markdown("""
<style>
[data-testid="stAppViewContainer"]{background:#10131C!important}
.semaforo-box{border:1.5px solid #FFD700;border-radius:16px;padding:16px;background:#181B27;box-shadow:0 0 15px rgba(255,215,0,0.2);margin-bottom:14px}
.box{border:1.5px solid #FFC800;background:rgba(255,200,0,0.08);padding:14px;border-radius:14px;min-height:85px;color:#E8E6D9}
.backtest{border:1.5px solid #FFC800;background:#1C1A08;padding:18px;border-radius:14px;margin-top:12px;color:#E8E6D9}
.port-card{border:1.5px solid #00FF88;background:#0B1A13;padding:12px;border-radius:12px;margin-bottom:10px}
.equity-box{border:1.5px solid #00FF88;background:#0B1A13;padding:16px;border-radius:14px;margin-top:12px}
.ultimate-bar{border:2px solid #FFD700;border-radius:14px;padding:12px 18px;background:linear-gradient(90deg,#0B0F1A 0%,#1A1A0B 100%);margin-bottom:12px;box-shadow:0 0 20px rgba(255,215,0,0.3)}
.seguro-box{border:2px solid #00FF88;border-radius:14px;padding:14px;background:linear-gradient(90deg,#0B1A13 0%,#0F1A0B 100%);margin:12px 0}
.cooldown-bar{height:8px;border-radius:10px;background:#2B2B2B;margin-top:6px;overflow:hidden}
.cooldown-fill{height:100%;background:linear-gradient(90deg,#FFD700,#FF8C00);transition:width 1s}
@keyframes drive{0%{transform:translateX(0)}100%{transform:translateX(calc(-100vw - 650px))}}
@keyframes flagwave{0%{transform:rotate(-6deg)}100%{transform:rotate(12deg)}}
@keyframes road{0%{background-position:0 0}100%{background-position:80px 0}}
@keyframes coinFloat{0%{transform:translateY(0)}50%{transform:translateY(-6px)}100%{transform:translateY(0)}}
@keyframes coinCollect{0%,18%{opacity:1}20%{transform:scale(1.9)}23%{opacity:0;transform:scale(0)}100%{opacity:0}}
</style>
""", unsafe_allow_html=True)

car_html = '<div style="position:relative;width:100%;height:122px;background:linear-gradient(90deg,#0F0F0F 0%,#1A1A1A 50%,#0F0F0F 100%);border:2px solid #FFD700;border-radius:16px;overflow:hidden;margin-bottom:10px;box-shadow:0 0 25px rgba(255,215,0,0.35)"><div style="position:absolute;top:8px;left:16px;color:#FFD700;font-weight:900;font-size:11px;z-index:10">🛡️ V45 COMPLETO - ESCUDERIA ChristianLE - TODO + ASEGURADO</div><div style="position:absolute;top:32px;right:-350px;animation:drive 5.5s linear infinite;font-size:60px;z-index:8">🏎️</div><div style="position:absolute;top:38px;left:72%;animation:coinFloat 0.9s infinite,coinCollect 5.5s infinite;font-size:26px;z-index:9">🪙</div><div style="position:absolute;top:40px;left:48%;animation:coinFloat 0.9s infinite 0.3s,coinCollect 5.5s infinite 1s;font-size:22px;z-index:9">🪙</div><div style="position:absolute;top:36px;left:24%;animation:coinFloat 0.9s infinite 0.6s,coinCollect 5.5s infinite 2s;font-size:24px;z-index:9">💎</div><div style="position:absolute;top:20px;left:22px;animation:flagwave 0.4s infinite alternate;font-size:42px;z-index:6">🏁</div><div style="position:absolute;bottom:10px;left:0;width:100%;height:6px;background:repeating-linear-gradient(90deg,white 0 22px,black 22px 44px);animation:road 0.3s linear infinite;z-index:2"></div></div>'
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
        try: client.close_all_positions(cancel_orders=True); st.error("PANICO CERRADO")
        except Exception as e: st.error(str(e))
with c3: st.session_state.auto_pilot=st.toggle("🤖 Auto",value=st.session_state.auto_pilot)

mapa={"BTC/USD":"BTC-USD","ETH/USD":"ETH-USD","AAPL":"AAPL","SOL/USD":"SOL-USD"}
tk=mapa[symbol]
h=yf.Ticker(tk).history(period="1mo")
precios=h['Close'].values; high=h['High'].max(); low=h['Low'].min(); price=precios[-1]
vol=h['Volume'].values if 'Volume' in h.columns and len(h['Volume'])>0 else np.ones(len(precios))
h1y=yf.Ticker(tk).history(period="1y")['Close'].values
xb=np.mean(precios); s=np.std(precios,ddof=1)
z=(precios[-1]-xb)/(s/np.sqrt(len(precios))) if s>0 else -7.37
lr=np.log(precios[-1]/precios[-2]) if precios[-2]>0 else -0.0061
fib=high-(high-low)*0.618
max1y=np.max(h1y) if len(h1y)>0 else price
ret24=np.log(precios[-1]/precios[-2])*100 if len(precios)>=2 else -0.61
ret7=((price/precios[-7])-1)*100 if len(precios)>=7 else -0.26
ret30=((price/precios[0])-1)*100; vsmax=((price/max1y)-1)*100

delta = np.diff(precios)
gain = np.where(delta>0, delta, 0); loss = np.where(delta<0, -delta, 0)
avg_gain = np.mean(gain[-14:]) if len(gain)>=14 else 0.5
avg_loss = np.mean(loss[-14:]) if len(loss)>=14 else 0.5
rs = avg_gain/(avg_loss+0.0001)
rsi = 100 - (100/(1+rs))
vol_avg = np.mean(vol[-20:]) if len(vol)>=20 else 1
vol_ratio = vol[-1]/vol_avg if vol_avg>0 else 1
ema20 = np.mean(precios[-20:]) if len(precios)>=20 else xb
tendencia = "BAJISTA" if price < ema20 else "ALCISTA"

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
    if z > 0 or lr < -0.05: sema_color="ROJO"; sema_txt="🔴 Freno total"
    else: sema_color="AMARILLO"; sema_txt="🟡 Esperas"

orden_msg=""; seguro_msg=""; cooldown_ok=True; cooldown_pct=100
if st.session_state.last_buy_time:
    diff = datetime.now() - st.session_state.last_buy_time
    cooldown_ok = diff > timedelta(hours=1)
    if not cooldown_ok:
        mins = 60 - int(diff.total_seconds()/60)
        cooldown_pct = int(diff.total_seconds()/3600*100)
        orden_msg = f"Cooldown {mins}min"
    else:
        orden_msg = "Cooldown OK"; cooldown_pct=100
else:
    orden_msg="Listo para comprar"; cooldown_pct=100

try:
    positions=client.get_all_positions(); account=client.get_account(); total=float(account.equity); cash=float(account.cash)
    equity_file="equity_log.json"; buy_file="buy_marks.json"; tp_file="tp_marks.json"
    hist=[]; buy_marks=[]; tp_marks=[]
    for fpath, arr in [(equity_file,hist),(buy_file,buy_marks),(tp_file,tp_marks)]:
        if os.path.exists(fpath):
            try:
                with open(fpath,"r") as ff: arr.extend(json.load(ff))
            except: pass
    hist.append({"t":datetime.now().strftime("%m-%d %H:%M"),"eq":total}); hist=hist[-200:]
    with open(equity_file,"w") as f: json.dump(hist,f)

    heat_buys=len(buy_marks) if buy_marks else 13
    leader="BTC/USD"
    if buy_marks:
        counts={}
        for b in buy_marks: counts[b.get("symbol","BTC/USD")]=counts.get(b.get("symbol","BTC/USD"),0)+1
        leader=max(counts,key=counts.get) if counts else "BTC/USD"
        st.session_state.coins=len(buy_marks)*10
    else:
        st.session_state.coins=130

    st.markdown(f"<div class='ultimate-bar'><span style='color:#FFD700;font-weight:900;font-size:13px'>💎 V45 COMPLETO TODO + ASEGURADO</span> <span style='color:#00FF88;font-weight:800;margin-left:12px'>{symbol} ${price:,.2f} • {sema_txt}</span> <span style='color:#8A93A8;float:right;font-weight:700;font-size:12px'>💰 ${total:,.2f} • 🪙 {st.session_state.coins} • 🔥 Heat {heat_buys} buys • 🏆 Leader {leader} • Hoy {st.session_state.buys_today}/5</span></div>", unsafe_allow_html=True)

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

    filtros_ok=[]
    if rsi < 45: filtros_ok.append(f"✅ RSI {rsi:.0f} <45")
    else: filtros_ok.append(f"❌ RSI {rsi:.0f} alto")
    if vol_ratio > 0.8: filtros_ok.append(f"✅ Vol {vol_ratio:.1f}x")
    else: filtros_ok.append(f"❌ Vol bajo {vol_ratio:.1f}x")
    if tendencia=="BAJISTA": filtros_ok.append(f"✅ Tendencia {tendencia} (oferta)")
    else: filtros_ok.append(f"⚠️ {tendencia}")
    if total > 95000: filtros_ok.append(f"✅ Equity ${total:,.0f} >95k")
    else: filtros_ok.append(f"🛑 Equity bajo ${total:,.0f}")
    if st.session_state.buys_today < 5: filtros_ok.append(f"✅ Hoy {st.session_state.buys_today}/5")
    else: filtros_ok.append(f"🛑 Límite 5/día")

    score_seguro = sum(1 for x in filtros_ok if "✅" in x)
    puede_seguro = puede and cooldown_ok and score_seguro>=4 and total>95000 and st.session_state.buys_today<5 and rsi<50

    st.markdown(f"""
<div class='seguro-box'>
 <div style='color:#00FF88;font-weight:900;font-size:13px'>🛡️ BOX ASEGURADO - Para no perder (aparte de tu semáforo original)</div>
 <div style='color:#E8E6D9;font-size:12px;margin-top:8px;display:flex;flex-wrap:wrap;gap:8px'>{" • ".join(filtros_ok)}</div>
 <div style='margin-top:10px'><span style='color:#FFD700;font-weight:800'>Score Seguro: {score_seguro}/5</span> <span style='color:{"#00FF88" if puede_seguro else "#FF4D4D"};font-weight:900;margin-left:12px'>{"✅ PUEDE COMPRAR ASEGURADO" if puede_seguro else "⛔ ESPERA ASEGURADO"}</span></div>
 <div class='cooldown-bar'><div class='cooldown-fill' style='width:{cooldown_pct}%'></div></div>
 <div style='color:#8A93A8;font-size:10px;margin-top:4px'>⏳ Cooldown 1h: {cooldown_pct}% • {orden_msg} • Auto {"ON" if st.session_state.auto_pilot else "OFF"}</div>
</div>
""", unsafe_allow_html=True)

    if puede_seguro and (st.session_state.auto_pilot or st.session_state.analizar):
        try:
            if abs(price-st.session_state.last_verde_price)>2:
                monto=15 if z<-5 else 10
                order=client.submit_order(MarketOrderRequest(symbol=symbol,notional=monto,side=OrderSide.BUY,time_in_force=TimeInForce.GTC))
                st.session_state.last_verde_price=price; st.session_state.last_buy_time=datetime.now()
                st.session_state.buys_today+=1
                orden_msg=f"ID {str(order.id)[:8]} - ${monto} ASEGURADO"
                buy_marks.append({"idx":len(hist)-1,"symbol":symbol,"price":float(price),"t":datetime.now().strftime("%H:%M")})
                buy_marks=buy_marks[-100:]
                with open(buy_file,"w") as f: json.dump(buy_marks,f)
                notificar_f1(symbol=symbol,equity=total,cash=cash,order_id=str(order.id)[:8],monto=monto,auto_on=st.session_state.auto_pilot,cooldown_ok=True)
                st.toast(f"🛡️ COMPRA ASEGURADA {symbol} ${monto} - Score {score_seguro}/5", icon="🪙")
                st.balloons()
        except Exception as e: orden_msg=f"Error {e}"
    elif puede and not puede_seguro:
        seguro_msg=f" ⛔ Bloqueado seguro {score_seguro}/5"

    pl_color="#00FF88" if (total-100000)>=0 else "#FF4D4D"
    st.markdown(f"<div style='border:1.5px solid #FFD700;border-radius:14px;padding:10px 16px;background:#0B0F1A;margin-bottom:10px'><span style='color:#FFD700;font-weight:800;font-size:12px'>💰 ALPACA PAPER • Total ${total:,.2f} • P/L <span style='color:{pl_color}'>{(total-100000):+.2f}</span> • {symbol} • {orden_msg}{seguro_msg} • 🪙 {st.session_state.coins} • 🔥 {heat_buys} buys • 🏆 {leader}</span> <span style='color:#8A93A8;font-size:10px;float:right'>escuderia ChristianLE</span></div>", unsafe_allow_html=True)

    c_alp1,c_alp2=st.columns(2)
    with c_alp1:
        if st.button("💰 Ver en Alpaca →",use_container_width=True): st.session_state.show_alpaca=not st.session_state.show_alpaca
    with c_alp2: st.link_button("🔗 Abrir Dashboard Alpaca","https://app.alpaca.markets/brokerage/dashboard/overview",use_container_width=True)
    if st.session_state.show_alpaca:
        st.markdown(f"<div class='port-card'>🏦 <b>Escudería {st.session_state.perfil_nombre}</b> • Equity ${total:,.2f} • Cash ${cash:,.2f} • Auto {'ON 🤖' if st.session_state.auto_pilot else 'OFF'}</div>", unsafe_allow_html=True)
        for p in positions:
            pl=float(p.unrealized_pl); pct=float(p.unrealized_plpc)*100 if hasattr(p,'unrealized_plpc') else 0
            st.markdown(f"**{'🟢' if pl>=0 else '🔴'} {p.symbol}** {float(p.qty):.6f} • ${float(p.market_value):.2f} • P/L {pl:+.2f} ({pct:+.2f}%)", unsafe_allow_html=True)

    if len(hist)>1:
        st.markdown("<div class='equity-box'>🏁 <b>CIRCUIT INTERLAGOS HD - V45 COMPLETO - VUELTA + P/L + BTC/USD TAGS + HEATMAP + ASEGURADO</b></div>", unsafe_allow_html=True)
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
        st.markdown(f"<div style='display:flex;gap:16px;font-size:11px;color:#8A93A8;margin-top:6px'><span style='width:14px;height:10px;background:#2B2B2B;display:inline-block'></span> Sin compras <span style='width:14px;height:10px;background:#FF8C00;display:inline-block;margin-left:8px'></span> Pocas <span style='width:14px;height:10px;background:#8B0000;display:inline-block;margin-left:8px'></span> Muchas <span style='width:14px;height:10px;background:#FFFF00;display:inline-block;margin-left:8px'></span> Zona caliente 🔥 <span style='margin-left:16px'>🪙 {st.session_state.coins} coins</span> <span style='margin-left:8px'>🏆 Leader {leader}</span> <span style='margin-left:8px'>🛡️ Score {score_seguro}/5</span></div>", unsafe_allow_html=True)

except Exception as e: st.error(f"Alpaca: {e}")

st.markdown(f"<div style='display:grid;grid-template-columns:1.2fr 0.6fr 0.7fr;gap:12px;margin:16px 0'><div><div style='color:#FFD700;font-weight:900;font-size:32px'>${price:,.0f}...</div><div style='font-size:10px;padding:4px 10px;border-radius:20px;background:rgba(0,255,136,0.15);color:#00FF88;display:inline-block'>Fib: ${fib:,.2f}</div></div><div><div style='color:#FFD700;font-weight:900;font-size:32px'>{z:.2f}</div><div style='font-size:10px;padding:4px 10px;border-radius:20px;background:rgba(0,255,136,0.15);color:#00FF88;display:inline-block'>Compra si -2</div></div><div><div style='color:#FFD700;font-weight:900;font-size:32px'>{lr*100:.3f}%</div><div style='font-size:10px;padding:4px 10px;border-radius:20px;background:rgba(255,70,70,0.15);color:#FF6B7A;display:inline-block'>-0.8 a -0.05</div></div></div>", unsafe_allow_html=True)
st.markdown(f"<div style='background:{"#00FF88" if puede_seguro else "#2B2B2B"};colo
