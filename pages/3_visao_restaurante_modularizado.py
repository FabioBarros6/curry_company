# Bibliotecas

from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import streamlit as st
import folium
from streamlit_folium import folium_static

#---------------------------------------
#Funções
#---------------------------------------
def media_desvio_traffic(df1):
    colunas = ['Time_taken(min)', 'City', 'Road_traffic_density']
    df_aux = df1.loc[:, colunas].groupby(['City', 'Road_traffic_density']).agg( {'Time_taken(min)': ['mean', 'std']} )
    df_aux.columns = ['Tempo_Medio', 'D.P_Tempo']
    df_aux = df_aux.reset_index()

    #gráfico
    figura = px.sunburst( df_aux, path=['City', 'Road_traffic_density'], values='Tempo_Medio', color='D.P_Tempo', color_continuous_scale='RdBu', color_continuous_midpoint=np.average(df_aux['D.P_Tempo']))
    
    return figura

def desvio_padrao_graffic(df1):
    colunas = ['Time_taken(min)', 'City']
    df_aux = df1.loc[:, colunas].groupby('City').agg( {'Time_taken(min)': ['mean', 'std']} )
    df_aux.columns = ['Tempo_Medio', 'D.P_Tempo']
    df_aux = df_aux.reset_index()

    #grafico
    figura = go.Figure()
    figura.add_trace(go.Bar(name='Control', x=df_aux['City'], y=df_aux['Tempo_Medio'], error_y=dict( type='data', array=df_aux['D.P_Tempo'])))
    figura.update_layout(barmode='group')

    return figura 

def media_desvio_de_tempo(df1, festival, op):
    """
        Esta função calcula o tempo médio e desvio padão por entrega.
        Parametros:
            Input:
                -df: Dataframe com dados necessários para os calculos
                -op: Tipo de operação que precisa ser calculado
                    'Tempo_Medio' : Calcula o tempo médio
                    'Desvio_Padrao': Calcula o desvio padrão do tempo
            Output:
                -df: Dataframe com 2 colunas e 1 linha.

    """
    df_aux = df1.loc[:, ['Time_taken(min)', 'Festival']].groupby('Festival').agg( {'Time_taken(min)': ['mean', 'std']} )

    df_aux.columns = ['Tempo_Medio', 'Desvio_Padrao']
    df_aux = df_aux.reset_index()
    df_aux = np.round(df_aux.loc[df_aux['Festival'] == festival, op], 2)

    return df_aux


def distance(df1, fig):
    if fig == False:
        colunas = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']

        distancia_media = df1['distance'] = df1.loc[:, colunas].apply( lambda x: haversine( (x['Restaurant_latitude'], x['Restaurant_longitude']), (x['Delivery_location_latitude'], x['Delivery_location_longitude']) ), axis=1 )

        distancia_media = np.round( df1['distance'].mean(), 2 )

        return distancia_media
    
    else:
        colunas = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']

        distancia_media = df1['distance'] = df1.loc[:, colunas].apply( lambda x: haversine( (x['Restaurant_latitude'], x['Restaurant_longitude']), (x['Delivery_location_latitude'], x['Delivery_location_longitude']) ), axis=1 )

        distancia_media = df1.loc[:, ['City', 'distance']].groupby('City').mean().reset_index()   
        figure = go.Figure(data = go.Pie(labels= distancia_media['City'], values= distancia_media['distance'], pull=[0, 0.1, 0]))
        
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
    df1['Festival'] = df1.loc[:, 'Festival'].str.strip()

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

st.title('Marketplace - Visão Restaurante')

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
    #container 1
    with st.container():
        st.title("Overall Metrics")
        col1, col2, col3, col4, col5, col6 = st.columns(6, gap='small')
        with col1:
            entregadores_unicos = len(df1.loc[:, 'Delivery_person_ID'].unique())
            col1.metric('Entregadores Únicos', entregadores_unicos)
            
        with col2:
            distancia_media = distance(df1, fig=False)
            col2.metric('Distância média das entregas', distancia_media)
 
        with col3:
            df_aux = media_desvio_de_tempo(df1, 'Yes', 'Tempo_Medio')
            col3.metric('T.M de entregas com Festival', df_aux)
              
        with col4:
            df_aux = media_desvio_de_tempo(df1, 'Yes', 'Desvio_Padrao')
            col4.metric('D.P de entregas com Festival', df_aux)
              
            
            
        with col5:
            df_aux = media_desvio_de_tempo(df1, 'No', 'Desvio_Padrao')
            col5.metric('T.M de entregas sem Festival', df_aux)
            
        with col6:
            df_aux = media_desvio_de_tempo(df1, 'No', 'Desvio_Padrao')
            col6.metric('D.P de entregas sem Festival', df_aux)
            
        st.markdown('''___''')
    
    #container 2
    with st.container():
        
        col1, col2 = st.columns(2, gap='large')
        with col1:
            figura = desvio_padrao_graffic(df1)
            st.plotly_chart(figura)          
            
        with col2:
            colunas = ['Time_taken(min)', 'City', 'Type_of_order']
            df_aux = df1.loc[:, colunas].groupby(['City', 'Type_of_order']).agg( {'Time_taken(min)': ['mean', 'std']} )
            df_aux.columns = ['Tempo_Medio', 'D.P_Tempo']
            df_aux = df_aux.reset_index()
            st.dataframe(df_aux)

        st.markdown('''___''')
    
    #container 3
    with st.container():
        st.title("Distribuição por tempo")
        
        col1, col2 = st.columns(2, gap='medium')
        with col1:            
            figure = distance(df1, fig=True)
            st.plotly_chart(figure)

        with col2:                
            figura = media_desvio_traffic(df1)
            st.plotly_chart(figura)
            
        st.markdown('''___''')
        

