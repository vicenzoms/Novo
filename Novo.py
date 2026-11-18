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


# =====================================================================
# SIMULAÇÃO DUAL-SOURCING (ORIENTADA A EVENTOS) E OTIMIZAÇÃO DA POLÍTICA (s*, s, S)
# =====================================================================
#
# Principais diferenças em relação à versão anterior:
#  - A simulação avança de evento em evento (falha, chegada de pedido, fim de
#    impressão) em vez de hora a hora. Entre eventos o estado não muda, então o
#    resultado é idêntico ao da versão horária, só que muito mais rápido.
#  - Números aleatórios comuns: a réplica r usa a mesma semente para TODAS as
#    políticas, então elas são comparadas contra os mesmos cenários de falha.
#  - Período de aquecimento descartado das métricas (remove o transiente inicial).
#  - Custos separados por componente (pedido, compra, impressão, posse, downtime).
#  - Busca por "successive halving": poucas réplicas para todas as políticas,
#    mais réplicas só para as promissoras.
#  - Espaço de busca expandido automaticamente quando o ótimo cai na borda, e o
#    lote máximo de impressão 3D (Q_3D_lote) também é variável de decisão.
#  - Validação do vencedor com réplicas independentes das usadas na busca
#    (elimina o viés otimista de escolher o mínimo entre muitas médias ruidosas).
#  - Política de referência sem MA (apenas s, S) para quantificar o ganho da MA.

SEMENTE_BUSCA = 0
SEMENTE_VALIDACAO = 1_000_000
SEMENTE_MAPA = 2_000_000

ETAPAS_REPLICAS = (10, 30, 100)   # réplicas acumuladas em cada etapa da busca
FRACAO_SOBREVIVENTES = 0.30       # fração de políticas que passa para a etapa seguinte
MIN_SOBREVIVENTES = 8
N_FINALISTAS = 5
FATORES_LOTE_3D = (0.5, 0.75, 1.0, 1.5, 2.0)
LOTE_SEM_LIMITE = 10_000          # lote tão grande que nunca restringe a impressão
MAX_RODADAS_EXPANSAO = 8
REPLICAS_MAPA = 30

COLUNAS_RESULTADO = ['Custo', 'C_pedido', 'C_compra', 'C_impressao', 'C_posse',
                     'C_downtime', 'Disponibilidade', 'Impressas', 'Ciclos']
IDX_CUSTO, IDX_DISP, IDX_IMPRESSAS = 0, 6, 7


def fmt_brl(valor, casas=2):
    texto = f"{valor:,.{casas}f}"
    return "R$ " + texto.replace(",", "X").replace(".", ",").replace("X", ".")


def fmt_lote(Q):
    return "sem limite" if Q >= LOTE_SEM_LIMITE else str(Q)


def ic95(x):
    x = np.asarray(x, dtype=float)
    if len(x) < 2:
        return 0.0
    return float(1.96 * np.std(x, ddof=1) / np.sqrt(len(x)))


def simular_politica(s_star, s, S, params, seed, registrar=False):
    """
    Simula uma réplica da política (s*, s, S) com fila contínua de impressão 3D.

    Retorna um vetor com COLUNAS_RESULTADO, medido apenas após o aquecimento.
    Com registrar=True devolve (vetor, df_historico, df_eventos), onde o
    histórico tem uma linha por hora em que houve evento (o estoque é constante
    entre linhas, ideal para gráficos em degraus).
    """
    H = int(params['Horizonte_T'])
    W = int(params.get('Warmup_T', 0))
    N = int(params['N'])
    L_rep = int(params['L_rep'])
    L_ef = int(params['L_ef'])
    MTBF_conv = params['MTBF_conv']
    MTBF_print = params['MTBF_print']
    C1, C2, K = params['C1'], params['C2'], params['K']
    Ch, Cb = params['Ch_hora'], params['Cb']
    Q_lote = params.get('Q_3D_lote', 1)
    inf = float('inf')

    # Dois fluxos independentes por réplica: tempos de falha e tipo de peça que falhou
    seq_tempo, seq_tipo = np.random.SeedSequence(int(seed)).spawn(2)
    rng_tempo = np.random.default_rng(seq_tempo)
    rng_tipo = np.random.default_rng(seq_tipo)

    def gerar_tempo_falha(u_3d, paradas):
        ativas = N - paradas
        if ativas <= 0:
            return inf
        taxa_total = ((ativas - u_3d) / MTBF_conv) + (u_3d / MTBF_print)
        return max(1, int(rng_tempo.exponential(1.0 / taxa_total)))

    It, Bt, Ot, Pt, U = S, 0, 0, 0, 0
    Jt, imp_ciclo = 0, 0
    pedidos = {}                      # {hora_de_chegada: quantidade}
    c_K = c_C1 = c_C2 = c_posse = c_down = 0.0
    horas_ind = n_imp = n_ciclos = 0
    historico, eventos = [], []

    T_falha = gerar_tempo_falha(U, Bt)
    T_imp = inf

    def linha_hist(t, q_ch_o=0, q_ch_3=0, q_us_o=0, q_us_3=0):
        return {
            'Tempo_Hora': t, 'Estoque_Original_It': It, 'Em_Transito_Ot': Ot,
            'Estoque_3D_Pt': Pt, 'Impressao_Ativa_Jt': Jt, 'Backlog_Bt': Bt,
            'Posicao_Estoque_IPt': It + Ot - Bt - U, 'Peca_Em_Uso': f"{U} em 3D",
            'Qtd_Chegada_Original': q_ch_o, 'Qtd_Chegada_3D': q_ch_3,
            'Qtd_Usada_Original': q_us_o, 'Qtd_Usada_3D': q_us_3
        }

    t = 1
    while t <= H:
        medido = t > W
        if registrar:
            desc = []
            q_ch_o = q_ch_3 = q_us_o = q_us_3 = 0

        # 1. Conclusão da impressão
        if t == T_imp:
            imp_ciclo += 1
            if medido:
                n_imp += 1
            if registrar:
                q_ch_3 = 1
                desc.append(f"Peça 3D Concluída ({imp_ciclo}/{Q_lote})")
            if Bt > 0:
                Bt -= 1
                U += 1
                if registrar:
                    q_us_3 = 1
                    desc.append("Peça 3D em Uso Imediato")
                T_falha = t + gerar_tempo_falha(U, Bt)
            else:
                Pt += 1
            if Ot > 0 and imp_ciclo < Q_lote:
                Jt = 1
                T_imp = t + L_ef
                if medido:
                    c_C2 += C2
            else:
                Jt = 0
                T_imp = inf

        # 2. Chegada de compras
        q = pedidos.pop(t, None)
        if q is not None:
            It += q
            Ot -= q
            Jt, imp_ciclo, T_imp = 0, 0, inf
            n1 = min(Bt, It)
            Bt -= n1
            It -= n1
            n2 = min(U, It)
            U -= n2
            It -= n2
            if registrar:
                q_ch_o = q
                q_us_o = n1 + n2
                desc.append(f"Chegada Lote Regular (Q={q})")
            T_falha = t + gerar_tempo_falha(U, Bt)

        # 3. Falha
        if t == T_falha:
            if registrar:
                desc.append("Falha no Componente")
            ativas = N - Bt
            if ativas > 0:
                taxa_orig = (ativas - U) / MTBF_conv
                taxa_3d = U / MTBF_print
                prob_orig = taxa_orig / (taxa_orig + taxa_3d)
                if rng_tipo.random() > prob_orig:
                    U -= 1  # a peça que quebrou era 3D
                if It > 0:
                    It -= 1
                    if registrar:
                        q_us_o += 1
                elif Pt > 0:
                    Pt -= 1
                    U += 1
                    if registrar:
                        q_us_3 += 1
                else:
                    Bt += 1
                    if registrar:
                        desc.append("Estoque Esgotado: Backlog")
                T_falha = t + gerar_tempo_falha(U, Bt)

        # 4. Avaliação de gatilhos
        IP_orig = It + Ot - Bt - U
        IP_total = IP_orig + Pt
        if IP_orig <= s:
            Q = S - IP_orig
            pedidos[t + L_rep] = Q
            Ot += Q
            imp_ciclo = 0
            if medido:
                c_K += K
                c_C1 += Q * C1
                n_ciclos += 1
            if registrar:
                desc.append(f"Gatilho s Ativado (Pedido Regular Q={Q})")

        if IP_total <= s_star and Jt == 0 and imp_ciclo < Q_lote and Ot > 0:
            Jt = 1
            T_imp = t + L_ef
            if medido:
                c_C2 += C2
            if registrar:
                desc.append("Gatilho s* Ativado (Disparo 3D)")

        # Custos e indisponibilidade da hora t
        if medido:
            c_posse += It * Ch
            c_down += Bt * Cb
            if Bt > 0:
                horas_ind += 1

        if registrar:
            historico.append(linha_hist(t, q_ch_o, q_ch_3, q_us_o, q_us_3))
            if desc:
                eventos.append({'Tempo_Hora': t, 'Estoque_Original': It,
                                'Estoque_3D': Pt, 'Descricao': " | ".join(desc)})

        # Próximo evento: o estado fica constante até lá
        prox = H + 1
        if T_imp < prox:
            prox = T_imp
        if T_falha < prox:
            prox = T_falha
        if pedidos:
            chegada = min(pedidos)
            if chegada < prox:
                prox = chegada
        prox = int(max(t + 1, prox))

        ini = max(t + 1, W + 1)
        fim = prox - 1
        if fim >= ini:
            n = fim - ini + 1
            c_posse += n * It * Ch
            c_down += n * Bt * Cb
            if Bt > 0:
                horas_ind += n
        t = prox

    horas_medidas = max(1, H - W)
    custo = c_K + c_C1 + c_C2 + c_posse + c_down
    resultado = np.array([custo, c_K, c_C1, c_C2, c_posse, c_down,
                          1.0 - horas_ind / horas_medidas, n_imp, n_ciclos], dtype=float)

    if registrar:
        if not historico or historico[-1]['Tempo_Hora'] < H:
            historico.append(linha_hist(H))
        df_ev = pd.DataFrame(eventos, columns=['Tempo_Hora', 'Estoque_Original', 'Estoque_3D', 'Descricao'])
        return resultado, pd.DataFrame(historico), df_ev
    return resultado


def avaliar_politica(politica, params, sementes):
    """Simula a política (S, s, s*, Q_lote) nas sementes dadas. Retorna matriz (n_replicas x 9)."""
    S, s, s_star, Q = politica
    p = dict(params)
    p['Q_3D_lote'] = Q
    return np.array([simular_politica(s_star, s, S, p, sd) for sd in sementes])


# ---------------------------------------------------------------------
# Espaço de busca
# ---------------------------------------------------------------------

def _valores_grade(limite_superior, passo):
    """0, passo, 2*passo, ... sempre incluindo limite_superior."""
    return sorted(set(range(0, limite_superior + 1, passo)) | {limite_superior})


def gerar_politicas(S_vals, Q_vals, usar_ma):
    """
    Gera tuplas (S, s, s*, Q_lote) com s* <= s < S. Para S grande usa uma grade
    mais grossa (passo = S // 10); o refinamento local completa a busca depois.
    Sem MA, apenas (S, s) importam (s* = 0 e Q_lote = 0 desligam a impressão).
    """
    politicas = []
    for S in S_vals:
        passo = max(1, S // 10)
        for s in _valores_grade(S - 1, passo):
            if usar_ma:
                for s_star in _valores_grade(s, passo):
                    for Q in Q_vals:
                        politicas.append((S, s, s_star, Q))
            else:
                politicas.append((S, s, 0, 0))
    return politicas


def _media_custo(cache, pol):
    return cache[pol][:, IDX_CUSTO].mean()


def _notificar(ctx):
    cb = ctx.get('cb')
    if cb is None:
        return
    frac = min(0.99, ctx['feitas'] / max(1, ctx['total']))
    if frac - ctx['ultimo'] >= 0.01:
        ctx['ultimo'] = frac
        cb(frac, ctx['rotulo'])


def _garantir_replicas(pol, n_rep, params, cache, ctx):
    atual = cache.get(pol)
    feitas = 0 if atual is None else len(atual)
    if feitas >= n_rep:
        return
    novo = avaliar_politica(pol, params, range(SEMENTE_BUSCA + feitas, SEMENTE_BUSCA + n_rep))
    cache[pol] = novo if atual is None else np.vstack([atual, novo])
    ctx['feitas'] += n_rep - feitas
    _notificar(ctx)


def _estimar_simulacoes(n_pol):
    vivas, anterior, total = n_pol, 0, 0
    for n_rep in ETAPAS_REPLICAS:
        total += vivas * (n_rep - anterior)
        anterior = n_rep
        vivas = min(vivas, max(MIN_SOBREVIVENTES, int(np.ceil(vivas * FRACAO_SOBREVIVENTES))))
    return total


def _successive_halving(politicas, params, cache, ctx):
    """Réplicas crescentes (sementes comuns) e descarte das piores a cada etapa."""
    vivas = list(politicas)
    for i, n_rep in enumerate(ETAPAS_REPLICAS):
        for pol in vivas:
            _garantir_replicas(pol, n_rep, params, cache, ctx)
        vivas.sort(key=lambda p: _media_custo(cache, p))
        if i < len(ETAPAS_REPLICAS) - 1:
            manter = max(MIN_SOBREVIVENTES, int(np.ceil(len(vivas) * FRACAO_SOBREVIVENTES)))
            vivas = vivas[:manter]
    return vivas


def otimizar_politica(S_base, params, usar_ma=True, Q_base=1, progresso=None, rotulo="Otimizando..."):
    """
    Busca a melhor política. Retorna dict com os finalistas (ordenados pelo custo
    da busca) e informações sobre o espaço explorado.
    """
    cache = {}
    ctx = {'feitas': 0, 'total': 1, 'ultimo': -1.0, 'cb': progresso, 'rotulo': rotulo}

    S_lo = max(1, S_base - 2)
    S_hi = S_base + (2 if usar_ma else 6)
    if usar_ma:
        Q_vals = sorted({max(1, int(round(Q_base * f))) for f in FATORES_LOTE_3D} | {LOTE_SEM_LIMITE})
    else:
        Q_vals = [0]

    avaliadas, ranking, rodadas = set(), [], 0
    while rodadas < MAX_RODADAS_EXPANSAO:
        rodadas += 1
        novas = [p for p in gerar_politicas(range(S_lo, S_hi + 1), Q_vals, usar_ma)
                 if p not in avaliadas]
        if not novas:
            break
        avaliadas.update(novas)
        ctx['total'] += _estimar_simulacoes(len(novas))
        sobreviventes = _successive_halving(novas, params, cache, ctx)
        ranking = sorted(set(ranking) | set(sobreviventes), key=lambda p: _media_custo(cache, p))

        # Se o ótimo caiu na borda do espaço de busca, amplia e repete
        S_b, Q_b = ranking[0][0], ranking[0][3]
        mudou = False
        if S_b == S_hi:
            S_hi += 2
            mudou = True
        if S_b == S_lo and S_lo > 1:
            S_lo = max(1, S_lo - 2)
            mudou = True
        if usar_ma:
            if Q_b == Q_vals[0] and Q_vals[0] > 1:
                Q_vals = sorted(set(Q_vals) | {max(1, Q_vals[0] // 2)})
                mudou = True
        if not mudou:
            break

    # Refinamento local (só necessário quando a grade foi grossa)
    vizinhos = set()
    for (S, s, s_star, Q) in ranking[:3]:
        raio = max(1, S // 10) - 1
        if raio == 0:
            continue
        for ds in range(-raio, raio + 1):
            for dss in (range(-raio, raio + 1) if usar_ma else (0,)):
                s2, ss2 = s + ds, s_star + dss
                if 0 <= ss2 <= s2 <= S - 1:
                    vizinhos.add((S, s2, ss2, Q))
    vizinhos -= avaliadas
    if vizinhos:
        ctx['total'] += len(vizinhos) * ETAPAS_REPLICAS[-1]
        for pol in vizinhos:
            _garantir_replicas(pol, ETAPAS_REPLICAS[-1], params, cache, ctx)
        avaliadas |= vizinhos
        ranking = sorted(set(ranking) | vizinhos, key=lambda p: _media_custo(cache, p))

    if progresso is not None:
        progresso(1.0, rotulo)

    return {
        'finalistas': ranking[:N_FINALISTAS],
        'n_politicas': len(avaliadas),
        'S_min': S_lo, 'S_max': S_hi, 'Q_vals': Q_vals, 'rodadas': rodadas,
    }


# ---------------------------------------------------------------------
# Execução completa: busca, validação independente, mapa e trajetória
# ---------------------------------------------------------------------

def executar_otimizacao(e, progresso=None):
    """
    e: dict com MTBF_conv, MTBF_print, L_rep, L_ef, C1, C2, K, Cb, Ch_ano,
       R_PCT, Anos, Aquecimento, N, N_validacao.
    progresso: função opcional (fracao, texto).
    """
    def faixa(a, b):
        def f(frac, texto):
            if progresso is not None:
                progresso(a + (b - a) * min(1.0, max(0.0, frac)), texto)
        return f

    risco = e['R_PCT'] / 100.0
    lambda_hora = 1.0 / e['MTBF_conv']
    m_leadtime = lambda_hora * e['N'] * e['L_rep']
    Q_base = max(1, int(np.ceil(poisson.ppf(1 - risco, m_leadtime))))
    _, S_teto, _ = calcular_poisson(lambda_hora, e['N'], e['L_rep'], risco)
    S_base = max(1, S_teto)

    anos = int(e['Anos'])
    params = {
        'Horizonte_T': int((anos + e['Aquecimento']) * 8760),
        'Warmup_T': int(e['Aquecimento'] * 8760),
        'N': e['N'], 'L_rep': e['L_rep'], 'L_ef': e['L_ef'],
        'MTBF_conv': e['MTBF_conv'], 'MTBF_print': e['MTBF_print'],
        'C1': e['C1'], 'C2': e['C2'], 'K': e['K'],
        'Ch_hora': e['Ch_ano'] / 8760.0, 'Cb': e['Cb'],
        'Q_3D_lote': Q_base,
    }

    # 1) Busca: referência sem MA e política com MA
    busca_base = otimizar_politica(S_base, params, usar_ma=False, Q_base=Q_base,
                                   progresso=faixa(0.00, 0.20),
                                   rotulo="Buscando a melhor política sem MA (s, S)...")
    busca_ma = otimizar_politica(S_base, params, usar_ma=True, Q_base=Q_base,
                                 progresso=faixa(0.20, 0.60),
                                 rotulo="Buscando a melhor política com MA (s*, s, S, lote 3D)...")

    # 2) Validação com réplicas independentes das usadas na busca (mesmas sementes
    #    para todas as políticas, o que permite comparações pareadas)
    n_val = int(e['N_validacao'])
    sementes = range(SEMENTE_VALIDACAO, SEMENTE_VALIDACAO + n_val)
    candidatas = [('ma', p) for p in busca_ma['finalistas']] + \
                 [('base', p) for p in busca_base['finalistas'][:3]]
    validacao = {}
    for i, (tipo, pol) in enumerate(candidatas):
        validacao[(tipo, pol)] = avaliar_politica(pol, params, sementes)
        faixa(0.60, 0.80)((i + 1) / len(candidatas), "Validando finalistas com réplicas independentes...")

    fin_ma = busca_ma['finalistas']
    fin_base = busca_base['finalistas'][:3]
    pol_ma = min(fin_ma, key=lambda p: validacao[('ma', p)][:, IDX_CUSTO].mean())
    pol_base = min(fin_base, key=lambda p: validacao[('base', p)][:, IDX_CUSTO].mean())
    a_ma = validacao[('ma', pol_ma)]
    a_base = validacao[('base', pol_base)]

    # Tabela dos finalistas, com teste pareado contra a política recomendada
    linhas = []
    for pol in sorted(fin_ma, key=lambda p: validacao[('ma', p)][:, IDX_CUSTO].mean()):
        a = validacao[('ma', pol)]
        dif = a[:, IDX_CUSTO] - a_ma[:, IDX_CUSTO]
        if pol == pol_ma:
            status = "Recomendada"
        else:
            status = "Sem diferença significativa" if abs(dif.mean()) <= ic95(dif) else "Pior"
        linhas.append({
            'S': pol[0], 's': pol[1], 's*': pol[2], 'Lote 3D': pol[3],
            'Custo anual': a[:, IDX_CUSTO].mean() / anos,
            'IC95': ic95(a[:, IDX_CUSTO]) / anos,
            'Disponibilidade': a[:, IDX_DISP].mean(),
            'Impressas/ano': a[:, IDX_IMPRESSAS].mean() / anos,
            'Status': status,
        })
    df_finalistas = pd.DataFrame(linhas)

    # KPIs com intervalo de confiança e economia pareada (mesmas sementes)
    dif_custo = a_base[:, IDX_CUSTO] - a_ma[:, IDX_CUSTO]
    dif_disp = a_ma[:, IDX_DISP] - a_base[:, IDX_DISP]
    custo_base_medio = a_base[:, IDX_CUSTO].mean()
    kpi = {
        'custo_ano_ma': a_ma[:, IDX_CUSTO].mean() / anos,
        'ic_custo_ma': ic95(a_ma[:, IDX_CUSTO]) / anos,
        'custo_ano_base': custo_base_medio / anos,
        'disp_ma': a_ma[:, IDX_DISP].mean(),
        'ic_disp_ma': ic95(a_ma[:, IDX_DISP]),
        'disp_base': a_base[:, IDX_DISP].mean(),
        'dif_disp_pp': dif_disp.mean() * 100,
        'impressas_ano': a_ma[:, IDX_IMPRESSAS].mean() / anos,
        'economia_ano': dif_custo.mean() / anos,
        'ic_economia': ic95(dif_custo) / anos,
        'economia_pct': dif_custo.mean() / custo_base_medio * 100 if custo_base_medio else 0.0,
        'ic_economia_pct': ic95(dif_custo) / custo_base_medio * 100 if custo_base_medio else 0.0,
    }

    # 3) Mapa de custo (s x s*) para o S e o lote ótimos
    S_o, s_o, ss_o, Q_o = pol_ma
    pares = {(s, ss) for (_, s, ss, _) in gerar_politicas([S_o], [Q_o], True)} | {(s_o, ss_o)}
    sementes_mapa = range(SEMENTE_MAPA, SEMENTE_MAPA + REPLICAS_MAPA)
    linhas_mapa = []
    for i, (s, ss) in enumerate(sorted(pares)):
        a = avaliar_politica((S_o, s, ss, Q_o), params, sementes_mapa)
        linhas_mapa.append({'s': s, 's*': ss, 'Custo anual': a[:, IDX_CUSTO].mean() / anos})
        faixa(0.80, 0.92)((i + 1) / len(pares), "Calculando o mapa de custo (s x s*)...")
    df_mapa = pd.DataFrame(linhas_mapa)

    # 4) Trajetória da réplica mais próxima da mediana de custo (mesma semente da validação)
    custos = a_ma[:, IDX_CUSTO]
    idx_med = int(np.argmin(np.abs(custos - np.median(custos))))
    semente_med = SEMENTE_VALIDACAO + idx_med
    p_hist = dict(params)
    p_hist['Q_3D_lote'] = Q_o
    res_med, df_hist, df_ev = simular_politica(ss_o, s_o, S_o, p_hist, semente_med, registrar=True)
    faixa(0.92, 1.0)(1.0, "Finalizando...")

    return {
        'politica': pol_ma, 'politica_base': pol_base,
        'amostras_ma': a_ma, 'amostras_base': a_base,
        'finalistas': df_finalistas, 'mapa': df_mapa, 'kpi': kpi,
        'anos': anos, 'params': params,
        'df_hist': df_hist, 'df_ev': df_ev,
        'replica_mediana': {'semente': semente_med, 'custo_ano': res_med[IDX_CUSTO] / anos},
        'busca': {
            'S_teto': S_base, 'Q_base': Q_base,
            'ma': {k: busca_ma[k] for k in ('n_politicas', 'S_min', 'S_max', 'Q_vals', 'rodadas')},
            'base': {k: busca_base[k] for k in ('n_politicas', 'S_min', 'S_max', 'rodadas')},
            'etapas': ETAPAS_REPLICAS, 'n_validacao': n_val, 'replicas_mapa': REPLICAS_MAPA,
        },
    }


# ---------------------------------------------------------------------
# Figuras (Plotly)
# ---------------------------------------------------------------------

COR_MA, COR_BASE = '#2E7D32', '#9E9E9E'


def _estilo_eixos(fig, **kwargs):
    fig.update_xaxes(showline=True, linewidth=1, linecolor='black', gridcolor='#e6e6e6', **kwargs)
    fig.update_yaxes(showline=True, linewidth=1, linecolor='black', gridcolor='#e6e6e6')


def _layout_base(fig, altura):
    fig.update_layout(height=altura, plot_bgcolor='white', paper_bgcolor='white',
                      font=dict(color='black'), margin=dict(t=40, b=40, l=60, r=30))


def figura_mapa_calor(r):
    S_o, s_o, ss_o, Q_o = r['politica']
    df = r['mapa']
    piv = df.pivot(index='s*', columns='s', values='Custo anual').sort_index()
    xs = [str(c) for c in piv.columns]
    ys = [str(i) for i in piv.index]
    fig = go.Figure(go.Heatmap(
        z=piv.values, x=xs, y=ys, colorscale='YlGn_r', hoverongaps=False,
        colorbar=dict(title="R$/ano"),
        hovertemplate="s=%{x} | s*=%{y}<br>Custo anual: R$ %{z:,.0f}<extra></extra>"))
    fig.add_trace(go.Scatter(
        x=[str(s_o)], y=[str(ss_o)], mode='markers', showlegend=False,
        marker=dict(symbol='star', size=18, color='#D32F2F', line=dict(color='white', width=1)),
        hovertemplate="Política recomendada<extra></extra>"))
    _layout_base(fig, 420)
    fig.update_xaxes(title_text="Ponto de encomenda regular (s)", type='category')
    fig.update_yaxes(title_text="Gatilho de impressão (s*)", type='category')
    return fig


def figura_composicao_custo(r):
    anos = r['anos']
    S_o, s_o, ss_o, Q_o = r['politica']
    S_b, s_b, _, _ = r['politica_base']
    rotulos = [f"Sem MA<br>(s={s_b}, S={S_b})", f"Com MA<br>(s*={ss_o}, s={s_o}, S={S_o})"]
    componentes = [('Pedido fixo (K)', 1, '#90A4AE'), ('Compra de peças originais (C1)', 2, '#2E7D32'),
                   ('Impressão 3D (C2)', 3, '#9C27B0'), ('Posse de estoque', 4, '#FFB300'),
                   ('Downtime', 5, '#E53935')]
    fig = go.Figure()
    for nome, idx, cor in componentes:
        valores = [r['amostras_base'][:, idx].mean() / anos, r['amostras_ma'][:, idx].mean() / anos]
        fig.add_trace(go.Bar(name=nome, x=rotulos, y=valores, marker_color=cor,
                             hovertemplate=nome + ": R$ %{y:,.0f}/ano<extra></extra>"))
    totais = [r['kpi']['custo_ano_base'], r['kpi']['custo_ano_ma']]
    for x, tot in zip(rotulos, totais):
        fig.add_annotation(x=x, y=tot, text=fmt_brl(tot, 0), showarrow=False, yshift=12)
    fig.update_layout(barmode='stack', legend=dict(orientation="h", y=-0.25))
    _layout_base(fig, 420)
    _estilo_eixos(fig)
    fig.update_yaxes(title_text="Custo anual (R$)")
    return fig


def figura_histograma(r):
    anos = r['anos']
    fig = go.Figure()
    fig.add_trace(go.Histogram(x=r['amostras_base'][:, IDX_CUSTO] / anos, name='Sem MA',
                               marker_color=COR_BASE, opacity=0.65, nbinsx=30))
    fig.add_trace(go.Histogram(x=r['amostras_ma'][:, IDX_CUSTO] / anos, name='Com MA',
                               marker_color=COR_MA, opacity=0.65, nbinsx=30))
    fig.update_layout(barmode='overlay', legend=dict(orientation="h", y=-0.25))
    _layout_base(fig, 420)
    _estilo_eixos(fig)
    fig.update_xaxes(title_text="Custo anual na réplica (R$)")
    fig.update_yaxes(title_text="Nº de réplicas")
    return fig


def _recortar_janela(df, ini, fim):
    """Linhas dentro da janela + pontos de borda para o gráfico em degraus não ficar truncado."""
    antes = df[df['Tempo_Hora'] < ini]
    dentro = df[(df['Tempo_Hora'] >= ini) & (df['Tempo_Hora'] <= fim)]
    partes = []
    if len(antes) and (len(dentro) == 0 or dentro['Tempo_Hora'].iloc[0] > ini):
        borda = antes.iloc[[-1]].copy()
        borda['Tempo_Hora'] = ini
        for c in ('Qtd_Chegada_Original', 'Qtd_Chegada_3D', 'Qtd_Usada_Original', 'Qtd_Usada_3D'):
            borda[c] = 0
        partes.append(borda)
    partes.append(dentro)
    sub = pd.concat(partes) if len(partes) > 1 else dentro.copy()
    if len(sub) and sub['Tempo_Hora'].iloc[-1] < fim:
        fecha = sub.iloc[[-1]].copy()
        fecha['Tempo_Hora'] = fim
        for c in ('Qtd_Chegada_Original', 'Qtd_Chegada_3D', 'Qtd_Usada_Original', 'Qtd_Usada_3D'):
            fecha[c] = 0
        sub = pd.concat([sub, fecha])
    return sub, dentro


def figura_trajetoria(r, janela):
    S_o, s_o, ss_o, Q_o = r['politica']
    W = r['params']['Warmup_T']
    ini, fim = janela
    df_sub, df_in = _recortar_janela(r['df_hist'], ini, fim)

    chegadas_3d = df_in[df_in['Qtd_Chegada_3D'] > 0]
    chegadas_orig = df_in[df_in['Qtd_Chegada_Original'] > 0]
    uso_3d = df_in[df_in['Qtd_Usada_3D'] > 0]

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.08, row_heights=[0.65, 0.35],
                        subplot_titles=("Nível de Estoque Original e Linhas de Disparo",
                                        "Peças Impressas 3D em Reserva (Pt)"))
    fig.add_trace(go.Scatter(x=df_sub['Tempo_Hora'], y=df_sub['Estoque_Original_It'], mode='lines',
                             name='Estoque Original (It)', line=dict(color='#2E7D32', width=2, shape='hv')),
                  row=1, col=1)
    for valor, nome, cor in ((S_o, f"Teto S ({S_o})", 'gray'), (s_o, f"Gatilho s ({s_o})", 'orange'),
                             (ss_o, f"Gatilho MA s* ({ss_o})", 'red')):
        fig.add_trace(go.Scatter(x=[ini, fim], y=[valor, valor], mode='lines', name=nome,
                                 line=dict(color=cor, dash='dash')), row=1, col=1)
    fig.add_trace(go.Scatter(x=chegadas_orig['Tempo_Hora'], y=chegadas_orig['Estoque_Original_It'],
                             mode='markers', name='Chegada Pedido Regular',
                             marker=dict(symbol='triangle-up', size=10, color='blue')), row=1, col=1)

    fig.add_trace(go.Scatter(x=df_sub['Tempo_Hora'], y=df_sub['Estoque_3D_Pt'], mode='lines',
                             name='Reserva 3D (Pt)', line=dict(color='#9C27B0', width=2, shape='hv')),
                  row=2, col=1)
    fig.add_trace(go.Scatter(x=chegadas_3d['Tempo_Hora'], y=chegadas_3d['Estoque_3D_Pt'], mode='markers',
                             name='Conclusão Impressão 3D', marker=dict(symbol='star', size=11, color='purple')),
                  row=2, col=1)
    fig.add_trace(go.Scatter(x=uso_3d['Tempo_Hora'], y=uso_3d['Estoque_3D_Pt'], mode='markers',
                             name='Uso de Peça 3D', marker=dict(symbol='square', size=8, color='magenta')),
                  row=2, col=1)

    if W > 0 and ini < W:
        for linha in (1, 2):
            fig.add_vrect(x0=ini, x1=min(fim, W), fillcolor='lightgray', opacity=0.3, line_width=0,
                          row=linha, col=1,
                          annotation_text="Aquecimento" if linha == 1 else None,
                          annotation_position="top left")

    fig.update_layout(height=650, hovermode="x unified",
                      legend=dict(orientation="h", yanchor="bottom", y=1.06, xanchor="center", x=0.5),
                      margin=dict(t=60, b=40, l=60, r=40), plot_bgcolor='white', paper_bgcolor='white',
                      font=dict(color='black'))
    _estilo_eixos(fig)
    fig.update_xaxes(title_text="Tempo (Horas)", row=2, col=1)
    fig.update_yaxes(title_text="Peças Originais", row=1, col=1)
    fig.update_yaxes(title_text="Peças 3D em Reserva", row=2, col=1)
    return fig


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
        col_m2.metric("Custo Total (Inventário Atual)", fmt_brl(custo_total))
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
        col_m3.metric("Custo Total (Inventário Ótimo)", fmt_brl(custo_total))

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
    st.header(menu[2] + " - Simulação Dual-Sourcing com Fila Contínua MA")
    st.write("Dimensionamento otimizado de política (s*, s, S) com produção continuada de peças 3D durante o lead time de ressuprimento.")

    st.subheader("Parâmetros de Manutenção e Falha")
    col1, col2 = st.columns(2)
    MTBF_conv = col1.number_input("MTBF Peça Original (horas)", min_value=100, value=5000, step=500)
    MTBF_print = col2.number_input("MTBF Peça Impressa FDM (horas)", min_value=100, value=2500, step=500)

    st.subheader("Parâmetros Logísticos (Lead Times)")
    col3, col4 = st.columns(2)
    L_rep = col3.number_input("Lead Time do Fornecedor Original (horas)", min_value=1, value=1500, step=24)
    L_ef = col4.number_input("Tempo de Impressão de 1 Unidade 3D (horas)", min_value=1, value=8, step=1)

    st.subheader("Parâmetros de Custo (R$)")
    col5, col6, col7 = st.columns(3)
    C1 = col5.number_input("Custo Unitário Original (C1)", min_value=0.0, value=300.0)
    C2 = col6.number_input("Custo de Impressão Unitário (C2)", min_value=0.0, value=50.0)
    K = col7.number_input("Custo Fixo por Pedido (K)", min_value=0.0, value=200.0)

    col8, col9 = st.columns(2)
    Cb = col8.number_input("Custo de Downtime por Hora (Cb)", min_value=0.0, value=3000.0)
    Ch_ano = col9.number_input("Custo de Posse Anual (R$/Unidade)", min_value=0.0, value=50.0)

    st.subheader("Parâmetros de Otimização e Fila 3D")
    col10, col11, col12 = st.columns(3)
    R_PCT = col10.number_input("Risco Alvo para Teto S (%)", min_value=0.01, max_value=99.99, value=5.00)
    Anos_Simulacao = col11.number_input("Horizonte de Simulação (Anos)", min_value=1, value=5)
    N_Maquinas = col12.number_input("Número de Máquinas (N)", min_value=1, value=10)

    col13, col14 = st.columns(2)
    Anos_Aquecimento = col13.number_input(
        "Aquecimento da Simulação (Anos)", min_value=0, value=0, step=1,
        help="Período inicial descartado das métricas. Com 0 (padrão), o custo de formar o estoque no início "
             "(inclusive imprimir peças 3D logo na primeira reposição) entra na conta. Use valores maiores "
             "somente se quiser avaliar o regime estacionário: políticas que investem no começo ficam favorecidas.")
    N_Validacao = col14.number_input(
        "Réplicas de Validação", min_value=100, value=1000, step=100,
        help="Réplicas independentes das usadas na busca, para estimar custo e disponibilidade da política "
             "recomendada com intervalo de confiança.")

    botao_ma = st.button("Executar Simulação e Otimizar (s*, s, S)")

    if botao_ma:
        entradas = {
            'MTBF_conv': MTBF_conv, 'MTBF_print': MTBF_print, 'L_rep': L_rep, 'L_ef': L_ef,
            'C1': C1, 'C2': C2, 'K': K, 'Cb': Cb, 'Ch_ano': Ch_ano, 'R_PCT': R_PCT,
            'Anos': Anos_Simulacao, 'Aquecimento': Anos_Aquecimento, 'N': N_Maquinas,
            'N_validacao': N_Validacao,
        }
        chave = tuple(sorted(entradas.items()))
        memo = st.session_state.setdefault('ma_memo', {})

        if chave in memo:
            st.session_state['ma_resultado'] = memo[chave]
            st.info("Estes parâmetros já foram otimizados nesta sessão: resultado reaproveitado.")
        else:
            barra = st.progress(0.0, text="Iniciando a otimização...")
            resultado = executar_otimizacao(
                entradas, progresso=lambda frac, texto: barra.progress(min(1.0, float(frac)), text=texto))
            barra.empty()
            memo[chave] = resultado
            while len(memo) > 4:
                memo.pop(next(iter(memo)))
            st.session_state['ma_resultado'] = resultado

    if 'ma_resultado' in st.session_state:
        r = st.session_state['ma_resultado']
        k = r['kpi']
        S_o, s_o, ss_o, Q_o = r['politica']
        S_b, s_b, _, _ = r['politica_base']

        st.success("Otimização Concluída!")

        st.markdown("### Política Recomendada (s*, s, S)")
        rc1, rc2, rc3, rc4 = st.columns(4)
        rc1.metric(label="Gatilho de Impressão (s*)", value=ss_o, delta="Preventivo/Emergência", delta_color="off")
        rc2.metric(label="Ponto de Encomenda Regular (s)", value=s_o, delta="Pedido ao Fornecedor", delta_color="off")
        rc3.metric(label="Teto de Inventário (S)", value=S_o, delta="Nível Alvo", delta_color="off")
        rc4.metric(label="Lote Máx. de Impressão 3D", value=fmt_lote(Q_o), delta="Por ciclo de ressuprimento", delta_color="off")

        st.divider()
        st.markdown("### Performance Projetada da Política")
        st.caption(f"Médias de {r['busca']['n_validacao']} réplicas independentes das usadas na busca, com intervalo de confiança de 95%.")
        p1, p2, p3, p4 = st.columns(4)
        p1.metric(label="Custo Médio Operacional (por Ano)", value=fmt_brl(k['custo_ano_ma']))
        p1.caption(f"IC 95%: ± {fmt_brl(k['ic_custo_ma'])}")
        p2.metric(label="Disponibilidade da Fábrica (KPI)", value=f"{k['disp_ma'] * 100:.3f}%",
                  delta=f"{k['dif_disp_pp']:+.3f} p.p. vs. sem MA")
        p2.caption(f"IC 95%: ± {k['ic_disp_ma'] * 100:.3f} p.p.")
        p3.metric(label="Média de Peças Impressas por Ano", value=f"{k['impressas_ano']:.2f} peças/ano")
        p4.metric(label="Economia Anual vs. Sem MA", value=fmt_brl(k['economia_ano']),
                  delta=f"{k['economia_pct']:+.1f}% do custo sem MA")
        p4.caption(f"IC 95%: ± {fmt_brl(k['ic_economia'])} (± {k['ic_economia_pct']:.1f} p.p.) · "
                   f"referência sem MA: s={s_b}, S={S_b}")

        if k['economia_ano'] + k['ic_economia'] < 0:
            st.warning("Com estes parâmetros, a melhor política sem MA é significativamente mais barata que a melhor "
                       "política com MA (IC 95%). A impressão 3D não se paga neste cenário.")
        elif k['economia_ano'] - k['ic_economia'] <= 0:
            st.info("A economia da MA sobre a política sem MA não é estatisticamente distinguível de zero "
                    "(o IC 95% inclui zero). Aumente as réplicas de validação para refinar a estimativa.")

        # --- Comparativo e composição do custo ---
        st.divider()
        st.markdown("### De Onde Vem o Custo e o Que a MA Muda")
        cc1, cc2 = st.columns(2)
        with cc1:
            st.markdown("**Composição do custo anual**")
            st.plotly_chart(figura_composicao_custo(r), use_container_width=True)
        with cc2:
            st.markdown("**Distribuição do custo anual entre as réplicas**")
            st.plotly_chart(figura_histograma(r), use_container_width=True)

        # --- Mapa de calor e finalistas ---
        st.divider()
        st.markdown("### Sensibilidade da Política")
        st.caption(f"Custo anual para cada combinação (s, s*), com S={S_o} e lote máx. 3D = {fmt_lote(Q_o)}. "
                   "A estrela marca a política recomendada; regiões de cor parecida indicam políticas praticamente equivalentes.")
        st.plotly_chart(figura_mapa_calor(r), use_container_width=True)

        st.markdown("**Melhores políticas encontradas (validadas com réplicas independentes)**")
        df_fin = r['finalistas']
        df_tab = pd.DataFrame({
            'S': df_fin['S'], 's': df_fin['s'], 's*': df_fin['s*'],
            'Lote 3D máx.': df_fin['Lote 3D'].apply(fmt_lote),
            'Custo anual': df_fin['Custo anual'].apply(fmt_brl),
            'IC 95% (±)': df_fin['IC95'].apply(fmt_brl),
            'Disponibilidade': df_fin['Disponibilidade'].apply(lambda v: f"{v * 100:.3f}%"),
            'Peças 3D/ano': df_fin['Impressas/ano'].apply(lambda v: f"{v:.2f}"),
            'Comparada à recomendada': df_fin['Status'],
        })
        st.dataframe(df_tab, use_container_width=True, hide_index=True)
        n_equiv = int((df_fin['Status'] == "Sem diferença significativa").sum())
        if n_equiv > 0:
            st.info(f"{n_equiv} política(s) finalista(s) não diferem de forma estatisticamente significativa da recomendada "
                    "(teste pareado, 95%). A escolha entre elas pode considerar outros critérios, como menor estoque ou menos peças impressas.")

        with st.expander("Detalhes da busca"):
            b = r['busca']
            st.write(
                f"- Teto analítico de partida (Poisson, risco alvo): S = {b['S_teto']}; lote 3D de referência: {b['Q_base']}.\n"
                f"- Com MA: {b['ma']['n_politicas']} políticas avaliadas, S de {b['ma']['S_min']} a {b['ma']['S_max']}, "
                f"lotes 3D testados: {', '.join(fmt_lote(q) for q in b['ma']['Q_vals'])} ({b['ma']['rodadas']} rodada(s) de expansão do espaço).\n"
                f"- Sem MA (referência): {b['base']['n_politicas']} políticas, S de {b['base']['S_min']} a {b['base']['S_max']}.\n"
                f"- Busca em etapas de {' → '.join(str(n) for n in b['etapas'])} réplicas, descartando as piores a cada etapa; "
                "todas as políticas enfrentam os mesmos cenários de falha (sementes comuns).\n"
                f"- Validação final com {b['n_validacao']} réplicas independentes; mapa de custo com {b['replicas_mapa']} réplicas por ponto.\n"
                f"- Aquecimento descartado: {r['params']['Warmup_T'] / 8760:.0f} ano(s).")

        # --- Trajetória ---
        st.divider()
        st.markdown("###  Trajetória do Estoque Físico, Reservas 3D e Ativação em Sequência")
        rm = r['replica_mediana']
        st.caption(f"Réplica representativa: a mais próxima da mediana de custo (semente {rm['semente']}, "
                   f"{fmt_brl(rm['custo_ano'])} por ano), simulada com a política recomendada.")

        max_horas = r['params']['Horizonte_T']
        janela_horas = st.slider(
            "Selecione o intervalo de horas para visualizar o fluxo:",
            min_value=1,
            max_value=max_horas,
            value=(1, min(8760 * 2, max_horas)),
            step=100
        )

        fig = figura_trajetoria(r, janela_horas)
        st.plotly_chart(fig, use_container_width=True)

        d1, d2 = st.columns(2)
        d1.download_button("Baixar gráfico (HTML interativo)",
                           data=fig.to_html(include_plotlyjs='cdn').encode('utf-8'),
                           file_name="trajetoria_estoque.html", mime="text/html")
        if d2.button("Preparar PNG de alta resolução"):
            try:
                st.session_state['ma_png'] = (janela_horas, fig.to_image(format="png", scale=3, width=1200, height=700))
            except Exception:
                st.session_state['ma_png'] = None
                st.warning("Para exportar em PNG instale o pacote kaleido (pip install kaleido). O HTML interativo funciona sem ele.")
        png = st.session_state.get('ma_png')
        if png and tuple(png[0]) == tuple(janela_horas):
            d2.download_button("Baixar PNG", data=png[1], file_name="figura1_alta_res.png", mime="image/png")

        st.markdown("###  Diário de Eventos do Período Selecionado")
        df_ev = r['df_ev']
        df_ev_sub = df_ev[(df_ev['Tempo_Hora'] >= janela_horas[0]) & (df_ev['Tempo_Hora'] <= janela_horas[1])]
        st.dataframe(df_ev_sub, use_container_width=True, hide_index=True)
