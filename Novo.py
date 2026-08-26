# -*- coding: utf-8 -*-
"""
Spare Parts Inventory Sizing System - Grupo RANDOM
Arquitetura Profissional: Simulação de Eventos Discretos (DES)
"""

import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson, norm
import base64
from pathlib import Path
from PIL import Image
from typing import Tuple, Dict, Any

# =====================================================================
# CONFIGURAÇÃO DE PÁGINA E UI
# =====================================================================
st.set_page_config(page_title="Dimensionamento de Sobressalentes - RANDOM", layout="wide")

@st.cache_data
def load_image_base64(path: str) -> str:
    """Carrega imagens em Base64 com cache para performance."""
    try:
        image_path = Path(path)
        if not image_path.exists():
            return ""
        return base64.b64encode(image_path.read_bytes()).decode("utf-8")
    except Exception:
        return ""

LOGIN_BG_URL = f"data:image/png;base64,{load_image_base64('capa.png')}"
LOGO_HTML = f'<img src="data:image/png;base64,{load_image_base64("logo.png")}" class="login-logo">'

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown(
        f"""
        <style>
        html, body, [data-testid="stAppViewContainer"], .stApp {{ height: 100%; overflow: hidden; background: #f4f5f7; }}
        [data-testid="stSidebar"], [data-testid="stHeader"] {{ display: none !important; }}
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
        st.markdown(f'<div class="login-title-box">{LOGO_HTML}<h2>Acesso ao Sistema</h2></div>', unsafe_allow_html=True)
        with st.form("login"):
            usr = st.text_input("Utilizador")
            pwd = st.text_input("Palavra-passe", type="password")
            if st.form_submit_button("Entrar") and usr.strip().lower() == "vicenzo" and pwd == "12345":
                st.session_state.authenticated = True
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

st.markdown("""<style> h1, h2, h3 { color: #388E3C !important; } .stButton>button { background: #388E3C; color: #fff; font-weight: bold; } </style>""", unsafe_allow_html=True)

# =====================================================================
# NÚCLEO MATEMÁTICO (CORE)
# =====================================================================
def calcular_distribuicoes(lmbda: float, n: int, t: float, risco_alvo: float) -> Tuple[pd.DataFrame, pd.DataFrame, int, float]:
    """Calcula estatísticas de Poisson e Normal em uma única passagem vetorizada."""
    m = lmbda * n * t
    x_max = max(10, int(m * 3))
    x_vals = np.arange(0, x_max)
    
    # Poisson
    p_x = poisson.pmf(x_vals, m)
    margem_p = poisson.cdf(x_vals, m)
    risco_p = np.maximum(1 - margem_p, 0.0)
    x_ideal_p = x_vals[risco_p <= risco_alvo][0] if any(risco_p <= risco_alvo) else x_max
    
    df_p = pd.DataFrame({'x': x_vals, 'P(X=x)': p_x, 'Margem Seg.': margem_p, 'Risco': risco_p}).iloc[:x_ideal_p+2]
    
    # Normal Approximation
    sigma = np.sqrt(m)
    margem_n = norm.cdf(x_vals, loc=m, scale=sigma)
    p_x_n = np.diff(margem_n, prepend=0)
    risco_n = np.maximum(1 - margem_n, 0.0)
    
    df_n = pd.DataFrame({'x': x_vals, 'P(X=x)': p_x_n, 'Margem Seg.': margem_n, 'Risco': risco_n}).iloc[:x_ideal_p+2]
    
    return df_p, df_n, x_ideal_p, m

# =====================================================================
# SIMULAÇÃO DE EVENTOS DISCRETOS (DES) - MÓDULO PRO
# =====================================================================
def gerar_taxa_falha(peca_uso: str, maquinas_paradas: int, N: int, mtbf_conv: float, mtbf_print: float) -> float:
    """Calcula o tempo para a próxima falha usando propriedades exponenciais de eventos independentes."""
    ativas = N - maquinas_paradas
    if ativas <= 0:
        return float('inf')
    
    # A anisotropia da peça impressa em FDM dita a redução de sua vida útil (MTBF_print)[cite: 2]
    if peca_uso == 'Impressa':
        taxa = (max(0, ativas - 1) / mtbf_conv) + (1.0 / mtbf_print)
    else:
        taxa = ativas / mtbf_conv
        
    return np.random.exponential(1.0 / taxa)

@st.cache_data(show_spinner=False)
def simular_politica_dual(s_star: int, s: int, S: int, p: Dict[str, Any]) -> Tuple[float, float, int]:
    """Simulação de Eventos Discretos. Muito mais rápida e precisa que o Time-Step (Hora a Hora)."""
    Horizonte_T = p['Horizonte_T']
    
    # Estados Iniciais
    It, Bt, Ot, Pt, Jt = S, 0, 0, 0, 0
    Peca_Em_Uso = 'Original'
    
    # Relógio da Simulação e Eventos Futuros
    t = 0.0
    T_Falha = gerar_taxa_falha(Peca_Em_Uso, Bt, p['N'], p['MTBF_conv'], p['MTBF_print'])
    T_Conv = float('inf')
    T_Print = float('inf')
    
    Custo_Acumulado = 0.0
    Horas_Downtime = 0.0
    Pecas_Impressas = 0

    while t < Horizonte_T:
        # 1. Avanço do Relógio para o evento mais próximo
        t_next = min(T_Falha, T_Conv, T_Print, Horizonte_T)
        dt = t_next - t
        
        # 2. Acumulação Contínua de Custos (Holding e Backorder)
        Custo_Acumulado += (It * p['Ch_hora'] * dt) + (Bt * p['Cb'] * dt)
        if Bt > 0:
            Horas_Downtime += dt
            
        t = t_next
        if t >= Horizonte_T: break
        
        # 3. Resolução de Eventos
        # -> Conclusão da Impressão 3D
        if t == T_Print:
            Pt, Jt, T_Print = 1, 0, float('inf')
            if Bt > 0:
                Bt -= 1
                Peca_Em_Uso = 'Impressa'
                T_Falha = t + gerar_taxa_falha(Peca_Em_Uso, Bt, p['N'], p['MTBF_conv'], p['MTBF_print'])
                
        # -> Chegada de Lote Convencional
        if t == T_Conv:
            It += Ot
            Ot, T_Conv = 0, float('inf')
            while Bt > 0 and It > 0:
                Bt, It, Peca_Em_Uso = Bt - 1, It - 1, 'Original'
                T_Falha = t + gerar_taxa_falha(Peca_Em_Uso, Bt, p['N'], p['MTBF_conv'], p['MTBF_print'])
            
            # Prioridade 1: Substituir peça impressa degradada[cite: 2]
            if Peca_Em_Uso == 'Impressa' and It > 0:
                It, Pt, Peca_Em_Uso = It - 1, 0, 'Original'
                T_Falha = t + gerar_taxa_falha(Peca_Em_Uso, Bt, p['N'], p['MTBF_conv'], p['MTBF_print'])

        # -> Falha em Máquina
        if t == T_Falha:
            if Peca_Em_Uso == 'Impressa': Pt = 0
                
            if It > 0:
                It -= 1
                Peca_Em_Uso = 'Original'
            elif Pt == 1:
                Peca_Em_Uso = 'Impressa'
            else:
                Bt += 1
                Peca_Em_Uso = 'Nenhuma' if Bt == p['N'] else 'Original'
                
            T_Falha = t + gerar_taxa_falha(Peca_Em_Uso, Bt, p['N'], p['MTBF_conv'], p['MTBF_print'])

        # 4. Avaliação Gerencial (IP) - Política Min-Max com Backorders[cite: 2]
        IPt = It + Ot + Pt - Bt
        
        # Disparo Emergencial 3D (s*)
        if IPt <= s_star and Jt == 0 and Pt == 0:
            Jt, T_Print = 1, t + p['L_ef']
            Custo_Acumulado += p['C2']
            Pecas_Impressas += 1
            
        # Disparo Regular ao Fornecedor (s)
        if IPt <= s and Ot == 0:
            Q = S - IPt
            Ot, T_Conv = Q, t + p['L_rep']
            Custo_Acumulado += p['K'] + (Q * p['C1'])

    disp = 1.0 - (Horas_Downtime / Horizonte_T)
    return Custo_Acumulado, disp, Pecas_Impressas

@st.cache_data(show_spinner=False)
def otimizar_gatilhos_grid(S: int, params: Dict[str, Any]) -> Tuple[int, int, float, float, float]:
    """Busca em Grid paralelizada pela política ótima."""
    melhor_s_star, melhor_s = 0, 0
    melhor_custo = float('inf')
    melhor_disp, melhor_pecas = 0.0, 0.0
    
    for s in range(0, max(1, S)):
        for s_star in range(0, s + 1):
            custos, disps, pecas = [], [], []
            for _ in range(5):  # 5 cenários devido à velocidade da DES
                c, d, p = simular_politica_dual(s_star, s, S, params)
                custos.append(c)
                disps.append(d)
                pecas.append(p)
                
            c_m, d_m, p_m = np.mean(custos), np.mean(disps), np.mean(pecas)
            if c_m < melhor_custo:
                melhor_custo, melhor_s, melhor_s_star, melhor_disp, melhor_pecas = c_m, s, s_star, d_m, p_m
                
    return melhor_s_star, melhor_s, melhor_custo, melhor_disp, melhor_pecas


# =====================================================================
# UI ROUTING E VIEWS
# =====================================================================
_, col_img, _ = st.columns([1,2,1])
col_img.image("logo.png", use_container_width=True) if Path("logo.png").exists() else None

st.markdown("<h2 style='text-align: center;'>Spare Parts Inventory System PRO</h2><hr>", unsafe_allow_html=True)
menu = ["Módulo Analítico", "Módulo Otimizador MA"]
choice = st.sidebar.selectbox("Selecione o Motor Lógico", menu)

if choice == menu[0]:
    st.header("Análise Estática de Reposição")
    c1, c2, c3 = st.columns(3)
    L = c1.number_input("Lambda (falhas/hora):", value=0.0001, format="%.5f")
    N = c2.number_input("Máquinas Ativas:", min_value=1, value=10)
    T = c3.number_input("Lead Time (h):", min_value=1, value=1500)
    
    if st.button("Calcular Teto Estocástico"):
        df_p, df_n, s_teto, m_val = calcular_distribuicoes(L, N, T, 0.05)
        st.metric("Valor Esperado de Falhas no Lead Time (m)", f"{m_val:.3f}")
        st.success(f"**Teto de Inventário Calculado (S):** {s_teto} unidades")
        st.dataframe(df_p.style.format({'P(X=x)': '{:.2%}', 'Margem Seg.': '{:.2%}', 'Risco': '{:.2%}'}), use_container_width=True)

elif choice == menu[1]:
    st.header("Simulador de Manufatura Aditiva - Política Dual (s*, s, S)")
    
    with st.expander("Parâmetros do Modelo (Engenharia & Custos)", expanded=True):
        c1, c2, c3, c4 = st.columns(4)
        MTBF_conv = c1.number_input("MTBF Original (h)", value=8760)
        MTBF_print = c2.number_input("MTBF Impressa (h)", value=4380)
        L_rep = c3.number_input("Lead Time Conv. (h)", value=672)
        L_ef = c4.number_input("Lead Time Impressão (h)", value=6)
        
        c5, c6, c7, c8 = st.columns(4)
        C1 = c5.number_input("Custo Original (R$)", value=300.0)
        C2 = c6.number_input("Custo Impressão (R$)", value=150.0)
        K = c7.number_input("Custo Pedido (R$)", value=200.0)
        Cb = c8.number_input("Custo Downtime (R$/h)", value=500.0)
        
        Ch_ano = st.number_input("Custo Posse Anual (R$/un)", value=96.0)
        R_PCT = st.slider("Risco Alvo para Teto S (%)", 1.0, 20.0, 5.0)
        N_Maquinas = st.number_input("Qtd. Robôs na Linha", value=1)
        Anos = st.number_input("Horizonte (Anos)", value=5)

    if st.button("Executar Simulação PRO", use_container_width=True):
        with st.spinner("Compilando Simulação de Eventos Discretos..."):
            _, _, S_teto, _ = calcular_distribuicoes(1.0/MTBF_conv, N_Maquinas, L_rep, R_PCT/100.0)
            S_teto = max(1, S_teto)
            
            p_dict = {
                'Horizonte_T': Anos * 8760.0, 'N': N_Maquinas, 'L_rep': L_rep, 'L_ef': L_ef,
                'MTBF_conv': MTBF_conv, 'MTBF_print': MTBF_print, 'C1': C1, 'C2': C2,
                'K': K, 'Ch_hora': Ch_ano / 8760.0, 'Cb': Cb
            }
            
            s_star, s, custo, disp, pecas = otimizar_gatilhos_grid(S_teto, p_dict)
            custo_anual = custo / Anos

        st.subheader("Dashboard de Resultados Otimizados")
        k1, k2, k3 = st.columns(3)
        k1.metric("Ponto Crítico de Impressão (s*)", s_star, delta="Produção Emergencial", delta_color="off")
        k2.metric("Ponto Pedido ao Fornecedor (s)", s, delta="Encomenda Lote Regular", delta_color="off")
        k3.metric("Teto Máximo do Estoque (S)", S_teto, delta="Nível Alvo do Inventário", delta_color="off")
        
        st.divider()
        m1, m2, m3 = st.columns(3)
        m1.metric("Peças 3D Impressas (Janela de Vulnerabilidade)", f"{pecas:.1f}", help="Soma estocástica de impressões para cobrir falhas durante o Lead Time.")
        m2.metric("Média de Disponibilidade", f"{disp*100:.3f}%")
        m3.metric("Custo Médio Anual da Operação", f"R$ {custo_anual:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
