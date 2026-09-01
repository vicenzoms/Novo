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

    It, Bt, Ot, Pt, U_3D = S, 0, 0, 0, 0
    Jt, impressas_ciclo_atual = 0, 0
    Custo_Total, Horas_Indisponivel = 0, 0
    Pecas_Impressas_Total, Ciclos_Ressuprimento = 0, 0
    pedidos_convencionais = []

    def gerar_tempo_falha(u_3d, paradas):
        ativas = N - paradas
        if ativas <= 0: return float('inf')
        taxa_total = ((ativas - u_3d) / MTBF_conv) + (u_3d / MTBF_print)
        return max(1, int(np.random.exponential(1.0 / taxa_total)))

    Tempo_Proxima_Falha = gerar_tempo_falha(U_3D, Bt)
    Tempo_Chegada_Impressao = float('inf')

    for t in range(1, Horizonte_T + 1):
        # 1. Conclusão da Impressão
        if t == Tempo_Chegada_Impressao:
            Pecas_Impressas_Total += 1
            impressas_ciclo_atual += 1
            if Bt > 0:
                Bt -= 1
                U_3D += 1
                Tempo_Proxima_Falha = t + gerar_tempo_falha(U_3D, Bt)
            else:
                Pt += 1
            
            if Ot > 0 and impressas_ciclo_atual < Q_3D_lote:
                Jt = 1
                Tempo_Chegada_Impressao = t + L_ef
                Custo_Total += C2
            else:
                Jt = 0
                Tempo_Chegada_Impressao = float('inf')

        # 2. Chegada de Compras
        chegaram_agora = [p for p in pedidos_convencionais if p['chegada'] == t]
        if chegaram_agora:
            for pedido in chegaram_agora:
                It += pedido['qtd']
                Ot -= pedido['qtd']
            pedidos_convencionais = [p for p in pedidos_convencionais if p['chegada'] != t]
            Jt, impressas_ciclo_atual = 0, 0
            Tempo_Chegada_Impressao = float('inf')
            
            while Bt > 0 and It > 0:
                Bt -= 1
                It -= 1
            while U_3D > 0 and It > 0:
                U_3D -= 1
                It -= 1
            Tempo_Proxima_Falha = t + gerar_tempo_falha(U_3D, Bt)

        # 3. Falha
        if t == Tempo_Proxima_Falha:
            ativas = N - Bt
            if ativas > 0:
                taxa_orig = (ativas - U_3D) / MTBF_conv
                taxa_3d = U_3D / MTBF_print
                prob_orig = taxa_orig / (taxa_orig + taxa_3d)
                
                if np.random.rand() > prob_orig:
                    U_3D -= 1  # 3D quebrou
                    
                if It > 0:
                    It -= 1
                elif Pt > 0:
                    Pt -= 1
                    U_3D += 1
                else:
                    Bt += 1
                Tempo_Proxima_Falha = t + gerar_tempo_falha(U_3D, Bt)

        # 4. Avaliação de Gatilhos (Corrigido)
        IPt_orig = It + Ot - Bt - U_3D
        IPt_total = It + Ot + Pt - Bt - U_3D

        if IPt_orig <= s:
            Q = S - IPt_orig
            pedidos_convencionais.append({'chegada': t + L_rep, 'qtd': Q})
            Ot += Q
            Custo_Total += K + (Q * C1)
            Ciclos_Ressuprimento += 1
            impressas_ciclo_atual = 0

        if IPt_total <= s_star and Jt == 0 and impressas_ciclo_atual < Q_3D_lote and Ot > 0:
            Jt = 1
            Tempo_Chegada_Impressao = t + L_ef
            Custo_Total += C2

        Custo_Total += (It * Ch_hora) + (Bt * Cb)
        if Bt > 0: Horas_Indisponivel += 1

    return Custo_Total, 1 - (Horas_Indisponivel / Horizonte_T), Pecas_Impressas_Total, Ciclos_Ressuprimento


def simular_politica_dual_com_historico(s_star, s, S, params):
    Horizonte_T = params['Horizonte_T']
    N = params['N']
    L_rep = params['L_rep']
    L_ef = params['L_ef']
    MTBF_conv = params['MTBF_conv']
    MTBF_print = params['MTBF_print']
    Q_3D_lote = params.get('Q_3D_lote', 1)

    It, Bt, Ot, Pt, U_3D, Jt = S, 0, 0, 0, 0, 0
    impressas_ciclo_atual = 0
    pedidos_convencionais = []
    historico, eventos = [], []

    def gerar_tempo_falha(u_3d, paradas):
        ativas = N - paradas
        if ativas <= 0: return float('inf')
        taxa_total = ((ativas - u_3d) / MTBF_conv) + (u_3d / MTBF_print)
        return max(1, int(np.random.exponential(1.0 / taxa_total)))

    Tempo_Proxima_Falha = gerar_tempo_falha(U_3D, Bt)
    Tempo_Chegada_Impressao = float('inf')

    for t in range(1, Horizonte_T + 1):
        evento_descricao = []
        qtd_chegada_orig = qtd_chegada_3d = qtd_usada_orig = qtd_usada_3d = 0

        if t == Tempo_Chegada_Impressao:
            qtd_chegada_3d = 1
            impressas_ciclo_atual += 1
            evento_descricao.append(f"Peça 3D Concluída ({impressas_ciclo_atual}/{Q_3D_lote})")
            if Bt > 0:
                Bt -= 1
                U_3D += 1
                qtd_usada_3d = 1
                Tempo_Proxima_Falha = t + gerar_tempo_falha(U_3D, Bt)
                evento_descricao.append("Peça 3D em Uso Imediato")
            else:
                Pt += 1
            
            if Ot > 0 and impressas_ciclo_atual < Q_3D_lote:
                Jt = 1
                Tempo_Chegada_Impressao = t + L_ef
            else:
                Jt = 0
                Tempo_Chegada_Impressao = float('inf')

        chegaram_agora = [p for p in pedidos_convencionais if p['chegada'] == t]
        if chegaram_agora:
            for pedido in chegaram_agora:
                It += pedido['qtd']
                Ot -= pedido['qtd']
                qtd_chegada_orig += pedido['qtd']
                evento_descricao.append(f"Chegada Lote Regular (Q={pedido['qtd']})")
            
            pedidos_convencionais = [p for p in pedidos_convencionais if p['chegada'] != t]
            Jt, impressas_ciclo_atual = 0, 0
            Tempo_Chegada_Impressao = float('inf')
            
            while Bt > 0 and It > 0:
                Bt -= 1
                It -= 1
                qtd_usada_orig += 1
            while U_3D > 0 and It > 0:
                U_3D -= 1
                It -= 1
                qtd_usada_orig += 1
            Tempo_Proxima_Falha = t + gerar_tempo_falha(U_3D, Bt)

        if t == Tempo_Proxima_Falha:
            evento_descricao.append("Falha no Componente")
            ativas = N - Bt
            if ativas > 0:
                taxa_orig = (ativas - U_3D) / MTBF_conv
                taxa_3d = U_3D / MTBF_print
                prob_orig = taxa_orig / (taxa_orig + taxa_3d)
                
                if np.random.rand() > prob_orig:
                    U_3D -= 1 
                
                if It > 0:
                    It -= 1
                    qtd_usada_orig += 1
                elif Pt > 0:
                    Pt -= 1
                    U_3D += 1
                    qtd_usada_3d += 1
                else:
                    Bt += 1
                    evento_descricao.append("Estoque Esgotado: Backlog")
                Tempo_Proxima_Falha = t + gerar_tempo_falha(U_3D, Bt)

        IPt_orig = It + Ot - Bt - U_3D
        IPt_total = It + Ot + Pt - Bt - U_3D
        
        if IPt_orig <= s:
            Q = S - IPt_orig
            pedidos_convencionais.append({'chegada': t + L_rep, 'qtd': Q})
            Ot += Q
            impressas_ciclo_atual = 0
            evento_descricao.append(f"Gatilho s Ativado (Pedido Regular Q={Q})")

        if IPt_total <= s_star and Jt == 0 and impressas_ciclo_atual < Q_3D_lote and Ot > 0:
            Jt = 1
            Tempo_Chegada_Impressao = t + L_ef
            evento_descricao.append(f"Gatilho s* Ativado (Disparo 3D)")

        historico.append({
            'Tempo_Hora': t, 'Estoque_Original_It': It, 'Em_Transito_Ot': Ot,
            'Estoque_3D_Pt': Pt, 'Impressao_Ativa_Jt': Jt, 'Backlog_Bt': Bt,
            'Posicao_Estoque_IPt': IPt_orig, 'Peca_Em_Uso': f"{U_3D} em 3D",
            'Qtd_Chegada_Original': qtd_chegada_orig, 'Qtd_Chegada_3D': qtd_chegada_3d,
            'Qtd_Usada_Original': qtd_usada_orig, 'Qtd_Usada_3D': qtd_usada_3d
        })

        if evento_descricao:
            eventos.append({
                'Tempo_Hora': t, 'Estoque_Original': It, 'Estoque_3D': Pt,
                'Descricao': " | ".join(evento_descricao)
            })

    return pd.DataFrame(historico), pd.DataFrame(eventos)
