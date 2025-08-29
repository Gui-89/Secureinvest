import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime
from datetime import timedelta
import warnings
import requests
import yfinance as yf
import time
import io
import base64
from streamlit.components.v1 import html
import json

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

warnings.filterwarnings('ignore')

# Configuração da página
st.set_page_config(
    page_title="SecureInvest - Simulador de Investimentos",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# URL da logo
LOGO_URL = "https://i.ibb.co/MkVDCtgD/Secure-Invest.png"

# Gerenciamento de tema
if 'theme' not in st.session_state:
    st.session_state.theme = 'light'

def toggle_theme():
    if st.session_state.theme == 'light':
        st.session_state.theme = 'dark'
    else:
        st.session_state.theme = 'light'
    st.rerun()

# Função para resetar todos os parâmetros
def reset_parameters():
    st.session_state.monthly_investment = 1000.0
    st.session_state.quarterly_investment = 0.0
    st.session_state.annual_investment = 0.0
    st.session_state.financial_goal = 100000.0
    st.session_state.simulate_selic = True
    st.session_state.simulate_cdb = True
    st.session_state.simulate_fii = True
    st.session_state.simulate_stocks = True
    st.session_state.simulate_treasury = True
    st.session_state.include_ipca = True
    st.session_state.include_taxes = True
    st.session_state.start_date = datetime.date.today()
    st.session_state.end_date = datetime.date.today() + timedelta(days=365*5)
    st.session_state.economic_scenario = 'neutro'
    st.session_state.continuous_simulation = False
    st.rerun()

# Componente de Ticker para mostrar cotações em tempo real
def ticker_component():
    ticker_html = """
    <div style="background: linear-gradient(90deg, #1E3A8A 0%, #3B82F6 100%); 
                color: white; 
                padding: 10px; 
                border-radius: 5px;
                margin-bottom: 20px;
                overflow: hidden;
                position: relative;
                box-shadow: 0 4px 15px rgba(0,0,0,0.2);">
        <div class="ticker-wrap">
            <div class="ticker">
                <div class="ticker__item">IBOV: 128.456,32 (+1,23%)</div>
                <div class="ticker__item">S&P 500: 4.890,21 (+0,87%)</div>
                <div class="ticker__item">DOW JONES: 38.456,78 (-0,32%)</div>
                <div class="ticker__item">NASDAQ: 16.345,67 (+1,45%)</div>
                <div class="ticker__item">USD/BRL: R$ 5,42 (-0,15%)</div>
                <div class="ticker__item">EUR/BRL: R$ 5,89 (+0,32%)</div>
                <div class="ticker__item">BTC: $62.345,21 (+3,45%)</div>
                <div class="ticker__item">PETR4: R$ 36,78 (+2,11%)</div>
                <div class="ticker__item">VALE3: R$ 68,92 (-0,87%)</div>
                <div class="ticker__item">ITUB4: R$ 34,15 (+1,24%)</div>
                <div class="ticker__item">BBDC4: R$ 16,43 (+0,92%)</div>
                <div class="ticker__item">WEGE3: R$ 42,56 (+1,78%)</div>
            </div>
        </div>
    </div>
    <style>
    .ticker-wrap {
        width: 100%;
        overflow: hidden;
        height: 40px;
        padding-left: 100%;
        box-sizing: content-box;
    }
    .ticker {
        display: inline-block;
        height: 40px;
        line-height: 40px;
        white-space: nowrap;
        padding-right: 100%;
        box-sizing: content-box;
        animation-iteration-count: infinite;
        animation-timing-function: linear;
        animation-name: ticker;
        animation-duration: 40s;
    }
    .ticker__item {
        display: inline-block;
        padding: 0 2rem;
        font-size: 16px;
        font-weight: bold;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
    }
    @keyframes ticker {
        0% { transform: translate3d(0, 0, 0); }
        100% { transform: translate3d(-100%, 0, 0); }
    }
    </style>
    """
    st.markdown(ticker_html, unsafe_allow_html=True)

# Aplicar tema antes de qualquer outro conteúdo
if st.session_state.theme == 'dark':
    st.markdown("""
    <style>
    .stApp {
        background-color: #0E1117;
        color: #E5E7EB;
    }
    .logo-header {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-bottom: 1rem;
        padding: 1.5rem;
        background: linear-gradient(90deg, #1a1a2e 0%, #16213e 100%);
        border-radius: 15px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.3);
        border: 1px solid #2D3748;
    }
    .logo-image {
        height: 140px;
        border-radius: 12px;
        box-shadow: 0 6px 20px rgba(0,0,0,0.4);
        transition: transform 0.3s ease;
    }
    .logo-image:hover {
        transform: scale(1.02);
    }
    .stSidebar {
        background-color: #1F2937;
    }
    .stSidebar .stMarkdown, .stSidebar .stText, .stSidebar .stNumberInput label, 
    .stSidebar .stDateInput label, .stSidebar .stCheckbox label, .stSidebar .stSelectbox label,
    .stSidebar .stMultiselect label {
        color: #E5E7EB !important;
    }
    .css-1d391kg, .css-1y4p8pa, .css-1v3fvcr, .css-1q8dd3e {
        color: #E5E7EB;
    }
    .stTextInput>div>div>input, .stNumberInput>div>div>input, .stDateInput>div>div>input {
        background-color: #374151;
        color: #E5E7EB;
        border: 1px solid #4B5563;
        border-radius: 8px;
    }
    .stCheckbox>label, .stSelectbox>label, .stMultiselect>label {
        color: #E5E7EB !important;
    }
    .stDataFrame {
        background-color: #1F2937;
    }
    .stDataFrame * {
        color: #E5E7EB !important;
    }
    .stExpander {
        border: 1px solid #374151;
        background-color: #1F2937;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    .stExpander .streamlit-expanderHeader {
        color: #E5E7EB !important;
        background-color: #1F2937;
        font-weight: 600;
    }
    .stExpander .streamlit-expanderContent {
        color: #E5E7EB !important;
    }
    .main-header {
        font-size: 2.8rem;
        color: #FFFFFF;
        text-align: center;
        margin-bottom: 0.5rem;
        font-weight: 700;
        background: linear-gradient(90deg, #2563EB 0%, #059669 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .subheader {
        font-size: 1.2rem;
        color: #60A5FA;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #1F2937;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 8px 20px rgba(255, 255, 255, 0.1);
        margin-bottom: 1rem;
        color: #E5E7EB;
        border: 1px solid #374151;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 25px rgba(255, 255, 255, 0.15);
    }
    .investment-option {
        background-color: #374151;
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        border-left: 6px solid #3B82F6;
        color: #E5E7EB;
        box-shadow: 0 6px 15px rgba(0,0,0,0.2);
        transition: transform 0.3s ease;
    }
    .investment-option:hover {
        transform: translateX(5px);
    }
    .investment-option h3, .investment-option p, .investment-option ul {
        color: #E5E7EB !important;
    }
    .positive-return {
        color: #10B981;
        font-weight: 600;
    }
    .negative-return {
        color: #EF4444;
        font-weight: 600;
    }
    .stButton>button {
        background: linear-gradient(90deg, #2563EB 0%, #059669 100%);
        color: white;
        font-weight: 600;
        border-radius: 12px;
        padding: 0.75rem 1.5rem;
        width: 100%;
        border: none;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #1D4ED8 0%, #047857 100%);
        transform: translateY(-2px);
        box-shadow: 0 6px 15px rgba(37, 99, 235, 0.4);
    }
    /* Ajustes para texto geral */
    .stMarkdown, .stText, .stInfo, .stSuccess, .stWarning {
        color: #E5E7EB !important;
    }
    p, li, h1, h2, h3, h4, h5, h6 {
        color: #E5E7EB !important;
    }
    /* Correção para multiselect no modo escuro */
    .stMultiSelect [data-baseweb="select"] {
        background-color: #374151;
        color: #E5E7EB;
        border: 1px solid #4B5563;
        border-radius: 8px;
    }
    .stMultiSelect [data-baseweb="select"]:hover {
        border-color: #60A5FA;
    }
    .stMultiSelect [data-baseweb="select"] div {
        color: #E5E7EB !important;
    }
    .stMultiSelect [data-baseweb="select"] input {
        color: #E5E7EB !important;
    }
    .stMultiSelect [data-baseweb="select"]::placeholder {
        color: #9CA3AF !important;
    }
    .stMultiSelect [data-baseweb="tag"] {
        background-color: #3B82F6;
        color: white;
        border-radius: 6px;
        padding: 0.25rem 0.5rem;
        margin: 0.125rem;
    }
    .stMultiSelect [data-baseweb="popover"] {
        background-color: #1F2937;
        border: 1px solid #374151;
    }
    .stMultiSelect [data-baseweb="menu"] {
        background-color: #1F2937;
        color: #E5E7EB;
    }
    .stMultiSelect [data-baseweb="option"] {
        background-color: #1F2937;
        color: #E5E7EB;
    }
    .stMultiSelect [data-baseweb="option"]:hover {
        background-color: #374151;
    }
    /* Correção para checkbox no modo escuro */
    .stCheckbox [data-baseweb="checkbox"] {
        background-color: #374151;
        border-color: #4B5563;
    }
    .stCheckbox [data-baseweb="checkbox"]:checked {
        background-color: #3B82F6;
        border-color: #3B82F6;
    }
    .stCheckbox label {
        color: #E5E7EB !important;
    }
    /* Correção para date input no modo escuro */
    .stDateInput [data-baseweb="input"] {
        background-color: #374151;
        color: #E5E7EB;
        border: 1px solid #4B5563;
        border-radius: 8px;
    }
    .stDateInput [data-baseweb="input"] input {
        color: #E5E7EB !important;
    }
    /* Correção para selectbox no modo escuro */
    .stSelectbox [data-baseweb="select"] {
        background-color: #374151;
        color: #E5E7EB;
        border: 1px solid #4B5563;
        border-radius: 8px;
    }
    .stSelectbox [data-baseweb="select"] div {
        color: #E5E7EB !important;
    }
    .stSelectbox [data-baseweb="select"]:hover {
        border-color: #60A5FA;
    }
    .stSelectbox [data-baseweb="popover"] {
        background-color: #1F2937;
        border: 1px solid #374151;
    }
    .stSelectbox [data-baseweb="menu"] {
        background-color: #1F2937;
        color: #E5E7EB;
    }
    .stSelectbox [data-baseweb="option"] {
        background-color: #1F2937;
        color: #E5E7EB;
    }
    .stSelectbox [data-baseweb="option"]:hover {
        background-color: #374151;
    }
    /* Melhoria para labels e textos da sidebar */
    .stSidebar .stMarkdown {
        color: #E5E7EB !important;
        font-weight: 500;
    }
    .stSidebar .stSubheader {
        color: #60A5FA !important;
        margin-top: 1.5rem;
        font-weight: 600;
    }
    /* Novos estilos para melhorias */
    .card {
        background-color: #1F2937;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 8px 20px rgba(255, 255, 255, 0.1);
        margin-bottom: 1rem;
        border: 1px solid #374151;
        transition: transform 0.3s ease;
    }
    .card:hover {
        transform: translateY(-3px);
    }
    .card-header {
        font-size: 1.25rem;
        font-weight: 600;
        margin-bottom: 1rem;
        color: #3B82F6;
    }
    .asset-card {
        background-color: #374151;
        padding: 1.25rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        border-left: 5px solid #3B82F6;
        transition: transform 0.3s ease;
    }
    .asset-card:hover {
        transform: translateX(5px);
    }
    .asset-card h4 {
        margin: 0;
        color: #E5E7EB;
    }
    .asset-card p {
        margin: 0.25rem 0;
        color: #E5E7EB;
    }
    .tab-container {
        background-color: #1F2937;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 6px 18px rgba(0,0,0,0.2);
    }
    .logo-container {
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 1rem;
    }
    .inspirational-quote {
        font-style: italic;
        text-align: center;
        color: #60A5FA;
        margin-top: 0.5rem;
        font-size: 1.1rem;
        background: rgba(37, 99, 235, 0.1);
        padding: 1.25rem;
        border-radius: 10px;
        border-left: 5px solid #2563EB;
        transition: all 0.3s ease;
    }
    .inspirational-quote:hover {
        background: rgba(37, 99, 235, 0.15);
        transform: translateY(-2px);
    }
    .quote-author {
        text-align: right;
        color: #9CA3AF;
        margin-top: 0.5rem;
        font-size: 0.9rem;
    }
    .sidebar-header {
        font-size: 1.5rem;
        font-weight: 700;
        color: #3B82F6;
        margin-bottom: 1rem;
        text-align: center;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
    }
    .logo-subtitle {
        font-size: 1.3rem;
        color: #9CA3AF;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 500;
    }
    .risk-metric {
        background: linear-gradient(135deg, #1F2937 0%, #374151 100%);
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        border: 1px solid #4B5563;
        text-align: center;
        box-shadow: 0 6px 15px rgba(0,0,0,0.2);
        transition: transform 0.3s ease;
    }
    .risk-metric:hover {
        transform: translateY(-3px);
    }
    .alert-card {
        background: rgba(239, 68, 68, 0.1);
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #EF4444;
        margin-bottom: 1rem;
        transition: all 0.3s ease;
    }
    .alert-card:hover {
        background: rgba(239, 68, 68, 0.15);
        transform: translateX(3px);
    }
    .success-card {
        background: rgba(16, 185, 129, 0.1);
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #10B981;
        margin-bottom: 1rem;
        transition: all 0.3s ease;
    }
    .success-card:hover {
        background: rgba(16, 185, 129, 0.15);
        transform: translateX(3px);
    }
    .info-card {
        background: rgba(59, 130, 246, 0.1);
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #3B82F6;
        margin-bottom: 1rem;
        transition: all 0.3s ease;
    }
    .info-card:hover {
        background: rgba(59, 130, 246, 0.15);
        transform: translateX(3px);
    }
    .export-button {
        background: linear-gradient(135deg, #059669 0%, #10B981 100%);
        color: white;
        padding: 0.75rem 1.5rem;
        border-radius: 10px;
        border: none;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(5, 150, 105, 0.3);
        width: 100%;
        text-align: center;
        display: inline-block;
        margin: 0.5rem 0;
    }
    .export-button:hover {
        background: linear-gradient(135deg, #047857 0%, #059669 100%);
        transform: translateY(-2px);
        box-shadow: 0 6px 15px rgba(5, 150, 105, 0.4);
        color: white;
        text-decoration: none;
    }
    </style>
    """, unsafe_allow_html=True)
else:
    # Modo claro
    st.markdown("""
    <style>
    .logo-header {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-bottom: 1rem;
        padding: 1.5rem;
        background: linear-gradient(90deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 15px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        border: 1px solid #D1D5DB;
    }
    .logo-image {
        height: 140px;
        border-radius: 12px;
        box-shadow: 0 6px 20px rgba(0,0,0,0.1);
        transition: transform 0.3s ease;
    }
    .logo-image:hover {
        transform: scale(1.02);
    }
    .main-header {
        font-size: 2.8rem;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 0.5rem;
        font-weight: 700;
        background: linear-gradient(90deg, #1E3A8A 0%, #059669 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .subheader {
        font-size: 1.2rem;
        color: #2E4F8A;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #F8FAFC;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
        border: 1px solid #E5E7EB;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 25px rgba(0, 0, 0, 0.15);
    }
    .investment-option {
        background-color: #F1F5F9;
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        border-left: 6px solid #1E3A8A;
        box-shadow: 0 6px 15px rgba(0,0,0,0.1);
        transition: transform 0.3s ease;
    }
    .investment-option:hover {
        transform: translateX(5px);
    }
    .positive-return {
        color: #059669;
        font-weight: 600;
    }
    .negative-return {
        color: #DC2626;
        font-weight: 600;
    }
    .stButton>button {
        background: linear-gradient(90deg, #1E3A8A 0%, #059669 100%);
        color: white;
        font-weight: 600;
        border-radius: 12px;
        padding: 0.75rem 1.5rem;
        width: 100%;
        border: none;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(30, 58, 138, 0.3);
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #1E40AF 0%, #047857 100%);
        transform: translateY(-2px);
        box-shadow: 0 6px 15px rgba(30, 58, 138, 0.4);
    }
    /* Novos estilos para melhorias */
    .card {
        background-color: #FFFFFF;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
        border: 1px solid #E5E7EB;
        transition: transform 0.3s ease;
    }
    .card:hover {
        transform: translateY(-3px);
    }
    .card-header {
        font-size: 1.25rem;
        font-weight: 600;
        margin-bottom: 1rem;
        color: #1E3A8A;
    }
    .asset-card {
        background-color: #F1F5F9;
        padding: 1.25rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        border-left: 5px solid #1E3A8A;
        transition: transform 0.3s ease;
    }
    .asset-card:hover {
        transform: translateX(5px);
    }
    .asset-card h4 {
        margin: 0;
        color: #1F2937;
    }
    .asset-card p {
        margin: 0.25rem 0;
        color: #4B5563;
    }
    .tab-container {
        background-color: #FFFFFF;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 6px 18px rgba(0, 0, 0, 0.05);
    }
    .logo-container {
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 1rem;
    }
    .inspirational-quote {
        font-style: italic;
        text-align: center;
        color: #3B82F6;
        margin-top: 0.5rem;
        font-size: 1.1rem;
        background: rgba(59, 130, 246, 0.1);
        padding: 1.25rem;
        border-radius: 10px;
        border-left: 5px solid #3B82F6;
        transition: all 0.3s ease;
    }
    .inspirational-quote:hover {
        background: rgba(59, 130, 246, 0.15);
        transform: translateY(-2px);
    }
    .quote-author {
        text-align: right;
        color: #6B7280;
        margin-top: 0.5rem;
        font-size: 0.9rem;
    }
    .sidebar-header {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 1rem;
        text-align: center;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }
    .logo-subtitle {
        font-size: 1.3rem;
        color: #6B7280;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 500;
    }
    .risk-metric {
        background: linear-gradient(135deg, #F8FAFC 0%, #F1F5F9 100%);
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        border: 1px solid #E5E7EB;
        text-align: center;
        box-shadow: 0 6px 15px rgba(0,0,0,0.1);
        transition: transform 0.3s ease;
    }
    .risk-metric:hover {
        transform: translateY(-3px);
    }
    .alert-card {
        background: rgba(220, 38, 38, 0.1);
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #DC2626;
        margin-bottom: 1rem;
        transition: all 0.3s ease;
    }
    .alert-card:hover {
        background: rgba(220, 38, 38, 0.15);
        transform: translateX(3px);
    }
    .success-card {
        background: rgba(5, 150, 105, 0.1);
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #059669;
        margin-bottom: 1rem;
        transition: all 0.3s ease;
    }
    .success-card:hover {
        background: rgba(5, 150, 105, 0.15);
        transform: translateX(3px);
    }
    .info-card {
        background: rgba(59, 130, 246, 0.1);
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #3B82F6;
        margin-bottom: 1rem;
        transition: all 0.3s ease;
    }
    .info-card:hover {
        background: rgba(59, 130, 246, 0.15);
        transform: translateX(3px);
    }
    .export-button {
        background: linear-gradient(135deg, #059669 0%, #10B981 100%);
        color: white;
        padding: 0.75rem 1.5rem;
        border-radius: 10px;
        border: none;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(5, 150, 105, 0.3);
        width: 100%;
        text-align: center;
        display: inline-block;
        margin: 0.5rem 0;
    }
    .export-button:hover {
        background: linear-gradient(135deg, #047857 0%, #059669 100%);
        transform: translateY(-2px);
        box-shadow: 0 6px 15px rgba(5, 150, 105, 0.4);
        color: white;
        text-decoration: none;
    }
    </style>
    """, unsafe_allow_html=True)

# Funções para buscar dados de ativos
def search_asset(ticker, asset_type):
    """Busca informações do ativo usando Yahoo Finance"""
    try:
        # Adiciona sufixo .SA para ativos brasileiros
        if asset_type == 'fii':
            ticker_symbol = f"{ticker}.SA"
        elif asset_type == 'stocks':
            ticker_symbol = f"{ticker}.SA"
        elif asset_type == 'treasury':
            ticker_symbol = f"{ticker}.SA"
        else:
            ticker_symbol = f"{ticker}.SA"
        
        # Busca informações do ativo
        asset = yf.Ticker(ticker_symbol)
        info = asset.info
        
        # Obtém dados históricos para calcular dividend yield
        hist = asset.history(period="1y")
        
        # Calcula dividend yield baseado nos últimos 12 meses
        if 'dividendYield' in info and info['dividendYield'] is not None:
            dividend_yield = info['dividendYield']
        else:
            # Tenta calcular manualmente se não estiver disponível
            dividends = asset.dividends.last('1Y').sum()
            current_price = info.get('currentPrice', info.get('regularMarketPrice', 1))
            dividend_yield = dividends / current_price if current_price > 0 else 0.05
        
        # Retorno anual médio baseado no histórico (últimos 3 anos)
        hist_3y = asset.history(period="3y")
        if len(hist_3y) > 1:
            annual_return = (hist_3y['Close'][-1] / hist_3y['Close'][0]) ** (1/3) - 1
        else:
            annual_return = 0.12  # Valor padrão se não houver histórico suficiente
        
        return {
            'nome': info.get('longName', ticker),
            'dividend_yield': max(0.01, min(dividend_yield, 0.2)),  # Limita entre 1% e 20%
            'annual_return': max(0.05, min(annual_return, 0.3)),   # Limita entre 5% e 30%
            'setor': info.get('sector', 'Não especificado'),
            'segmento': info.get('industry', 'Não especificado'),
            'preco_atual': info.get('currentPrice', info.get('regularMarketPrice', 0)),
            'success': True
        }
    
    except Exception as e:
        st.error(f"Erro ao buscar informações para {ticker}: {str(e)}")
        # Valores padrão para fallback
        return {
            'nome': ticker,
            'dividend_yield': 0.065 if asset_type == 'stocks' else 0.075,
            'annual_return': 0.12 if asset_type == 'stocks' else 0.10,
            'setor': 'Não especificado',
            'segmento': 'Não especificado',
            'preco_atual': 0,
            'success': False
        }

# Classe principal do simulador
class SecureInvestSimulator:
    def __init__(self):
        # Taxas de referência (podem ser atualizadas)
        self.selic_annual = 0.1175  # 11.75% ao ano
        self.cdb_monthly = 0.01     # 1% ao mês
        self.inflation_annual = 0.045  # 4.5% ao ano (IPCA)
        
        # Novos parâmetros para impostos e taxas
        self.income_tax_rates = {
            'LCI_LCA': 0.00,  # Isentos
            'tesouro_direto': 0.15,  # 15% fixo
            'fundos_imobiliarios': 0.20,  # 20% sobre dividendos
            'acoes': 0.15,  # 15% sobre ganhos de capital
            'cdb': 0.175,  # 17.5% (varia com tempo)
        }
        
        self.brokerage_fee = 0.005  # 0.5% por operação
        self.administration_fee = 0.01  # 1% ao ano
        
        # Dados históricos de FIIs e ações (valores ilustrativos)
        self.fii_data = {
            'KNRI11': {'dividend_yield': 0.085, 'annual_return': 0.12, 'nome': 'Kinea Renda Imobiliária', 'segmento': 'Títulos e Val. Mob.'},
            'HGLG11': {'dividend_yield': 0.068, 'annual_return': 0.10, 'nome': 'CSHG Logística', 'segmento': 'Logística'},
            'XPLG11': {'dividend_yield': 0.072, 'annual_return': 0.11, 'nome': 'XP Log', 'segmento': 'Logística'},
            'VRTA11': {'dividend_yield': 0.078, 'annual_return': 0.13, 'nome': 'Vectis Renda Residencial', 'segmento': 'Residencial'},
            'BCFF11': {'dividend_yield': 0.082, 'annual_return': 0.14, 'nome': 'BTG Pactual Fundo de Fundos', 'segmento': 'Fundo de Fundos'}
        }
        
        self.stock_data = {
            'ITSA4': {'dividend_yield': 0.065, 'annual_return': 0.09, 'nome': 'Itaúsa', 'setor': 'Holdings'},
            'BBAS3': {'dividend_yield': 0.058, 'annual_return': 0.11, 'nome': 'Banco do Brasil', 'setor': 'Bancos'},
            'PETR4': {'dividend_yield': 0.072, 'annual_return': 0.15, 'nome': 'Petrobras', 'setor': 'Petróleo e Gás'},
            'VALE3': {'dividend_yield': 0.084, 'annual_return': 0.13, 'nome': 'Vale', 'setor': 'Mineração'},
            'WEGE3': {'dividend_yield': 0.032, 'annual_return': 0.18, 'nome': 'WEG', 'setor': 'Equipamentos Elétricos'}
        }
        
        # Dados para Tesouro Direto (valores ilustrativos)
        self.treasury_data = {
            'Tesouro Selic': {'annual_return': 0.1175, 'ipca_linked': False, 'nome': 'Tesouro Selic'},
            'Tesouro IPCA+ 2026': {'annual_return': 0.065, 'ipca_linked': True, 'nome': 'Tesouro IPCA+ 2026'},
            'Tesouro IPCA+ 2035': {'annual_return': 0.06, 'ipca_linked': True, 'nome': 'Tesouro IPCA+ 2035'},
            'Tesouro Prefixado 2026': {'annual_return': 0.12, 'ipca_linked': False, 'nome': 'Tesouro Prefixado 2026'},
            'Tesouro Prefixado 2029': {'annual_return': 0.125, 'ipca_linked': False, 'nome': 'Tesouro Prefixado 2029'}
        }
        
        # Dicionário para ativos pesquisados
        self.searched_assets = {'fii': {}, 'stocks': {}, 'treasury': {}}
        
        # Sistema de portfólios
        self.portfolios = {}
        
        # Cenários econômicos
        self.economic_scenarios = {
            'otimista': {'fator': 1.2, 'descricao': 'Crescimento econômico acelerado'},
            'neutro': {'fator': 1.0, 'descricao': 'Cenário base de projeção'},
            'pessimista': {'fator': 0.8, 'descricao': 'Retração econômica moderada'},
            'crise': {'fator': 0.6, 'descricao': 'Cenário de crise econômica'}
        }
    
    def search_and_add_asset(self, ticker, asset_type):
        """Busca e adiciona um ativo usando a API"""
        if ticker in self.searched_assets[asset_type]:
            return self.searched_assets[asset_type][ticker]
        
        asset_info = search_asset(ticker, asset_type)
        
        if asset_info['success']:
            if asset_type == 'fii':
                self.searched_assets['fii'][ticker] = {
                    'dividend_yield': asset_info['dividend_yield'],
                    'annual_return': asset_info['annual_return'],
                    'nome': asset_info['nome'],
                    'segmento': asset_info['segmento']
                }
            elif asset_type == 'stocks':
                self.searched_assets['stocks'][ticker] = {
                    'dividend_yield': asset_info['dividend_yield'],
                    'annual_return': asset_info['annual_return'],
                    'nome': asset_info['nome'],
                    'setor': asset_info['setor']
                }
            elif asset_type == 'treasury':
                self.searched_assets['treasury'][ticker] = {
                    'annual_return': asset_info['annual_return'],
                    'ipca_linked': True,  # Assume que é indexado ao IPCA
                    'nome': asset_info['nome']
                }
        
        return asset_info
    
    def get_asset_data(self, asset_type):
        """Retorna dados de ativos incluindo os pesquisados"""
        if asset_type == 'fii':
            return {**self.fii_data, **self.searched_assets['fii']}
        elif asset_type == 'stocks':
            return {**self.stock_data, **self.searched_assets['stocks']}
        elif asset_type == 'treasury':
            return {**self.treasury_data, **self.searched_assets['treasury']}
        else:
            return {}
    
    def calculate_fixed_income(self, amount, frequency, start_date, end_date, investment_type, include_inflation=False, include_taxes=False):
        """Calcula rendimentos da renda fixa"""
        months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
        
        if investment_type == 'selic':
            monthly_rate = (1 + self.selic_annual) ** (1/12) - 1
        elif investment_type == 'cdb':
            monthly_rate = self.cdb_monthly
        else:
            monthly_rate = 0
        
        # Ajustar pela inflação se solicitado
        if include_inflation:
            monthly_inflation = (1 + self.inflation_annual) ** (1/12) - 1
            monthly_rate = ((1 + monthly_rate) / (1 + monthly_inflation)) - 1
        
        contributions = self._calculate_contributions(amount, frequency, start_date, end_date)
        total_contributed = sum(contribution['amount'] for contribution in contributions)
        
        balance = 0
        history = []
        
        for contribution in contributions:
            remaining_months = months - contribution['elapsed_months']
            if remaining_months > 0:
                balance += contribution['amount'] * (1 + monthly_rate) ** remaining_months
            history.append({
                'date': contribution['date'],
                'balance': balance,
                'contribution': contribution['amount']
            })
        
        earnings = balance - total_contributed
        
        # Calcular impostos se solicitado
        taxes = 0
        if include_taxes:
            taxes = self.calculate_taxes(investment_type, earnings, months)
            earnings -= taxes
        
        earnings_percentage = (earnings / total_contributed) * 100 if total_contributed > 0 else 0
        
        return {
            'final_balance': balance - taxes,
            'total_contributed': total_contributed,
            'earnings': earnings,
            'taxes': taxes,
            'earnings_percentage': earnings_percentage,
            'history': history,
            'monthly_rate': monthly_rate
        }
    
    def calculate_treasury(self, amount, frequency, start_date, end_date, selected_treasury, include_inflation=False, include_taxes=False):
        """Calcula rendimentos do Tesouro Direto"""
        months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
        
        # Obter dados do tesouro selecionado
        treasury_data = self.get_asset_data('treasury')
        if selected_treasury and selected_treasury in treasury_data:
            annual_return = treasury_data[selected_treasury]['annual_return']
            is_ipca_linked = treasury_data[selected_treasury]['ipca_linked']
        else:
            # Valores padrão se nenhum tesouro for selecionado
            annual_return = 0.10
            is_ipca_linked = False
        
        monthly_rate = (1 + annual_return) ** (1/12) - 1
        
        # Se for título indexado ao IPCA, o retorno já inclui a inflação
        # Se não for indexado e queremos considerar a inflação, ajustamos
        if include_inflation and not is_ipca_linked:
            monthly_inflation = (1 + self.inflation_annual) ** (1/12) - 1
            monthly_rate = ((1 + monthly_rate) / (1 + monthly_inflation)) - 1
        
        contributions = self._calculate_contributions(amount, frequency, start_date, end_date)
        total_contributed = sum(contribution['amount'] for contribution in contributions)
        
        balance = 0
        history = []
        
        for contribution in contributions:
            remaining_months = months - contribution['elapsed_months']
            if remaining_months > 0:
                balance += contribution['amount'] * (1 + monthly_rate) ** remaining_months
            history.append({
                'date': contribution['date'],
                'balance': balance,
                'contribution': contribution['amount']
            })
        
        earnings = balance - total_contributed
        
        # Calcular impostos se solicitado
        taxes = 0
        if include_taxes:
            taxes = self.calculate_taxes('tesouro_direto', earnings, months)
            earnings -= taxes
        
        earnings_percentage = (earnings / total_contributed) * 100 if total_contributed > 0 else 0
        
        return {
            'final_balance': balance - taxes,
            'total_contributed': total_contributed,
            'earnings': earnings,
            'taxes': taxes,
            'earnings_percentage': earnings_percentage,
            'history': history,
            'monthly_rate': monthly_rate,
            'is_ipca_linked': is_ipca_linked
        }
    
    def calculate_variable_income(self, amount, frequency, start_date, end_date, asset_type, selected_assets=None, include_inflation=False, include_taxes=False):
        """Calcula rendimentos da renda variável"""
        months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
        
        if asset_type == 'fii':
            data = self.get_asset_data('fii')
            avg_dividend_yield = 0.075
            avg_annual_return = 0.12
            tax_type = 'fundos_imobiliarios'
        else:  # stocks
            data = self.get_asset_data('stocks')
            avg_dividend_yield = 0.062
            avg_annual_return = 0.13
            tax_type = 'acoes'
        
        # Se ativos específicos foram selecionados, calcular média ponderada
        if selected_assets:
            valid_assets = [asset for asset in selected_assets if asset in data]
            if valid_assets:
                dividend_yield = np.mean([data[asset]['dividend_yield'] for asset in valid_assets])
                annual_return = np.mean([data[asset]['annual_return'] for asset in valid_assets])
            else:
                dividend_yield = avg_dividend_yield
                annual_return = avg_annual_return
        else:
            dividend_yield = avg_dividend_yield
            annual_return = avg_annual_return
        
        monthly_appreciation = (1 + annual_return) ** (1/12) - 1
        monthly_dividends = dividend_yield / 12
        
        # Ajustar pela inflação se solicitado
        if include_inflation:
            monthly_inflation = (1 + self.inflation_annual) ** (1/12) - 1
            monthly_appreciation = ((1 + monthly_appreciation) / (1 + monthly_inflation)) - 1
            monthly_dividends = monthly_dividends / (1 + monthly_inflation)
        
        monthly_rate = monthly_appreciation + monthly_dividends
        
        contributions = self._calculate_contributions(amount, frequency, start_date, end_date)
        total_contributed = sum(contribution['amount'] for contribution in contributions)
        
        balance = 0
        dividends_accumulated = 0
        history = []
        
        for contribution in contributions:
            remaining_months = months - contribution['elapsed_months']
            if remaining_months > 0:
                # Apreciação do capital
                future_value = contribution['amount'] * (1 + monthly_appreciation) ** remaining_months
                # Dividendos
                dividends = contribution['amount'] * monthly_dividends * remaining_months
                
                balance += future_value
                dividends_accumulated += dividends
            
            history.append({
                'date': contribution['date'],
                'balance': balance + dividends_accumulated,
                'dividends': dividends_accumulated
            })
        
        final_balance = balance + dividends_accumulated
        earnings = final_balance - total_contributed
        
        # Calcular impostos se solicitado
        taxes = 0
        if include_taxes:
            taxes = self.calculate_taxes(tax_type, earnings, months)
            earnings -= taxes
        
        return {
            'final_balance': final_balance - taxes,
            'total_contributed': total_contributed,
            'earnings': earnings,
            'taxes': taxes,
            'dividends': dividends_accumulated,
            'history': history,
            'monthly_rate': monthly_rate
        }
    
    def _calculate_contributions(self, amount, frequency, start_date, end_date):
        """Calcula todas as contribuições no período"""
        contributions = []
        current_date = start_date
        elapsed_months = 0
        
        while current_date <= end_date:
            if frequency == 'monthly':
                contributions.append({
                    'date': current_date,
                    'amount': amount,
                    'elapsed_months': elapsed_months
                })
                current_date += timedelta(days=30)
                elapsed_months += 1
            elif frequency == 'quarterly':
                if current_date.month in [1, 4, 7, 10]:
                    contributions.append({
                        'date': current_date,
                        'amount': amount,
                        'elapsed_months': elapsed_months
                    })
                current_date += timedelta(days=30)
                elapsed_months += 1
            elif frequency == 'annually':
                if current_date.month == 1:
                    contributions.append({
                        'date': current_date,
                        'amount': amount,
                        'elapsed_months': elapsed_months
                    })
                current_date += timedelta(days=30)
                elapsed_months += 1
        
        return contributions
    
    def calculate_taxes(self, investment_type, earnings, months):
        """Calcula impostos sobre os rendimentos"""
        if investment_type in self.income_tax_rates:
            rate = self.income_tax_rates[investment_type]
            
            # Ajustar taxa para CDB baseado no tempo (regressivo)
            if investment_type == 'cdb':
                if months <= 6:
                    rate = 0.225
                elif months <= 12:
                    rate = 0.20
                elif months <= 24:
                    rate = 0.175
                else:
                    rate = 0.15
            
            return earnings * rate
        return 0
    
    def calculate_fees(self, total_contributed, months):
        """Calcula taxas de administração"""
        monthly_fee = self.administration_fee / 12
        return total_contributed * monthly_fee * months
    
    def calculate_time_to_goal(self, monthly_investment, monthly_rate, goal_amount):
        """Calcula o tempo necessário para atingir um objetivo"""
        if monthly_rate <= 0 or monthly_investment <= 0:
            return float('inf')
        
        try:
            months_needed = np.log(1 + (goal_amount * monthly_rate) / monthly_investment) / np.log(1 + monthly_rate)
            return max(0, months_needed)
        except:
            return float('inf')
    
    def calculate_required_contribution(self, monthly_rate, goal_amount, months_available):
        """Calcula o aporte necessário para atingir o objetivo no tempo especificado"""
        if monthly_rate <= 0 or months_available <= 0:
            return goal_amount / months_available
        
        try:
            required_monthly = (goal_amount * monthly_rate) / ((1 + monthly_rate) ** months_available - 1)
            return max(0, required_monthly)
        except:
            return float('inf')
    
    def calculate_goal_scenario(self, monthly_rate, goal_amount, current_monthly_investment, total_months):
        """Calcula cenário completo para atingir o objetivo"""
        # Tempo necessário com aportes atuais
        time_with_current = self.calculate_time_to_goal(
            current_monthly_investment, monthly_rate, goal_amount
        )
        
        # Aporte necessário para atingir no período definido
        required_monthly = self.calculate_required_contribution(
            monthly_rate, goal_amount, total_months
        )
        
        # Aporte adicional necessário
        additional_monthly = max(0, required_monthly - current_monthly_investment)
        
        return {
            'time_with_current': time_with_current,
            'required_monthly': required_monthly,
            'additional_monthly': additional_monthly,
            'additional_quarterly': additional_monthly * 3,
            'additional_semiannual': additional_monthly * 6,
            'additional_annual': additional_monthly * 12
        }
    
    def simulate_partial_withdrawal(self, amount, frequency, start_date, end_date, 
                                  withdrawal_amount, withdrawal_date, investment_type, 
                                  selected_assets=None, include_inflation=False, include_taxes=False):
        """Simula resgates parciais durante o período de investimento"""
        # Implementação simplificada para resgates parciais
        months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
        withdrawal_months = (withdrawal_date.year - start_date.year) * 12 + (withdrawal_date.month - start_date.month)
        
        # Calcular até o resgate
        if investment_type in ['selic', 'cdb']:
            result_until_withdrawal = self.calculate_fixed_income(
                amount, frequency, start_date, withdrawal_date, investment_type, include_inflation, include_taxes
            )
        elif investment_type == 'treasury':
            result_until_withdrawal = self.calculate_treasury(
                amount, frequency, start_date, withdrawal_date, selected_assets, include_inflation, include_taxes
            )
        else:
            result_until_withdrawal = self.calculate_variable_income(
                amount, frequency, start_date, withdrawal_date, investment_type, selected_assets, include_inflation, include_taxes
            )
        
        # Aplicar resgate
        balance_after_withdrawal = max(0, result_until_withdrawal['final_balance'] - withdrawal_amount)
        
        # Calcular do resgate até o final
        remaining_months = months - withdrawal_months
        if remaining_months > 0:
            if investment_type in ['selic', 'cdb']:
                monthly_rate = result_until_withdrawal['monthly_rate']
                final_balance = balance_after_withdrawal * (1 + monthly_rate) ** remaining_months
            elif investment_type == 'treasury':
                monthly_rate = result_until_withdrawal['monthly_rate']
                final_balance = balance_after_withdrawal * (1 + monthly_rate) ** remaining_months
            else:
                monthly_rate = result_until_withdrawal['monthly_rate']
                final_balance = balance_after_withdrawal * (1 + monthly_rate) ** remaining_months
        else:
            final_balance = balance_after_withdrawal
        
        # Ajustar resultados
        result_until_withdrawal['final_balance'] = final_balance
        result_until_withdrawal['withdrawal_amount'] = withdrawal_amount
        result_until_withdrawal['balance_after_withdrawal'] = balance_after_withdrawal
        
        return result_until_withdrawal
    
    def calculate_risk_metrics(self, historical_data):
        """Calcula métricas de risco (volatilidade, drawdown)"""
        if not historical_data or len(historical_data) < 2:
            return {
                'volatility': 0,
                'max_drawdown': 0,
                'sharpe_ratio': 0
            }
        
        # Extrair valores de balance
        balances = [point['balance'] for point in historical_data]
        
        # Calcular retornos
        returns = []
        for i in range(1, len(balances)):
            if balances[i-1] > 0:
                returns.append((balances[i] - balances[i-1]) / balances[i-1])
            else:
                returns.append(0)
        
        # Volatilidade (anualizada)
        volatility = np.std(returns) * np.sqrt(12) * 100 if returns else 0
        
        # Drawdown máximo
        peak = balances[0]
        max_drawdown = 0
        for balance in balances:
            if balance > peak:
                peak = balance
            drawdown = (peak - balance) / peak * 100
            if drawdown > max_drawdown:
                max_drawdown = drawdown
        
        # Ratio de Sharpe (simplificado)
        sharpe_ratio = (np.mean(returns) * 12 - self.inflation_annual) / (np.std(returns) * np.sqrt(12)) if returns and np.std(returns) > 0 else 0
        
        return {
            'volatility': volatility,
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe_ratio
        }
    
    def simulate_economic_scenario(self, scenario, base_result):
        """Aplica um cenário econômico aos resultados"""
        if scenario in self.economic_scenarios:
            factor = self.economic_scenarios[scenario]['fator']
            adjusted_result = base_result.copy()
            adjusted_result['final_balance'] *= factor
            adjusted_result['earnings'] *= factor
            if 'dividends' in adjusted_result:
                adjusted_result['dividends'] *= factor
            return adjusted_result
        return base_result

# Função para criar PDF
def create_pdf(data, title="Relatório de Investimentos"):
    """Cria um relatório PDF com os resultados da simulação"""
    try:
        # Tentar importar reportlab
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        import io
        
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        
        # Adicionar título
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, height - 50, title)
        
        # Adicionar data
        c.setFont("Helvetica", 10)
        c.drawString(50, height - 70, f"Data do relatório: {datetime.date.today().strftime('%d/%m/%Y')}")
        
        # Adicionar dados
        y_position = height - 100
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y_position, "Resultados da Simulação")
        y_position -= 30
        
        c.setFont("Helvetica", 10)
        for i, (key, value) in enumerate(data.items()):
            if y_position < 100:
                c.showPage()
                y_position = height - 50
                c.setFont("Helvetica", 10)
            
            c.drawString(50, y_position, f"{key}: {value}")
            y_position -= 15
        
        c.save()
        buffer.seek(0)
        return buffer
        
    except ImportError:
        # Fallback se reportlab não estiver instalado
        st.error("""
        ⚠️ **Módulo reportlab não instalado**
        
        Para exportar relatórios em PDF, instale o reportlab:
        ```
        pip install reportlab
        ```
        
        Enquanto isso, use a exportação em Excel que está disponível.
        """)
        
        # Retornar um buffer vazio
        return io.BytesIO()
    except Exception as e:
        st.error(f"Erro ao gerar PDF: {str(e)}")
        return io.BytesIO()

# Função para criar Excel
def create_excel(data):
    """Cria uma planilha Excel com os resultados da simulação"""
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        # Dados resumidos
        summary_data = []
        for key, value in data.items():
            if isinstance(value, (int, float)):
                summary_data.append([key, value])
        
        summary_df = pd.DataFrame(summary_data, columns=['Métrica', 'Valor'])
        summary_df.to_excel(writer, sheet_name='Resumo', index=False)
        
        # Dados detalhados (exemplo)
        details_data = {
            'Mês': list(range(1, 13)),
            'Retorno': [i * 0.01 for i in range(12)],
            'Acumulado': [1000 * (1 + i * 0.01) for i in range(12)]
        }
        details_df = pd.DataFrame(details_data)
        details_df.to_excel(writer, sheet_name='Detalhes', index=False)
    
    buffer.seek(0)
    return buffer

# Interface principal
def main():
    # Inicializar variáveis de sessão se não existirem
    session_vars = [
        'monthly_investment', 'quarterly_investment', 'annual_investment',
        'financial_goal', 'simulate_selic', 'simulate_cdb', 'simulate_fii',
        'simulate_stocks', 'simulate_treasury', 'include_ipca', 'include_taxes',
        'start_date', 'end_date', 'economic_scenario', 'continuous_simulation'
    ]
    
    default_values = {
        'monthly_investment': 1000.0,
        'quarterly_investment': 0.0,
        'annual_investment': 0.0,
        'financial_goal': 100000.0,
        'simulate_selic': True,
        'simulate_cdb': True,
        'simulate_fii': True,
        'simulate_stocks': True,
        'simulate_treasury': True,
        'include_ipca': True,
        'include_taxes': True,
        'start_date': datetime.date.today(),
        'end_date': datetime.date.today() + timedelta(days=365*5),
        'economic_scenario': 'neutro',
        'continuous_simulation': False
    }
    
    for var in session_vars:
        if var not in st.session_state:
            st.session_state[var] = default_values[var]
    
    # Painel de ticker no topo
    ticker_component()
    
    # Cabeçalho com logo centralizada e aumentada
    st.markdown(f'''
    <div class="logo-header">
        <img src="{LOGO_URL}" class="logo-image">
    </div>
    ''', unsafe_allow_html=True)
    
    st.markdown('<p class="logo-subtitle">Simulador Inteligente de Investimentos</p>', unsafe_allow_html=True)
    
    # Frase inspiradora
    st.markdown('<p class="inspirational-quote">"A melhor época para plantar uma árvore foi há 20 anos. A segunda melhor é agora."</p>', unsafe_allow_html=True)
    st.markdown('<p class="quote-author">- Provérbio Chinês</p>', unsafe_allow_html=True)
    
    # Inicializar simulador
    simulator = SecureInvestSimulator()
    
    # Sidebar com parâmetros de entrada
    with st.sidebar:
        st.markdown('<p class="sidebar-header">📊 Parâmetros do Investimento</p>', unsafe_allow_html=True)
        
        # Botão de alternância de tema
        theme_label = "🌙 Modo Escuro" if st.session_state.theme == 'light' else "☀️ Modo Claro"
        if st.button(theme_label, key="theme_toggle"):
            toggle_theme()
        
        # Botão de reset
        if st.button("🔄 Resetar", key="reset_button", use_container_width=True):
            reset_parameters()
        
        # Informações sobre IPCA
        with st.expander("ℹ️ Sobre o IPCA"):
            st.markdown("""
            **IPCA** (Índice Nacional de Preços ao Consumidor Amplo) é o indicador oficial de inflação no Brasil.
            
            **Por que considerar a inflação?**
            - Mostra o **ganho real** dos investimentos
            - Ajuda a comparar diferentes modalidades
            - Evita ilusão monetária
            
            **Taxa de inflação considerada:** {:.2f}% ao ano
            """.format(simulator.inflation_annual * 100))
        
        # Datas
        st.subheader("📅 Período de Investimento")
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                "Data Início",
                st.session_state.start_date,
                min_value=datetime.date(2010, 1, 1),
                key="start_date_input"
            )
        with col2:
            end_date = st.date_input(
                "Data Final",
                st.session_state.end_date,
                min_value=datetime.date(2021, 1, 1),
                key="end_date_input"
            )
        
        # Modo de simulação contínua
        continuous_simulation = st.checkbox("Simulação Contínua (sem data final)", 
                                           value=st.session_state.continuous_simulation,
                                           key="continuous_simulation_input")
        
        # Valores de aporte
        st.subheader("💵 Valores de Aporte")
        monthly_investment = st.number_input("Aporte Mensal (R$)", min_value=0.0, 
                                           value=st.session_state.monthly_investment, 
                                           step=100.0, key="monthly_investment_input")
        quarterly_investment = st.number_input("Aporte Trimestral (R$)", min_value=0.0, 
                                             value=st.session_state.quarterly_investment, 
                                             step=1000.0, key="quarterly_investment_input")
        annual_investment = st.number_input("Aporte Anual (R$)", min_value=0.0, 
                                          value=st.session_state.annual_investment, 
                                          step=5000.0, key="annual_investment_input")
        
        # Campo para objetivo financeiro
        st.subheader("🎯 Objetivo Financeiro")
        financial_goal = st.number_input("Valor do Objetivo (R$)", min_value=0.0, 
                                       value=st.session_state.financial_goal, 
                                       step=1000.0, key="financial_goal_input")
        
        # Opção para incluir IPCA
        include_ipca = st.checkbox("Considerar inflação (IPCA) nos cálculos", 
                                 value=st.session_state.include_ipca, 
                                 key="include_ipca_input")
        
        # Opção para incluir impostos e taxas
        include_taxes = st.checkbox("Considerar impostos e taxas", 
                                  value=st.session_state.include_taxes, 
                                  key="include_taxes_input")
        
        # Cenário econômico
        economic_scenario = st.selectbox(
            "Cenário Econômico",
            options=list(simulator.economic_scenarios.keys()),
            format_func=lambda x: f"{x.capitalize()} ({simulator.economic_scenarios[x]['descricao']})",
            index=list(simulator.economic_scenarios.keys()).index(st.session_state.economic_scenario),
            key="economic_scenario_input"
        )
        
        # Modalidades de investmento
        st.subheader("📈 Modalidades de Investimento")
        simulate_selic = st.checkbox("Tesouro Selic", value=st.session_state.simulate_selic, key="simulate_selic_input")
        simulate_cdb = st.checkbox("CDB 1% ao mês", value=st.session_state.simulate_cdb, key="simulate_cdb_input")
        simulate_fii = st.checkbox("Fundos Imobiliários", value=st.session_state.simulate_fii, key="simulate_fii_input")
        simulate_stocks = st.checkbox("Ações", value=st.session_state.simulate_stocks, key="simulate_stocks_input")
        simulate_treasury = st.checkbox("Tesouro Direto", value=st.session_state.simulate_treasury, key="simulate_treasury_input")
        
        # Sistema de portfólios
        with st.expander("💼 Gerenciar Portfólios"):
            portfolio_name = st.text_input("Nome do Portfólio", placeholder="Meu Portfólio")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Salvar Portfólio"):
                    if portfolio_name:
                        # Salvar configuração atual como portfólio
                        simulator.portfolios[portfolio_name] = {
                            'monthly_investment': monthly_investment,
                            'financial_goal': financial_goal,
                            'selected_modalities': {
                                'selic': simulate_selic,
                                'cdb': simulate_cdb,
                                'fii': simulate_fii,
                                'stocks': simulate_stocks,
                                'treasury': simulate_treasury
                            }
                        }
                        st.success(f"Portfólio '{portfolio_name}' salvo!")
            with col2:
                if st.button("Carregar Portfólio"):
                    if portfolio_name in simulator.portfolios:
                        portfolio = simulator.portfolios[portfolio_name]
                        st.session_state.monthly_investment = portfolio['monthly_investment']
                        st.session_state.financial_goal = portfolio['financial_goal']
                        st.session_state.simulate_selic = portfolio['selected_modalities']['selic']
                        st.session_state.simulate_cdb = portfolio['selected_modalities']['cdb']
                        st.session_state.simulate_fii = portfolio['selected_modalities']['fii']
                        st.session_state.simulate_stocks = portfolio['selected_modalities']['stocks']
                        st.session_state.simulate_treasury = portfolio['selected_modalities']['treasury']
                        st.rerun()
        
        # Alertas do Fed
        with st.expander("🔔 Próximos Eventos do Fed"):
            st.info("""
            **Próximas reuniões do FOMC:**
            - 14-15 de Dezembro de 2023
            - 31 de Janeiro - 1 de Fevereiro de 2024
            - 19-20 de Março de 2024
            
            **Indicadores importantes:**
            - Inflação (CPI): 7.1%
            - Taxa de desemprego: 3.7%
            - PIB: +2.9%
            """)
        
        # Botão de simulação
        simulate_button = st.button("🚀 Simular Investimentos", type="primary", use_container_width=True)
    
    # Conteúdo principal
    if simulate_button:
        # Atualizar session state com os valores atuais
        for var, value in zip(session_vars, [
            monthly_investment, quarterly_investment, annual_investment,
            financial_goal, simulate_selic, simulate_cdb, simulate_fii,
            simulate_stocks, simulate_treasury, include_ipca, include_taxes,
            start_date, end_date, economic_scenario, continuous_simulation
        ]):
            st.session_state[var] = value
        
        # Cálculos
        results = {}
        monthly_rates = {}
        results_real = {}  # Resultados considerando inflação
        monthly_rates_real = {}  # Taxas mensais considerando inflação
        
        if simulate_selic:
            results['selic'] = simulator.calculate_fixed_income(
                monthly_investment, 'monthly', start_date, end_date, 'selic', False, include_taxes
            )
            monthly_rates['selic'] = results['selic']['monthly_rate']
            
            if include_ipca:
                results_real['selic'] = simulator.calculate_fixed_income(
                    monthly_investment, 'monthly', start_date, end_date, 'selic', True, include_taxes
                )
                monthly_rates_real['selic'] = results_real['selic']['monthly_rate']
        
        if simulate_cdb:
            results['cdb'] = simulator.calculate_fixed_income(
                monthly_investment, 'monthly', start_date, end_date, 'cdb', False, include_taxes
            )
            monthly_rates['cdb'] = results['cdb']['monthly_rate']
            
            if include_ipca:
                results_real['cdb'] = simulator.calculate_fixed_income(
                    monthly_investment, 'monthly', start_date, end_date, 'cdb', True, include_taxes
                )
                monthly_rates_real['cdb'] = results_real['cdb']['monthly_rate']
        
        if simulate_fii:
            results['fii'] = simulator.calculate_variable_income(
                monthly_investment, 'monthly', start_date, end_date, 'fii', None, False, include_taxes
            )
            monthly_rates['fii'] = results['fii']['monthly_rate']
            
            if include_ipca:
                results_real['fii'] = simulator.calculate_variable_income(
                    monthly_investment, 'monthly', start_date, end_date, 'fii', None, True, include_taxes
                )
                monthly_rates_real['fii'] = results_real['fii']['monthly_rate']
        
        if simulate_stocks:
            results['stocks'] = simulator.calculate_variable_income(
                monthly_investment, 'monthly', start_date, end_date, 'stocks', None, False, include_taxes
            )
            monthly_rates['stocks'] = results['stocks']['monthly_rate']
            
            if include_ipca:
                results_real['stocks'] = simulator.calculate_variable_income(
                    monthly_investment, 'monthly', start_date, end_date, 'stocks', None, True, include_taxes
                )
                monthly_rates_real['stocks'] = results_real['stocks']['monthly_rate']
        
        if simulate_treasury:
            # Usar o primeiro tesouro selecionado ou um padrão
            selected_t = 'Tesouro Selic'
            results['treasury'] = simulator.calculate_treasury(
                monthly_investment, 'monthly', start_date, end_date, selected_t, False, include_taxes
            )
            monthly_rates['treasury'] = results['treasury']['monthly_rate']
            
            if include_ipca:
                results_real['treasury'] = simulator.calculate_treasury(
                    monthly_investment, 'monthly', start_date, end_date, selected_t, True, include_taxes
                )
                monthly_rates_real['treasury'] = results_real['treasury']['monthly_rate']
        
        # Aplicar cenário econômico
        for key in list(results.keys()):
            results[key] = simulator.simulate_economic_scenario(economic_scenario, results[key])
            if include_ipca and key in results_real:
                results_real[key] = simulator.simulate_economic_scenario(economic_scenario, results_real[key])
        
        # Exibir resultados em abas
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Resumo", "📈 Gráficos", "🎯 Análise de Objetivo", "📋 Detalhes", "⚠️ Análise de Risco"])
        
        with tab1:
            st.header("📊 Resultados da Simulação")
            
            if include_ipca:
                st.info(f"💡 **Simulação considerando inflação (IPCA de {simulator.inflation_annual*100:.2f}% ao ano)**")
            
            st.info(f"📊 **Cenário econômico:** {economic_scenario.capitalize()} ({simulator.economic_scenarios[economic_scenario]['descricao']})")
            
            # Métricas
            cols = st.columns(len(results))
            for i, (key, result) in enumerate(results.items()):
                with cols[i]:
                    if key == 'selic':
                        name = "Tesouro Selic"
                        icon = "🏦"
                    elif key == 'cdb':
                        name = "CDB"
                        icon = "📈"
                    elif key == 'fii':
                        name = "Fundos Imobiliários"
                        icon = "🏢"
                    elif key == 'stocks':
                        name = "Ações"
                        icon = "📊"
                    else:
                        name = "Tesouro Direto"
                        icon = "🇧🇷"
                    
                    st.markdown(f'<div class="metric-card">', unsafe_allow_html=True)
                    
                    # Mostrar resultado nominal e real se aplicável
                    if include_ipca and key in results_real:
                        real_result = results_real[key]
                        real_earnings_percentage = ((real_result['final_balance'] - real_result['total_contributed']) / 
                                                  real_result['total_contributed'] * 100) if real_result['total_contributed'] > 0 else 0
                        
                        st.metric(
                            f"{icon} {name}",
                            f"R$ {result['final_balance']:,.2f}",
                            f"R$ {real_result['final_balance']:,.2f} (valor real)"
                        )
                    else:
                        earnings_percentage = ((result['final_balance'] - result['total_contributed']) / 
                                             result['total_contributed'] * 100) if result['total_contributed'] > 0 else 0
                        st.metric(
                            f"{icon} {name}",
                            f"R$ {result['final_balance']:,.2f}",
                            f"{earnings_percentage:.2f}%"
                        )
                    
                    st.markdown(f"**Total Aportado:** R$ {result['total_contributed']:,.2f}")
                    
                    if include_ipca and key in results_real:
                        real_earnings = real_result['final_balance'] - real_result['total_contributed']
                        st.markdown(f"**Rendimento Real:** R$ {real_earnings:,.2f}")
                        st.markdown(f"**Rendimento Nominal:** R$ {result['final_balance'] - result['total_contributed']:,.2f}")
                    else:
                        st.markdown(f"**Rendimento:** R$ {result['final_balance'] - result['total_contributed']:,.2f}")
                    
                    if include_taxes and 'taxes' in result:
                        st.markdown(f"**Impostos:** R$ {result['taxes']:,.2f}")
                    
                    st.markdown('</div>', unsafe_allow_html=True)
            
            # Comparativo entre modalidades
            st.subheader("📌 Comparativo entre Modalidades")
            
            fig_comparison = make_subplots(rows=1, cols=2, subplot_titles=('Rentabilidade Absoluta', 'Rentabilidade Percentual'))
            
            labels = {'selic': 'Tesouro Selic', 'cdb': 'CDB', 'fii': 'FIIs', 'stocks': 'Ações', 'treasury': 'Tesouro'}
            modalities = [labels[key] for key in results.keys()]
            final_balances = [results[key]['final_balance'] for key in results.keys()]
            earnings = [results[key]['final_balance'] - results[key]['total_contributed'] for key in results.keys()]
            
            # CORREÇÃO DO ERRO: Fechamento correto dos colchetes e parênteses
            earnings_percentages = [
                ((results[key]['final_balance'] - results[key]['total_contributed']) / 
                 results[key]['total_contributed'] * 100) if results[key]['total_contributed'] > 0 else 0 
                for key in results.keys()
            ]
            
            colors = ['#1E3A8A', '#3B82F6', '#10B981', '#EF4444', '#8B5CF6']
            if st.session_state.theme == 'dark':
                colors = ['#3B82F6', '#60A5FA', '#10B981', '#EF4444', '#A78BFA']
            
            fig_comparison.add_trace(
                go.Bar(x=modalities, y=earnings, name='Ganho Absoluto', marker_color=colors[:len(modalities)]),
                row=1, col=1
            )
            
            fig_comparison.add_trace(
                go.Bar(x=modalities, y=earnings_percentages, name='Ganho Percentual', marker_color=colors[:len(modalities)]),
                row=1, col=2
            )
            
            # Ajustar tema do gráfico comparativo
            if st.session_state.theme == 'dark':
                fig_comparison.update_layout(
                    template="plotly_dark",
                    height=400, 
                    showlegend=False,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)'
                )
            else:
                fig_comparison.update_layout(
                    template="plotly_white",
                    height=400, 
                    showlegend=False
                )
                
            fig_comparison.update_yaxes(title_text="Rentabilidade (R$)", row=1, col=1)
            fig_comparison.update_yaxes(title_text="Rentabilidade (%)", row=1, col=2)
            
            st.plotly_chart(fig_comparison, use_container_width=True)
            
            # Se estamos considerando inflação, mostrar comparação entre nominal e real
            if include_ipca and results_real:
                st.subheader("📊 Comparativo: Rentabilidade Nominal vs Real")
                
                fig_real_vs_nominal = go.Figure()
                
                # Dados nominais
                nominal_balances = [results[key]['final_balance'] for key in results.keys()]
                real_balances = [results_real[key]['final_balance'] for key in results_real.keys()]
                
                fig_real_vs_nominal.add_trace(go.Bar(
                    name='Nominal',
                    x=modalities,
                    y=nominal_balances,
                    marker_color=colors[:len(modalities)]
                ))
                
                fig_real_vs_nominal.add_trace(go.Bar(
                    name='Real (ajustado pela inflação)',
                    x=modalities,
                    y=real_balances,
                    marker_color=['#9CA3AF'] * len(modalities)
                ))
                
                if st.session_state.theme == 'dark':
                    fig_real_vs_nominal.update_layout(
                        template="plotly_dark",
                        barmode='group',
                        title="Comparação entre Valores Nominais e Reais",
                        xaxis_title="Modalidade",
                        yaxis_title="Valor (R$)",
                        height=400
                    )
                else:
                    fig_real_vs_nominal.update_layout(
                        template="plotly_white",
                        barmode='group',
                        title="Comparação entre Valores Nominais e Reais",
                        xaxis_title="Modalidade",
                        yaxis_title="Valor (R$)",
                        height=400
                    )
                
                st.plotly_chart(fig_real_vs_nominal, use_container_width=True)
            
            # Botões de exportação
            st.subheader("📤 Exportar Resultados")
            col1, col2 = st.columns(2)
            
            with col1:
                # Preparar dados para exportação
                export_data = {
                    'Data da Simulação': datetime.datetime.now().strftime('%d/%m/%Y %H:%M'),
                    'Cenário Econômico': f"{economic_scenario.capitalize()} ({simulator.economic_scenarios[economic_scenario]['descricao']})",
                    'Total Aportado': f"R$ {sum(results[key]['total_contributed'] for key in results.keys()):,.2f}",
                    'Patrimônio Final Médio': f"R$ {np.mean([results[key]['final_balance'] for key in results.keys()]):,.2f}",
                }
                
                for key, result in results.items():
                    export_data[f"{labels[key]} - Patrimônio Final"] = f"R$ {result['final_balance']:,.2f}"
                    export_data[f"{labels[key]} - Rentabilidade"] = f"{((result['final_balance'] - result['total_contributed']) / result['total_contributed'] * 100):.2f}%"
                
                pdf_buffer = create_pdf(export_data, "Relatório de Investimentos - SecureInvest")
                st.download_button(
                    label="📄 Exportar PDF",
                    data=pdf_buffer,
                    file_name="relatorio_investimentos.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            
            with col2:
                excel_buffer = create_excel(export_data)
                st.download_button(
                    label="📊 Exportar Excel",
                    data=excel_buffer,
                    file_name="relatorio_investimentos.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
        
        with tab2:
            st.header("📈 Evolução dos Investimentos")
            
            fig = go.Figure()
            
            colors = {'selic': '#1E3A8A', 'cdb': '#3B82F6', 'fii': '#10B981', 'stocks': '#EF4444', 'treasury': '#8B5CF6'}
            if st.session_state.theme == 'dark':
                colors = {'selic': '#3B82F6', 'cdb': '#60A5FA', 'fii': '#10B981', 'stocks': '#EF4444', 'treasury': '#A78BFA'}
                
            labels = {'selic': 'Tesouro Selic', 'cdb': 'CDB', 'fii': 'FIIs', 'stocks': 'Ações', 'treasury': 'Tesouro'}
            
            for key, result in results.items():
                if 'history' in result:
                    dates = [item['date'] for item in result['history']]
                    balances = [item['balance'] for item in result['history']]
                    
                    fig.add_trace(go.Scatter(
                        x=dates,
                        y=balances,
                        name=labels[key],
                        line=dict(color=colors[key], width=3),
                        mode='lines'
                    ))
            
            # Adicionar linha do objetivo
            fig.add_hline(y=financial_goal, line_dash="dash", line_color="orange", 
                         annotation_text=f"Objetivo: R$ {financial_goal:,.2f}", 
                         annotation_position="bottom right")
            
            # Adicionar linha de referência do IPCA se aplicável
            if include_ipca:
                # Calcular evolução da inflação
                months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
                monthly_inflation = (1 + simulator.inflation_annual) ** (1/12) - 1
                inflation_values = [monthly_investment * (1 + monthly_inflation) ** i for i in range(months)]
                
                # Ajustar datas para a linha de inflação
                inflation_dates = [start_date + timedelta(days=30*i) for i in range(months)]
                
                fig.add_trace(go.Scatter(
                    x=inflation_dates,
                    y=inflation_values,
                    name="IPCA (Inflação)",
                    line=dict(color="#9CA3AF", width=2, dash="dot"),
                    mode='lines'
                ))
            
            # Ajustar tema do gráfico conforme seleção
            if st.session_state.theme == 'dark':
                fig.update_layout(
                    template="plotly_dark",
                    title="Evolução do Patrimônio",
                    xaxis_title="Data",
                    yaxis_title="Valor (R$)",
                    hovermode='x unified',
                    height=500,
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)'
                )
            else:
                fig.update_layout(
                    template="plotly_white",
                    title="Evolução do Patrimônio",
                    xaxis_title="Data",
                    yaxis_title="Valor (R$)",
                    hovermode='x unified',
                    height=500,
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Gráfico de composição do patrimônio
            st.subheader("📊 Composição do Patrimônio")
            
            fig_pie = go.Figure(data=[go.Pie(
                labels=[labels[key] for key in results.keys()],
                values=[results[key]['final_balance'] for key in results.keys()],
                hole=.4,
                marker_colors=[colors[key] for key in results.keys()]
            )])
            
            if st.session_state.theme == 'dark':
                fig_pie.update_layout(template="plotly_dark")
            else:
                fig_pie.update_layout(template="plotly_white")
                
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with tab3:
            # Análise de objetivo
            st.header("🎯 Análise Específica para o Objetivo Financeiro")
            st.info("Esta análise calcula quanto tempo levaria para atingir seu objetivo e quais aportes seriam necessários.")
            
            total_months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
            
            labels = {'selic': 'Tesouro Selic', 'cdb': 'CDB', 'fii': 'FIIs', 'stocks': 'Ações', 'treasury': 'Tesouro'}
            
            for key, monthly_rate in monthly_rates.items():
                # Calcular cenário para o objetivo
                goal_scenario = simulator.calculate_goal_scenario(
                    monthly_rate, financial_goal, monthly_investment, total_months
                )
                
                # Exibir resultados
                with st.expander(f"Análise para {labels[key]}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if goal_scenario['time_with_current'] == float('inf'):
                            st.metric("Tempo para objetivo com aportes atuais", "Não atingível")
                        else:
                            st.metric(
                                "Tempo para objetivo com aportes atuais", 
                                f"{goal_scenario['time_with_current']:.1f} meses", 
                                f"{(goal_scenario['time_with_current']/12):.1f} anos"
                            )
                        
                        st.metric(
                            "Aporte mensal necessário para o objetivo", 
                            f"R$ {goal_scenario['required_monthly']:,.2f}"
                        )
                    
                    with col2:
                        st.metric(
                            "Patrimônio projetado com aportes atuais", 
                            f"R$ {results[key]['final_balance']:,.2f}"
                        )
                        
                        if goal_scenario['additional_monthly'] > 0:
                            st.metric(
                                "Aporte adicional mensal necessário", 
                                f"R$ {goal_scenario['additional_monthly']:,.2f}"
                            )
                        else:
                            st.metric("Aporte adicional mensal necessário", "R$ 0,00")
                    
                    st.subheader("Aportes periódicos necessários para o objetivo:")
                    col3, col4, col5, col6 = st.columns(4)
                    
                    with col3:
                        st.metric("Mensal", f"R$ {goal_scenario['required_monthly']:,.2f}")
                    with col4:
                        st.metric("Trimestral", f"R$ {goal_scenario['required_monthly'] * 3:,.2f}")
                    with col5:
                        st.metric("Semestral", f"R$ {goal_scenario['required_monthly'] * 6:,.2f}")
                    with col6:
                        st.metric("Anual", f"R$ {goal_scenario['required_monthly'] * 12:,.2f}")
                    
                    # Verificar se o objetivo será atingido
                    if results[key]['final_balance'] >= financial_goal:
                        st.success(f"🎉 Parabéns! Você atingirá seu objetivo de R$ {financial_goal:,.2f} com {labels[key]}")
                    else:
                        st.warning(f"⚠️ Com os aportes atuais, você não atingirá o objetivo de R$ {financial_goal:,.2f} com {labels[key]}")
                        
                        if goal_scenario['additional_monthly'] > 0:
                            st.info(
                                f"💡 Para atingir seu objetivo no período desejado, você precisaria aportar "
                                f"**R$ {goal_scenario['additional_monthly']:,.2f} adicionais por mês** "
                                f"em {labels[key]}"
                            )
        
        with tab4:
            # Tabela detalhada
            st.header("📋 Detalhamento dos Resultados")
            
            detail_data = []
            for key, result in results.items():
                earnings_percentage = ((result['final_balance'] - result['total_contributed']) / 
                                      result['total_contributed'] * 100) if result['total_contributed'] > 0 else 0
                
                detail_row = {
                    'Modalidade': labels[key],
                    'Total Aportado': f"R$ {result['total_contributed']:,.2f}",
                    'Saldo Final': f"R$ {result['final_balance']:,.2f}",
                    'Rentabilidade': f"R$ {result['final_balance'] - result['total_contributed']:,.2f}",
                    'Rentabilidade %': f"{earnings_percentage:.2f}%",
                    'Atinge Objetivo': '✅' if result['final_balance'] >= financial_goal else '❌'
                }
                
                # Adicionar informações sobre ganho real se aplicável
                if include_ipca and key in results_real:
                    real_result = results_real[key]
                    real_earnings = real_result['final_balance'] - real_result['total_contributed']
                    real_earnings_percentage = ((real_result['final_balance'] - real_result['total_contributed']) / 
                                              real_result['total_contributed'] * 100) if real_result['total_contributed'] > 0 else 0
                    
                    detail_row['Saldo Final Real'] = f"R$ {real_result['final_balance']:,.2f}"
                    detail_row['Rentabilidade Real'] = f"R$ {real_earnings:,.2f}"
                    detail_row['Rentabilidade Real %'] = f"{real_earnings_percentage:.2f}%"
                
                if include_taxes and 'taxes' in result:
                    detail_row['Impostos'] = f"R$ {result['taxes']:,.2f}"
                
                detail_data.append(detail_row)
            
            # Ajustar a tabela para o tema
            st.dataframe(pd.DataFrame(detail_data), use_container_width=True)
            
            # Relatório final
            st.subheader("📄 Relatório de Análise")
            
            best_modality = max(results.items(), key=lambda x: x[1]['final_balance'])
            best_modality_name = labels[best_modality[0]]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                **🔍 Análise de Resultados:**
                
                - A modalidade com melhor desempenho foi **{}**
                - O patrimônio final estimado é de **R$ {:,.2f}**
                - Período de investimento: {} meses
                """.format(
                    best_modality_name,
                    best_modality[1]['final_balance'],
                    total_months
                ))
            
            with col2:
                st.markdown("""
                **💡 Recomendações:**
                
                - Considere diversificar entre diferentes modalidades
                - Reveja periodicamente sua estratégia de investimentos
                - Mantenha uma reserva de emergência em aplicações de liquidez imediata
                """)
        
        with tab5:
            st.header("⚠️ Análise de Risco")
            
            # Calcular métricas de risco para cada modalidade
            risk_data = {}
            for key, result in results.items():
                if 'history' in result:
                    risk_metrics = simulator.calculate_risk_metrics(result['history'])
                    risk_data[key] = risk_metrics
            
            # Exibir métricas de risco
            if risk_data:
                cols = st.columns(len(risk_data))
                colors = ['#3B82F6', '#60A5FA', '#10B981', '#EF4444', '#A78BFA']
                
                for i, (key, metrics) in enumerate(risk_data.items()):
                    with cols[i]:
                        st.markdown(f'<div class="risk-metric">', unsafe_allow_html=True)
                        st.subheader(f"{labels[key]}")
                        st.metric("Volatilidade Anual", f"{metrics['volatility']:.2f}%")
                        st.metric("Drawdown Máximo", f"{metrics['max_drawdown']:.2f}%")
                        st.metric("Índice Sharpe", f"{metrics['sharpe_ratio']:.2f}")
                        st.markdown('</div>', unsafe_allow_html=True)
                
                # Gráfico de drawdown
                st.subheader("📉 Drawdown Máximo por Modalidade")
                
                fig_drawdown = go.Figure()
                
                modalities = [labels[key] for key in risk_data.keys()]
                drawdowns = [risk_data[key]['max_drawdown'] for key in risk_data.keys()]
                
                fig_drawdown.add_trace(go.Bar(
                    x=modalities,
                    y=drawdowns,
                    marker_color=colors[:len(modalities)]
                ))
                
                if st.session_state.theme == 'dark':
                    fig_drawdown.update_layout(
                        template="plotly_dark",
                        title="Drawdown Máximo por Modalidade",
                        xaxis_title="Modalidade",
                        yaxis_title="Drawdown Máximo (%)",
                        height=400
                    )
                else:
                    fig_drawdown.update_layout(
                        template="plotly_white",
                        title="Drawdown Máximo por Modalidade",
                        xaxis_title="Modalidade",
                        yaxis_title="Drawdown Máximo (%)",
                        height=400
                    )
                
                st.plotly_chart(fig_drawdown, use_container_width=True)
            
            # Análise de cenários
            st.subheader("🌍 Análise de Cenários Econômicos")
            
            scenario_results = {}
            base_key = list(results.keys())[0] if results else None
            
            if base_key:
                for scenario in simulator.economic_scenarios.keys():
                    scenario_results[scenario] = simulator.simulate_economic_scenario(
                        scenario, results[base_key]
                    )
                
                scenario_fig = go.Figure()
                
                scenarios = list(scenario_results.keys())
                scenario_names = [f"{s.capitalize()}\n({simulator.economic_scenarios[s]['descricao']})" for s in scenarios]
                final_balances = [scenario_results[s]['final_balance'] for s in scenarios]
                
                scenario_fig.add_trace(go.Bar(
                    x=scenario_names,
                    y=final_balances,
                    marker_color=['#10B981', '#3B82F6', '#F59E0B', '#EF4444']
                ))
                
                if st.session_state.theme == 'dark':
                    scenario_fig.update_layout(
                        template="plotly_dark",
                        title="Impacto dos Cenários Econômicos no Patrimônio Final",
                        xaxis_title="Cenário Econômico",
                        yaxis_title="Patrimônio Final (R$)",
                        height=400
                    )
                else:
                    scenario_fig.update_layout(
                        template="plotly_white",
                        title="Impacto dos Cenários Econômicos no Patrimônio Final",
                        xaxis_title="Cenário Econômico",
                        yaxis_title="Patrimônio Final (R$)",
                        height=400
                    )
                
                st.plotly_chart(scenario_fig, use_container_width=True)
    
    else:
        # Página inicial quando não há simulação
        st.info("💡 Configure os parâmetros do investimento na barra lateral, basta clicar nas setas no canto superior esquerdo (>>), após preencher os campos desejados clique em 'Simular Investimentos' para ver os resultados.")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown('<div class="investment-option">', unsafe_allow_html=True)
            st.subheader("💰 Renda Fixa")
            st.markdown("""
            - Tesouro Selic
            - CDBs
            - LCIs e LCAs
            - Debêntures
            """)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="investment-option">', unsafe_allow_html=True)
            st.subheader("🏢 Fundos Imobiliários")
            st.markdown("""
            - Alto potencial de dividendos
            - Diversificação imobiliária
            - Liquidez diária
            """)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="investment-option">', unsafe_allow_html=True)
            st.subheader("📈 Ações")
            st.markdown("""
            - Maior potencial de valorização
            - Dividendos regulares
            - Participação societária
            """)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col4:
            st.markdown('<div class="investment-option">', unsafe_allow_html=True)
            st.subheader("🇧🇷 Tesouro Direto")
            st.markdown("""
            - Títulos públicos federais
            - Segurança e liquidez
            - Indexados a diferentes indicadores
            """)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Alertas inteligentes
        with st.expander("🔔 Alertas do Mercado"):
            st.info("📅 **Próxima reunião do Fed**: 14-15 de Dezembro")
            st.warning("⚠️ **IBOVESPA** em alta de 2.3% hoje")
            st.success("✅ **Taxa Selic** mantida em 11.75% ao ano")
        
        # Informações sobre o simulador
        with st.expander("ℹ️ Sobre o SecureInvest"):
            st.markdown("""
            **SecureInvest** é um simulador de investimentos que permite projetar rentabilidade de diferentes modalidades:
            
            - **Renda Fixa**: Simula investimentos em Tesouro Selic e CDBs
            - **Fundos Imobiliários**: Projeta rentabilidade baseada em dados históricos de FIIs
            - **Ações**: Calcula possíveis retornos do mercado acionário
            - **Tesouro Direto**: Simula investimentos em títulos públicos
            
                        
            **Aviso importante**: Este simulador utiliza projeções baseadas em dados históricos e não garante resultados futuros.
            Todas as simulações são meramente ilustrativas.
            """)

if __name__ == "__main__":
    main()