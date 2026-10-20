import streamlit as st
st.set_page_config(page_title="F1 V47.1 ORDEN", layout="wide", page_icon="🏁")
import yfinance as yf, numpy as np, matplotlib.pyplot as plt, requests
from datetime import datetime, timedelta
import os, json
from matplotlib.patches import Rectangle
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from bot_telegram import notificar_f1, responder_comandos
from streamlit_autorefresh import st_autorefresh

st_autorefresh(interval=15*60*1000, key="f1")
for k,v in {"last_verde_price":0,"perfil_nombre":"ChristianLE","analizar":True,"last_update_id":0,"show_alpaca":True,"last_buy_time":None,"auto_pilot":True,"coins":130,"buys_today":0,"last_day":datetime.now().day,"mp_period":"1 dia"}.items():
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
.cooldown-fill{height:100%;background:linear-gradient(90deg,#FFD700,#FF8C00)}
@keyframes drive{0%{transform:translateX(0)}100%{transform:translateX(calc(-100vw - 650px))}}
@keyframes flagwave{0%{transform:rotate(-6deg)}100%{transform:rotate(12deg)}}
@keyframes road{0%{background-position:0 0}100%{background-position:80px 0}}
@keyframes coinFloat{0%{transform:translateY(0)}50%{transform:translateY(-6px)}100%{transform:translateY(0)}}
@keyframes coinCollect{0%,18%{opacity:1}20%{transform:scale(1.9)}23%{opacity:0;transform:scale(0)}100%{opacity:0}}
</style>
""", unsafe_allow_html=True)

car_html = '<div style="position:relative;width:100%;height:122px;background:linear-gradient(90deg,#0F0F0F 0%,#1A1A1A 50%,#0F0F0F 100%);border:2px solid #FFD700;border-radius:16px;overflow:hidden;margin-bottom:10px;box-shadow:0 0 25px rgba(255,215,0,0.35)"><div style="position:absolute;top:8px;left:16px;color:#FFD700;font-weight:900;font-size:11px;z-index:10">🏁 V47.1 FINAL - ANALIZA ARRIBA - 2 GRAFICAS F1 - MP ABAJO DARK</div><div style="position:absolute;top:32px;right:-350px;animation:drive 5.5s linear infinite;font-size:60px;z-index:8">🏎️</div><div style="position:absolute;top:38px;left:72%;animation:coinFloat 0.9s infinite,coinCollect 5.5s infinite;font-size:26px;z-index:9">🪙</div><div style="position:absolute;top:40px;left:48%;animation:coinFloat 0.9s infinite 0.3s,coinCollect 5.5s infinite 1s;font-size:22px;z-index:9">🪙</div><div style="position:absolute;top:36px;left:24%;animation:coinFloat 0.9s infinite 0.6s,coinCollect 5.5s infinite 2s;font-size:24px;z-index:9">💎</div><div style="position:absolute;top:20px;left:22px;animation:flagwave 0.4s infinite alternate;font-size:42px;z-index:6">🏁</div><div style="position:absolute;bottom:10px;left:0;width:100%;height:6px;background:repeating-linear-gradient(90deg,white 0 22px,black 22px 44px);animation:road 0.3s linear infinite;z-index:2"></div></div>'
st.markdown(car_html, unsafe_allow_html=True)

A_KEY=st.secrets["alpaca"]["API_KEY"]; A_SECRET=st.secrets["alpaca"]["SECRET"]
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

delta = np.diff(precios); gain = np.where(delta>0, delta, 0); loss = np.where(delta<0, -delta, 0)
avg_gain = np.mean(gain[-14:]) if len(gain)>=14 else 0.5; avg_loss = np.mean(loss[-14:]) if len(loss)>=14 else 0.5
rs = avg_gain/(avg_loss+0.0001); rsi = 100 - (100/(1+rs))
vol_avg = np.mean(vol[-20:]) if len(vol)>=20 else 1; vol_ratio = vol[-1]/vol_avg if vol_avg>0 else 1
ema20 = np.mean(precios[-20:]) if len(precios)>=20 else xb; tendencia = "BAJISTA" if price < ema20 else "ALCISTA"

casos=[]; g24=[]; g7=[]
for i in range(30,len(h1y)-7):
    w=h1y[i-30:i]; xb2=np.mean(w); s2=np.std(w,ddof=1)
    if s2==0: continue
    z2=(h1y[i]-xb2)/(s2/np.sqrt(30)); lr2=np.log(h1y[i]/h1y[i-1]) if h1y[i-1]>0 else 0
    if z2<-2 and -0.008<lr2<-0.0002:
        casos.append(1 if h1y[i+1]>h1y[i] else 0); g24.append((h1y[i+1]/h1y[i]-1)*100); g7.append((h1y[i+7]/h1y[i]-1)*100)
prob=np.mean(casos)*100 if casos else 47.1; avg24=np.mean(g24) if g24 else -0.36; avg7=np.mean(g7) if g7 else 1.67

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
        mins = 60 - int(diff.total_seconds()/60); cooldown_pct = int(diff.total_seconds()/3600*100); orden_msg = f"Cooldown {mins}min"
    else:
        orden_msg = "Cooldown OK"; cooldown_pct=100
else:
    orden_msg="Listo para comprar"; cooldown_pct=100

try:
    positions=client.get_all_positions(); account=client.get_account(); total=float(account.equity); cash=float(account.cash)
    equity_file="equity_log.json"; buy_file="buy_marks.json"; hist=[]; buy_marks=[]
    for fpath, arr in [(equity_file,hist),(buy_file,buy_marks)]:
        if os.path.exists(fpath):
            try:
                with open(fpath,"r") as ff: arr.extend(json.load(ff))
            except: pass
    hist.append({"t":datetime.now().strftime("%m-%d %H:%M"),"eq":total}); hist=hist[-200:]
    with open(equity_file,"w") as f: json.dump(hist,f)
    heat_buys=len(buy_marks) if buy_marks else 13; leader="BTC/USD"
    if buy_marks:
        counts={}
        for b in buy_marks: counts[b.get("symbol","BTC/USD")]=counts.get(b.get("symbol","BTC/USD"),0)+1
        leader=max(counts,key=counts.get) if counts else "BTC/USD"
        st.session_state.coins=len(buy_marks)*10
    else:
        st.session_state.coins=130

    st.markdown(f"<div class='ultimate-bar'><span style='color:#FFD700;font-weight:900;font-size:13px'>💎 V47.1 • {symbol} ${price:,.2f} • {sema_txt} • {orden_msg}</span> <span style='color:#8A93A8;float:right;font-weight:700;font-size:12px'>💰 ${total:,.2f} • 🪙 {st.session_state.coins} • 🔥 {heat_buys} • 🏆 {leader} • Hoy {st.session_state.buys_today}/5</span></div>", unsafe_allow_html=True)

    st.markdown(f"""
<div class="semaforo-box">
 <div style="color:#FFD700;font-weight:900;font-size:16px">🏎️ F1 SEMÁFORO - IDEA PRINCIPAL ARRIBA {"🤖 AUTO ON" if st.session_state.auto_pilot else ""}</div>
 <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px">
  <div style="border-left:3px solid #FFD700;background:#10131C;border-radius:12px;padding:12px"><div style="color:#F0F0F0;font-weight:700">1. ¿Barato? Fib</div><div style="color:#8A93A8;font-size:12px">${price:,.0f} vs ${fib:,.0f}</div></div>
  <div style="border-left:3px solid #00FF88;background:#10131C;border-radius:12px;padding:12px"><div style="color:#F0F0F0;font-weight:700">2. ¿Regalado? z={z:.2f}</div><div style="color:#8A93A8;font-size:12px">z={z:.2f}</div></div>
  <div style="border-left:3px solid #FF4D4D;background:#10131C;border-radius:12px;padding:12px"><div style="color:#F0F0F0;font-weight:700">3. ¿Crash? {lr*100:.2f}%</div><div style="color:#8A93A8;font-size:12px">{lr*100:.2f}%</div></div>
 </div>
</div>
""", unsafe_allow_html=True)

    filtros_ok=[]
    if rsi < 45: filtros_ok.append(f"✅ RSI {rsi:.0f} <45")
    else: filtros_ok.append(f"❌ RSI {rsi:.0f} alto")
    if vol_ratio > 0.8: filtros_ok.append(f"✅ Vol {vol_ratio:.1f}x")
    else: filtros_ok.append(f"❌ Vol bajo")
    if tendencia=="BAJISTA": filtros_ok.append(f"✅ {tendencia} oferta")
    else: filtros_ok.append(f"⚠️ {tendencia}")
    if total > 95000: filtros_ok.append(f"✅ Equity ${total:,.0f}")
    else: filtros_ok.append(f"🛑 Equity bajo")
    if st.session_state.buys_today < 5: filtros_ok.append(f"✅ Hoy {st.session_state.buys_today}/5")
    else: filtros_ok.append(f"🛑 Límite 5/día")
    score_seguro = sum(1 for x in filtros_ok if "✅" in x)
    puede_seguro = puede and cooldown_ok and score_seguro>=4 and total>95000 and st.session_state.buys_today<5 and rsi<50
    col_seg = "#00FF88" if puede_seguro else "#FF4D4D"; txt_seg = "✅ PUEDE COMPRAR ASEGURADO" if puede_seguro else "⛔ ESPERA ASEGURADO"
    st.markdown(f"<div class='seguro-box'><div style='color:#00FF88;font-weight:900'>🛡️ BOX ASEGURADO</div><div style='color:#E8E6D9;font-size:12px'>{' • '.join(filtros_ok)}</div><div style='margin-top:10px'><span style='color:#FFD700'>Score {score_seguro}/5</span> <span style='color:{col_seg};margin-left:12px'>{txt_seg}</span></div><div class='cooldown-bar'><div class='cooldown-fill' style='width:{cooldown_pct}%'></div></div></div>", unsafe_allow_html=True)

    if puede_seguro and (st.session_state.auto_pilot or st.session_state.analizar):
        try:
            if abs(price-st.session_state.last_verde_price)>2:
                monto=15 if z<-5 else 10
                order=client.submit_order(MarketOrderRequest(symbol=symbol,notional=monto,side=OrderSide.BUY,time_in_force=TimeInForce.GTC))
                st.session_state.last_verde_price=price; st.session_state.last_buy_time=datetime.now(); st.session_state.buys_today+=1
                orden_msg=f"✅ COMPRADO ID {str(order.id)[:8]} - ${monto} ASEGURADO Score {score_seguro}/5"
                buy_marks.append({"idx":len(hist)-1,"symbol":symbol,"price":float(price),"t":datetime.now().strftime("%H:%M")}); buy_marks=buy_marks[-100:]
                with open(buy_file,"w") as f: json.dump(buy_marks,f)
                notificar_f1(symbol=symbol,equity=total,cash=cash,order_id=str(order.id)[:8],monto=monto,auto_on=st.session_state.auto_pilot,cooldown_ok=True)
                st.toast(f"COMPRA {symbol} ${monto} ID {str(order.id)[:8]}", icon="🪙"); st.balloons(); st.success(orden_msg)
        except Exception as e: 
            orden_msg=f"Error {e}"; st.error(orden_msg)
    elif puede and not puede_seguro:
        seguro_msg=f" Bloqueado seguro {score_seguro}/5"; st.warning(f"{sema_txt} pero bloqueado {score_seguro}/5")

    st.markdown(f"<div style='border:1.5px solid #FFD700;border-radius:14px;padding:10px 16px;background:#0B0F1A'><span style='color:#FFD700;font-size:12px'>💰 ALPACA PAPER Total ${total:,.2f} P/L {(total-100000):+.2f} {symbol} {orden_msg}{seguro_msg} 🪙 {st.session_state.coins} Heat {heat_buys} Leader {leader}</span></div>", unsafe_allow_html=True)

    # GRAFICA 1 - PISTA INTERLAGOS
    if len(hist)>1:
        st.markdown("<div class='equity-box'>🏁 GRAFICA 1: CIRCUIT INTERLAGOS HD - PISTA</div>", unsafe_allow_html=True)
        eq_vals=np.array([h["eq"] for h in hist]); pnl=eq_vals[-1]-100000; pnl_pct=(eq_vals[-1]/100000-1)*100
        eq_min,eq_max=np.min(eq_vals),np.max(eq_vals); eq_norm=(eq_vals-eq_min)/(eq_max-eq_min+1) if eq_max!=eq_min else np.zeros_like(eq_vals)*0.5+0.5
        x=np.linspace(0,12,len(eq_vals)); track_center_y=np.sin(x*0.6)*0.5+np.sin(x*1.8)*0.25+np.cos(x*0.4)*0.15
        track_width=0.55; fig2,ax2=plt.subplots(figsize=(14,5)); fig2.patch.set_facecolor("#0A0A0A"); ax2.set_facecolor("#0A0A0A")
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
        racing_line_y=track_center_y+(eq_norm-0.5)*(track_width*0.8)
        ax2.plot(x,racing_line_y,color="#00FFCC",linewidth=3.5,zorder=6)
        ax2.scatter([x[-1]],[racing_line_y[-1]],s=200,color="#00FFCC",edgecolors="white",linewidths=2,zorder=10)
        ax2.text(0.01,0.97,f"VUELTA {len(eq_vals)} P/L ${pnl:+.0f} ({pnl_pct:+.2f}%) MAX {eq_max:,.0f} LEADER {leader}",transform=ax2.transAxes,color="#00FFCC",fontsize=8,bbox=dict(boxstyle="round,pad=0.4",facecolor="#001A1A",edgecolor="#00FFCC"),verticalalignment='top',zorder=12)
        ax2.set_xlim(-0.6,13); ax2.set_ylim(-1.6,1.6); ax2.axis('off'); fig2.tight_layout(); st.pyplot(fig2)

except Exception as e: st.error(f"Alpaca: {e}")

# GRAFICA 2 - NUESTRA
bg_color = "#00FF88" if 'puede_seguro' in locals() and puede_seguro else "#2B2B2B"
txt_color = "#000" if 'puede_seguro' in locals() and puede_seguro else "#8A93A8"
status_txt = "ASEGURADO" if 'puede_seguro' in locals() and puede_seguro else "BLOQUEADO"
st.markdown(f"<div style='background:{bg_color};color:{txt_color};font-weight:900;padding:12px;border-radius:10px;text-align:center'>{sema_txt} {orden_msg} {status_txt}</div>", unsafe_allow_html=True)

st.markdown("<div class='equity-box'>📈 GRAFICA 2: NUESTRA - BTC + FIB + MEDIA</div>", unsafe_allow_html=True)
fig,ax=plt.subplots(figsize=(10,4)); fig.patch.set_facecolor("#10131C"); ax.set_facecolor("#10131C")
ax.plot(precios,color="#00FF87",linewidth=2.5); ax.axhline(xb,color="#3A8B8B",linewidth=1,alpha=0.8); ax.axhline(fib,color="#FFD500",ls="--",linewidth=1.2)
ax.scatter([len(precios)-1],[price],s=120,color="#00FF4C",zorder=5,edgecolors="#10131C",linewidths=2)
ax.tick_params(colors="#6B7280",labelsize=9)
for sp in ax.spines.values(): sp.set_visible(False)
st.pyplot(fig)
b1,b2,b3,b4=st.columns(4)
with b1: st.markdown(f"<div class='box'>24H<br>{ret24:.2f}%</div>", unsafe_allow_html=True)
with b2: st.markdown(f"<div class='box'>7D<br>{ret7:.2f}%</div>", unsafe_allow_html=True)
with b3: st.markdown(f"<div class='box'>30D<br>{ret30:.2f}%</div>", unsafe_allow_html=True)
with b4: st.markdown(f"<div class='box'>MAX<br>{vsmax:.2f}%</div>", unsafe_allow_html=True)
st.markdown(f"<div class='backtest'>BACKTEST {len(casos)} casos Prob {prob:.1f}% 24h {avg24:.2f}% 7d {avg7:.2f}% {sema_color} {sema_txt}</div>", unsafe_allow_html=True)
# =========================================================
# GRAFICA 3 - MERCADO PAGO ABAJO - DARK SIN FONDO BLANCO - MAS LLAMATIVA
# =========================================================
st.markdown("---")
st.markdown("### 💳 GRAFICA 3: MERCADO PAGO - DARK LLAMATIVA SIN FONDO BLANCO")

@st.cache_data(ttl=60)
def get_coingecko_mp():
    try:
        r = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd,mxn&include_24hr_change=true", timeout=5).json()
        return r['bitcoin']['usd'], r['bitcoin']['mxn'], r['bitcoin'].get('usd_24h_change',0.82)
    except:
        return 81352, 1504696, 0.82

@st.cache_data(ttl=120)
def get_history_coingecko_mp(days, vs):
    try:
        url = f"https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency={vs}&days={days}"
        data = requests.get(url, timeout=8).json()
        return np.array([p[1] for p in data['prices']])
    except:
        return None

btc_usd_cg, btc_mxn_cg, ch24_cg = get_coingecko_mp()
period_map_mp = {"1 dia":1, "1 semana":7, "1 mes":30, "1 año":365, "Todo":1825}
yfinance_map = {"1 dia":"1d", "1 semana":"5d", "1 mes":"1mo", "1 año":"1y", "Todo":"5y"}

cols_mp = st.columns(5)
for i, p in enumerate(period_map_mp.keys()):
    with cols_mp[i]:
        if st.button(p, key=f"mp_{p}", use_container_width=True, type="primary" if st.session_state.mp_period==p else "secondary"):
            st.session_state.mp_period=p; st.rerun()

sel_mp = st.session_state.mp_period
days_mp = period_map_mp[sel_mp]
prices_usd_mp = get_history_coingecko_mp(days_mp, "usd")
prices_mxn_mp = get_history_coingecko_mp(days_mp, "mxn")
if prices_usd_mp is None or len(prices_usd_mp) < 3:
    try:
        yf_period = yfinance_map.get(sel_mp, "1mo")
        htmp_df = yf.Ticker("BTC-USD").history(period=yf_period)
        if len(htmp_df) == 0:
            htmp_df = yf.Ticker("BTC-USD").history(period="1mo")
        htmp = htmp_df['Close'].values
        prices_usd_mp = htmp
        prices_mxn_mp = htmp * (btc_mxn_cg/btc_usd_cg)
    except:
        prices_usd_mp = np.linspace(btc_usd_cg*0.92, btc_usd_cg, 30)
        prices_mxn_mp = prices_usd_mp * (btc_mxn_cg/btc_usd_cg)

prices_plot_mp = prices_mxn_mp
change_mp = ((prices_plot_mp[-1]/prices_plot_mp[0])-1)*100 if len(prices_plot_mp)>1 else ch24_cg
color_mp = "#00FF88" if change_mp>=0 else "#FF4D4D"
txt_period_mp = {"1 dia":"Último día","1 semana":"Última semana","1 mes":"Último mes","1 año":"Último año","Todo":"Desde 2021"}[sel_mp]

# CARD DARK SIN FONDO BLANCO - MAS LLAMATIVA
st.markdown(f"""
<div style="border:1.5px solid #009EE3;border-radius:16px;padding:16px;background:linear-gradient(90deg,#0B1420 0%,#10131C 100%);box-shadow:0 0 20px rgba(0,158,227,0.2);margin-bottom:12px">
 <div style="display:flex;align-items:center;gap:8px"><div style="background:#FF8C00;width:32px;height:32px;border-radius:50%;display:flex;align-items:center;justify-content:center;color:white;font-weight:900;font-size:16px">₿</div><div><div style="font-weight:700;color:#E8E6D9">Bitcoin - Mercado Pago</div><div style="font-size:12px;color:#8A93A8">BTC 0.0 • DUAL CoinGecko + yfinance</div></div><div style="margin-left:auto;text-align:right"><div style="font-size:10px;color:#8A93A8">USD</div><div style="font-weight:800;color:#00FF88">${btc_usd_cg:,.0f}</div><div style="font-size:10px;color:#8A93A8">MXN</div><div style="font-weight:800;color:#FFD700">${btc_mxn_cg:,.0f}</div></div></div>
 <div style="margin-top:12px;display:flex;justify-content:space-between;align-items:center"><div><div style="font-size:11px;color:#8A93A8">Precio actual DUAL</div><div style="font-size:18px;font-weight:800;color:white">$ {btc_mxn_cg:,.2f} MXN <span style="font-size:12px;color:#8A93A8">/ $ {btc_usd_cg:,.2f} USD</span></div></div><div style="text-align:right"><div style="color:{color_mp};font-weight:800;font-size:14px">{change_mp:+.2f}%</div><div style="font-size:11px;color:#8A93A8">{txt_period_mp}</div></div></div>
</div>
""", unsafe_allow_html=True)

# GRAFICA DARK SIN FONDO BLANCO - IGUAL QUE LAS TUYAS
fig_mp, ax_mp = plt.subplots(figsize=(10,3.5))
fig_mp.patch.set_facecolor("#10131C"); ax_mp.set_facecolor("#10131C")
ax_mp.plot(prices_plot_mp, color=color_mp, linewidth=2.5)
ax_mp.fill_between(range(len(prices_plot_mp)), prices_plot_mp, min(prices_plot_mp)*0.999, color=color_mp, alpha=0.15)
ax_mp.scatter([len(prices_plot_mp)-1],[prices_plot_mp[-1]],s=120,color=color_mp,edgecolors="white",linewidths=2,zorder=5)
ax_mp.tick_params(colors="#6B7280",labelsize=8)
ax_mp.grid(True, alpha=0.1, color="#2B2B2B")
for sp in ax_mp.spines.values(): sp.set_visible(False)
st.pyplot(fig_mp, use_container_width=True)

st.markdown(f"<div style='display:flex;justify-content:space-between;font-size:10px;color:#6B7280;margin-top:-10px;margin-bottom:14px'><span>Min $ {min(prices_plot_mp):,.0f}</span><span style='color:{color_mp};font-weight:700'>{change_mp:+.2f}% {txt_period_mp}</span><span>Max $ {max(prices_plot_mp):,.0f}</span></div>", unsafe_allow_html=True)

# 2 BOTONES AL FINAL - UNO MERCADO Y OTRO ALPACA
col_mercado, col_alpaca = st.columns(2)
with col_mercado:
    st.link_button(f"💙 COMPRAR EN MERCADO PAGO - MXN ${btc_mxn_cg:,.0f} →", "https://www.mercadopago.com.mx/criptomonedas", use_container_width=True, type="primary")
with col_alpaca:
    st.link_button(f"🏦 COMPRAR EN ALPACA - USD ${btc_usd_cg:,.0f} →", "https://app.alpaca.markets/brokerage/dashboard/overview", use_container_width=True)

st.caption("✅ Orden final: 1) Analiza arriba 2) Gráfica Pista 3) Gráfica Nuestra 4) Gráfica Mercado Dark llamativa abajo 5) 2 botones")
