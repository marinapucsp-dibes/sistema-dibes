import streamlit as st
import pandas as pd

st.set_page_config(page_title="Sistema de Monitoramento DIBES", layout="wide")

st.title("📊 Sistema de Monitoramento DIBES")

arquivo = st.file_uploader("Envie sua planilha (Excel ou CSV)", type=["xlsx", "csv"])

if arquivo:
    # 📂 Leitura automática
    if arquivo.name.endswith(".csv"):
        df = pd.read_csv(arquivo, sep=";", encoding="latin1", on_bad_lines="skip")
    else:
        df = pd.read_excel(arquivo, engine="openpyxl")
    st.subheader("📋 Dados carregados")
    st.dataframe(df, use_container_width=True)

    colunas = df.columns.tolist()
    colunas_lower = [c.lower() for c in colunas]

    # 🧠 Identificação automática
    tipo_detectado = "Desconhecido"

    if any("renda" in c for c in colunas_lower):
        tipo_detectado = "Cadastro Único / Renda"
    elif any("beneficio" in c for c in colunas_lower):
        tipo_detectado = "Benefícios (BPC / Bolsa Família)"
    elif any("condicionalidade" in c for c in colunas_lower):
        tipo_detectado = "Condicionalidades"
    elif any("atualizacao" in c or "atualização" in c for c in colunas_lower):
        tipo_detectado = "Atualização Cadastral"

    st.success(f"📌 Tipo identificado: {tipo_detectado}")

    # 🔎 Busca inteligente
    st.sidebar.header("🔎 Busca")
    busca = st.sidebar.text_input("Buscar por Nome, NIS ou CPF")

    if busca:
        df = df[df.apply(lambda x: x.astype(str).str.contains(busca, case=False).any(), axis=1)]

    # 📅 Filtro por data (se existir)
    coluna_data = next((c for c in colunas if "atual" in c.lower()), None)

    if coluna_data:
        st.sidebar.header("📅 Atualização cadastral")
        anos = st.sidebar.number_input("Sem atualizar há (anos)", value=2)

        if st.sidebar.button("Ver desatualizados"):
            df[coluna_data] = pd.to_datetime(df[coluna_data], errors="coerce")
            limite = pd.Timestamp.now() - pd.DateOffset(years=anos)

            filtro = df[df[coluna_data] <= limite]

            st.warning("Cadastros desatualizados")
            st.dataframe(filtro)
            st.metric("Total", len(filtro))

    # 💰 Filtro de renda (se existir)
    coluna_renda = next((c for c in colunas if "renda" in c.lower()), None)

    if coluna_renda:
        st.sidebar.header("💰 Renda")
        valor = st.sidebar.number_input("Renda até", value=218)

        if st.sidebar.button("Filtrar por renda"):
            filtro = df[df[coluna_renda] <= valor]
            st.dataframe(filtro)
            st.metric("Total", len(filtro))

    # ⚠️ Situação (se existir)
    coluna_situacao = next((c for c in colunas if "situacao" in c.lower()), None)

    if coluna_situacao:
        st.sidebar.header("⚠️ Situação")
        opcoes = df[coluna_situacao].dropna().unique()
        escolha = st.sidebar.selectbox("Filtrar situação", ["Todas"] + list(opcoes))

        if escolha != "Todas":
            df = df[df[coluna_situacao] == escolha]

    # 📊 Resultado final
    st.subheader("📊 Resultado Final")
    st.metric("Total de registros", len(df))
    st.dataframe(df, use_container_width=True)

    # 📥 Download
    if not df.empty:
        df.to_excel("resultado.xlsx", index=False)

        with open("resultado.xlsx", "rb") as f:
            st.download_button(
                "📥 Baixar resultado",
                data=f,
                file_name="resultado.xlsx"
            )
