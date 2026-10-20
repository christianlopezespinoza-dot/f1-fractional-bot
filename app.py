import streamlit as st
import yfinance as yf
import requests
import time
import math
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from bot_telegram import notificar_f1

st.set_page_config(page_title="F1 V21 SEMAFORO PRO", page_icon="🏎️", layout="wide")

# SECRETS
A_KEY = st.secrets["alpaca"]["API_KEY"]
A_SECRET = st.secrets["alpaca"]["SECRET"]
T_TOKEN = st.secrets["telegram"]["BOT_TOKEN"]
T_CHAT = st.secrets["telegram"]["CHAT_ID"]
client = TradingClient(A_KEY, A_SECRET, paper=True)

def telegram_msg(msg, tipo="verde"):
    # Usa tu bot_telegram.py con sonidos locales
    try:
        notificar_f1("BTC/USD", 0.001, 0, tipo=tipo)
    except: pass

def calcular_quant(precios):
    n = len(precios)
    x_bar = np.mean(precios)
    s = np.std(precios, ddof=1)
    z = (precios[-1] - x_bar) / (s / math.sqrt(n)) if s>0 else 0
    log_ret = math.log(precios[-1]/precios[-2]) if precios[-2]>0 else 0
    return x_bar, s, z, log_ret

def get_semaforo(price, fib, z, log_ret):
    # 1. FIB: ¿Está barato? Abajo de dorada = oferta
    # 2. Z: ¿Regalado? -2 a -7 = pánico = oportunidad
    # 3. LOG: ¿Crash? -0.62% ok, -5% no tocar
    if price < fib and z < -2.0 and -0.008 < log_ret < -0.0002:
        return "VERDE", "🟢 COMPRAR $2", "#00FF88"
    elif log_ret < -0.05 or z > 1.0:
        return "ROJO", "🔴 NO COMPRAR - Crash/Caro", "#FF3B3B"
    else:
        return "AMARILLO", "🟡 ESPERAR - Paciencia", "#FFD60A"

# ========== TARJETA PRO MEGA PRO ==========
st.markdown("""
<style>
.pro-card {
    background: linear-gradient(135deg, #0E1117 0%, #1A1D29 100%);
    border: 1px solid gold; border-radius: 16px; padding: 20px;
    box-shadow: 0 0 20px rgba(255,215,0,0.15);
}
.pro-title {color: gold; font-size: 22px; font-weight: 800; margin-bottom: 10px;}
.pro-row {display:flex; gap:12px; margin-top:12px;}
.pro-box {flex:1; background:#111; border-radius:12px; padding:12px; border-left:4px solid;}
.pro-box p {margin:4px 0; color:#CCC; font-size:13px;}
