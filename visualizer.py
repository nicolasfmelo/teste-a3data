import streamlit as stlt

import pandas as pd
import numpy as np

import folium
from streamlit_folium import folium_static
import plotly.express as px

class View:

    def __init__(self) -> None:
        self.pagination = 1

    def header(self):
        stlt.image("project/view/assets/logo_original.png", width=500)
        stlt.markdown('-----')
    
    def body(self):
        self.register_session_state('intro', False)
        if not stlt.session_state['intro']:
            container = stlt.empty()
            with container.container():
                self.header()
                stlt.subheader('Acidentes e incidentes na aviação civil brasileira')
                collumn_1, collumn_2, collumn_3 = stlt.columns(3)
                collumn_1.image("project/view/assets/1.jpg")
                collumn_2.image("project/view/assets/2.jpg")
                collumn_3.image("project/view/assets/3.jpg")
                stlt.markdown('-----')
                self.render_text("project/view/assets/about.txt")
                stlt.markdown('-----')
                self.render_text("project/view/assets/database.txt")
            self.button(self.bar_chart)
    
    def register_session_state(self, key, flag):
        if key not in stlt.session_state:
            stlt.session_state[key] = flag

    def render_text(self, path_to_text):
        with open(path_to_text, 'r') as file:
            text = file.read()
            stlt.write(text)


    def switch_session_state(self, key, flag):
        stlt.session_state[key] = flag

    def scatter_map(self):
        self.pagination+=1
        container = stlt.empty()
        with container.container():
            self.header()
            stlt.subheader('Distribuição geográfica dos acidentes e incidentes aéreos no Brasil')
            new_ocurrence = pd.read_csv('csv/new_ocurrence.csv', sep=',', index_col=0)
            dataframe = pd.DataFrame({"classificacao": new_ocurrence["classificacao"], "latitude": new_ocurrence['latitude'], "longitude": new_ocurrence['longitude']})
            chart_map = folium.Map(location=[dataframe['latitude'].mean(), dataframe['longitude'].mean()],zoom_start=4)
            for index, row in dataframe.iterrows():
                if row['classificacao'] == "ACIDENTE":
                    color = "red"
                else:
                    color = "blue"
                folium.CircleMarker(location=[row['latitude'], row['longitude']], popup=row['classificacao'], radius=1, fill=True, fill_opacity=0.8, color=color).add_to(chart_map)
            folium_static(chart_map)
            self.caption("Acidentes", "red")
            self.caption("Incidentes", "blue")
        self.button(self.acident_register)
    
    def button(self, on_click):
        stlt.button(f'Page {self.pagination}', on_click=on_click)

    def caption(self, text, color):
        stlt.markdown(f"<h5 style='color: {color};'> &#x2022 {text}</h5>", unsafe_allow_html=True)

    def bar_chart(self):
        self.pagination+=1
        self.switch_session_state('intro', True)
        container = stlt.empty()
        with container.container():
            self.header()
            stlt.subheader('Distribuição temporal dos acidentes e incidentes aéreos no Brasil')
            new_ocurrence = pd.read_csv('csv/new_ocurrence.csv', sep=',', index_col=0)
            dataframe = pd.DataFrame({"classificacao": new_ocurrence["classificacao"], "ocorrencia_dia": new_ocurrence['dia_ocorrencia']})
            dataframe['ocorrencia_dia'] = pd.to_datetime(dataframe['ocorrencia_dia'])
            dataframe['ocorrencia_dia'] = dataframe['ocorrencia_dia'].dt.year
            dataframe = dataframe.groupby(['ocorrencia_dia', 'classificacao']).size().unstack()
            stlt.bar_chart(dataframe)
        self.button(self.scatter_map)

    def acident_register(self):
        self.header()
        self.pagination+=1
        self.switch_session_state('intro', True)
        container = stlt.empty()
        with container.container():
            df_ocurrence = pd.read_csv("ocorrencia.csv")
            data = df_ocurrence[(df_ocurrence["classificacao"]=="INCIDENTE GRAVE") & (df_ocurrence["pais"]=="BRASIL")].groupby("tipo").size().sort_values(ascending=False).to_dict()
            df = pd.DataFrame(data.items(), columns=['Incidente', 'Quantidade'])
            fig = px.pie(df[:10], values='Quantidade', names='Incidente', title='10 maiores causas de incidentes aéreos no Brasil')
            stlt.plotly_chart(fig)
            data = df_ocurrence[(df_ocurrence["classificacao"]=="ACIDENTE") & (df_ocurrence["pais"]=="BRASIL")].groupby("tipo").size().sort_values(ascending=False).to_dict()
            df = pd.DataFrame(data.items(), columns=['Acidente', 'Quantidade'])
            fig = px.pie(df[:10], values='Quantidade', names='Acidente', title='10 maiores causas de acidentes aéreos no Brasil')
            stlt.plotly_chart(fig)
        self.button(self.acident_stages)

    def acident_stages(self):
        self.header()
        self.pagination+=1
        self.switch_session_state('intro', True)
        container = stlt.empty()
        with container.container():
            df_acident = pd.read_csv("./csv/bre_acidente.csv")
            data = df_acident[df_acident["classificacao"]=="ACIDENTE"].groupby("fase_operacao").size().sort_values(ascending=False)
            df = pd.DataFrame(data.items(), columns=['Fase da Operacao', 'Quantidade'])
            fig = px.pie(df[:10], values='Quantidade', names='Fase da Operacao', title='Fases de operação com maior número de acidentes')
            stlt.plotly_chart(fig)
            data = df_acident[df_acident["classificacao"]=="INCIDENTE GRAVE"].groupby("fase_operacao").size().sort_values(ascending=False)
            df = pd.DataFrame(data.items(), columns=['Fase da Operacao', 'Quantidade'])
            fig = px.pie(df[:10], values='Quantidade', names='Fase da Operacao', title='Fases de operação com maior número de incidentes')
            stlt.plotly_chart(fig)
        self.button(self.airplane_type)


    def airplane_type(self):
        self.header()
        self.pagination+=1
        self.switch_session_state('intro', True)
        container = stlt.empty()
        with container.container():
            df_composed = pd.read_csv("./csv/composed.csv")
            data = df_composed[df_composed["classificacao"]=="ACIDENTE"].groupby("equipamento").size().sort_values(ascending=False)
            df = pd.DataFrame(data.items(), columns=['Aeronave', 'Quantidade'])
            fig = px.pie(df, values='Quantidade', names='Aeronave', title='Tipos de aeronaves com maior número de acidentes')
            stlt.plotly_chart(fig)
            data = df_composed[df_composed["classificacao"]=="INCIDENTE GRAVE"].groupby("equipamento").size().sort_values(ascending=False)
            df = pd.DataFrame(data.items(), columns=['Aeronave', 'Quantidade'])
            fig = px.pie(df, values='Quantidade', names='Aeronave', title='Tipos de aeronaves com maior número de incidentes')
            stlt.plotly_chart(fig)
        self.button(self.airplane_size)

    def airplane_size(self):
        self.header()
        self.pagination+=1
        self.switch_session_state('intro', True)
        container = stlt.empty()
        with container.container():
            df_composed = pd.read_csv("./csv/composed.csv")
            data = df_composed[df_composed["classificacao"]=="ACIDENTE"].groupby("tipo_motor").size().sort_values(ascending=False)
            df = pd.DataFrame(data.items(), columns=['Tipo de Motor', 'Quantidade'])
            fig = px.pie(df, values='Quantidade', names='Tipo de Motor', title='Tipos de motor com maior número de acidentes')
            stlt.plotly_chart(fig)
            data = df_composed[df_composed["classificacao"]=="INCIDENTE GRAVE"].groupby("tipo_motor").size().sort_values(ascending=False)
            df = pd.DataFrame(data.items(), columns=['Tipo de Motor', 'Quantidade'])
            fig = px.pie(df, values='Quantidade', names='Tipo de Motor', title='Tipos de motor com maior número de incidentes')
            stlt.plotly_chart(fig)
        self.button(self.lvl_damge)

    def lvl_damge(self):
        self.header()
        self.pagination+=1
        self.switch_session_state('intro', True)
        container = stlt.empty()
        with container.container():
            df_composed = pd.read_csv("./csv/composed.csv")
            data = df_composed[df_composed["classificacao"]=="ACIDENTE"].groupby("nivel_dano").size().sort_values(ascending=False)
            df = pd.DataFrame(data.items(), columns=['Nivel de Dano', 'Quantidade'])
            fig = px.pie(df, values='Quantidade', names='Nivel de Dano', title='Níveis de dano com maior número de acidentes')
            stlt.plotly_chart(fig)
            data = df_composed[df_composed["classificacao"]=="INCIDENTE GRAVE"].groupby("nivel_dano").size().sort_values(ascending=False)
            df = pd.DataFrame(data.items(), columns=['Nivel de Dano', 'Quantidade'])
            fig = px.pie(df, values='Quantidade', names='Nivel de Dano', title='Níveis de dano com maior número de incidentes')
            stlt.plotly_chart(fig)
        self.button(self.categorie_plane)


    def categorie_plane(self):
        self.header()
        self.pagination+=1
        self.switch_session_state('intro', True)
        container = stlt.empty()
        with container.container():
            df_composed = pd.read_csv("./csv/composed.csv")
            data = df_composed[df_composed["classificacao"]=="ACIDENTE"].groupby("categoria_aviacao").size().sort_values(ascending=False)
            df = pd.DataFrame(data.items(), columns=['Categoria', 'Quantidade'])
            fig = px.pie(df, values='Quantidade', names='Categoria', title='Categorias de aviação com maior número de acidentes')
            stlt.plotly_chart(fig)
            data = df_composed[df_composed["classificacao"]=="INCIDENTE GRAVE"].groupby("categoria_aviacao").size().sort_values(ascending=False)
            df = pd.DataFrame(data.items(), columns=['Categoria', 'Quantidade'])
            fig = px.pie(df, values='Quantidade', names='Categoria', title='Categorias de aviação com maior número de incidentes')
            stlt.plotly_chart(fig)
    
    def run(self):
        self.body()


if __name__ == "__main__":
    view = View()
    view.run()