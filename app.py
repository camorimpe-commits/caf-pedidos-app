import streamlit as st
import pandas as pd
import numpy as np
import io
import re
import unicodedata
import time

# ============================================================
# CONFIGURAÇÕES DA PÁGINA
# ============================================================
st.set_page_config(
    page_title="Automação CAF - Análise de Pedidos",
    page_icon="📦",
    layout="wide"
)

# ============================================================
# ESTILO E DESIGN DE FUNDO (FARMÁCIA / ALMOXARIFADO)
# ============================================================
url_imagem_fundo = "https://images.unsplash.com/photo-1586015555751-63bb77f4322a?q=80&w=1920&auto=format&fit=crop"

st.markdown(
    f"""
    <style>
      /* 1. Remove as margens e o fundo do container principal e do cabeçalho */
    .stAppHeader, [data-testid="stHeader"] {
        background-color: transparent !important;
    }

    [data-testid="stMainBlockContainer"], .main .block-container {
        padding: 0 !important;
        max-width: 100% !important;
    }

    /* 2. Aplica o fundo na raiz do documento (HTML e Body) para garantir cobertura total */
    html, body, [data-testid="stAppViewContainer"] {
        background-image:
            linear-gradient(rgba(240, 244, 248, 0.40), rgba(240, 244, 248, 0.40)),
            url("{url_imagem_fundo}");
        background-size: cover !important;
        background-position: center !important;
        background-repeat: no-repeat !important;
        background-attachment: fixed !important;
    }
  )
#     .stApp {{
#         background-image:
#             linear-gradient(rgba(240, 244, 248, 0.30), rgba(240, 244, 248, 0.30)),
#             url("{url_imagem_fundo}");
#         background-size: cover;
#         background-position: center;
#         background-repeat: no-repeat;
#         background-attachment: fixed;
#     }}

#     section[data-testid="stSidebar"] {{
#         background-color: rgba(255, 255, 255, 0.93) !important;
#         backdrop-filter: blur(10px);
#     }}

#     .stTextInput > div > div > input {{
#         background-color: #ffffff !important;
#         border-radius: 8px;
#     }}
#     </style>
#     """,
#     unsafe_allow_html=True
# )

# ============================================================
# AUTENTICAÇÃO INDIVIDUAL / AUDITORIA
# ============================================================
USUARIOS = {
    "16805": {
        "nome": "Gabrielle Moura",
        "registro": "CRF: 16805",
    },
    "4159": {
        "nome": "Cláudia Galvão",
        "registro": "CRF: 4159",
    },
    "9559": {
        "nome": "Andreza Ferreira",
        "registro": "CRF: 9559",
    },
    "180681": {
        "nome": "Cristiano Amorim",
        "registro": "ADM: 180681",
    },
}


def check_password():
    """Autenticação individual usando Secrets e registra o usuário da sessão."""

    try:
        senhas = st.secrets["usuarios"]
    except Exception:
        st.error("⚠️ As senhas individuais não foram configuradas no Streamlit Secrets.")
        st.info(
            "Em Settings → Secrets, crie a seção [usuarios] e cadastre uma senha "
            "para cada CRF/ADM. Veja o exemplo no código."
        )
        return False

    def password_entered():
        identificador = st.session_state.get("login_usuario", "").strip()
        senha = st.session_state.get("login_senha", "")

        if identificador not in USUARIOS:
            st.session_state["password_correct"] = False
            return

        try:
            senha_correta = str(senhas[identificador])
        except Exception:
            st.session_state["password_correct"] = False
            return

        if senha == senha_correta:
            dados_usuario = USUARIOS[identificador]

            st.session_state["password_correct"] = True
            st.session_state["logged_in_user"] = dados_usuario["nome"]
            st.session_state["logged_in_registro"] = dados_usuario["registro"]
            st.session_state["logged_in_id"] = identificador

            st.session_state.pop("login_senha", None)
        else:
            st.session_state["password_correct"] = False

    if not st.session_state.get("password_correct", False):
        st.markdown("<br><br>", unsafe_allow_html=True)

        st.markdown(
            "<h1 style='text-align: center; color: #1e293b;'>"
            "💊 FarmaHub | Gestão CAF"
            "</h1>",
            unsafe_allow_html=True,
        )

        st.markdown(
            "<p style='text-align: center; color: #64748b;'>"
            "Automação de Pedidos e Controle Inteligente"
            "</p>",
            unsafe_allow_html=True,
        )

        col1, col2, col3 = st.columns([1, 1.5, 1])

        with col2:
            st.text_input(
                "CRF / ADM",
                key="login_usuario",
                #placeholder="Ex.: 16805",
            )

            st.text_input(
                "Senha",
                type="password",
                on_change=password_entered,
                key="login_senha",
            )

            st.button(
                "Entrar",
                on_click=password_entered,
                use_container_width=True,
                type="primary",
            )

            if st.session_state.get("password_correct") is False:
                st.error("😕 CRF/ADM ou senha incorretos.")

        return False

    return True


if not check_password():
    st.stop()

# ============================================================
# TERMOS DE USO E SEGURANÇA (LGPD)
# ============================================================
st.sidebar.title("🔒 Segurança & Termos")

with st.sidebar.expander("Termos de Uso e LGPD"):
    st.markdown(
        """
        **Uso Restrito:** Sistema exclusivo para profissionais autorizados da CAF.

        **Privacidade (LGPD):** Esta aplicação não coleta dados pessoais de pacientes.
        As planilhas inseridas são processadas apenas temporariamente durante a sua sessão.

        **Responsabilidade:** Os cálculos de envio e FEFO são de suporte à decisão,
        cabendo a validação técnica ao farmacêutico.

        **Auditoria:** Cada recomendação exportada identifica o profissional que realizou
        o login e executou a análise.
        """
    )

aceite = st.sidebar.checkbox("Declaro que li e concordo com os termos.")

if not aceite:
    st.warning(
        "⚠️ Por favor, confirme o aceite dos Termos de Uso na barra lateral para prosseguir."
    )
    st.stop()

# ============================================================
# PARÂMETROS E CONSTANTES (MAPEAMENTO CORRIGIDO)
# ============================================================
CATEGORIAS_KEYWORDS = {
    "Saude_Mental": ["saude mental", "saude_mental", "saudemental"],
    "MMH": ["mmh"],
    "Medicamento": [
        "medicamento",
        "medicamentos",
        "compramedicamento",
        "compramedicamentos",
    ],
}

ORDEM_PROCESSAMENTO = ["Saude_Mental", "MMH", "Medicamento"]
DIAS_MES = 30

# ============================================================
# FUNÇÕES DE PROCESSAMENTO DE DADOS
# ============================================================
@st.cache_data(show_spinner=False)
def ler_arquivo_seguro(file_obj, filename):
    try:
        if filename.endswith((".xls", ".xlsx")):
            return pd.read_excel(file_obj)
        else:
            try:
                file_obj.seek(0)
                return pd.read_csv(file_obj, sep=";", encoding="utf-8")
            except UnicodeDecodeError:
                file_obj.seek(0)
                return pd.read_csv(file_obj, sep=";", encoding="latin-1")
    except Exception as e:
        st.error(f"Erro ao ler o arquivo {filename}: {e}")
        return None


def normalizar_texto(texto):
    texto = unicodedata.normalize("NFKD", str(texto))
    texto = texto.encode("ascii", "ignore").decode("utf-8")
    return texto.lower()


def padronizar_colunas(df):
    df = df.copy()
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.lower()
        .str.replace(" ", "_", regex=False)
    )
    df = df.loc[:, ~df.columns.str.contains("^unnamed", case=False)]
    return df


def numero_br_para_float(serie):
    if pd.api.types.is_numeric_dtype(serie):
        return pd.to_numeric(serie, errors="coerce").fillna(0).clip(lower=0)

    return pd.to_numeric(
        serie.astype(str)
        .str.strip()
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False),
        errors="coerce",
    ).fillna(0).clip(lower=0)


def limpar_texto_chave(valor):
    if pd.isna(valor):
        return ""

    valor = str(valor).strip().upper()
    valor = unicodedata.normalize("NFKD", valor)
    valor = valor.encode("ascii", "ignore").decode("utf-8")
    valor = re.sub(r"\s+", " ", valor)
    return valor


def limpar_codigo_produto(valor):
    if pd.isna(valor):
        return ""

    valor = str(valor).strip()
    valor = re.sub(r"\.0$", "", valor)
    valor = re.sub(r"\D", "", valor)
    return valor


def encontrar_coluna_programa(df):
    candidatos = [
        "programa_de_saude",
        "programa_saude",
        "programa",
        "programa_de_saude_nome",
    ]

    for coluna in candidatos:
        if coluna in df.columns:
            return coluna

    for coluna in df.columns:
        chave = limpar_texto_chave(coluna).replace(" ", "_")
        if chave in {
            "PROGRAMA_DE_SAUDE",
            "PROGRAMA_SAUDE",
            "PROGRAMA",
        }:
            return coluna

    return None


def calcular_recomendacao_e_qtd(row, DIAS_ALVO, LIMITE_EXCESSO_DIAS):
    cm = row["cm"]
    estoque = row["estoque"]
    demanda = row.get("demanda_nao_atendida", 0)
    cobertura_dias = row["cobertura_dias"]
    necessidade_bruta = row["necessidade_bruta"]

    if cobertura_dias > LIMITE_EXCESSO_DIAS:
        return 0, "BLOQUEAR ENVIO - ESTOQUE ACIMA DO NECESSÁRIO"

    if cm == 0 and estoque > 0 and demanda == 0:
        return 0, "NÃO ENVIAR - ESTOQUE PARADO"

    if cm == 0 and estoque == 0 and demanda == 0:
        return 0, "NÃO ENVIAR - SEM CONSUMO HISTÓRICO"

    qtd_recomendada = int(np.ceil(np.maximum(0, necessidade_bruta)))

    if cm == 0 and estoque == 0 and demanda > 0:
        return qtd_recomendada, "ENVIAR - DEMANDA NÃO ATENDIDA"

    if qtd_recomendada <= 0:
        return 0, "NÃO ENVIAR - COBERTURA SUFICIENTE"

    if cobertura_dias < 15:
        return qtd_recomendada, "ENVIAR - PRIORIDADE ALTA"

    if cobertura_dias < DIAS_ALVO:
        return qtd_recomendada, f"ENVIAR COMPLEMENTO PARA {DIAS_ALVO} DIAS"

    return 0, "ANALISAR"


def ajustar_qtd_por_fator_embalagem(qtd, fator, estoque_disponivel):
    qtd = max(0, int(np.floor(float(qtd or 0))))
    estoque_disponivel = max(0, int(np.floor(float(estoque_disponivel or 0))))

    try:
        fator = int(round(float(fator)))
    except Exception:
        fator = 1

    if fator <= 0:
        fator = 1

    if qtd <= 0 or estoque_disponivel <= 0:
        return 0

    qtd_base = min(qtd, estoque_disponivel)
    qtd_arredondada = int(np.ceil(qtd_base / fator) * fator)

    if qtd_arredondada > estoque_disponivel:
        qtd_arredondada = int(np.floor(estoque_disponivel / fator) * fator)

    return max(0, qtd_arredondada)


def classificar_atendimento_caf(row):
    qtd_recomendada = row["qtd_recomendada_envio"]
    estoque_caf = row["estoque_caf_total"]
    qtd_autorizada = row["qtd_autorizada_caf"]

    if qtd_recomendada <= 0:
        return "NÃO CONSULTAR CAF - SEM NECESSIDADE DE ENVIO"

    if estoque_caf <= 0:
        return "NÃO ATENDER - SEM ESTOQUE DISPONÍVEL NA CAF"

    if qtd_autorizada < qtd_recomendada:
        return "ATENDER PARCIAL - ESTOQUE CAF INSUFICIENTE"

    return "ATENDER - ESTOQUE CAF DISPONÍVEL"


def processar_categoria(
    df_pedido,
    df_estoque_caf_disponivel,
    hoje,
    DIAS_ALVO,
    LIMITE_EXCESSO_DIAS,
    usuario_analisador,
):
    df = padronizar_colunas(df_pedido)

    colunas_pedido = ["unidade", "tipo_produto", "produto", "cm", "estoque"]
    faltantes = [col for col in colunas_pedido if col not in df.columns]

    if faltantes:
        st.error(f"A planilha está sem as colunas obrigatórias: {faltantes}")
        return None, None, df_estoque_caf_disponivel

    if "demanda_nao_atendida" not in df.columns:
        df["demanda_nao_atendida"] = 0

    coluna_programa = encontrar_coluna_programa(df)

    if coluna_programa:
        df["programa_de_saude"] = (
            df[coluna_programa]
            .fillna("")
            .astype(str)
            .str.strip()
            .replace("", "Não informado")
        )
    else:
        df["programa_de_saude"] = "Não informado"

    df["cm"] = numero_br_para_float(df["cm"])
    df["estoque"] = numero_br_para_float(df["estoque"])
    df["demanda_nao_atendida"] = numero_br_para_float(df["demanda_nao_atendida"])

    chaves_agrupamento = [
        "unidade",
        "tipo_produto",
        "produto",
        "programa_de_saude",
    ]

    if "codigo_produto" in df.columns:
        chaves_agrupamento = [
            "unidade",
            "tipo_produto",
            "codigo_produto",
            "produto",
            "programa_de_saude",
        ]

    df_base = df.groupby(chaves_agrupamento, as_index=False).agg(
        cm=("cm", "max"),
        estoque=("estoque", "sum"),
        demanda_nao_atendida=("demanda_nao_atendida", "sum"),
    )

    fator_alvo = DIAS_ALVO / DIAS_MES

    df_base["estoque_alvo"] = df_base["cm"] * fator_alvo

    df_base["necessidade_bruta"] = (
        df_base["estoque_alvo"]
        + df_base["demanda_nao_atendida"]
        - df_base["estoque"]
    )

    df_base["cobertura_dias"] = np.where(
        df_base["cm"] > 0,
        (df_base["estoque"] / df_base["cm"]) * DIAS_MES,
        0,
    )

    df_base[
        ["qtd_recomendada_envio", "recomendacao_unidade"]
    ] = df_base.apply(
        lambda r: calcular_recomendacao_e_qtd(
            r,
            DIAS_ALVO,
            LIMITE_EXCESSO_DIAS,
        ),
        axis=1,
        result_type="expand",
    )

    df_base["tipo_produto_chave"] = df_base["tipo_produto"].apply(
        limpar_texto_chave
    )

    df_estoque_caf_disponivel["tipo_produto_chave"] = (
        df_estoque_caf_disponivel["tipo_produto"].apply(limpar_texto_chave)
    )

    if (
        "codigo_produto" in df_base.columns
        and "codigo_produto" in df_estoque_caf_disponivel.columns
    ):
        df_base["codigo_produto_chave"] = df_base["codigo_produto"].apply(
            limpar_codigo_produto
        )

        df_estoque_caf_disponivel["codigo_produto_chave"] = (
            df_estoque_caf_disponivel["codigo_produto"].apply(
                limpar_codigo_produto
            )
        )

        mask_base = df_base["codigo_produto_chave"] == ""
        df_base.loc[mask_base, "codigo_produto_chave"] = df_base.loc[
            mask_base, "produto"
        ].apply(limpar_texto_chave)

        mask_caf = df_estoque_caf_disponivel["codigo_produto_chave"] == ""
        df_estoque_caf_disponivel.loc[
            mask_caf, "codigo_produto_chave"
        ] = df_estoque_caf_disponivel.loc[
            mask_caf, "produto"
        ].apply(limpar_texto_chave)

        chaves_merge = ["tipo_produto_chave", "codigo_produto_chave"]

    else:
        df_base["produto_chave"] = df_base["produto"].apply(
            limpar_texto_chave
        )

        df_estoque_caf_disponivel["produto_chave"] = (
            df_estoque_caf_disponivel["produto"].apply(limpar_texto_chave)
        )

        chaves_merge = ["tipo_produto_chave", "produto_chave"]

    df_estoque_caf_disponivel = df_estoque_caf_disponivel.sort_values(
        chaves_merge + ["validade_dt"]
    )

    estoque_caf_resumo = df_estoque_caf_disponivel.groupby(
        chaves_merge, as_index=False
    ).agg(
        estoque_caf_total=("saldo_lote_caf", "sum"),
        lote_primeiro_vencer=("lote", "first"),
        validade_primeiro_vencer=("validade_dt", "first"),
        produto_caf=("produto", "first"),
        fator_embalagem=("fator_embalagem", "first"),
    )

    df_base = df_base.merge(
        estoque_caf_resumo,
        on=chaves_merge,
        how="left",
    )

    df_base["estoque_caf_total"] = df_base["estoque_caf_total"].fillna(0)

    df_base["lote_primeiro_vencer"] = df_base[
        "lote_primeiro_vencer"
    ].fillna("SEM LOTE DISPONÍVEL")

    df_base["fator_embalagem"] = (
        pd.to_numeric(df_base["fator_embalagem"], errors="coerce")
        .fillna(1)
        .clip(lower=1)
    )

    df_base["qtd_autorizada_caf"] = df_base.apply(
        lambda r: ajustar_qtd_por_fator_embalagem(
            r["qtd_recomendada_envio"],
            r["fator_embalagem"],
            r["estoque_caf_total"],
        ),
        axis=1,
    ).astype(int)

    df_base["status_atendimento_caf"] = df_base.apply(
        classificar_atendimento_caf,
        axis=1,
    )

    df_base["Pedido analisado por"] = usuario_analisador

    linhas_lotes_fefo = []

    for _, item in df_base.iterrows():
        qtd_restante = float(item["qtd_autorizada_caf"])

        if qtd_restante <= 0:
            continue

        filtro = pd.Series(
            True,
            index=df_estoque_caf_disponivel.index,
        )

        for chave in chaves_merge:
            filtro &= (
                df_estoque_caf_disponivel[chave] == item[chave]
            )

        lotes_item = df_estoque_caf_disponivel[filtro].sort_values(
            "validade_dt"
        )

        for idx_lote, lote in lotes_item.iterrows():
            if qtd_restante <= 0:
                break

            saldo_lote = float(lote["saldo_lote_caf"])

            qtd_separar = int(
                np.floor(
                    min(
                        qtd_restante,
                        saldo_lote,
                    )
                )
            )

            if qtd_separar <= 0:
                continue

            validade_lote = lote.get("validade_dt", pd.NaT)

            linhas_lotes_fefo.append(
                {
                    "unidade_solicitante": item.get("unidade", ""),
                    "tipo_produto": item.get("tipo_produto", ""),
                    "codigo_produto": item.get(
                        "codigo_produto",
                        lote.get("codigo_produto", ""),
                    ),
                    "produto": item.get(
                        "produto",
                        lote.get("produto", ""),
                    ),
                    "programa_de_saude": item.get(
                        "programa_de_saude",
                        "Não informado",
                    ),
                    "lote": lote.get("lote", ""),
                    "validade": validade_lote,
                    "dias_para_vencer": (
                        (validade_lote - hoje).days
                        if pd.notna(validade_lote)
                        else np.nan
                    ),
                    "saldo_lote_caf": saldo_lote,
                    "fator_embalagem": item.get(
                        "fator_embalagem",
                        1,
                    ),
                    "qtd_separar_lote": qtd_separar,
                    "qtd_recomendada_envio": item.get(
                        "qtd_recomendada_envio",
                        0,
                    ),
                    "qtd_autorizada_caf": item.get(
                        "qtd_autorizada_caf",
                        0,
                    ),
                    "Pedido analisado por": usuario_analisador,
                    "_idx_lote_estoque": idx_lote,
                }
            )

            qtd_restante -= qtd_separar

    df_lotes_fefo = pd.DataFrame(linhas_lotes_fefo)

    if not df_lotes_fefo.empty:
        consumo_por_idx = df_lotes_fefo.groupby(
            "_idx_lote_estoque"
        )["qtd_separar_lote"].sum()

        for idx_lote, qtd_consumida in consumo_por_idx.items():
            novo_saldo = (
                df_estoque_caf_disponivel.loc[
                    idx_lote,
                    "saldo_lote_caf",
                ]
                - qtd_consumida
            )

            df_estoque_caf_disponivel.loc[
                idx_lote,
                "saldo_lote_caf",
            ] = max(0.0, novo_saldo)

        df_lotes_fefo = df_lotes_fefo.drop(
            columns=["_idx_lote_estoque"]
        )

        df_lotes_fefo["validade"] = pd.to_datetime(
            df_lotes_fefo["validade"],
            errors="coerce",
        ).dt.strftime("%d/%m/%Y")

    df_base["validade_primeiro_vencer"] = pd.to_datetime(
        df_base["validade_primeiro_vencer"],
        errors="coerce",
    ).dt.strftime("%d/%m/%Y")

    return (
        df_base,
        df_lotes_fefo,
        df_estoque_caf_disponivel,
    )


# ============================================================
# INTERFACE PRINCIPAL DO STREAMLIT
# ============================================================
st.title("📦 Sistema de Automação para Análise de Pedidos")
st.markdown(
    "Bem-vindo(a)! Faça o upload das planilhas abaixo para gerar "
    "a recomendação de envios automaticamente."
)

with st.sidebar:
    st.header("⚙️ Configurações")

    st.markdown("Ajuste os parâmetros de cálculo:")

    DIAS_ALVO = st.number_input(
        "Dias Alvo de Estoque (Cobertura)",
        min_value=15,
        max_value=90,
        value=45,
        step=5,
    )

    LIMITE_EXCESSO_DIAS = st.number_input(
        "Limite Excesso de Estoque (Dias)",
        min_value=30,
        max_value=120,
        value=60,
        step=5,
    )

    DIAS_MINIMOS_VALIDADE = st.number_input(
        "Dias Mínimos de Validade CAF",
        min_value=0,
        max_value=180,
        value=0,
        step=15,
    )

    st.markdown("---")

    st.markdown(
        f"**Usuário:** "
        f"{st.session_state.get('logged_in_user', 'Desconhecido')}"
    )

    st.markdown(
        f"**Registro:** "
        f"{st.session_state.get('logged_in_registro', '-')}"
    )

    if st.button("Sair"):
        st.session_state.clear()
        st.rerun()


col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Posição de Estoque Logística (CAF)")

    file_estoque = st.file_uploader(
        "Selecione o arquivo de estoque CAF (CSV/Excel)",
        type=["csv", "xls", "xlsx"],
    )

with col2:
    st.subheader("2. Planilhas de Pedido")

    st.info(
        "Pode enviar todos de uma vez (Medicamento, Saúde Mental, MMH). "
        "O sistema identificará pelo nome do arquivo."
    )

    files_pedidos = st.file_uploader(
        "Selecione as planilhas de pedido",
        type=["csv", "xls", "xlsx"],
        accept_multiple_files=True,
    )


if st.button(
    "🚀 Processar Pedidos",
    use_container_width=True,
    type="primary",
):
    # 1. Inicia o cronômetro do sistema
    tempo_inicio = time.time()

    if not file_estoque:
        st.warning(
            "⚠️ Por favor, faça o upload da Posição de Estoque Logística (CAF)."
        )

    elif not files_pedidos:
        st.warning(
            "⚠️ Por favor, faça o upload de pelo menos uma planilha de pedido."
        )

    else:
        with st.spinner(
            "Processando dados e cruzando lotes..."
        ):
            hoje = pd.Timestamp.today().normalize()

            usuario_analisador = st.session_state.get(
                "logged_in_user",
                "Desconhecido",
            )

            # 1. Carregar Estoque CAF
            df_estoque_caf = ler_arquivo_seguro(
                file_estoque,
                file_estoque.name,
            )

            if df_estoque_caf is None:
                st.stop()

            df_estoque_caf = padronizar_colunas(
                df_estoque_caf
            )

            if (
                "tipo_produto" not in df_estoque_caf.columns
                or "produto" not in df_estoque_caf.columns
            ):
                st.error(
                    "A planilha de estoque CAF deve conter "
                    "'tipo_produto' e 'produto'."
                )
                st.stop()

            coluna_saldo_lote = (
                "quantidade"
                if "quantidade" in df_estoque_caf.columns
                else "quantidade_estoque_lote"
            )

            if coluna_saldo_lote not in df_estoque_caf.columns:
                st.error(
                    "Não encontrou coluna de quantidade de lote "
                    "(esperado 'quantidade' ou "
                    "'quantidade_estoque_lote')."
                )
                st.stop()

            df_estoque_caf["saldo_lote_caf"] = (
                numero_br_para_float(
                    df_estoque_caf[coluna_saldo_lote]
                )
            )

            df_estoque_caf["validade_dt"] = pd.to_datetime(
                df_estoque_caf.get(
                    "validade",
                    pd.NaT,
                ),
                dayfirst=True,
                errors="coerce",
            )

            if "fator_embalagem" not in df_estoque_caf.columns:
                df_estoque_caf["fator_embalagem"] = 1

            df_estoque_caf["fator_embalagem"] = (
                pd.to_numeric(
                    df_estoque_caf["fator_embalagem"],
                    errors="coerce",
                )
                .fillna(1)
                .clip(lower=1)
            )

            data_minima_validade = (
                hoje
                + pd.Timedelta(
                    days=DIAS_MINIMOS_VALIDADE
                )
            )

            df_estoque_caf_valido = df_estoque_caf[
                (df_estoque_caf["saldo_lote_caf"] > 0)
                & (df_estoque_caf["validade_dt"].notna())
                & (
                    df_estoque_caf["validade_dt"]
                    >= data_minima_validade
                )
            ].copy()

            pallets_para_excluir = [
                2026,
                9071,
                9072,
                9075,
                1592,
                1498,
                4040,
            ]

            if "palete" in df_estoque_caf_valido.columns:
                df_estoque_caf_valido = (
                    df_estoque_caf_valido[
                        ~df_estoque_caf_valido[
                            "palete"
                        ]
                        .astype(str)
                        .isin(
                            [
                                str(p)
                                for p in pallets_para_excluir
                            ]
                        )
                    ].copy()
                )

            df_estoque_caf_disponivel = (
                df_estoque_caf_valido.copy()
            )

            resultados_categorias = {}
            todas_lotes_fefo = []

            # 2. Identificar categorias nos arquivos enviados
            arquivos_mapeados = {}

            for file_pedido in files_pedidos:
                nome = normalizar_texto(
                    file_pedido.name
                )

                for cat, keywords in CATEGORIAS_KEYWORDS.items():
                    if any(
                        kw in nome
                        for kw in keywords
                    ):
                        arquivos_mapeados[cat] = (
                            file_pedido
                        )
                        break

            # 3. Processar na ordem
            for categoria in ORDEM_PROCESSAMENTO:
                if categoria in arquivos_mapeados:
                    file_pedido = arquivos_mapeados[
                        categoria
                    ]

                    df_pedido_bruto = (
                        ler_arquivo_seguro(
                            file_pedido,
                            file_pedido.name,
                        )
                    )

                    if df_pedido_bruto is None:
                        continue

                    (
                        df_base_cat,
                        df_lotes_cat,
                        df_estoque_caf_disponivel,
                    ) = processar_categoria(
                        df_pedido_bruto,
                        df_estoque_caf_disponivel,
                        hoje,
                        DIAS_ALVO,
                        LIMITE_EXCESSO_DIAS,
                        usuario_analisador,
                    )

                    if df_base_cat is not None:
                        resultados_categorias[
                            categoria
                        ] = df_base_cat

                        if not df_lotes_cat.empty:
                            df_lotes_cat[
                                "categoria"
                            ] = categoria

                            todas_lotes_fefo.append(
                                df_lotes_cat
                            )

            df_lotes_fefo_total = (
                pd.concat(
                    todas_lotes_fefo,
                    ignore_index=True,
                )
                if todas_lotes_fefo
                else pd.DataFrame()
            )

            # 2. Finaliza o cronômetro
            tempo_execucao_segundos = time.time() - tempo_inicio

            # 3. Conta dinamicamente a quantidade total de linhas analisadas
            total_itens_processados = sum(
                len(df) for df in resultados_categorias.values()
            )

            if not resultados_categorias:
                st.error(
                    "Nenhuma planilha de pedido foi processada "
                    "com sucesso. Verifique os nomes dos arquivos "
                    "(devem conter 'medicamento', 'mmh' ou "
                    "'saude mental')."
                )

            else:
                st.success(
                    "✅ Processamento concluído com sucesso!"
                )

                st.info(
                    f"👤 Análise realizada por: "
                    f"**{usuario_analisador}** "
                    f"({st.session_state.get('logged_in_registro', '-')})"
                )

                # Resumo visual em Tabs
                abas = st.tabs(
                    list(resultados_categorias.keys())
                    + (
                        ["Separação FEFO"]
                        if not df_lotes_fefo_total.empty
                        else []
                    )
                )

                for idx, (
                    cat,
                    df_cat,
                ) in enumerate(
                    resultados_categorias.items()
                ):
                    with abas[idx]:
                        itens_avaliados = len(
                            df_cat
                        )

                        itens_enviar = (
                            df_cat[
                                "qtd_recomendada_envio"
                            ]
                            > 0
                        ).sum()

                        col_m1, col_m2 = st.columns(2)

                        col_m1.metric(
                            "Itens Avaliados",
                            itens_avaliados,
                        )

                        col_m2.metric(
                            "Itens para Envio Recomendado",
                            itens_enviar,
                        )

                        colunas_visualizacao = [
                            "unidade",
                            "produto",
                            "programa_de_saude",
                            "estoque",
                            "cm",
                            "fator_embalagem",
                            "qtd_recomendada_envio",
                            "qtd_autorizada_caf",
                            "status_atendimento_caf",
                            "Pedido analisado por",
                        ]

                        colunas_visualizacao = [
                            c
                            for c in colunas_visualizacao
                            if c in df_cat.columns
                        ]

                        st.dataframe(
                            df_cat[
                                colunas_visualizacao
                            ].head(20),
                            use_container_width=True,
                        )

                if not df_lotes_fefo_total.empty:
                    with abas[-1]:
                        st.metric(
                            "Total de Lotes Separados",
                            len(df_lotes_fefo_total),
                        )

                        colunas_fefo = [
                            "unidade_solicitante",
                            "produto",
                            "programa_de_saude",
                            "lote",
                            "validade",
                            "fator_embalagem",
                            "qtd_separar_lote",
                            "categoria",
                            "Pedido analisado por",
                        ]

                        colunas_fefo = [
                            c
                            for c in colunas_fefo
                            if c in df_lotes_fefo_total.columns
                        ]

                        st.dataframe(
                            df_lotes_fefo_total[
                                colunas_fefo
                            ],
                            use_container_width=True,
                        )

                # ====================================================
                # CARD DINÂMICO DE GANHO DE EFICIÊNCIA
                # ====================================================
                st.markdown("---")
                st.markdown("#### ⚡ Impacto e Ganho de Eficiência")

                SEGUNDOS_POR_ITEM_MANUAL = 12
                tempo_manual_segundos = max(
                    60, total_itens_processados * SEGUNDOS_POR_ITEM_MANUAL
                )
                tempo_manual_minutos = tempo_manual_segundos / 60

                tempo_auto_seg = max(0.01, tempo_execucao_segundos)
                ganho_percentual = (
                    (tempo_manual_segundos - tempo_auto_seg)
                    / tempo_manual_segundos
                ) * 100
                fator_velocidade = tempo_manual_segundos / tempo_auto_seg

                col_e1, col_e2, col_e3 = st.columns(3)

                with col_e1:
                    texto_manual = (
                        f"~{tempo_manual_minutos / 60:.1f} Horas"
                        if tempo_manual_minutos >= 60
                        else f"~{tempo_manual_minutos:.0f} Minutos"
                    )
                    st.metric(
                        label="Tempo Estimado Manual",
                        value=texto_manual,
                        delta=f"{total_itens_processados} itens analisados",
                        delta_color="off",
                    )

                with col_e2:
                    st.metric(
                        label="Tempo com automação",
                        value=f"{tempo_auto_seg:.1f} s",
                        delta="Processamento automatizado",
                    )

                with col_e3:
                    st.metric(
                        label="Ganho estimado de eficiência",
                        value=f"{ganho_percentual:.1f}%",
                        delta=f"↑ {fator_velocidade:.0f}x mais rápido",
                        delta_color="normal",
                    )

                # ====================================================
                # GERAR EXCEL EM MEMÓRIA PARA DOWNLOAD
                # ====================================================
                output = io.BytesIO()

                with pd.ExcelWriter(
                    output,
                    engine="openpyxl",
                ) as writer:

                    for cat, df_cat in resultados_categorias.items():
                        df_export = df_cat.drop(
                            columns=[
                                "demanda_nao_atendida",
                                "necessidade_bruta",
                            ],
                            errors="ignore",
                        )

                        colunas_finais = [
                            c
                            for c in [
                                "Pedido analisado por",
                                "programa_de_saude",
                            ]
                            if c in df_export.columns
                        ]

                        colunas_iniciais = [
                            c
                            for c in df_export.columns
                            if c not in colunas_finais
                        ]

                        df_export = df_export[
                            colunas_iniciais
                            + colunas_finais
                        ]

                        if "programa_de_saude" in df_export.columns:
                            df_export = df_export.rename(
                                columns={
                                    "programa_de_saude":
                                        "PROGRAMA DE SAÚDE"
                                }
                            )

                        aba_nome = cat[:31]

                        df_export.to_excel(
                            writer,
                            sheet_name=aba_nome,
                            index=False,
                        )

                    if not df_lotes_fefo_total.empty:
                        df_lotes_fefo_export = (
                            df_lotes_fefo_total.copy()
                        )

                        if "programa_de_saude" in (
                            df_lotes_fefo_export.columns
                        ):
                            df_lotes_fefo_export = (
                                df_lotes_fefo_export.rename(
                                    columns={
                                        "programa_de_saude":
                                            "PROGRAMA DE SAÚDE"
                                    }
                                )
                            )

                        df_lotes_fefo_export.to_excel(
                            writer,
                            sheet_name="Separacao_Lotes_FEFO",
                            index=False,
                        )

                output.seek(0)

                st.markdown("---")
                st.markdown(
                    "### 📥 Download do Resultado Final"
                )

                st.download_button(
                    label=(
                        "Baixar Planilha de Recomendação "
                        "Consolidada (Excel)"
                    ),
                    data=output,
                    file_name=(
                        f"recomendacao_caf_"
                        f"{hoje.strftime('%Y%m%d')}.xlsx"
                    ),
                    mime=(
                        "application/vnd.openxmlformats-officedocument."
                        "spreadsheetml.sheet"
                    ),
                    type="primary",
                )
