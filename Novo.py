# -*- coding: utf-8 -*-
"""
Spare Parts Inventory Sizing System - Grupo RANDOM
"""

import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson, norm
import base64
from pathlib import Path
from PIL import Image

# Configuração inicial da página
st.set_page_config(page_title="Dimensionamento de Sobressalentes - RANDOM", layout="wide")

def image_to_base64(path):
    """Função para converter imagens em Base64 e renderizá-las no HTML/CSS"""
    try:
        image_path = Path(path)
        if not image_path.exists():
            return ""
        return base64.b64encode(image_path.read_bytes()).decode("utf-8")
    except Exception:
        return ""

# Carrega as imagens para a tela de login (capa de fundo e logo)
LOGIN_BG_BASE64 = image_to_base64("capa.png")
LOGIN_BG_URL = f"data:image/png;base64,{LOGIN_BG_BASE64}" if LOGIN_BG_BASE64 else ""

LOGO_BASE64 = image_to_base64("logo.png")
LOGO_HTML = f'<img src="data:image/png;base64,{LOGO_BASE64}" class="login-logo">' if LOGO_BASE64 else ''

# Inicializa o estado de autenticação
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# TELA DE LOGIN 
if not st.session_state.authenticated:
    st.markdown(
        f"""
        <style>
        /* Oculta menus padrão do Streamlit no ecrã de login */
        html, body, [data-testid="stAppViewContainer"], .stApp {{
            height: 100%;
            overflow: hidden !important;
            background: #f4f5f7 !important;
        }}
        [data-testid="stSidebar"], [data-testid="stToolbar"], [data-testid="stDecoration"], [data-testid="stHeader"] {{
            display: none !important;
        }}
        .main, .stApp {{ background: transparent !important; }}
        .block-container {{ max-width: 100% !important; padding: 0 !important; margin: 0 !important; }}

        .login-bg-full {{
            position: fixed;
            inset: 0;
            background-image:
                linear-gradient(135deg, rgba(255,255,255,0.92) 0%, rgba(240,242,245,0.98) 100%),
                url("{LOGIN_BG_URL}");
            background-size: cover;
            background-position: center center;
            background-repeat: no-repeat;
            background-color: #f4f5f7;
            z-index: 0;
        }}

        .login-page-content {{
            position: relative;
            z-index: 5;
            padding: 8vh 38px 18px 38px;
            display: flex;
            justify-content: center;
        }}

        .login-title-box {{
            margin-top: 5px;
            margin-bottom: 20px;
            text-align: center;
        }}
        
        .login-logo {{
            max-height: 150px;
            width: auto;
            margin-bottom: 15px;
        }}

        .login-title-box h2 {{
            margin: 0;
            font-size: 1.8rem;
            font-weight: 700;
            letter-spacing: -0.02em;
            color: #388E3C;
            font-family: 'Roboto', sans-serif;
        }}
        
        .login-title-box p {{
            color: #666666;
            font-size: 0.95rem;
            margin-top: 5px;
        }}

        div[data-testid="stForm"] {{
            background: #ffffff !important;
            border-radius: 8px !important;
            border: 1px solid #e0e0e0 !important;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08) !important;
            padding: 2.5rem 2rem 2rem 2rem !important;
        }}
        div[data-testid="stForm"] > div {{ background: transparent !important; border: 0 !important; box-shadow: none !important; }}
        div[data-testid="stForm"] label {{ color: #333333 !important; font-weight: 600 !important; font-size: 0.90rem !important; }}
        div[data-testid="stForm"] input {{
            background: #fafafa !important;
            color: #333333 !important;
            border: 1px solid #cccccc !important;
            border-radius: 4px !important;
            min-height: 2.8rem !important;
            font-size: 0.95rem !important;
            transition: all 0.2s ease-in-out;
        }}
        div[data-testid="stForm"] input:focus {{ border-color: #388E3C !important; box-shadow: 0 0 0 1px #388E3C !important; }}

        .stFormSubmitButton > button {{
            width: 100% !important;
            min-height: 2.8rem !important;
            border-radius: 4px !important;
            background: #388E3C !important;
            color: #ffffff !important;
            border: 0 !important;
            font-size: 0.95rem !important;
            font-weight: 600 !important;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            box-shadow: 0 2px 5px rgba(56, 142, 60, 0.3) !important;
            transition: background 0.2s;
        }}
        .stFormSubmitButton > button:hover {{
            background: #2E7D32 !important;
            color: #ffffff !important;
            box-shadow: 0 4px 8px rgba(56, 142, 60, 0.4) !important;
        }}

        div[data-testid="stAlert"] {{ border-radius: 4px !important; margin-top: 0.75rem !important; }}
        @media (max-width: 980px) {{ .login-page-content {{ padding: 4vh 18px; }} }}
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown('<div class="login-bg-full"></div>', unsafe_allow_html=True)
    st.markdown('<div class="login-page-content">', unsafe_allow_html=True)

    col_vazia1, col_login, col_vazia2 = st.columns([1, 1.2, 1])

    with col_login:
        st.markdown(
            f"""
            <div class="login-title-box">
                {LOGO_HTML}
                <h2>Acesso ao Sistema</h2>
                <p>RANDOM - Grupo de Pesquisa</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("Utilizador", placeholder="Digite o seu utilizador")
            password = st.text_input("Palavra-passe", type="password", placeholder="Digite a sua palavra-passe")
            submitted = st.form_submit_button("Entrar", use_container_width=True)

        if submitted:
            if username.strip().lower() == "vicenzo" and password == "12345":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Utilizador ou palavra-passe incorretos.")

    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()  


# CSS DA TELA PRINCIPAL
st.markdown("""
    <style>
    .stApp { background-color: #fdfdfd; }
    h1, h2, h3 { color: #388E3C !important; font-family: 'Roboto', sans-serif !important; }
    [data-testid="stSidebar"] { background-color: #ffffff !important; border-right: 1px solid #e0e0e0; }
    
    .stButton > button {
        background-color: #388E3C !important;
        color: white !important;
        border-radius: 4px !important;
        border: none !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
        font-weight: 600 !important;
        transition: 0.2s;
    }
    .stButton > button:hover {
        background-color: #2E7D32 !important;
        color: white !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.15) !important;
    }
    
    [data-testid="stMetricValue"] { color: #333333 !important; }
    [data-testid="stMetricLabel"] { color: #666666 !important; font-weight: 600 !important; }
    hr { border-color: #eeeeee !important; }
    </style>
""", unsafe_allow_html=True)


# =====================================================================
# FUNÇÕES AUXILIARES E DE SIMULAÇÃO (CORE)
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

def calcular_normal(lmbda, n, t, risco_alvo):
    m = lmbda * n * t
    sigma = np.sqrt(m)
    x = 0
    x_ideal = -1
    lista_x, lista_p, lista_margem, lista_risco = [], [], [], []
    
    while True:
        prob_acum = norm.cdf(x, loc=m, scale=sigma)
        p_x = prob_acum if x == 0 else prob_acum - norm.cdf(x - 1, loc=m, scale=sigma)
        risco_atual = max(1 - prob_acum, 0.0)
        
        lista_x.append(x)
        lista_p.append(p_x)
        lista_margem.append(prob_acum)
        lista_risco.append(risco_atual)
        
        if risco_atual < risco_alvo and x_ideal == -1:
            x_ideal = x
            
        if x_ideal != -1 and x >= x_ideal + 1:
            break
        x += 1
        
    df = pd.DataFrame({'x': lista_x, 'P(X=x)': lista_p, 'Margem Seg.': lista_margem, 'Risco': lista_risco})
    return df, x_ideal, sigma

def exibir_resumo_streamlit(df, x_alvo, titulo, texto_destaque="Quantidade Recomendada", mostrar_contexto=True):
    st.subheader(titulo)
    if mostrar_contexto:
        idx_inicio = max(0, x_alvo - 1)
        resumo = df.iloc[idx_inicio : x_alvo + 2].copy()
    else:
        resumo = df[df['x'] == x_alvo].copy()
    
    resumo['P(X=x)'] = resumo['P(X=x)'].apply(lambda v: f"{v:.4%}")
    resumo['Margem Seg.'] = resumo['Margem Seg.'].apply(lambda v: f"{v:.4%}")
    resumo['Risco'] = resumo['Risco'].apply(lambda v: f"{v:.4%}")
    
    st.success(f"**{texto_destaque}:** {x_alvo} peças")
    st.dataframe(resumo, use_container_width=True, hide_index=True)


# --- FUNÇÃO SIMULAÇÃO DUAL (s*, s, S) COM RASTREAMENTO DE PEÇAS 3D ---

def simular_politica_dual(s_star, s, S, params):
    """Executa a simulação horária (Time-Step) registrando peças impressas na vulnerabilidade."""
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

    def gerar_tempo_falha_sistema(peca_uso, maquinas_paradas):
        ativas = N - maquinas_paradas
        if ativas <= 0:
            return float('inf')
        
        if peca_uso == 'Impressa':
            ativas_originais = max(0, ativas - 1)
            taxa_total = (ativas_originais / MTBF_conv) + (1.0 / MTBF_print)
        else:
            taxa_total = ativas / MTBF_conv
            
        mtbf_equivalente = 1.0 / taxa_total
        return max(1, int(np.random.exponential(mtbf_equivalente)))

    # Inicialização de Estados
    It = S
    Bt = 0
    Ot = 0
    Pt = 0
    Jt = 0
    Peca_Em_Uso = 'Original'
    Custo_Total = 0
    Horas_Indisponivel = 0
    Pecas_Impressas_Total = 0  # <--- Rastreia peças 3D impressas

    Tempo_Proxima_Falha = gerar_tempo_falha_sistema(Peca_Em_Uso, Bt)
    Tempo_Chegada_Convencional = float('inf')
    Tempo_Chegada_Impressao = float('inf')

    for t in range(1, Horizonte_T + 1):
        
        # 1. Evento: Conclusão da Impressão 3D
        if t == Tempo_Chegada_Impressao:
            Pt = 1
            Jt = 0
            Tempo_Chegada_Impressao = float('inf')
            
            if Bt > 0:
                Bt -= 1
                Peca_Em_Uso = 'Impressa'
                Tempo_Proxima_Falha = t + gerar_tempo_falha_sistema(Peca_Em_Uso, Bt)

        # 2. Evento: Chegada do Pedido Convencional
        if t == Tempo_Chegada_Convencional:
            It += Ot
            Ot = 0
            Tempo_Chegada_Convencional = float('inf')
            
            while Bt > 0 and It > 0:
                Bt -= 1
                It -= 1
                Peca_Em_Uso = 'Original'
                Tempo_Proxima_Falha = t + gerar_tempo_falha_sistema(Peca_Em_Uso, Bt)
                
            if Peca_Em_Uso == 'Impressa' and It > 0:
                It -= 1
                Peca_Em_Uso = 'Original'
                Pt = 0
                Tempo_Proxima_Falha = t + gerar_tempo_falha_sistema(Peca_Em_Uso, Bt)

        # 3. Evento: Chegada da Falha
        if t == Tempo_Proxima_Falha:
            if Peca_Em_Uso == 'Impressa':
                Pt = 0  
                
            if It > 0:
                It -= 1
                Peca_Em_Uso = 'Original'
                Tempo_Proxima_Falha = t + gerar_tempo_falha_sistema(Peca_Em_Uso, Bt)
            elif Pt == 1:
                Peca_Em_Uso = 'Impressa'
                Tempo_Proxima_Falha = t + gerar_tempo_falha_sistema(Peca_Em_Uso, Bt)
            else:
                Bt += 1
                Peca_Em_Uso = 'Nenhuma' if Bt == N else 'Original'
                Tempo_Proxima_Falha = t + gerar_tempo_falha_sistema(Peca_Em_Uso, Bt)

        # 4. Avaliação dos Gatilhos (Posição Gerencial de Estoque IP)
        IPt = It + Ot + Pt - Bt
        
        # Gatilho Emergencial MA (s*)
        if IPt <= s_star and Jt == 0 and Pt == 0:
            Jt = 1
            Tempo_Chegada_Impressao = t + L_ef
            Custo_Total += C2
            Pecas_Impressas_Total += 1  # <--- Incrementa total impresso

        # Gatilho Regular (s)
        if IPt <= s and Ot == 0:
            Q = S - IPt
            Ot = Q
            Tempo_Chegada_Convencional = t + L_rep
            Custo_Total += K + (Q * C1)

        # 5. Acumulador Financeiro e de KPI
        Custo_Total += (It * Ch_hora) + (Bt * Cb)
        if Bt > 0:
            Horas_Indisponivel += 1

    disponibilidade = 1 - (Horas_Indisponivel / Horizonte_T)
    return Custo_Total, disponibilidade, Pecas_Impressas_Total

def otimizar_gatilhos_grid(S, params):
    """Varre combinações de s e s* para encontrar o menor custo estocástico."""
    melhor_custo = float('inf')
    melhor_s = 0
    melhor_s_star = 0
    melhor_disp = 0.0
    melhor_impressas = 0.0
    
    limite_s = max(1, S)
    
    for s in range(0, limite_s):
        for s_star in range(0, s + 1):
            
            custos_parciais = []
            disps_parciais = []
            impressas_parciais = []
            for _ in range(3):
                c, d, p = simular_politica_dual(s_star, s, S, params)
                custos_parciais.append(c)
                disps_parciais.append(d)
                impressas_parciais.append(p)
                
            custo_medio = sum(custos_parciais) / len(custos_parciais)
            disp_media = sum(disps_parciais) / len(disps_parciais)
            impressas_media = sum(impressas_parciais) / len(impressas_parciais)
            
            if custo_medio < melhor_custo:
                melhor_custo = custo_medio
                melhor_s = s
                melhor_s_star = s_star
                melhor_disp = disp_media
                melhor_impressas = impressas_media
                
    return melhor_s_star, melhor_s, melhor_custo, melhor_disp, melhor_impressas


# =====================================================================
# INTERFACE PRINCIPAL DO STREAMLIT
# =====================================================================

col_img1, col_img2, col_img3 = st.columns(3)
if Path('randomen.png').exists():
    foto = Image.open('randomen.png')
    col_img2.image(foto, use_container_width=True)
elif Path('logo.png').exists():
    foto = Image.open('logo.png')
    col_img2.image(foto, use_container_width=True)

st.markdown("<h2 style='text-align: center; color: #388E3C;'>Spare Parts Inventory Sizing System</h2>", unsafe_allow_html=True)

menu = ["Analytical", "Optimizer", "Optimizer MA"]
choice = st.sidebar.selectbox("Select here", menu)

# --- MODO 1: ANALYTICAL ---
if choice == menu[0]:
    st.header(menu[0])
    
    st.subheader("Avaliação da Situação Atual do Sistema")
    st.write("Insira a quantidade de peças sobressalentes em uso e os parâmetros operacionais para calcular a margem de segurança e o custo atual.")
    
    Q_atual = st.number_input("Quantidade atual de peças Sobressalentes (x):", min_value=0, value=5, step=1)
    L = st.number_input("Lambda (taxa de falha):", min_value=0.0000, value=0.05, step=0.01, format="%.6f")
    N = st.number_input("Número de máquinas ativas (n):", min_value=1, value=10, step=1)
    T = st.number_input("Tempo de reposição (t):", min_value=1, value=1, step=1)
    custo_unitario = st.number_input("Custo Unitário por Peça (R$):", min_value=0.00, value=150.00, step=10.00, format="%.2f")
    
    botao_analytical = st.button("Calcular Situação Atual")
    
    if botao_analytical:
        m_val = L * N * T
        LG = L * N
        custo_total = Q_atual * custo_unitario
        
        st.subheader("Parâmetros do Sistema")
        col_m1, col_m2 = st.columns(2)
        col_m1.metric("Valor Esperado de Falhas (m)", f"{m_val:.2f}")
        col_m2.metric("Custo Total (Inventário Atual)", f"R$ {custo_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        st.divider()
        
        lista_x, lista_p, lista_margem, lista_risco = [], [], [], []
        prob_acumulada = 0
        for x in range(Q_atual + 1):
            p_x = poisson.pmf(x, m_val)
            prob_acumulada += p_x
            lista_x.append(x)
            lista_p.append(p_x)
            lista_margem.append(prob_acumulada)
            lista_risco.append(max(1 - prob_acumulada, 0.0))
        df_p_analitico = pd.DataFrame({'x': lista_x, 'P(X=x)': lista_p, 'Margem Seg.': lista_margem, 'Risco': lista_risco})
        
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            exibir_resumo_streamlit(df_p_analitico, Q_atual, "Distribuição de Poisson", texto_destaque="Quantidade Atual", mostrar_contexto=False)
            
        with col_t2:
            if LG >= 20:
                lista_x_n, lista_p_n, lista_margem_n, lista_risco_n = [], [], [], []
                sigma = np.sqrt(m_val)
                for x in range(Q_atual + 1):
                    prob_acum_n = norm.cdf(x, loc=m_val, scale=sigma)
                    p_x_n = prob_acum_n if x == 0 else prob_acum_n - norm.cdf(x - 1, loc=m_val, scale=sigma)
                    lista_x_n.append(x)
                    lista_p_n.append(p_x_n)
                    lista_margem_n.append(prob_acum_n)
                    lista_risco_n.append(max(1 - prob_acum_n, 0.0))
                df_n_analitico = pd.DataFrame({'x': lista_x_n, 'P(X=x)': lista_p_n, 'Margem Seg.': lista_margem_n, 'Risco': lista_risco_n})
                
                exibir_resumo_streamlit(df_n_analitico, Q_atual, "Aproximação Normal", texto_destaque="Quantidade Atual", mostrar_contexto=False)
            else:
                st.subheader("Aproximação Normal")
                st.warning("Aproximação pela Normal não recomendada.")


# --- MODO 2: OPTIMIZER PADRÃO ---
elif choice == menu[1]:
    st.header(menu[1])
    st.subheader("Insert the parameter values below:")
    
    L = st.number_input("Lambda (taxa de falha):", min_value=0.0000, value=0.05, step=0.01, format="%.6f")
    N = st.number_input("Número de máquinas ativas (n):", min_value=1, value=10, step=1)
    T = st.number_input("Tempo de reposição (t):", min_value=1, value=1, step=1)
    R_PCT = st.number_input("Risco Alvo (%):", min_value=0.01, max_value=99.99, value=5.00, step=1.0, format="%.2f")
    custo_unitario = st.number_input("Custo Unitário por Peça (R$):", min_value=0.00, value=150.00, step=10.00, format="%.2f")

    st.subheader("Click on button below to run this application:")    
    botao = st.button("Calcular Dimensionamento")        
    
    if botao:
        risco = R_PCT / 100.0
        LG = L * N
        
        df_p, x_p, m_val = calcular_poisson(L, N, T, risco)
        df_n, x_n, sigma_val = calcular_normal(L, N, T, risco)
        
        custo_total = custo_unitario * x_p

        st.subheader("Parâmetros Utilizados")
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("Valor Esperado de Falhas (m)", f"{m_val:.2f}")
        col_m2.metric("Risco Alvo", f"{R_PCT}%")
        col_m3.metric("Custo Total (Inventário Ótimo)", f"R$ {custo_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

        st.divider()

        col_tabela1, col_tabela2 = st.columns(2)
        with col_tabela1:
            exibir_resumo_streamlit(df_p, x_p, "Distribuição de Poisson", mostrar_contexto=True)
            
        with col_tabela2:
            if LG >= 20:
                exibir_resumo_streamlit(df_n, x_n, "Aproximação Normal", mostrar_contexto=True)
            else:
                st.subheader("Aproximação Normal")
                st.warning("Aproximação pela Normal não recomendada.")


# --- MODO 3: OPTIMIZER MA (MANUFATURA ADITIVA) ---
elif choice == menu[2]:
    st.header(menu[2] + " - Simulação Dual-Sourcing")
    st.write("Dimensionamento otimizado de política (s*, s, S) minimizando Custos de Inventário, Pedidos e Indisponibilidade.")
    
    st.subheader("Parâmetros de Manutenção e Falha")
    col1, col2 = st.columns(2)
    MTBF_conv = col1.number_input("MTBF Peça Original (horas)", min_value=100, value=5000, step=500)
    MTBF_print = col2.number_input("MTBF Peça Impressa FDM (horas)", min_value=100, value=2500, step=500)
    
    st.subheader("Parâmetros Logísticos (Lead Times)")
    col3, col4 = st.columns(2)
    L_rep = col3.number_input("Lead Time do Fornecedor Original (horas)", min_value=1, value=1500, step=24)
    L_ef = col4.number_input("Tempo de Impressão Emergencial (horas)", min_value=1, value=8, step=1)
    
    st.subheader("Parâmetros de Custo (R$)")
    col5, col6, col7 = st.columns(3)
    C1 = col5.number_input("Custo Unitário Original (C1)", min_value=0.0, value=300.0)
    C2 = col6.number_input("Custo de Impressão (C2)", min_value=0.0, value=50.0)
    K = col7.number_input("Custo Fixo por Pedido (K)", min_value=0.0, value=200.0)
    
    col8, col9 = st.columns(2)
    Cb = col8.number_input("Custo de Downtime por Hora (Cb)", min_value=0.0, value=3000.0)
    Ch_ano = col9.number_input("Custo de Posse Anual (R$/Unidade)", min_value=0.0, value=50.0)
    
    st.subheader("Parâmetros de Otimização")
    col10, col11, col12 = st.columns(3)
    R_PCT = col10.number_input("Risco Alvo para Teto S (%)", min_value=0.01, max_value=99.99, value=5.00)
    Anos_Simulacao = col11.number_input("Horizonte de Simulação (Anos)", min_value=1, value=5)
    N_Maquinas = col12.number_input("Número de Máquinas (N)", min_value=1, value=10)

    botao_ma = st.button("Executar Simulação e Otimizar (s*, s, S)")

    if botao_ma:
        with st.spinner("A gerar Cenários Estocásticos e Otimizar... Aguarde."):
            
            risco = R_PCT / 100.0
            lambda_hora = 1.0 / MTBF_conv
            Ch_hora = Ch_ano / 8760.0
            Horizonte_T = int(Anos_Simulacao * 8760)
            
            df_p, S_teto, m_val = calcular_poisson(lambda_hora, N_Maquinas, L_rep, risco)
            
            if S_teto <= 0:
                S_teto = 1 
            
            params = {
                'Horizonte_T': Horizonte_T,
                'N': N_Maquinas,
                'L_rep': L_rep,
                'L_ef': L_ef,
                'MTBF_conv': MTBF_conv,
                'MTBF_print': MTBF_print,
                'C1': C1,
                'C2': C2,
                'K': K,
                'Ch_hora': Ch_hora,
                'Cb': Cb
            }
            
            melhor_s_star, melhor_s, melhor_custo_total, disponibilidade, total_impressas = otimizar_gatilhos_grid(S_teto, params)
            
            custo_medio_anual = melhor_custo_total / Anos_Simulacao
            impressas_por_ano = total_impressas / Anos_Simulacao
            
        st.success("Otimização Concluída!")
        
        st.markdown("### Política Recomendada (s*, s, S)")
        rc1, rc2, rc3 = st.columns(3)
        rc1.metric(label="Gatilho de Impressão (s*)", value=melhor_s_star, delta="Emergência MA", delta_color="off")
        rc2.metric(label="Ponto de Encomenda Regular (s)", value=melhor_s, delta="Pedido ao Fornecedor", delta_color="off")
        rc3.metric(label="Teto de Inventário (S)", value=S_teto, delta="Nível Alvo", delta_color="off")
        
        st.divider()
        st.markdown("### Performance Projetada da Política")
        p1, p2 = st.columns(2)
        p1.metric(label="Custo Médio Operacional Estimado (por Ano)", value=f"R$ {custo_medio_anual:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        p2.metric(label="Disponibilidade da Fábrica (KPI)", value=f"{disponibilidade * 100:.3f}%")
        
        st.divider()
        st.markdown("### Cobertura por Manufatura Aditiva (Vulnerabilidade)")
        pi1, pi2 = st.columns(2)
        pi1.metric(label="Total Peças Impressas no Período", value=f"{total_impressas:.1f} peças", help="Total de peças fabricadas para suprir a vulnerabilidade do sistema.")
        pi2.metric(label="Média de Peças Impressas por Ano", value=f"{impressas_por_ano:.2f} peças/ano")
