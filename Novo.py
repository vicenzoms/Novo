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
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Configuração inicial da página
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
LOGO_HTML = f'<img src="data:image/png;base64,{LOGO_BASE64}" style="max-height: 120px; width: auto; margin-bottom: 15px;">' if LOGO_BASE64 else ''

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# TELA DE LOGIN 
if not st.session_state.authenticated:
    st.markdown(
        f"""
        <style>
        .stApp {{ background: #f4f5f7 !important; }}
        .login-title-box {{ text-align: center; margin-top: 20px; margin-bottom: 20px; }}
        .login-title-box h2 {{ color: #388E3C !important; font-size: 1.8rem; font-weight: 700; margin: 0; }}
        div[data-testid="stForm"] {{
            background: #ffffff !important; border-radius: 8px !important;
            border: 1px solid #e0e0e0 !important; box-shadow: 0 4px 12px rgba(0,0,0,0.08) !important; padding: 2rem !important;
        }}
        .stFormSubmitButton > button {{
            background: #388E3C !important; color: #ffffff !important; font-weight: 600 !important; border-radius: 4px !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

    col_vazia1, col_login, col_vazia2 = st.columns([1, 1.2, 1])

    with col_login:
        st.markdown(
            f"""
            <div class="login-title-box">
                {LOGO_HTML}
                <h2>Acesso ao Sistema</h2>
                <p style="color: #666;">RANDOM - Grupo de Pesquisa</p>
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

    st.stop()


# CSS DA TELA PRINCIPAL
st.markdown("""
    <style>
    .stApp { background-color: #fdfdfd; }
    h1, h2, h3 { color: #388E3C !important; font-family: 'Roboto', sans-serif !important; }
    [data-testid="stSidebar"] { background-color: #ffffff !important; border-right: 1px solid #e0e0e0; }
    .stButton > button { background-color: #388E3C !important; color: white !important; border-radius: 4px !important; border: none !important; }
    .stButton > button:hover { background-color: #2E7D32 !important; }
    </style>
""", unsafe_allow_html=True)


# =====================================================================
# FUNÇÕES DE CÁLCULO E SIMULAÇÃO
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


# --- CORE SIMULAÇÃO COM PRIORIDADE ABSOLUTA PARA ORIGINAIS ---

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
    Q_3D_lote = params.get('Q_3D_lote', 1)

    It = S
    Bt = 0
    Ot = 0
    Pt = 0
    Jt = 0
    M_orig = N
    M_3d = 0
    impressas_ciclo_atual = 0

    Custo_Total = 0
    Horas_Indisponivel = 0
    Pecas_Impressas_Total = 0
    Ciclos_Ressuprimento = 0

    def proximo_tempo_falha():
        taxa_orig = M_orig / MTBF_conv
        taxa_3d = M_3d / MTBF_print
        taxa_total = taxa_orig + taxa_3d
        if taxa_total <= 0:
            return float('inf')
        return max(1, int(np.random.exponential(1.0 / taxa_total)))

    Tempo_Proxima_Falha = proximo_tempo_falha()
    Tempo_Chegada_Convencional = float('inf')
    Tempo_Chegada_Impressao = float('inf')

    for t in range(1, Horizonte_T + 1):
        
        # 1. Chegada da Impressão 3D
        if t == Tempo_Chegada_Impressao:
            Pt += 1
            Pecas_Impressas_Total += 1
            impressas_ciclo_atual += 1
            
            if Bt > 0:
                Bt -= 1
                Pt -= 1
                M_3d += 1
                Tempo_Proxima_Falha = t + proximo_tempo_falha()
            
            if Ot > 0 and impressas_ciclo_atual < Q_3D_lote:
                Jt = 1
                Tempo_Chegada_Impressao = t + L_ef
                Custo_Total += C2
            else:
                Jt = 0
                Tempo_Chegada_Impressao = float('inf')

        # 2. Chegada do Lote Original (Prioridade Absoluta)
        if t == Tempo_Chegada_Convencional:
            It += Ot
            Ot = 0
            Tempo_Chegada_Convencional = float('inf')
            Jt = 0
            Tempo_Chegada_Impressao = float('inf')
            impressas_ciclo_atual = 0
            
            # Prioridade 1: Zerar backlog de máquinas paradas
            while Bt > 0 and It > 0:
                Bt -= 1
                It -= 1
                M_orig += 1
                
            # Prioridade 2: Substituir Peças 3D em uso nas máquinas por Originais recém-chegadas
            while M_3d > 0 and It > 0:
                M_3d -= 1
                It -= 1
                M_orig += 1

            Tempo_Proxima_Falha = t + proximo_tempo_falha()

        # 3. Ocorrência de Falha
        if t == Tempo_Proxima_Falha:
            taxa_orig = M_orig / MTBF_conv
            taxa_3d = M_3d / MTBF_print
            taxa_total = taxa_orig + taxa_3d
            
            if np.random.rand() < (taxa_orig / taxa_total if taxa_total > 0 else 1.0):
                M_orig = max(0, M_orig - 1)
            else:
                M_3d = max(0, M_3d - 1)

            # Atendimento à Falha: 1º Original, 2º 3D, 3º Backlog
            if It > 0:
                It -= 1
                M_orig += 1
            elif Pt > 0:
                Pt -= 1
                M_3d += 1
            else:
                Bt += 1

            Tempo_Proxima_Falha = t + proximo_tempo_falha()

        # 4. Avaliação de Gatilhos
        IPt = It + Ot + Pt - Bt
        
        if IPt <= s and Ot == 0:
            Q = S - IPt
            Ot = Q
            Tempo_Chegada_Convencional = t + L_rep
            Custo_Total += K + (Q * C1)
            Ciclos_Ressuprimento += 1
            impressas_ciclo_atual = 0

        if IPt <= s_star and Jt == 0 and impressas_ciclo_atual < Q_3D_lote and Ot > 0:
            Jt = 1
            Tempo_Chegada_Impressao = t + L_ef
            Custo_Total += C2

        Custo_Total += (It * Ch_hora) + (Bt * Cb)
        if Bt > 0:
            Horas_Indisponivel += 1

    disponibilidade = 1 - (Horas_Indisponivel / Horizonte_T)
    return Custo_Total, disponibilidade, Pecas_Impressas_Total, Ciclos_Ressuprimento


def simular_politica_dual_com_historico(s_star, s, S, params):
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
    Q_3D_lote = params.get('Q_3D_lote', 1)

    It = S
    Bt = 0
    Ot = 0
    Pt = 0
    Jt = 0
    M_orig = N
    M_3d = 0
    impressas_ciclo_atual = 0

    def proximo_tempo_falha():
        taxa_orig = M_orig / MTBF_conv
        taxa_3d = M_3d / MTBF_print
        taxa_total = taxa_orig + taxa_3d
        if taxa_total <= 0:
            return float('inf')
        return max(1, int(np.random.exponential(1.0 / taxa_total)))

    Tempo_Proxima_Falha = proximo_tempo_falha()
    Tempo_Chegada_Convencional = float('inf')
    Tempo_Chegada_Impressao = float('inf')

    historico = []
    eventos = []

    for t in range(1, Horizonte_T + 1):
        evento_descricao = []
        qtd_chegada_orig = 0
        qtd_chegada_3d = 0

        if t == Tempo_Chegada_Impressao:
            Pt += 1
            qtd_chegada_3d = 1
            impressas_ciclo_atual += 1
            evento_descricao.append(f"Peça 3D Concluída ({impressas_ciclo_atual}/{Q_3D_lote})")
            
            if Bt > 0:
                Bt -= 1
                Pt -= 1
                M_3d += 1
                Tempo_Proxima_Falha = t + proximo_tempo_falha()
                evento_descricao.append("Peça 3D Instalada para Zerar Backlog")
            
            if Ot > 0 and impressas_ciclo_atual < Q_3D_lote:
                Jt = 1
                Tempo_Chegada_Impressao = t + L_ef
            else:
                Jt = 0
                Tempo_Chegada_Impressao = float('inf')

        if t == Tempo_Chegada_Convencional:
            qtd_chegada_orig = Ot
            It += Ot
            Ot = 0
            Tempo_Chegada_Convencional = float('inf')
            Jt = 0
            Tempo_Chegada_Impressao = float('inf')
            impressas_ciclo_atual = 0
            evento_descricao.append(f"Chegada Lote Original ({qtd_chegada_orig} un)")
            
            while Bt > 0 and It > 0:
                Bt -= 1
                It -= 1
                M_orig += 1
                
            substituidas_3d = 0
            while M_3d > 0 and It > 0:
                M_3d -= 1
                It -= 1
                M_orig += 1
                substituidas_3d += 1
                
            if substituidas_3d > 0:
                evento_descricao.append(f"{substituidas_3d} Peça(s) 3D em Uso Substituída(s) por Originais")

            Tempo_Proxima_Falha = t + proximo_tempo_falha()

        if t == Tempo_Proxima_Falha:
            evento_descricao.append("Falha Registrada")
            taxa_orig = M_orig / MTBF_conv
            taxa_3d = M_3d / MTBF_print
            taxa_total = taxa_orig + taxa_3d
            
            if np.random.rand() < (taxa_orig / taxa_total if taxa_total > 0 else 1.0):
                M_orig = max(0, M_orig - 1)
            else:
                M_3d = max(0, M_3d - 1)

            if It > 0:
                It -= 1
                M_orig += 1
                evento_descricao.append("Reposição Imediata por Peça Original do Estoque")
            elif Pt > 0:
                Pt -= 1
                M_3d += 1
                evento_descricao.append("Reposição por Peça 3D da Reserva")
            else:
                Bt += 1
                evento_descricao.append("Estoque Esgotado: Entrada em Backlog")

            Tempo_Proxima_Falha = t + proximo_tempo_falha()

        IPt = It + Ot + Pt - Bt
        
        if IPt <= s and Ot == 0:
            Q = S - IPt
            Ot = Q
            Tempo_Chegada_Convencional = t + L_rep
            impressas_ciclo_atual = 0
            evento_descricao.append(f"Gatilho s Ativado (Pedido Original Q={Q})")

        if IPt <= s_star and Jt == 0 and impressas_ciclo_atual < Q_3D_lote and Ot > 0:
            Jt = 1
            Tempo_Chegada_Impressao = t + L_ef
            evento_descricao.append("Gatilho Preventivo s* Ativado (Produção 3D Initiated)")

        historico.append({
            'Tempo_Hora': t,
            'Estoque_Original_It': It,
            'Em_Transito_Ot': Ot,
            'Estoque_3D_Pt': Pt,
            'Maquinas_Originais': M_orig,
            'Maquinas_3D': M_3d,
            'Backlog_Bt': Bt,
            'Posicao_Estoque_IPt': IPt,
            'Qtd_Chegada_Original': qtd_chegada_orig,
            'Qtd_Chegada_3D': qtd_chegada_3d
        })

        if evento_descricao:
            eventos.append({
                'Tempo_Hora': t,
                'Estoque_Original': It,
                'Estoque_3D': Pt,
                'Maquinas_com_3D': M_3d,
                'Descricao': " | ".join(evento_descricao)
            })

    return pd.DataFrame(historico), pd.DataFrame(eventos)


def otimizar_gatilhos_grid(S_alvo, params):
    melhor_custo = float('inf')
    melhor_s = 0
    melhor_s_star = 0
    melhor_disp = 0.0
    melhor_impressas = 0.0
    melhor_ciclos = 1
    
    limite_s = max(1, S_alvo)
    
    for s in range(0, limite_s):
        for s_star in range(0, s + 1):
            custos_parciais = []
            disps_parciais = []
            impressas_parciais = []
            ciclos_parciais = []
            
            for _ in range(2):
                c, d, p, n_ciclos = simular_politica_dual(s_star, s, S_alvo, params)
                custos_parciais.append(c)
                disps_parciais.append(d)
                impressas_parciais.append(p)
                ciclos_parciais.append(n_ciclos)
                
            custo_medio = sum(custos_parciais) / len(custos_parciais)
            disp_media = sum(disps_parciais) / len(disps_parciais)
            impressas_media = sum(impressas_parciais) / len(impressas_parciais)
            ciclos_medio = max(1, sum(ciclos_parciais) / len(ciclos_parciais))
            
            if custo_medio < melhor_custo:
                melhor_custo = custo_medio
                melhor_s = s
                melhor_s_star = s_star
                melhor_disp = disp_media
                melhor_impressas = impressas_media
                melhor_ciclos = ciclos_medio
                
    return melhor_s_star, melhor_s, melhor_custo, melhor_disp, melhor_impressas, melhor_ciclos


# =====================================================================
# INTERFACE PRINCIPAL
# =====================================================================

col_img1, col_img2, col_img3 = st.columns(3)
if Path('randomen.png').exists():
    foto = Image.open('randomen.png')
    col_img2.image(foto, use_container_width=True)

st.markdown("<h2 style='text-align: center; color: #388E3C;'>Spare Parts Inventory Sizing System</h2>", unsafe_allow_html=True)

menu = ["Analytical", "Optimizer", "Optimizer MA"]
choice = st.sidebar.selectbox("Select here", menu)

if choice == menu[0]:
    st.header(menu[0])
    Q_atual = st.number_input("Quantidade atual de peças Sobressalentes (x):", min_value=0, value=5, step=1)
    L = st.number_input("Lambda (taxa de falha):", min_value=0.0000, value=0.05, step=0.01, format="%.6f")
    N = st.number_input("Número de máquinas ativas (n):", min_value=1, value=10, step=1)
    T = st.number_input("Tempo de reposição (t):", min_value=1, value=1, step=1)
    custo_unitario = st.number_input("Custo Unitário por Peça (R$):", min_value=0.00, value=150.00, step=10.00, format="%.2f")
    
    if st.button("Calcular Situação Atual"):
        m_val = L * N * T
        df_p_analitico, _, _ = calcular_poisson(L, N, T, 0.05)
        exibir_resumo_streamlit(df_p_analitico, Q_atual, "Distribuição de Poisson", texto_destaque="Quantidade Atual", mostrar_contexto=False)

elif choice == menu[1]:
    st.header(menu[1])
    L = st.number_input("Lambda (taxa de falha):", min_value=0.0000, value=0.05, step=0.01, format="%.6f")
    N = st.number_input("Número de máquinas ativas (n):", min_value=1, value=10, step=1)
    T = st.number_input("Tempo de reposição (t):", min_value=1, value=1, step=1)
    R_PCT = st.number_input("Risco Alvo (%):", min_value=0.01, max_value=99.99, value=5.00, step=1.0, format="%.2f")
    custo_unitario = st.number_input("Custo Unitário por Peça (R$):", min_value=0.00, value=150.00, step=10.00, format="%.2f")

    if st.button("Calcular Dimensionamento"):
        df_p, x_p, m_val = calcular_poisson(L, N, T, R_PCT / 100.0)
        exibir_resumo_streamlit(df_p, x_p, "Distribuição de Poisson", mostrar_contexto=True)

elif choice == menu[2]:
    st.header(menu[2] + " - Simulação Dual-Sourcing com Fila Contínua MA")
    
    col1, col2 = st.columns(2)
    MTBF_conv = col1.number_input("MTBF Peça Original (horas)", min_value=100, value=5000, step=500)
    MTBF_print = col2.number_input("MTBF Peça Impressa FDM (horas)", min_value=100, value=2500, step=500)
    
    col3, col4 = st.columns(2)
    L_rep = col3.number_input("Lead Time do Fornecedor Original (horas)", min_value=1, value=1500, step=24)
    L_ef = col4.number_input("Tempo de Impressão de 1 Unidade 3D (horas)", min_value=1, value=8, step=1)
    
    col5, col6, col7 = st.columns(3)
    C1 = col5.number_input("Custo Unitário Original (C1)", min_value=0.0, value=300.0)
    C2 = col6.number_input("Custo de Impressão Unitário (C2)", min_value=0.0, value=50.0)
    K = col7.number_input("Custo Fixo por Pedido (K)", min_value=0.0, value=200.0)
    
    col8, col9 = st.columns(2)
    Cb = col8.number_input("Custo de Downtime por Hora (Cb)", min_value=0.0, value=3000.0)
    Ch_ano = col9.number_input("Custo de Posse Anual (R$/Unidade)", min_value=0.0, value=50.0)
    
    col10, col11, col12 = st.columns(3)
    R_PCT = col10.number_input("Risco Alvo para Teto S (%)", min_value=0.01, max_value=99.99, value=5.00)
    Anos_Simulacao = col11.number_input("Horizonte de Simulação (Anos)", min_value=1, value=5)
    N_Maquinas = col12.number_input("Número de Máquinas (N)", min_value=1, value=10)

    lambda_hora = 1.0 / MTBF_conv
    m_leadtime = lambda_hora * N_Maquinas * L_rep
    
    # Cálculo Analítico do Teto S e do Lote Q_3D
    cobertura_leadtime = int(np.ceil(poisson.ppf(1 - (R_PCT / 100.0), m_leadtime)))
    Q_3D_calculado = max(1, cobertura_leadtime)
    
    # Teto S dimensionado para cobrir a demanda do lead time + lote de ciclo operacional
    S_teto = max(2, cobertura_leadtime + int(m_leadtime))

    st.info(f"💡 **Dimensionamento do Sistema:** Teto de Inventário Original $S = {S_teto}$ peças. Lote $Q_{{3D}} = {Q_3D_calculado}$ peças.")

    if st.button("Executar Simulação e Otimizar (s*, s, S)"):
        with st.spinner("A otimizar gatilhos e simular fila de impressão contínua..."):
            Ch_hora = Ch_ano / 8760.0
            Horizonte_T = int(Anos_Simulacao * 8760)
            
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
                'Cb': Cb,
                'Q_3D_lote': Q_3D_calculado
            }
            
            melhor_s_star, melhor_s, melhor_custo_total, disponibilidade, total_impressas, total_ciclos = otimizar_gatilhos_grid(S_teto, params)
            
            df_hist, df_ev = simular_politica_dual_com_historico(melhor_s_star, melhor_s, S_teto, params)

            st.session_state['df_hist'] = df_hist
            st.session_state['df_ev'] = df_ev
            st.session_state['ma_params'] = {
                's_star': melhor_s_star,
                's': melhor_s,
                'S': S_teto,
                'custo_medio_anual': melhor_custo_total / Anos_Simulacao,
                'disponibilidade': disponibilidade,
                'impressas_por_ano': total_impressas / Anos_Simulacao,
                'Q_3D_calculado': Q_3D_calculado,
                'media_impressa_por_ciclo': total_impressas / max(1, total_ciclos),
                'Horizonte_T': Horizonte_T
            }

    if 'ma_params' in st.session_state:
        p = st.session_state['ma_params']
        df_hist = st.session_state['df_hist']
        df_ev = st.session_state['df_ev']

        st.success("Otimização Concluída!")
        
        st.markdown("### Política Recomendada (s*, s, S)")
        rc1, rc2, rc3 = st.columns(3)
        rc1.metric(label="Gatilho de Impressão (s*)", value=p['s_star'])
        rc2.metric(label="Ponto de Encomenda Regular (s)", value=p['s'])
        rc3.metric(label="Teto de Inventário (S)", value=p['S'])
        
        st.divider()
        st.markdown("### Performance Projetada da Política")
        p1, p2, p3 = st.columns(3)
        p1.metric(label="Custo Médio Operacional (por Ano)", value=f"R$ {p['custo_medio_anual']:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        p2.metric(label="Disponibilidade da Fábrica (KPI)", value=f"{p['disponibilidade'] * 100:.3f}%")
        p3.metric(label="Média de Peças Impressas por Ano", value=f"{p['impressas_por_ano']:.2f} peças/ano")

        st.divider()
        st.markdown("### 📊 Trajetória do Estoque Regular e Peças 3D")
        
        max_horas = p['Horizonte_T']
        janela_horas = st.slider(
            "Selecione a janela de horas para visualização:",
            min_value=1,
            max_value=max_horas,
            value=(1, min(8760 * 2, max_horas)),
            step=100
        )
        
        df_sub = df_hist[(df_hist['Tempo_Hora'] >= janela_horas[0]) & (df_hist['Tempo_Hora'] <= janela_horas[1])].copy()

        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.1,
            subplot_titles=("Estoque Regular Original (It) e Pontos de Disparo", "Estoque 3D Reservado (Pt) e Máquinas Rodando com Peça 3D"),
            row_heights=[0.6, 0.4]
        )

        fig.add_trace(
            go.Scatter(x=df_sub['Tempo_Hora'], y=df_sub['Estoque_Original_It'], mode='lines', name='Estoque Original (It)', line=dict(color='#2E7D32', width=2)),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(x=[janela_horas[0], janela_horas[1]], y=[p['s'], p['s']], mode='lines', name=f"Gatilho s ({p['s']})", line=dict(color='orange', dash='dash')),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(x=df_sub['Tempo_Hora'], y=df_sub['Estoque_3D_Pt'], mode='lines', name='Estoque Reserva 3D (Pt)', line=dict(color='#9C27B0', width=2)),
            row=2, col=1
        )
        fig.add_trace(
            go.Scatter(x=df_sub['Tempo_Hora'], y=df_sub['Maquinas_3D'], mode='lines', name='Máquinas com Peça 3D em Uso', line=dict(color='#E91E63', width=1.5, dash='dot')),
            row=2, col=1
        )

        fig.update_layout(height=600, hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("### 📋 Diário de Eventos")
        df_ev_sub = df_ev[(df_ev['Tempo_Hora'] >= janela_horas[0]) & (df_ev['Tempo_Hora'] <= janela_horas[1])]
        st.dataframe(df_ev_sub, use_container_width=True, hide_index=True)
