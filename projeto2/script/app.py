import os
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Notícias EAJ - UFRN", page_icon="🌾", layout="centered"
)

st.title("🌾 Publicações de Notícias sobre a EAJ - UFRN")
st.markdown(
    "Visualização da quantidade de notícias publicadas no portal da UFRN que mencionam a **Escola Agrícola de Jundiaí (EAJ)**."
)

caminho = "noticias_eaj.txt"

if os.path.exists(caminho):
    df = pd.read_csv(caminho, sep="\t")

    if not df.empty and "ano" in df.columns:
        df["ano"] = df["ano"].astype(str)
        df_validos = df[df["ano"] != "Ano não identificado"]

        # Reestrutura a contagem para um DataFrame explícito
        contagem = (
            df_validos["ano"]
            .value_counts()
            .reset_index()
        )
        contagem.columns = ["Ano", "Quantidade"]
        contagem = contagem.sort_values("Ano")

        col1, col2 = st.columns(2)
        col1.metric("Total de Notícias", len(df))
        if not contagem.empty:
            col2.metric(
                "Período Analisado",
                f"{contagem['Ano'].min()} - {contagem['Ano'].max()}",
            )

        st.subheader("📊 Quantidade de Notícias Publicadas por Ano")
        
        # Mapeia explicitamente os eixos X e Y
        st.bar_chart(contagem, x="Ano", y="Quantidade")

        with st.expander("📋 Ver lista detalhada de URLs coletadas"):
            st.dataframe(df, use_container_width=True)
    else:
        st.warning(
            "O arquivo está vazio. Execute `python scraper.py` novamente."
        )
else:
    st.error(
        f"Arquivo '{caminho}' não encontrado. Execute o script `scraper.py` primeiro."
    )