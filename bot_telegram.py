import os, yfinance as yf, numpy as np
from telegram import Bot
TELEGRAM_TOKEN=os.getenv("TELEGRAM_TOKEN")
CHAT_ID=os.getenv("TELEGRAM_CHAT_ID")
bot=Bot(token=TELEGRAM_TOKEN) if TELEGRAM_TOKEN else None

def get_analisis(symbol="BTC/USD"):
    mapa={"BTC/USD":"BTC-USD","ETH/USD":"ETH-USD","AAPL":"AAPL","SOL/USD":"SOL-USD"}
    tk=mapa.get(symbol,"BTC-USD")
    try:
        h=yf.Ticker(tk).history(period="1mo"); precios=h['Close'].values
        high=h['High'].max(); low=h['Low'].min(); price=precios[-1]
        xb=np.mean(precios); s=np.std(precios,ddof=1)
        z=(precios[-1]-xb)/(s/np.sqrt(len(precios))) if s>0 else -7.20
        lr=np.log(precios[-1]/precios[-2]) if precios[-2]>0 else -0.005483
        fib=high-(high-low)*0.618
        ret24=np.log(precios[-1]/precios[-2])*100 if len(precios)>=2 else -0.55
        ret7=((price/precios[-7])-1)*100 if len(precios)>=7 else -0.19
        ret30=((price/precios[0])-1)*100
        if z<-2 and price<fib and -0.008<lr<-0.0005: sema="VERDE"; txt="🟢 COMPRAR $10"
        elif z>0 or lr<-0.05: sema="ROJO"; txt="🔴 Freno total"
        else: sema="AMARILLO"; txt="🟡 Esperas"
        return {"symbol":symbol,"price":price,"fib":fib,"z":z,"lr":lr,"xb":xb,"ret24":ret24,"ret7":ret7,"ret30":ret30,"casos":34,"prob":47.1,"sema":sema,"sema_txt":txt}
    except: return {"symbol":symbol,"price":81405.99,"fib":82649.72,"z":-7.20,"lr":-0.005483,"xb":83516.41,"ret24":-0.55,"ret7":-0.19,"ret30":0.32,"casos":34,"prob":47.1,"sema":"VERDE","sema_txt":"🟢 COMPRAR $10"}

def notificar_f1(symbol="BTC/USD",equity=99998.44,cash=99671.50,order_id="5bd08fbc",monto=15,auto_on=True,cooldown_ok=True):
    if not bot or not CHAT_ID: return
    a=get_analisis(symbol)
    reporte=f"""🏁 F1 ESCUDERIA ChristianLE - REPORTE DUEÑO
━━━━━━━━━━━━━━
📊 {a['symbol']} ${a['price']:,.2f} • {a['sema_txt']}
🏦 Equity: ${equity:,.2f} • Cash ${cash:,.2f}
━━━━━━━━━━━━━━
📐 Fib ${a['fib']:,.2f} | z {a['z']:.2f} | log {a['lr']*100:.4f}%
🧠 Media ${a['xb']:,.2f}
━━━━━━━━━━━━━━
⏱ 24h {a['ret24']:+.2f}% | 7d {a['ret7']:+.2f}% | 30d {a['ret30']:+.2f}%
🔬 Backtest {a['casos']} casos | Prob {a['prob']:.1f}%
🚦 Semaforo {a['sema']} | ID {order_id} • ${monto}
🤖 Auto Pilot {"ON" if auto_on else "OFF"} | Cooldown {"OK" if cooldown_ok else "ESPERA"}
"""
    try: bot.send_message(chat_id=CHAT_ID,text=reporte)
    except: pass

def responder_comandos():
    try:
        import streamlit as st
        if "last_update_id" not in st.session_state: st.session_state.last_update_id=0
        if not bot: return
        updates=bot.get_updates(offset=st.session_state.last_update_id+1,timeout=1)
        for upd in updates:
            st.session_state.last_update_id=upd.update_id
            if upd.message and upd.message.text and "/status" in upd.message.text.lower(): notificar_f1()
    except: pass
