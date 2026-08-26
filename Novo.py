# -*- coding: utf-8 -*-
"""
Spare Parts Inventory Sizing System - Grupo RANDOM
Simulação de Janela de Vulnerabilidade com Manufatura Aditiva
"""

import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson, norm
import base64
from pathlib import Path
from PIL import Image

st.set_page_config(page_title="Dimensionamento de Sobressalentes - RANDOM", layout="wide")

def image_to_base64(path):
    try:
        image_path = Path(path)
        if not image_path.exists():
            return ""
        return base64.b64encode(image_path.read_bytes()).decode("utf-8")
    except Exception:
        return ""

LOGIN_BG_BASE64 = image_to_base64("capa.png")
LOGIN_BG_URL = f"data:image/png;base64,{LOGIN_BG_BASE64}" if LOGIN_BG_BASE64 else ""
LOGO_BASE64 = image_to_base64("logo.png")
LOGO_HTML = f'<img src="data:image/png;base64,{LOGO_BASE64}" class="login-logo">' if LOGO_BASE64 else ''

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown(
        f"""
        <style>
        html, body, [data-testid="stAppViewContainer"], .stApp {{ height: 100%; overflow: hidden; background: #f4f5f7; }}
        [data-testid="stSidebar"], [data-testid="stToolbar"], [data-testid="stDecoration"], [data-testid="stHeader"] {{ display: none !important; }}
        .login-bg-full {{
            position: fixed; inset: 0;
            background-image: linear-gradient(135deg, rgba(255,255,255,0.92) 0%, rgba(240,242,245,0.98) 100%), url("{LOGIN_BG_URL}");
            background-size: cover; background-position: center; z-index: 0;
        }}
        .login-page-content {{ position: relative; z-index: 5; padding: 8vh 38px; display: flex; justify-content: center; }}
        .login-title-box {{ text-align: center; margin-bottom: 20px; }}
        .login-logo {{ max-height: 150px; margin-bottom: 15px; }}
        .login-title-box h2 {{ color: #388E3C; font-family: 'Roboto', sans-serif; font-weight: 700; margin: 0; }}
        div[data-testid="stForm"] {{ background: #fff; padding: 2.5rem; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); }}
        .stFormSubmitButton > button {{ background: #388E3C; color: white; width: 100%; text-transform: uppercase; font-weight: 600; }}
        </style>
        <div class="login-bg-full"></div>
        """, unsafe_allow_html=True
    )
    st.markdown('<div class="login-page-content">', unsafe_allow_html=True)
    _, col_login, _ = st.columns([1, 1.2, 1])
    with col_login:
        st.markdown(f'<div class="login-title-box">{LOGO_HTML}<h2>Acesso ao Sistema</h2><p>RANDOM - Grupo de Pesquisa</p></div>', unsafe_allow_html=True)
        with st.form("login_form"):
            usr = st.text_input("Utilizador")
            pwd = st.text_input("Palavra-passe", type="password")
            if st.form_submit_button("Entrar") and usr.strip().lower() == "vicenzo" and pwd == "12345":
                st.session_state.authenticated = True
                st.rerun()
            elif st.form_submit_button("Entrar"):
                st.error("Credenciais inválidas.")
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

st.markdown("""<style> h1, h2, h3 { color: #388E3C !important; } .stButton>button { background: #388E3C; color: #fff; font-weight: bold; } </style>""", unsafe_allow_html=True)

# =====================================================================
# CÁLCULOS E SIMULAÇÃO
# =====================================================================

def calcular_poisson(lmbda, n, t, risco_alvo):
    m = lmbda * n * t
    x = 0
    prob_acumulada = 0
    x_ideal = -1
    lista_x, lista_p, lista_margem, lista_risco = [], [], [], []
    while True:
        p_x = poisson.pmf(x, m)
        prob_acumulada += p_x
        risco_atual = max(1 - prob_acumulada, 0.0)
        lista_x.append(x)
        lista_p.append(p_x)
        lista_margem.append(prob_acumulada)
        lista_risco.append(risco_atual)
        if risco_atual < risco_alvo and x_ideal == -1:
            x_ideal = x
        if x_ideal != -1 and x >= x_ideal + 1:
            break
        x += 1
    df = pd.DataFrame({'x': lista_x, 'P(X=x)': lista_p, 'Margem Seg.': lista_margem, 'Risco': lista_risco})
    return df, x_ideal, m

def simular_politica_dual(s_star, s, S, params):
    Horizonte_T = params['Horizonte_T']
    N = params['N']
    L_rep = params['L_rep']
    L_ef = params['L_ef']
    MTBF_conv = params['MTBF_conv']
    MTBF_print = params['MTBF_print']
    C1 = params['C1']
    C2 = params['C2']
    K = params['K']
    Ch_hora = params['Ch_hora']
    Cb = params['Cb']

    def gerar_tempo_falha(peca_uso, maquinas_paradas):
        ativas = N - maquinas_paradas
        if ativas <= 0:
            return float('inf')
        if peca_uso == 'Impressa':
            taxa = (max(0, ativas - 1) / MTBF_conv) + (1.0 / MTBF_print)
        else:
            taxa = ativas / MTBF_conv
        return max(1, int(np.random.exponential(1.0 / taxa)))

    It, Bt, Ot, Pt, Jt = S, 0, 0, 0, 0
    Peca_Em_Uso = 'Original'
    Custo_Total = 0
    Custo_Sem_3D = 0
    Horas_Indisponivel = 0
    Horas_Indisponivel_Sem_3D = 0
    Pecas_Impressas_Total = 0

    Tempo_Proxima_Falha = gerar_tempo_falha(Peca_Em_Uso, Bt)
    Tempo_Chegada_Convencional = float('inf')
    Tempo_Chegada_Impressao = float('inf')

    for t in range(1, Horizonte_T + 1):
        # Chegada da peça 3D
        if t == Tempo_Chegada_Impressao:
            Pt = 1
            Jt = 0
            Tempo_Chegada_Impressao = float('inf')
            if Bt > 0:
                Bt -= 1
                Peca_Em_Uso = 'Impressa'
                Tempo_Proxima_Falha = t + gerar_tempo_falha(Peca_Em_Uso, Bt)

        # Chegada do pedido regular
        if t == Tempo_Chegada_Convencional:
            It += Ot
            Ot = 0
            Tempo_Chegada_Convencional = float('inf')
            while Bt > 0 and It > 0:
                Bt -= 1
                It -= 1
                Peca_Em_Uso = 'Original'
                Tempo_Proxima_Falha = t + gerar_tempo_falha(Peca_Em_Uso, Bt)
            if Peca_Em_Uso == 'Impressa' and It > 0:
                It -= 1
                Peca_Em_Uso = 'Original'
                Pt = 0
                Tempo_Proxima_Falha = t + gerar_tempo_falha(Peca_Em_Uso, Bt)

        # Falha da máquina
        if t == Tempo_Proxima_Falha:
            if Peca_Em_Uso == 'Impressa':
                Pt = 0
            if It > 0:
                It -= 1
                Peca_Em_Uso = 'Original'
            elif Pt == 1:
                Peca_Em_Uso = 'Impressa'
            else:
                Bt += 1
                Peca_Em_Uso = 'Nenhuma' if Bt == N else 'Original'
            Tempo_Proxima_Falha = t + gerar_tempo_falha(Peca_Em_Uso, Bt)

        # Posicao Gerencial (IP)
        IPt = It + Ot + Pt - Bt

        # Disparo de Impressão 3D durante a Janela de Vulnerabilidade
        if IPt <= s_star and Jt == 0 and Pt == 0:
            Jt = 1
            Tempo_Chegada_Impressao = t + L_ef
            Custo_Total += C2
            Pecas_Impressas_Total += 1

        # Disparo do Pedido Regular
        if IPt <= s and Ot == 0:
            Q = S - IPt
            Ot = Q
            Tempo_Chegada_Convencional = t + L_rep
            Custo_Total += K + (Q * C1)

        # Custos acumulados com e sem cobertura 3D
        Custo_Total += (It * Ch_hora) + (Bt * Cb)
        if Bt > 0:
            Horas_Indisponivel += 1
            
        # Estimativa de custo cego (Sem nenhuma impressão 3D na vulnerabilidade)
        if It == 0 and Ot > 0 and Bt > 0:
            Custo_Sem_3D += Cb
            Horas_Indisponivel_Sem_3D += 1

    disponibilidade = 1.0 - (Horas_Indisponivel / Horizonte_T)
    economia_gerada = Custo_Sem_3D - (Pecas_Impressas_Total * C2)
    return Custo_Total, disponibilidade, Pecas_Impressas_Total, economia_gerada

def otimizar_gatilhos_grid(S, params):
    melhor_custo = float('inf')
    melhor_s, melhor_s_star = 0, 0
    melhor_disp, melhor_impressas, melhor_economia = 0.0, 0.0, 0.0
    limite_s = max(1, S)

    for s in range(0, limite_s):
        for s_star in range(0, s + 1):
            c_p, d_p, p_p, e_p = [], [], [], []
            for _ in range(3):
                c, d, p, e = simular_politica_dual(s_star, s, S, params)
                c_p.append(c); d_p.append(d); p_p.append(p); e_p.append(e)
            
            c_m, d_m, p_m, e_m = np.mean(c_p), np.mean(d_p), np.mean(p_p), np.mean(e_p)
            if c_m < melhor_custo:
                melhor_custo, melhor_s, melhor_s_star = c_m, s, s_star
                melhor_disp, melhor_impressas, melhor_economia = d_m, p_m, e_m

    return melhor_s_star, melhor_s, melhor_custo, melhor_disp, melhor_impressas, melhor_economia

# =====================================================================
# INTERFACE
# =====================================================================

col1, col2, col3 = st.columns([1,2,1])
if Path('logo.png').exists():
    col2.image('logo.png', use_container_width=True)

st.markdown("<h2 style='text-align: center;'>Spare Parts Inventory System - Grupo RANDOM</h2>", unsafe_allow_html=True)
menu = ["Módulo Analítico", "Otimizador Padrão", "Otimizador MA (Janela de Vulnerabilidade)"]
choice = st.sidebar.selectbox("Selecione o Motor", menu)

if choice == menu[2]:
    st.header("Análise da Janela de Vulnerabilidade (Dual-Sourcing)")
    
    with st.expander("Configuração da Operação", expanded=True):
        c1, c2 = st.columns(2)
        MTBF_conv = c1.number_input("MTBF Peça Original (h)", value=5000)
        MTBF_print = c2.number_input("MTBF Peça Impressa (h)", value=2500)
        
        c3, c4 = st.columns(2)
        L_rep = c3.number_input("Lead Time Fornecedor Regular (h)", value=1500)
        L_ef = c4.number_input("Lead Time Impressão 3D (h)", value=8)
        
        c5, c6, c7 = st.columns(3)
        C1 = c5.number_input("Custo Peça Original (R$)", value=300.0)
        C2 = c6.number_input("Custo Impressão 3D (R$)", value=50.0)
        K = c7.number_input("Custo Fixo de Pedido Regular (R$)", value=200.0)
        
        c8, c9 = st.columns(2)
        Cb = c8.number_input("Custo de Downtime (R$/h)", value=3000.0)
        Ch_ano = c9.number_input("Custo de Posse Anual (R$/un)", value=50.0)
        
        c10, c11 = st.columns(2)
        R_PCT = c10.number_input("Risco Alvo (%)", value=5.0)
        Anos = c11.number_input("Horizonte (Anos)", value=5)

    if st.button("Simular e Avaliar Vulnerabilidade", use_container_width=True):
        params = {
            'Horizonte_T': int(Anos * 8760), 'N': 10, 'L_rep': L_rep, 'L_ef': L_ef,
            'MTBF_conv': MTBF_conv, 'MTBF_print': MTBF_print, 'C1': C1, 'C2': C2,
            'K': K, 'Ch_hora': Ch_ano / 8760.0, 'Cb': Cb
        }
        _, S_teto, _ = calcular_poisson(1.0/MTBF_conv, 10, L_rep, R_PCT/100.0)
        S_teto = max(1, S_teto)

        s_star, s, custo, disp, pecas, economia = otimizar_gatilhos_grid(S_teto, params)

        st.subheader("Resultados do Dimensionamento")
        m1, m2, m3 = st.columns(3)
        m1.metric("Gatilho Impressão (s*)", s_star)
        m2.metric("Ponto Pedido Regular (s)", s)
        m3.metric("Teto de Estoque (S)", S_teto)

        st.divider()
        k1, k2, k3 = st.columns(3)
        k1.metric("Peças Impressas no Período", f"{pecas:.1f} un")
        k2.metric("Disponibilidade da Linha", f"{disp*100:.2f}%")
        k3.metric("Economia vs Sem Impressão", f"R$ {economia:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
