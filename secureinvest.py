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
warnings.filterwarnings('ignore')

# Configuração da página
st.set_page_config(
    page_title="SecureInvest - Simulador de Investimentos",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# URL da sua logo (corrigida)
LOGO_URL = "https://i.ibb.co/MkVDCtgD/Secure-Invest.png"

# Gerenciamento de tema
if 'theme' not in st.session_state:
    st.session_state.theme = 'light'

def toggle_theme():
    if st.session_state.theme == 'light':
        st.session_state.theme = 'dark'
    else:
        st.session_state.theme = 'light'
    # Forçar rerun para aplicar o tema
    st.rerun()

# Aplicar tema antes de qualquer outro conteúdo
if st.session_state.theme == 'dark':
    # Modo escuro com cores mais contrastantes
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
        gap: 1rem;
        margin-bottom: 1rem;
    }
    .logo-image {
        max-height: 80px;
        border-radius: 10px;
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
    }
    .stExpander .streamlit-expanderHeader {
        color: #E5E7EB !important;
        background-color: #1F2937;
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
        border-radius: 0.5rem;
        box-shadow: 0 4px 6px rgba(255, 255, 255, 0.1);
        margin-bottom: 1rem;
        color: #E5E7EB;
        border: 1px solid #374151;
    }
    .investment-option {
        background-color: #374151;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        border-left: 4px solid #3B82F6;
        color: #E5E7EB;
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
        border-radius: 0.5rem;
        padding: 0.5rem 1rem;
        width: 100%;
        border: none;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #1D4ED8 0%, #047857 100%);
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
        border-radius: 0.25rem;
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
    }
    .stDateInput [data-baseweb="input"] input {
        color: #E5E7EB !important;
    }
    /* Correção para selectbox no modo escuro */
    .stSelectbox [data-baseweb="select"] {
        background-color: #374151;
        color: #E5E7EB;
        border: 1px solid #4B5563;
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
    }
    /* Novos estilos para melhorias */
    .card {
        background-color: #1F2937;
        padding: 1.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 4px 6px rgba(255, 255, 255, 0.1);
        margin-bottom: 1rem;
        border: 1px solid #374151;
    }
    .card-header {
        font-size: 1.25rem;
        font-weight: 600;
        margin-bottom: 1rem;
        color: #3B82F6;
    }
    .asset-card {
        background-color: #374151;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        border-left: 4px solid #3B82F6;
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
        border-radius: 0.5rem;
        padding: 1rem;
        margin-bottom: 1.5rem;
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
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #2563EB;
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
    }
    .secure-logo {
        font-size: 3.5rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: 0.5rem;
        background: linear-gradient(90deg, #2563EB 0%, #059669 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .invest-logo {
        font-size: 3.5rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: 1rem;
        background: linear-gradient(90deg, #059669 0%, #2563EB 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .logo-subtitle {
        font-size: 1.2rem;
        color: #9CA3AF;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 500;
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
        gap: 1rem;
        margin-bottom: 1rem;
    }
    .logo-image {
        max-height: 80px;
        border-radius: 10px;
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
        border-radius: 0.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
        border: 1px solid #E5E7EB;
    }
    .investment-option {
        background-color: #F1F5F9;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        border-left: 4px solid #1E3A8A;
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
        border-radius: 0.5rem;
        padding: 0.5rem 1rem;
        width: 100%;
        border: none;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #1E40AF 0%, #047857 100%);
    }
    /* Novos estilos para melhorias */
    .card {
        background-color: #FFFFFF;
        padding: 1.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
        border: 1px solid #E5E7EB;
    }
    .card-header {
        font-size: 1.25rem;
        font-weight: 600;
        margin-bottom: 1rem;
        color: #1E3A8A;
    }
    .asset-card {
        background-color: #F1F5F9;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        border-left: 4px solid #1E3A8A;
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
        border-radius: 0.5rem;
        padding: 1rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
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
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #3B82F6;
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
    }
    .secure-logo {
        font-size: 3.5rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: 0.5rem;
        background: linear-gradient(90deg, #1E3A8A 0%, #059669 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .invest-logo {
        font-size: 3.5rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: 1rem;
        background: linear-gradient(90deg, #059669 0%, #1E3A8A 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .logo-subtitle {
        font-size: 1.2rem;
        color: #6B7280;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 500;
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
        else:  # stocks
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
        self.inflation_annual = 0.045  # 4.5% ao ano
        
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
        
        # Dicionário para ativos pesquisados
        self.searched_assets = {'fii': {}, 'stocks': {}}
    
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
            else:
                self.searched_assets['stocks'][ticker] = {
                    'dividend_yield': asset_info['dividend_yield'],
                    'annual_return': asset_info['annual_return'],
                    'nome': asset_info['nome'],
                    'setor': asset_info['setor']
                }
        
        return asset_info
    
    def get_asset_data(self, asset_type):
        """Retorna dados de ativos incluindo os pesquisados"""
        if asset_type == 'fii':
            return {**self.fii_data, **self.searched_assets['fii']}
        else:
            return {**self.stock_data, **self.searched_assets['stocks']}
    
    def calculate_fixed_income(self, amount, frequency, start_date, end_date, investment_type):
        """Calcula rendimentos da renda fixa"""
        months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
        
        if investment_type == 'selic':
            monthly_rate = (1 + self.selic_annual) ** (1/12) - 1
        elif investment_type == 'cdb':
            monthly_rate = self.cdb_monthly
        else:
            monthly_rate = 0
        
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
        earnings_percentage = (earnings / total_contributed) * 100 if total_contributed > 0 else 0
        
        return {
            'final_balance': balance,
            'total_contributed': total_contributed,
            'earnings': earnings,
            'earnings_percentage': earnings_percentage,
            'history': history,
            'monthly_rate': monthly_rate
        }
    
    def calculate_variable_income(self, amount, frequency, start_date, end_date, asset_type, selected_assets=None):
        """Calcula rendimentos da renda variável"""
        months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
        
        if asset_type == 'fii':
            data = self.get_asset_data('fii')
            avg_dividend_yield = 0.075
            avg_annual_return = 0.12
        else:  # stocks
            data = self.get_asset_data('stocks')
            avg_dividend_yield = 0.062
            avg_annual_return = 0.13
        
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
        
        return {
            'final_balance': final_balance,
            'total_contributed': total_contributed,
            'earnings': earnings,
            'dividends': dividends_accumulated,
            'history': history,
            'monthly_rate': monthly_appreciation + monthly_dividends
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
    
    def calculate_time_to_goal(self, monthly_investment, monthly_rate, goal_amount):
        """Calcula o tempo necessário para atingir um objetivo"""
        if monthly_rate <= 0 or monthly_investment <= 0:
            # Se não há rendimento ou aporte, não é possível calcular
            return float('inf')
        
        # Fórmula para calcular o tempo necessário com juros compostos e aportes regulares
        # FV = PMT * (((1 + r)^n - 1) / r)
        # Onde:
        # FV = Valor futuro (goal_amount)
        # PMT = Pagamento periódico (monthly_investment)
        # r = Taxa de juros por período (monthly_rate)
        # n = Número de períodos (meses)
        
        # Isolando n na fórmula:
        # n = log(1 + (FV * r) / PMT) / log(1 + r)
        
        try:
            months_needed = np.log(1 + (goal_amount * monthly_rate) / monthly_investment) / np.log(1 + monthly_rate)
            return max(0, months_needed)
        except:
            return float('inf')
    
    def calculate_required_contribution(self, monthly_rate, goal_amount, months_available):
        """Calcula o aporte necessário para atingir o objetivo no tempo especificado"""
        if monthly_rate <= 0 or months_available <= 0:
            # Sem juros, apenas dividir o objetivo pelo número de meses
            return goal_amount / months_available
        
        # Fórmula para calcular o aporte necessário com juros compostos
        # FV = PMT * (((1 + r)^n - 1) / r)
        # Isolando PMT:
        # PMT = FV * (r / ((1 + r)^n - 1))
        
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

# Interface principal
def main():
    # Cabeçalho com logo
    st.markdown(f'''
    <div class="logo-header">
        <img src="{LOGO_URL}" class="logo-image">
        <div>
            <div class="secure-logo">Secure</div>
            <div class="invest-logo">Invest</div>
        </div>
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
        
        # Datas
        st.subheader("📅 Período de Investimento")
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                "Data Início",
                datetime.date.today(),
                min_value=datetime.date(2010, 1, 1)
            )
        with col2:
            end_date = st.date_input(
                "Data Final",
                datetime.date.today() + timedelta(days=365*5),
                min_value=datetime.date(2021, 1, 1)
            )
        
        # Valores de aporte
        st.subheader("💵 Valores de Aporte")
        monthly_investment = st.number_input("Aporte Mensal (R$)", min_value=0.0, value=1000.0, step=100.0)
        quarterly_investment = st.number_input("Aporte Trimestral (R$)", min_value=0.0, value=0.0, step=1000.0)
        annual_investment = st.number_input("Aporte Anual (R$)", min_value=0.0, value=0.0, step=5000.0)
        
        # Campo para objetivo financeiro
        st.subheader("🎯 Objetivo Financeiro")
        financial_goal = st.number_input("Valor do Objetivo (R$)", min_value=0.0, value=100000.0, step=1000.0)
        
        # Modalidades de investmento
        st.subheader("📈 Modalidades de Investimento")
        simulate_selic = st.checkbox("Tesouro Selic", value=True)
        simulate_cdb = st.checkbox("CDB 1% ao mês", value=True)
        simulate_fii = st.checkbox("Fundos Imobiliários", value=True)
        simulate_stocks = st.checkbox("Ações", value=True)
        
        # Seleção de ativos específicos
        selected_fiis = []
        if simulate_fii:
            with st.expander("Selecionar FIIs específicos"):
                # Pesquisa de FIIs em tempo real
                st.markdown("**🔍 Pesquisar FII**")
                fii_search = st.text_input("Digite o ticker do FII (ex: MXRF11)", key="fii_search", placeholder="MXRF11")
                
                if fii_search:
                    if st.button("Buscar FII", key="search_fii"):
                        with st.spinner("Buscando informações do FII..."):
                            asset_info = simulator.search_and_add_asset(fii_search.upper(), 'fii')
                            
                            if asset_info['success']:
                                st.success(f"FII encontrado: {asset_info['nome']}")
                                st.info(f"""
                                **Informações:**
                                - Dividend Yield: {asset_info['dividend_yield']*100:.2f}%
                                - Retorno Anual Esperado: {asset_info['annual_return']*100:.2f}%
                                - Segmento: {asset_info['segmento']}
                                - Preço Atual: R$ {asset_info['preco_atual']:.2f}
                                """)
                            else:
                                st.warning("FII não encontrado ou erro na busca")
                
                # FIIs disponíveis (pré-definidos + pesquisados)
                st.markdown("**📋 FIIs Disponíveis:**")
                all_fiis = simulator.get_asset_data('fii')
                
                for fii, data in all_fiis.items():
                    if st.checkbox(f"{fii} - {data['nome']}", 
                                  value=(fii in ['KNRI11', 'HGLG11']), 
                                  key=f"fii_{fii}"):
                        selected_fiis.append(fii)
        
        selected_stocks = []
        if simulate_stocks:
            with st.expander("Selecionar Ações específicas"):
                # Pesquisa de Ações em tempo real
                st.markdown("**🔍 Pesquisar Ação**")
                stock_search = st.text_input("Digite o ticker da ação (ex: PETR4)", key="stock_search", placeholder="PETR4")
                
                if stock_search:
                    if st.button("Buscar Ação", key="search_stock"):
                        with st.spinner("Buscando informações da ação..."):
                            asset_info = simulator.search_and_add_asset(stock_search.upper(), 'stocks')
                            
                            if asset_info['success']:
                                st.success(f"Ação encontrada: {asset_info['nome']}")
                                st.info(f"""
                                **Informações:**
                                - Dividend Yield: {asset_info['dividend_yield']*100:.2f}%
                                - Retorno Anual Esperado: {asset_info['annual_return']*100:.2f}%
                                - Setor: {asset_info['setor']}
                                - Preço Atual: R$ {asset_info['preco_atual']:.2f}
                                """)
                            else:
                                st.warning("Ação não encontrada ou erro na busca")
                
                # Ações disponíveis (pré-definidas + pesquisadas)
                st.markdown("**📋 Ações Disponíveis:**")
                all_stocks = simulator.get_asset_data('stocks')
                
                for stock, data in all_stocks.items():
                    if st.checkbox(f"{stock} - {data['nome']}", 
                                  value=(stock in ['ITSA4', 'BBAS3']), 
                                  key=f"stock_{stock}"):
                        selected_stocks.append(stock)
        
        # Botão de simulação
        simulate_button = st.button("🚀 Simular Investimentos", type="primary", use_container_width=True)
    
    # Conteúdo principal
    if simulate_button:
        # Cálculos
        results = {}
        monthly_rates = {}
        
        if simulate_selic:
            results['selic'] = simulator.calculate_fixed_income(
                monthly_investment, 'monthly', start_date, end_date, 'selic'
            )
            monthly_rates['selic'] = results['selic']['monthly_rate']
        
        if simulate_cdb:
            results['cdb'] = simulator.calculate_fixed_income(
                monthly_investment, 'monthly', start_date, end_date, 'cdb'
            )
            monthly_rates['cdb'] = results['cdb']['monthly_rate']
        
        if simulate_fii:
            results['fii'] = simulator.calculate_variable_income(
                monthly_investment, 'monthly', start_date, end_date, 'fii', selected_fiis
            )
            monthly_rates['fii'] = results['fii']['monthly_rate']
        
        if simulate_stocks:
            results['stocks'] = simulator.calculate_variable_income(
                monthly_investment, 'monthly', start_date, end_date, 'stocks', selected_stocks
            )
            monthly_rates['stocks'] = results['stocks']['monthly_rate']
        
        # Exibir resultados em abas
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Resumo", "📈 Gráficos", "🎯 Análise de Objetivo", "📋 Detalhes"])
        
        with tab1:
            st.header("📊 Resultados da Simulação")
            
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
                    else:
                        name = "Ações"
                        icon = "📊"
                    
                    st.markdown(f'<div class="metric-card">', unsafe_allow_html=True)
                    st.metric(
                        f"{icon} {name}",
                        f"R$ {result['final_balance']:,.2f}",
                        f"{((result['final_balance'] - result['total_contributed']) / result['total_contributed'] * 100):.2f}%"
                    )
                    st.markdown(f"**Total Aportado:** R$ {result['total_contributed']:,.2f}")
                    st.markdown(f"**Rendimento:** R$ {result['final_balance'] - result['total_contributed']:,.2f}")
                    st.markdown('</div>', unsafe_allow_html=True)
            
            # Comparativo entre modalidades
            st.subheader("📌 Comparativo entre Modalidades")
            
            fig_comparison = make_subplots(rows=1, cols=2, subplot_titles=('Rentabilidade Absoluta', 'Rentabilidade Percentual'))
            
            labels = {'selic': 'Tesouro Selic', 'cdb': 'CDB', 'fii': 'FIIs', 'stocks': 'Ações'}
            modalities = [labels[key] for key in results.keys()]
            final_balances = [results[key]['final_balance'] for key in results.keys()]
            earnings = [results[key]['final_balance'] - results[key]['total_contributed'] for key in results.keys()]
            
            # CORREÇÃO DO ERRO: Fechamento correto dos colchetes e parênteses
            earnings_percentages = [
                ((results[key]['final_balance'] - results[key]['total_contributed']) / 
                 results[key]['total_contributed'] * 100) if results[key]['total_contributed'] > 0 else 0 
                for key in results.keys()
            ]
            
            colors = ['#1E3A8A', '#3B82F6', '#10B981', '#EF4444']
            if st.session_state.theme == 'dark':
                colors = ['#3B82F6', '#60A5FA', '#10B981', '#EF4444']
            
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
        
        with tab2:
            st.header("📈 Evolução dos Investimentos")
            
            fig = go.Figure()
            
            colors = {'selic': '#1E3A8A', 'cdb': '#3B82F6', 'fii': '#10B981', 'stocks': '#EF4444'}
            if st.session_state.theme == 'dark':
                colors = {'selic': '#3B82F6', 'cdb': '#60A5FA', 'fii': '#10B981', 'stocks': '#EF4444'}
                
            labels = {'selic': 'Tesouro Selic', 'cdb': 'CDB', 'fii': 'FIIs', 'stocks': 'Ações'}
            
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
            
            labels = {'selic': 'Tesouro Selic', 'cdb': 'CDB', 'fii': 'FIIs', 'stocks': 'Ações'}
            
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
                
                detail_data.append({
                    'Modalidade': labels[key],
                    'Total Aportado': f"R$ {result['total_contributed']:,.2f}",
                    'Saldo Final': f"R$ {result['final_balance']:,.2f}",
                    'Rentabilidade': f"R$ {result['final_balance'] - result['total_contributed']:,.2f}",
                    'Rentabilidade %': f"{earnings_percentage:.2f}%",
                    'Atinge Objetivo': '✅' if result['final_balance'] >= financial_goal else '❌'
                })
            
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
    
    else:
        # Página inicial quando não há simulação
        st.info("💡 Configure os parâmetros de investimento na barra lateral e clique em 'Simular Investimentos' para ver os resultados.")
        
        col1, col2, col3 = st.columns(3)
        
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
        
        # Informações sobre o simulador
        with st.expander("ℹ️ Sobre o SecureInvest"):
            st.markdown("""
            **SecureInvest** é um simulador de investimentos que permite projetar rentabilidade de diferentes modalidades:
            
            - **Renda Fixa**: Simula investimentos em Tesouro Selic e CDBs
            - **Fundos Imobiliários**: Projeta rentabilidade baseada em dados históricos de FIIs
            - **Ações**: Calcula possíveis retornos do mercado acionário
            
            **Novo**: Agora com pesquisa em tempo real de ativos!
            - Busca automática de informações atualizadas
            - Dados de dividend yield e retornos em tempo real
            - Suporte a qualquer ativo listado na B3
            
            **Aviso importante**: Este simulador utiliza projeções baseadas em dados históricos e não garante resultados futuros.
            Todas as simulações são meramente ilustrativas.
            """)

if __name__ == "__main__":
    main()