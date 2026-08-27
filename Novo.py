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
    """Função para converter imagens em Base64 e renderizá-las no HTML/CSS"""
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

# TELA DE LOGIN 
if not st.session_state.authenticated:
    st.markdown(
        f"""
        <style>
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


# --- SIMULAÇÃO DUAL COM IMPRESSÃO SOB DEMANDA APENAS PARA SUPRIR O NÍVEL s* ---

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

    It = S
    Bt = 0
    Ot = 0
    Pt = 0  
    Jt = 0  
    Peca_Em_Uso = 'Original'
    Custo_Total = 0
    Horas_Indisponivel = 0
    Pecas_Impressas_Total = 0
    Ciclos_Ressuprimento = 0

    Tempo_Proxima_Falha = gerar_tempo_falha_sistema(Peca_Em_Uso, Bt)
    Tempo_Chegada_Convencional = float('inf')
    Tempo_Chegada_Impressao = float('inf')

    for t in range(1, Horizonte_T + 1):
        
        # 1. Evento: Conclusão da Impressão 3D de 1 peça
        if t == Tempo_Chegada_Impressao:
            Pt += 1
            Pecas_Impressas_Total += 1
            
            if Bt > 0:
                Bt -= 1
                Pt -= 1
                Peca_Em_Uso = 'Impressa'
                Tempo_Proxima_Falha = t + gerar_tempo_falha_sistema(Peca_Em_Uso, Bt)
            
            estoque_atual = It + Pt - Bt
            
            # NOVO LIMITADOR APLICADO AQUI: Se já existe uma peça 3D (Pt > 0), a impressora NÃO reinicia.
            if Ot > 0 and estoque_atual <= s_star and Pt == 0:
                Jt = 1
                Tempo_Chegada_Impressao = t + L_ef
                Custo_Total += C2
            else:
                Jt = 0
                Tempo_Chegada_Impressao = float('inf')

        # 2. Evento: Chegada do Pedido Convencional
        if t == Tempo_Chegada_Convencional:
            It = S  
            Ot = 0
            Tempo_Chegada_Convencional = float('inf')
            Jt = 0
            Tempo_Chegada_Impressao = float('inf')
            
            while Bt > 0 and It > 0:
                Bt -= 1
                It -= 1
                Peca_Em_Uso = 'Original'
                Tempo_Proxima_Falha = t + gerar_tempo_falha_sistema(Peca_Em_Uso, Bt)
                
            if Peca_Em_Uso == 'Impressa' and It > 0:
                It -= 1
                Peca_Em_Uso = 'Original'
                Tempo_Proxima_Falha = t + gerar_tempo_falha_sistema(Peca_Em_Uso, Bt)

        # 3. Evento: Chegada da Falha
        if t == Tempo_Proxima_Falha:
            if It > 0:
                It -= 1
                Peca_Em_Uso = 'Original'
                Tempo_Proxima_Falha = t + gerar_tempo_falha_sistema(Peca_Em_Uso, Bt)
            elif Pt > 0:
                Pt -= 1
                Peca_Em_Uso = 'Impressa'
                Tempo_Proxima_Falha = t + gerar_tempo_falha_sistema(Peca_Em_Uso, Bt)
            else:
                Bt += 1
                Peca_Em_Uso = 'Nenhuma' if Bt == N else 'Original'
                Tempo_Proxima_Falha = t + gerar_tempo_falha_sistema(Peca_Em_Uso, Bt)

        # 4. Avaliação dos Gatilhos
        IPt = It + Ot + Pt - Bt
        
        # Gatilho Regular (s)
        if IPt <= s and Ot == 0:
            Q = S - IPt
            Ot = Q
            Tempo_Chegada_Convencional = t + L_rep
            Custo_Total += K + (Q * C1)
            Ciclos_Ressuprimento += 1

        # Gatilho Emergencial (s*) - NOVO LIMITADOR (Pt == 0): Só imprime se não tiver NENHUMA peça 3D guardada.
        estoque_atual = It + Pt - Bt
        if estoque_atual <= s_star and Jt == 0 and Ot > 0 and Pt == 0:
            Jt = 1
            Tempo_Chegada_Impressao = t + L_ef
            Custo_Total += C2

        Custo_Total += (It * Ch_hora) + (Bt * Cb)
        if Bt > 0:
            Horas_Indisponivel += 1

    disponibilidade = 1 - (Horas_Indisponivel / Horizonte_T)
    return Custo_Total, disponibilidade, Pecas_Impressas_Total, Ciclos_Ressuprimento


def simular_politica_dual_com_historico(s_star, s, S, params):
    Horizonte_T = params['HorizonEntendi o problema! O sistema está gerando um lote fixo (6 peças) de uma vez e ultrapassando o limite, em vez de ajustar a quantidade com base no que já existe no estoque.

Como **você não colou o código na sua mensagem**, eu não consigo aplicar a correção exata no seu script. 

No entanto, a lógica para criar esse limitador envolve adicionar uma verificação (um `if`) antes do comando de imprimir/produzir as peças. A ideia é calcular a diferença entre o limite máximo ($S$ ou $s^*$) e o estoque atual, para imprimir apenas o necessário.

Aqui está um exemplo genérico de como essa trava funciona em Python:

```python
# Exemplo de variáveis
estoque_atual = 2
s_star = 6 # Limite máximo que o estoque deve atingir

# Lógica do limitador
if estoque_atual < s_star:
    # Calcula quantas peças realmente precisam ser feitas
    pecas_a_imprimir = s_star - estoque_atual
    
    print(f"Imprimindo {pecas_a_imprimir} peças...")
    estoque_atual += pecas_a_imprimir
else:
    print("Estoque já atingiu o limite s*. Nenhuma peça será impressa.")
