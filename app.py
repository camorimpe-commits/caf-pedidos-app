import streamlit as st
import pandas as pd
import numpy as np
import io
import re
import unicodedata
import datetime

# ============================================================
# CONFIGURAÇÕES DA PÁGINA
# ============================================================
st.set_page_config(
    page_title="Automação CAF - Análise de Pedidos",
    page_icon="📦",
    layout="wide"
)
# ============================================================
# ESTILIZAÇÃO E IMAGEM DE FUNDO DA APLICAÇÃO
# ============================================================
def aplicar_estilo_fundo():
    # URL de imagem de prateleiras farmacêuticas em alta resolução (estilo Clean/Farmácia)
    # Você pode trocar a URL abaixo por qualquer link direto de imagem de fundo (.jpg / .png)
    url_imagem_fundo = "https://images.unsplash.com/photo-1586015555751-63bb77f4322a?q=80&w=1920&auto=format&fit=crop"

    st.markdown(
        f"""
        <style>
        /* Aplica o fundo na aplicação inteira */
        .stApp {{
            background-image: 
                linear-gradient(rgba(240, 244, 248, 0.85), rgba(240, 244, 248, 0.85)),
                url("{url_imagem_fundo}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}

        /* Torna os cards e áreas de conteúdo levemente opacos e legíveis */
        .stApp > header {{
            background-color: transparent !important;
        }}
        
        /* Deixa o menu lateral (Sidebar) elegante e legível */
        section[data-testid="stSidebar"] {{
            background-color: rgba(255, 255, 255, 0.92) !important;
            backdrop-filter: blur(8px);
        }}

        /* Garante boa leitura dos textos principais */
        .stMarkdown, h1, h2, h3, p, label {{
            color: #1e293b !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Executa a aplicação do fundo
aplicar_estilo_fundo()
# ============================================================
# AUTENTICAÇÃO SIMPLES
# ============================================================
#def check_password():
    # """Retorna True se o usuário tiver a senha correta."""
    # def password_entered():
        # Usa .get() para evitar KeyError caso o estado não exista ou já tenha sido limpo
    #     user = st.session_state.get("username", "")
    #     pwd = st.session_state.get("password", "")
        
    #     if pwd == "caf2025" and user == "farmacia":
    #         st.session_state["password_correct"] = True
    #         st.session_state["logged_in_user"] = user  # <-- ADICIONE ESTA LINHA AQUI
    #         # Limpa a senha por segurança, mas verifica se a chave existe antes
    #         if "password" in st.session_state:
    #             del st.session_state["password"]
    #     else:
    #         st.session_state["password_correct"] = False

    # if "password_correct" not in st.session_state:
    #     st.markdown("<h1 style='text-align: center;'>🔐 Acesso Restrito - CAF</h1>", unsafe_allow_html=True)
    #     col1, col2, col3 = st.columns([1,2,1])
    #     with col2:
    #         st.text_input("Usuário", key="username")
    #         st.text_input("Senha", type="password", on_change=password_entered, key="password")
    #         st.button("Entrar", on_click=password_entered, use_container_width=True)
    #     return False
    # elif not st.session_state["password_correct"]:
    #     st.markdown("<h1 style='text-align: center;'>🔐 Acesso Restrito - CAF</h1>", unsafe_allow_html=True)
    #     col1, col2, col3 = st.columns([1,2,1])
    #     with col2:
    #         st.text_input("Usuário", key="username")
    #         st.text_input("Senha", type="password", on_change=password_entered, key="password")
    #         st.button("Entrar", on_click=password_entered, use_container_width=True)
    #         st.error("😕 Usuário ou senha incorretos.")
    #     return False
    # return True
# ============================================================
# AUTENTICAÇÃO SIMPLES COM DESIGN PERSONALIZADO
# ============================================================
def check_password():
    """Retorna True se o usuário tiver a senha correta."""
    def password_entered():
        user = st.session_state.get("username", "")
        pwd = st.session_state.get("password", "")
        
        if pwd == "caf2025" and user == "farmacia":
            st.session_state["password_correct"] = True
            st.session_state["logged_in_user"] = user
            if "password" in st.session_state:
                del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if not st.session_state.get("password_correct", False):
        # Injeção de CSS para o fundo, padrão de medicamentos e estilo do card
        st.markdown(
            """
            <style>
            /* Cor de fundo base e padrão de marca d'água de medicamentos em SVG */
            .stApp {
                background-color: #f0f4f8;
                background-image: 
                    linear-gradient(rgba(240, 244, 248, 0.90), rgba(240, 244, 248, 0.90)),
                    url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='160' height='160' viewBox='0 0 160 160'%3E%3Cg fill='%230f766e' fill-opacity='0.18'%3E%3C!-- Cápsula --%3E%3Cpath d='M30,30 L45,15 C50,10 58,10 63,15 C68,20 68,28 63,33 L48,48 C43,53 35,53 30,48 C25,43 25,35 30,30 Z M38,22 L55,39' stroke='%230f766e' stroke-width='3' fill='none'/%3E%3C!-- Comprimido Redondo --%3E%3Ccircle cx='120' cy='40' r='16' stroke='%230f766e' stroke-width='3' fill='none'/%3E%3Cline x1='106' y1='40' x2='134' y2='40' stroke='%230f766e' stroke-width='3'/%3E%3C!-- Frasco de Medicamento --%3E%3Cpath d='M35,110 L55,110 L55,145 C55,147 53,149 51,149 L39,149 C37,149 35,147 35,145 Z M40,104 L50,104 L50,110 L40,110 Z' stroke='%230f766e' stroke-width='3' fill='none'/%3E%3C!-- Cruz Hospitalar --%3E%3Cpath d='M115,110 H125 V120 H135 V130 H125 V140 H115 V130 H105 V120 H115 Z'/%3E%3C/g%3E%3C/svg%3E");
                background-repeat: repeat;
            }

            /* Estilização dos inputs para harmonizar com o fundo */
            .stTextInput > div > div > input {
                background-color: #ffffff !important;
                border-radius: 8px;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: center; color: #1e293b;'>💊 FarmaHub | Gestão CAF</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #64748b;'>Automação de Pedidos e Controle Inteligente</p>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 1.5, 1])
        with col2:
            st.text_input("Usuário", key="username")
            st.text_input("Senha", type="password", on_change=password_entered, key="password")
            st.button("Entrar", on_click=password_entered, use_container_width=True, type="primary")
            
            # Mostra erro se tentou logar e falhou
            if "password_correct" in st.session_state and not st.session_state["password_correct"]:
                st.error("😕 Usuário ou senha incorretos.")
                
        return False
        
    return True
if not check_password():
    st.stop()  # Para a execução aqui se não estiver logado

# ============================================================
# PARÂMETROS E CONSTANTES
# ============================================================
CATEGORIAS_KEYWORDS = {
    "Saude_Mental": ["saude mental", "saude_mental", "saudemental"],
    "MMH": ["mmh"],
    "Clinico": ["clinico", "clínico"],
}
ORDEM_PROCESSAMENTO = ["Saude_Mental", "MMH", "Clinico"]
DIAS_MES = 30

# ============================================================
# FUNÇÕES DE PROCESSAMENTO DE DADOS
# ============================================================
@st.cache_data(show_spinner=False)
def ler_arquivo_seguro(file_obj, filename):
    try:
        if filename.endswith(('.xls', '.xlsx')):
            return pd.read_excel(file_obj)
        else:
            # Tenta UTF-8 primeiro
            try:
                file_obj.seek(0)
                return pd.read_csv(file_obj, sep=';', encoding='utf-8')
            except UnicodeDecodeError:
                file_obj.seek(0)
                return pd.read_csv(file_obj, sep=';', encoding='latin-1')
    except Exception as e:
        st.error(f"Erro ao ler o arquivo {filename}: {e}")
        return None

def normalizar_texto(texto):
    texto = unicodedata.normalize("NFKD", str(texto))
    texto = texto.encode("ascii", "ignore").decode("utf-8")
    return texto.lower()

def padronizar_colunas(df):
    df.columns = df.columns.astype(str).str.strip().str.lower().str.replace(" ", "_", regex=False)
    df = df.loc[:, ~df.columns.str.contains("^unnamed", case=False)]
    return df

def numero_br_para_float(serie):
    if pd.api.types.is_numeric_dtype(serie):
        return pd.to_numeric(serie, errors="coerce").fillna(0).clip(lower=0)
    return pd.to_numeric(
        serie.astype(str).str.strip().str.replace(".", "", regex=False).str.replace(",", ".", regex=False),
        errors="coerce"
    ).fillna(0).clip(lower=0)

def limpar_texto_chave(valor):
    if pd.isna(valor): return ""
    valor = str(valor).strip().upper()
    valor = unicodedata.normalize("NFKD", valor)
    valor = valor.encode("ascii", "ignore").decode("utf-8")
    valor = re.sub(r"\s+", " ", valor)
    return valor

def limpar_codigo_produto(valor):
    if pd.isna(valor): return ""
    valor = str(valor).strip()
    valor = re.sub(r"\.0$", "", valor)
    valor = re.sub(r"\D", "", valor)
    return valor

def calcular_recomendacao_e_qtd(row, DIAS_ALVO, LIMITE_EXCESSO_DIAS):
    cm = row["cm"]; estoque = row["estoque"]; demanda = row.get("demanda_nao_atendida", 0)
    cobertura_dias = row["cobertura_dias"]; necessidade_bruta = row["necessidade_bruta"]

    if cobertura_dias > LIMITE_EXCESSO_DIAS: return 0, "BLOQUEAR ENVIO - ESTOQUE ACIMA DO NECESSÁRIO"
    if cm == 0 and estoque > 0 and demanda == 0: return 0, "NÃO ENVIAR - ESTOQUE PARADO"
    if cm == 0 and estoque == 0 and demanda == 0: return 0, "NÃO ENVIAR - SEM CONSUMO HISTÓRICO"

    qtd_recomendada = int(np.ceil(np.maximum(0, necessidade_bruta)))

    if cm == 0 and estoque == 0 and demanda > 0: return qtd_recomendada, "ENVIAR - DEMANDA NÃO ATENDIDA"
    if qtd_recomendada <= 0: return 0, "NÃO ENVIAR - COBERTURA SUFICIENTE"
    if cobertura_dias < 15: return qtd_recomendada, "ENVIAR - PRIORIDADE ALTA"
    if cobertura_dias < DIAS_ALVO: return qtd_recomendada, f"ENVIAR COMPLEMENTO PARA {DIAS_ALVO} DIAS"
    return 0, "ANALISAR"

def classificar_atendimento_caf(row):
    qtd_recomendada = row["qtd_recomendada_envio"]
    estoque_caf = row["estoque_caf_total"]
    qtd_autorizada = row["qtd_autorizada_caf"]
    if qtd_recomendada <= 0: return "NÃO CONSULTAR CAF - SEM NECESSIDADE DE ENVIO"
    if estoque_caf <= 0: return "NÃO ATENDER - SEM ESTOQUE DISPONÍVEL NA CAF"
    if qtd_autorizada < qtd_recomendada: return "ATENDER PARCIAL - ESTOQUE CAF INSUFICIENTE"
    return "ATENDER - ESTOQUE CAF DISPONÍVEL"

def processar_categoria(df_pedido, df_estoque_caf_disponivel, hoje, DIAS_ALVO, LIMITE_EXCESSO_DIAS):
    df = padronizar_colunas(df_pedido)
    
    colunas_pedido = ["unidade", "tipo_produto", "produto", "cm", "estoque"]
    faltantes = [col for col in colunas_pedido if col not in df.columns]
    if faltantes:
        st.error(f"A planilha está sem as colunas obrigatórias: {faltantes}")
        return None, None, df_estoque_caf_disponivel

    if "demanda_nao_atendida" not in df.columns: df["demanda_nao_atendida"] = 0

    df["cm"] = numero_br_para_float(df["cm"])
    df["estoque"] = numero_br_para_float(df["estoque"])
    df["demanda_nao_atendida"] = numero_br_para_float(df["demanda_nao_atendida"])

    chaves_agrupamento = ["unidade", "tipo_produto", "produto"]
    if "codigo_produto" in df.columns:
        chaves_agrupamento = ["unidade", "tipo_produto", "codigo_produto", "produto"]

    df_base = df.groupby(chaves_agrupamento, as_index=False).agg(
        cm=("cm", "max"), estoque=("estoque", "sum"), demanda_nao_atendida=("demanda_nao_atendida", "sum")
    )

    FATOR_ALVO = DIAS_ALVO / DIAS_MES
    df_base["estoque_alvo"] = df_base["cm"] * FATOR_ALVO
    df_base["necessidade_bruta"] = df_base["estoque_alvo"] + df_base["demanda_nao_atendida"] - df_base["estoque"]
    df_base["cobertura_dias"] = np.where(df_base["cm"] > 0, (df_base["estoque"] / df_base["cm"]) * DIAS_MES, 0)

    df_base[["qtd_recomendada_envio", "recomendacao_unidade"]] = df_base.apply(
        lambda r: calcular_recomendacao_e_qtd(r, DIAS_ALVO, LIMITE_EXCESSO_DIAS), axis=1, result_type='expand'
    )

    df_base["tipo_produto_chave"] = df_base["tipo_produto"].apply(limpar_texto_chave)
    df_estoque_caf_disponivel["tipo_produto_chave"] = df_estoque_caf_disponivel["tipo_produto"].apply(limpar_texto_chave)

    if "codigo_produto" in df_base.columns and "codigo_produto" in df_estoque_caf_disponivel.columns:
        df_base["codigo_produto_chave"] = df_base["codigo_produto"].apply(limpar_codigo_produto)
        df_estoque_caf_disponivel["codigo_produto_chave"] = df_estoque_caf_disponivel["codigo_produto"].apply(limpar_codigo_produto)

        mask_base = df_base["codigo_produto_chave"] == ""
        df_base.loc[mask_base, "codigo_produto_chave"] = df_base.loc[mask_base, "produto"].apply(limpar_texto_chave)

        mask_caf = df_estoque_caf_disponivel["codigo_produto_chave"] == ""
        df_estoque_caf_disponivel.loc[mask_caf, "codigo_produto_chave"] = df_estoque_caf_disponivel.loc[mask_caf, "produto"].apply(limpar_texto_chave)

        chaves_merge = ["tipo_produto_chave", "codigo_produto_chave"]
    else:
        df_base["produto_chave"] = df_base["produto"].apply(limpar_texto_chave)
        df_estoque_caf_disponivel["produto_chave"] = df_estoque_caf_disponivel["produto"].apply(limpar_texto_chave)
        chaves_merge = ["tipo_produto_chave", "produto_chave"]

    df_estoque_caf_disponivel = df_estoque_caf_disponivel.sort_values(chaves_merge + ["validade_dt"])
    estoque_caf_resumo = df_estoque_caf_disponivel.groupby(chaves_merge, as_index=False).agg(
        estoque_caf_total=("saldo_lote_caf", "sum"),
        lote_primeiro_vencer=("lote", "first"),
        validade_primeiro_vencer=("validade_dt", "first"),
        produto_caf=("produto", "first")
    )

    df_base = df_base.merge(estoque_caf_resumo, on=chaves_merge, how="left")
    df_base["estoque_caf_total"] = df_base["estoque_caf_total"].fillna(0)
    df_base["lote_primeiro_vencer"] = df_base["lote_primeiro_vencer"].fillna("SEM LOTE DISPONÍVEL")

    df_base["qtd_autorizada_caf"] = np.minimum(df_base["qtd_recomendada_envio"], df_base["estoque_caf_total"]).clip(lower=0).astype(int)
    df_base["status_atendimento_caf"] = df_base.apply(classificar_atendimento_caf, axis=1)

    linhas_lotes_fefo = []
    for _, item in df_base.iterrows():
        qtd_restante = float(item["qtd_autorizada_caf"])
        if qtd_restante <= 0: continue

        filtro = pd.Series(True, index=df_estoque_caf_disponivel.index)
        for chave in chaves_merge: filtro = filtro & (df_estoque_caf_disponivel[chave] == item[chave])

        lotes_item = df_estoque_caf_disponivel[filtro].sort_values("validade_dt").copy()

        for idx_lote, lote in lotes_item.iterrows():
            if qtd_restante <= 0: break
            saldo_lote = float(lote["saldo_lote_caf"])
            qtd_separar = int(np.floor(min(qtd_restante, saldo_lote)))
            if qtd_separar <= 0: continue

            linhas_lotes_fefo.append({
                "unidade_solicitante": item.get("unidade", ""), "tipo_produto": item.get("tipo_produto", ""),
                "codigo_produto": item.get("codigo_produto", lote.get("codigo_produto", "")),
                "produto": item.get("produto", lote.get("produto", "")),
                "lote": lote.get("lote", ""),
                "validade": lote.get("validade_dt", pd.NaT),
                "dias_para_vencer": (lote.get("validade_dt", pd.NaT) - hoje).days if pd.notna(lote.get("validade_dt", pd.NaT)) else np.nan,
                "saldo_lote_caf": saldo_lote, "qtd_separar_lote": qtd_separar,
                "qtd_recomendada_envio": item.get("qtd_recomendada_envio", 0),
                "qtd_autorizada_caf": item.get("qtd_autorizada_caf", 0),
                "_idx_lote_estoque": idx_lote,
            })
            qtd_restante -= qtd_separar

    df_lotes_fefo = pd.DataFrame(linhas_lotes_fefo)

    if not df_lotes_fefo.empty:
        consumo_por_idx = df_lotes_fefo.groupby("_idx_lote_estoque")["qtd_separar_lote"].sum()
        for idx_lote, qtd_consumida in consumo_por_idx.items():
            novo_saldo = df_estoque_caf_disponivel.loc[idx_lote, "saldo_lote_caf"] - qtd_consumida
            df_estoque_caf_disponivel.loc[idx_lote, "saldo_lote_caf"] = max(0.0, novo_saldo)
        df_lotes_fefo = df_lotes_fefo.drop(columns=["_idx_lote_estoque"])
        df_lotes_fefo["validade"] = pd.to_datetime(df_lotes_fefo["validade"], errors="coerce").dt.strftime("%d/%m/%Y")
    
    df_base["validade_primeiro_vencer"] = pd.to_datetime(df_base["validade_primeiro_vencer"], errors="coerce").dt.strftime("%d/%m/%Y")

    return df_base, df_lotes_fefo, df_estoque_caf_disponivel


# ============================================================
# INTERFACE PRINCIPAL DO STREAMLIT
# ============================================================
st.title("📦 Sistema de Automação para Análise de Pedidos")
st.markdown("Bem-vindo(a)! Faça o upload das planilhas abaixo para gerar a recomendação de envios automaticamente.")

with st.sidebar:
    st.header("⚙️ Configurações")
    st.markdown("Ajuste os parâmetros de cálculo:")
    DIAS_ALVO = st.number_input("Dias Alvo de Estoque (Cobertura)", min_value=15, max_value=90, value=45, step=5)
    LIMITE_EXCESSO_DIAS = st.number_input("Limite Excesso de Estoque (Dias)", min_value=30, max_value=120, value=60, step=5)
    DIAS_MINIMOS_VALIDADE = st.number_input("Dias Mínimos de Validade CAF", min_value=0, max_value=180, value=0, step=15)
    st.markdown("---")
    st.markdown(f"**Usuário:** {st.session_state.get('logged_in_user', 'Desconhecido')}")
    if st.button("Sair"):
        st.session_state.clear()
        st.rerun()

col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Posição de Estoque Logística (CAF)")
    file_estoque = st.file_uploader("Selecione o arquivo de estoque CAF (CSV/Excel)", type=['csv', 'xls', 'xlsx'])

with col2:
    st.subheader("2. Planilhas de Pedido")
    st.info("Pode enviar todos de uma vez (Clínico, Saúde Mental, MMH). O sistema identificará pelo nome do arquivo.")
    files_pedidos = st.file_uploader("Selecione as planilhas de pedido", type=['csv', 'xls', 'xlsx'], accept_multiple_files=True)

if st.button("🚀 Processar Pedidos", use_container_width=True, type="primary"):
    if not file_estoque:
        st.warning("⚠️ Por favor, faça o upload da Posição de Estoque Logística (CAF).")
    elif not files_pedidos:
        st.warning("⚠️ Por favor, faça o upload de pelo menos uma planilha de pedido.")
    else:
        with st.spinner("Processando dados e cruzando lotes..."):
            hoje = pd.Timestamp.today().normalize()
            
            # 1. Carregar Estoque CAF
            df_estoque_caf = ler_arquivo_seguro(file_estoque, file_estoque.name)
            df_estoque_caf = padronizar_colunas(df_estoque_caf)
            
            if "tipo_produto" not in df_estoque_caf.columns or "produto" not in df_estoque_caf.columns:
                st.error("A planilha de estoque CAF deve conter 'tipo_produto' e 'produto'.")
                st.stop()
                
            coluna_saldo_lote = "quantidade" if "quantidade" in df_estoque_caf.columns else "quantidade_estoque_lote"
            if coluna_saldo_lote not in df_estoque_caf.columns:
                st.error(f"Não encontrou coluna de quantidade de lote (esperado 'quantidade' ou 'quantidade_estoque_lote').")
                st.stop()
                
            df_estoque_caf["saldo_lote_caf"] = numero_br_para_float(df_estoque_caf[coluna_saldo_lote])
            df_estoque_caf["validade_dt"] = pd.to_datetime(df_estoque_caf.get("validade", pd.NaT), dayfirst=True, errors="coerce")

            data_minima_validade = hoje + pd.Timedelta(days=DIAS_MINIMOS_VALIDADE)
            df_estoque_caf_valido = df_estoque_caf[
                (df_estoque_caf["saldo_lote_caf"] > 0) &
                (df_estoque_caf["validade_dt"].notna()) &
                (df_estoque_caf["validade_dt"] >= data_minima_validade)
            ].copy()

            # Exclusão de pallets
            pallets_para_excluir = [2026, 9071, 9072, 9075, 1592, 1498, 4040]
            if 'palete' in df_estoque_caf_valido.columns:
                df_estoque_caf_valido = df_estoque_caf_valido[
                    ~df_estoque_caf_valido['palete'].astype(str).isin([str(p) for p in pallets_para_excluir])
                ].copy()

            df_estoque_caf_disponivel = df_estoque_caf_valido.copy()
            resultados_categorias = {}
            todas_lotes_fefo = []
            
            # 2. Identificar categorias nos arquivos enviados
            arquivos_mapeados = {}
            for file_pedido in files_pedidos:
                nome = normalizar_texto(file_pedido.name)
                for cat, keywords in CATEGORIAS_KEYWORDS.items():
                    if any(kw in nome for kw in keywords):
                        # Pega o último enviado caso envie repetido (ou pode juntar, mas manter simples)
                        arquivos_mapeados[cat] = file_pedido
                        break
            
            # 3. Processar na ordem
            for categoria in ORDEM_PROCESSAMENTO:
                if categoria in arquivos_mapeados:
                    file_pedido = arquivos_mapeados[categoria]
                    df_pedido_bruto = ler_arquivo_seguro(file_pedido, file_pedido.name)
                    
                    df_base_cat, df_lotes_cat, df_estoque_caf_disponivel = processar_categoria(
                        df_pedido_bruto, df_estoque_caf_disponivel, hoje, DIAS_ALVO, LIMITE_EXCESSO_DIAS
                    )
                    
                    if df_base_cat is not None:
                        resultados_categorias[categoria] = df_base_cat
                        if not df_lotes_cat.empty:
                            df_lotes_cat["categoria"] = categoria
                            todas_lotes_fefo.append(df_lotes_cat)
            
            df_lotes_fefo_total = pd.concat(todas_lotes_fefo, ignore_index=True) if todas_lotes_fefo else pd.DataFrame()

            if not resultados_categorias:
                st.error("Nenhuma planilha de pedido foi processada com sucesso. Verifique os nomes dos arquivos (devem conter 'clinico', 'mmh' ou 'saude mental').")
            else:
                st.success("✅ Processamento concluído com sucesso!")
                
                # Resumo visual em Tabs
                abas = st.tabs(list(resultados_categorias.keys()) + (["Separação FEFO"] if not df_lotes_fefo_total.empty else []))
                
                for idx, (cat, df_cat) in enumerate(resultados_categorias.items()):
                    with abas[idx]:
                        itens_avaliados = len(df_cat)
                        itens_enviar = (df_cat['qtd_recomendada_envio'] > 0).sum()
                        
                        col_m1, col_m2 = st.columns(2)
                        col_m1.metric("Itens Avaliados", itens_avaliados)
                        col_m2.metric("Itens para Envio Recomendado", itens_enviar)
                        
                        st.dataframe(df_cat[["unidade", "produto", "estoque", "cm", "qtd_recomendada_envio", "status_atendimento_caf"]].head(20), use_container_width=True)
                
                if not df_lotes_fefo_total.empty:
                    with abas[-1]:
                        st.metric("Total de Lotes Separados", len(df_lotes_fefo_total))
                        st.dataframe(df_lotes_fefo_total[["unidade_solicitante", "produto", "lote", "validade", "qtd_separar_lote", "categoria"]], use_container_width=True)

                # Gerar Excel em memória para Download
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine="openpyxl") as writer:
                    for cat, df_cat in resultados_categorias.items():
                        df_export = df_cat.drop(columns=["demanda_nao_atendida", "necessidade_bruta"], errors="ignore")
                        aba_nome = cat[:31]
                        df_export.to_excel(writer, sheet_name=aba_nome, index=False)

                    if not df_lotes_fefo_total.empty:
                        df_lotes_fefo_total.to_excel(writer, sheet_name="Separacao_Lotes_FEFO", index=False)
                        
                output.seek(0)
                
                st.markdown("---")
                st.markdown("### 📥 Download do Resultado Final")
                st.download_button(
                    label="Baixar Planilha de Recomendação Consolidada (Excel)",
                    data=output,
                    file_name=f"recomendacao_caf_{hoje.strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    type="primary"
                )

