import streamlit as st

st.set_page_config(
    page_title="Home",
    page_icon="🎢",
    layout="wide" 
)

st.sidebar.markdown('# Curry Company')
st.sidebar.markdown(' ## Fastest Delivery in Town')
st.sidebar.markdown("___")

st.write("# Curry Company Growth Dashboard")

st.markdown(
    """
    Growth Dashboard foi construído para acompanhar as métricas de crescimento dos Entregadores e Construídos.
    ### Como utilizar esse Growth Dashboard?
    - Visão Empresa:
        - Visão Gerencial: Métricas gerais de comportamento.
        - Visão Tática: Indicadores semanais de crescimento.
        - Visão Geográfica: Insights de geolocalização.
    - Visão Entregador:
        - Acompanhamento dos indicadores semanais de crescimento
    - Visão Restaurante:
        - Indicadores semanais de crescimento dos restaurantes
    ### Ask for Help
    - Time de Data Science no Discord
        - @eu
    """
)