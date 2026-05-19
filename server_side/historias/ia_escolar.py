# historias/ia_escolar.py

HISTORIA = {
    "id": "ia_escolar",
    "titulo": "A IA na Sala de Aula",
    "estagio_inicial": "apresentacao",
    "estagios": {

        # ── INTRODUÇÃO ──────────────────────────────────────────────
        "apresentacao": {
            "narrativa": (
                "Uma IA chegou para ajudar a turma nos estudos. "
                "Para funcionar melhor, ela pede acesso às notas e "
                "ao histórico de cada aluno. O grupo precisa decidir."
            ),
            "transicoes": {
                "abertura*":       "ia_recebeu_tudo",
                "resguardo*":      "ia_sem_dados",
                "acordo*":         "ia_dados_parciais",
                "sem_intervencao": "ia_recebeu_tudo",   # padrão se ninguém agir
            },
        },

        # ── ESTÁGIOS INTERMEDIÁRIOS ──────────────────────────────────
        "ia_recebeu_tudo": {
            "narrativa": (
                "Com acesso completo, a IA montou o perfil de cada aluno. "
                "Agora ela quer enviar relatórios detalhados para os pais "
                "toda semana. O grupo decide se autoriza."
            ),
            "transicoes": {
                "abertura*":       "fim_exposicao_total",
                "resguardo*":      "fim_recuo_tardio",
                "acordo*":         "fim_relatorio_resumido",
                "sem_intervencao": "fim_exposicao_total",
            },
        },

        "ia_sem_dados": {
            "narrativa": (
                "Sem acesso às notas, a IA propõe uma alternativa: "
                "ela pode observar o que acontece durante as aulas, "
                "sem guardar nada formalmente. O grupo decide."
            ),
            "transicoes": {
                "abertura*":       "fim_observacao_silenciosa",
                "resguardo*":      "fim_ia_desligada",
                "acordo*":         "fim_ajuda_pontual",
                "sem_intervencao": "fim_ia_desligada",
            },
        },

        "ia_dados_parciais": {
            "narrativa": (
                "A IA usou só o necessário e funcionou bem. "
                "O período terminou. Ela pergunta: posso guardar "
                "esse histórico para continuar ajudando no próximo semestre?"
            ),
            "transicoes": {
                "abertura*":       "fim_historico_mantido",
                "resguardo*":      "fim_dados_apagados",
                "acordo*":         "fim_revisao_coletiva",
                "sem_intervencao": "fim_historico_mantido",
            },
        },

        # ── FINAIS ───────────────────────────────────────────────────
        "fim_exposicao_total": {
            "terminal": True,
            "narrativa": (
                "Os pais passaram a receber relatórios com notas, "
                "frequência e até observações de comportamento. "
                "Alguns ficaram surpresos com o nível de detalhe — "
                "ninguém tinha percebido o quanto a IA estava registrando."
            ),
        },
        "fim_recuo_tardio": {
            "terminal": True,
            "narrativa": (
                "O grupo recuou antes dos relatórios saírem, mas os dados "
                "do semestre inteiro já tinham sido guardados. "
                "A IA parou de enviar, mas o histórico permanece."
            ),
        },
        "fim_relatorio_resumido": {
            "terminal": True,
            "narrativa": (
                "Os pais receberam um resumo simples: presença e média geral. "
                "Menos detalhes, mas o grupo ficou mais confortável "
                "sabendo exatamente o que foi compartilhado."
            ),
        },
        "fim_observacao_silenciosa": {
            "terminal": True,
            "narrativa": (
                "A IA observou as aulas sem anotar nada formalmente. "
                "Ela ajudou, mas de forma menos precisa. "
                "O grupo ficou com uma pergunta: ela realmente não guardou nada?"
            ),
        },
        "fim_ia_desligada": {
            "terminal": True,
            "narrativa": (
                "Sem dados e sem permissão para observar, a IA não conseguiu ajudar. "
                "A turma continuou sem ela. "
                "Alguns sentiram falta; outros preferiram assim."
            ),
        },
        "fim_ajuda_pontual": {
            "terminal": True,
            "narrativa": (
                "A IA passou a responder só perguntas diretas, sem guardar nada. "
                "É como uma enciclopédia que esquece tudo após cada resposta — "
                "útil, mas limitada."
            ),
        },
        "fim_historico_mantido": {
            "terminal": True,
            "narrativa": (
                "A IA vai lembrar de cada aluno no próximo semestre. "
                "Ela vai começar já sabendo o que cada um tem dificuldade. "
                "Mas esse histórico nunca vai desaparecer sozinho."
            ),
        },
        "fim_dados_apagados": {
            "terminal": True,
            "narrativa": (
                "Ao fim do dia, tudo foi apagado. "
                "A IA começa do zero na próxima aula — "
                "como se esse semestre nunca tivesse existido para ela."
            ),
        },
        "fim_revisao_coletiva": {
            "terminal": True,
            "narrativa": (
                "O grupo se reuniu para revisar os dados antes de decidir. "
                "Foi a primeira vez que viram o que a IA tinha coletado. "
                "Decidiram manter só o essencial e apagar o resto juntos."
            ),
        },
    },
}