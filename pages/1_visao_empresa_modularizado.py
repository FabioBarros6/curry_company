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
def country_map(df1):
    df_aux = df1.loc[:, ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']].groupby(['City', 'Road_traffic_density']).median().reset_index()

    #mapa de localização
    map = folium.Map()

    for index, location_info in df_aux.iterrows():
      folium.Marker( [location_info['Delivery_location_latitude'], 
                      location_info['Delivery_location_longitude']],
                      popup=location_info[['City', 'Road_traffic_density']]).add_to(map)

    folium_static(map, width=1024, height=600)

def order_share_week(df1):
    df_aux01 = df1.loc[:, ['ID', 'weeks']].groupby('weeks').count().reset_index()
    df_aux02 = df1.loc[:, ['Delivery_person_ID', 'weeks']].groupby('weeks').nunique().reset_index()

    #juntando os dois dataframes 01 e 02 em um unico
    df_aux = pd.merge(df_aux01, df_aux02, how='inner')
    df_aux['entregas_por_entregador'] = df_aux['ID'] / df_aux['Delivery_person_ID'] #Criação de nova coluna de entregas por entregador
    #gráfico
    figure = px.line(df_aux, x='weeks', y='entregas_por_entregador')

    return figure

def order_week(df1):
    df1['weeks'] = df1['Order_Date'].dt.strftime('%U')

    colunas = ['ID', 'weeks']

    df_aux = df1.loc[:, colunas].groupby('weeks').count().reset_index()

    #gráfico
    figure = px.line(df_aux, x='weeks', y='ID')

    return figure

def order_traffic_city(df1):
    df_aux = df1.loc[:, ['ID', 'City', 'Road_traffic_density']].groupby(['City', 'Road_traffic_density']).count().reset_index()

    #gráfico
    figure = px.scatter(df_aux, 'City', y='Road_traffic_density', size='ID', color='City')

    return figure

def order_traffic(df1):
    df_aux = df1.loc[:, ['ID', 'Road_traffic_density']].groupby('Road_traffic_density').count().reset_index()
    df_aux['percent_entregas'] = df_aux['ID'] / df_aux['ID'].sum()

    #gráfico
    figure = px.pie(df_aux, values='percent_entregas', names='Road_traffic_density')

    return figure

def order_day(df1):
    colunas = ['ID', 'Order_Date']
    #seleção das linhas
    df_aux = df1.loc[:, colunas].groupby('Order_Date').count().reset_index()

    #gráfico
    figure = px.bar(df_aux, x='Order_Date', y='ID')
    
    return figure

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
st.set_page_config(layout='wide')

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

#filtro de datas
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, :]

#filtro de transito
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas, :]

###########################
#Layout Streamlit
###########################

st.header('Marketplace - Visão Cliente')

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

with tab1:
    with st.container():
        figure = order_day(df1)
        st.markdown('# Order by Day')
        st.plotly_chart(figure, use_container_width=True)

    with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            figure = order_traffic(df1)
            st.markdown('# Order by Traffic')
            st.plotly_chart(figure, use_container_width=True)
                  
        with col2:
            st.markdown('# Traffic Order City')
            figure = order_traffic_city(df1)
            st.plotly_chart(figure, use_container_width=True)
            
with tab2:
    with st.container():
        st.header('Order by Week')
        figure = order_week(df1)
        st.plotly_chart(figure, use_container_width=True)

    with st.container():
        st.header('Order Share by Week')
        fgirue = order_share_week(df1)
        st.plotly_chart(figure, use_container_width=True)

with tab3:
    st.header('Country Maps')
    country_map(df1)
    