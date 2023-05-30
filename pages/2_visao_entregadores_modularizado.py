# Bibliotecas

from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st
import folium
from streamlit_folium import folium_static

#---------------------------------------
#Funções
#---------------------------------------
def top_delivers(df1, top_asc):
    df2 = df1.loc[:, ['Delivery_person_ID', 'City', 'Time_taken(min)']].groupby(['City', 'Delivery_person_ID']).mean().sort_values(['City', 'Time_taken(min)'], ascending=top_asc).reset_index()

    df_aux01 = df2.loc[df2['City']=='Metropolitian',:].head(10)
    df_aux02 = df2.loc[df2['City']=='Urban', :].head(10)
    df_aux03 = df2.loc[df2['City']=='Semi-Urban', :].head(10)

    df3 = pd.concat([df_aux01, df_aux02, df_aux03]).reset_index(drop=True)
    
    return df3

def clean_code(df1):
    #conversão da coluna Age de texto para inteiro
    remove_nan = df1['Delivery_person_Age'] != 'NaN '
    df1 = df1.loc[remove_nan, :].copy()
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)

    #conversão da coluna Ratings de texto para decimal(float)
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)

    #conversão da coluna Multiples Deliveries de texto para inteiro
    remove_nan = df1['multiple_deliveries'] != 'NaN '
    df1 = df1.loc[remove_nan, :].copy()
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int)

    #conversão da coluna data de texto para formato de data
    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format='%d-%m-%Y')

    #remoção dos NaN nas colunas
    remove_nan = df1['City'] != 'NaN '
    df1 = df1.loc[remove_nan, :].copy()

    remove_nan = df1['Weatherconditions'] != 'conditions NaN'
    df1 = df1.loc[remove_nan, :].copy()

    remove_nan = df1['Road_traffic_density'] != 'NaN '
    df1 = df1.loc[remove_nan, :].copy()

    remove_nan = df1['Festival'] != 'NaN '
    df1 = df1.loc[remove_nan, :].copy()

    # Resete nos index
    df1 = df1.reset_index(drop=True)


    #remoção dos espaços nos finais das strings
    df1['ID'] = df1.loc[:, 'ID'].str.strip()
    df1['City'] = df1.loc[:, 'City'].str.strip()
    df1['Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip()
    df1['Type_of_vehicle'] = df1.loc[:,'Type_of_vehicle'].str.strip()
    df1['Road_traffic_density'] = df1.loc[:, 'Road_traffic_density'].str.strip()
    df1['Delivery_person_ID'] = df1.loc[:, 'Delivery_person_ID'].str.strip()

    # Limpando a coluna time taken
    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply( lambda x: x.split( '(min) ')[1] ) #usando função lambda para remover de cada linha(x) o parametro passado pelo split
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(int) #transformando os valores da coluna em inteiro
    
    return df1

# --------------------- Inicio da estrutura logica do codigo ---------------------------------

# Importar dataset
df = pd.read_csv( 'dataset/train.csv' )

#limpesa do dataframe 
df1 = clean_code(df)

###########################
#Barra Lateral Streamlit
###########################

#Aumentando o tamanho da página usável 
st.set_page_config(layout="wide")

st.title('Marketplace - Visão Entregadores')

st.sidebar.markdown('# Curry Company')
st.sidebar.markdown(' ## Fastest Delivery in Town')
st.sidebar.markdown("___")

st.sidebar.markdown('Selecione uma data limite')

date_slider = st.sidebar.slider(
    'Até qual valor?',
    value=pd.to_datetime('2022-04-13').to_pydatetime(),
    min_value=pd.to_datetime('2022-02-11').to_pydatetime(),
    max_value=pd.to_datetime('2022-04-06').to_pydatetime(),
    format='DD-MM-YYYY')
st.sidebar.markdown("___")

traffic_options = st.sidebar.multiselect(
    'Quais condições de trânsito',
    ['Low', 'Medium', 'High', 'Jam'],
    default=['Low', 'Medium', 'High', 'Jam'])
st.sidebar.markdown("___")

conditions_option = st.sidebar.multiselect(
    'Quais condições climáticas?',
    ['conditions Sunny', 'conditions Stormy', 'conditions Sandstorms',
       'conditions Cloudy', 'conditions Fog', 'conditions Windy'],
    default=['conditions Sunny', 'conditions Stormy', 'conditions Sandstorms',
       'conditions Cloudy', 'conditions Fog', 'conditions Windy'])

st.sidebar.markdown("___")

#filtro de datas
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, :]

#filtro de transito
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas, :]

#filtro de condições climáticas
linhas_selecionadas = df1['Weatherconditions'].isin(conditions_option)
df1 = df1.loc[linhas_selecionadas, :]


###########################
#Layout Streamlit
###########################

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '_', '_'])

with tab1:
    with st.container():
        st.title('Overall Metrics')
        
        col1, col2, col3, col4 = st.columns(4, gap='large')
        with col1:
            maior_idade = df1.loc[:, 'Delivery_person_Age'].max()
            col1.metric('Maior Idade', maior_idade)
            
        with col2:
            menor_idade = df1.loc[:, 'Delivery_person_Age'].min()
            col2.metric('Menor Idade', menor_idade)
            
        with col3:
            melhor_condicao = df1.loc[:, 'Vehicle_condition'].max()
            col3.metric('Melhor Condição', melhor_condicao)
            
        with col4:
            pior_condicao = df1.loc[:, 'Vehicle_condition'].min()
            col4.metric('Pior Condição', pior_condicao)
        
    with st.container():
        st.markdown('''___''')
        st.title('Avaliações')
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader('Avaliação media por entregador')
            df_av_media = df1.loc[:, ['Delivery_person_ID', 'Delivery_person_Ratings']].groupby('Delivery_person_ID').mean().reset_index()
            st.dataframe(df_av_media)
        
        with col2:
            #avaliação por tipo de transito
            st.subheader('Avaliação media por trânsito')
            df_final = df1.loc[:, ['Delivery_person_Ratings', 'Road_traffic_density']].groupby('Road_traffic_density').agg( { 'Delivery_person_Ratings' : ['mean', 'std'] } )

            # mudança de nome das colunas
            df_final.columns = ['Delivery Media', 'Delivery D.P']
            
            st.dataframe(df_final)
            
            #Avaliação por clima
            st.subheader('Avaliação media por clima')
            df_final = df1.loc[:, ['Delivery_person_Ratings', 'Weatherconditions']].groupby('Weatherconditions').agg( {'Delivery_person_Ratings' : ['mean', 'std']} )

            df_final.columns = ['Delivery Media', 'Delivery D.P']
            
            st.dataframe(df_final)
    
    with st.container():
        st.markdown('''___''')
        st.title('Velocidade de entrega')
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader('Top entregadores mais rápidos')
            df3 = top_delivers(df1, top_asc=True)
            st.dataframe(df3)
            
        with col2:
            st.subheader('Top entregadores mais lentos')
            df3 = top_delivers(df1, top_asc=False)
            st.dataframe(df3)
            
            
            