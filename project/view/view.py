import streamlit as stlt
from streamlit_folium import folium_static
import folium
import pandas as pd

class View:

    def __init__(self, chart_maker: object) -> None:
        super().__init__()
        self.chart_maker = chart_maker
        self.pagination: int = 2
        self.register_session_state('intro', False)

    def render_header(self):
        stlt.image("view/assets/logo_original.png", width=500)
        stlt.markdown('-----')
    
    def body(self):
        if not stlt.session_state['intro']:
            container = stlt.empty()
            with container.container():
                self.render_header()
                stlt.subheader('Acidentes e incidentes na aviação civil brasileira')
                collumn_1, collumn_2, collumn_3 = stlt.columns(3)
                collumn_1.image("view/assets/1.jpg")
                collumn_2.image("view/assets/2.jpg")
                collumn_3.image("view/assets/3.jpg")
                stlt.markdown('-----')
                self.render_text("view/assets/about.txt")
                stlt.markdown('-----')
                self.render_text("view/assets/database.txt")
            self.button("bar_chart")
    
    def register_session_state(self, key, flag):
        if key not in stlt.session_state:
            stlt.session_state[key] = flag

    def render_text(self, path_to_text):
        with open(path_to_text, 'r') as file:
            text = file.read()
            stlt.write(text)

    def switch_session_state(self, key, flag):
        stlt.session_state[key] = flag

    def button(self,flag: str):
        stlt.button(f'Page {self.pagination}', on_click=self.chart_maker.make_chart, args=(flag,))
        self.pagination+=1


    def caption(self, text, color):
        stlt.markdown(f"<h5 style='color: {color};'> &#x2022 {text}</h5>", unsafe_allow_html=True)

    def scatter_map(self, dataframe: pd.DataFrame, title: str):
        container = stlt.empty()
        with container.container():
            self.render_header()
            stlt.subheader(title)
            dataframe = pd.DataFrame({"classificacao": dataframe["classificacao"], "latitude": dataframe['latitude'], "longitude": dataframe['longitude']})
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
        self.button("pie_chart")

    def bar_chart(self, dataframe, title):
        self.switch_session_state('intro', True)
        container = stlt.empty()
        with container.container():
            self.render_header()
            stlt.subheader(title)
            stlt.bar_chart(dataframe)
        self.button("map")

    def pie_chart(self, figures: list, callback: str):
        self.switch_session_state('intro', True)
        container = stlt.empty()
        with container.container():
            self.render_header()
            for figure in figures:
                stlt.plotly_chart(figure)
        if callback:
            self.button(callback)
    
    def run(self):
        self.body()


if __name__ == "__main__":
    view = View()
    view.run()