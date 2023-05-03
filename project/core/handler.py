import pandas as pd
import numpy as np

from unidecode import unidecode
import plotly.express as px
import toml

class ChartMaker:

    def __init__(self, dataframe: pd.DataFrame) -> None:
        self.dataframe = dataframe
        self.graphs = toml.load("config/order.cfg")

    
    def make_pie(self):
        figures = []
        subheader = "Acidentes e incidentes na aviação civil brasileira"
        title = 'Acidentes e incidentes na aviação civil brasileira'
        data = DataHandler().get_2collumn_by_condition_group(self.dataframe, 'classificacao', 'ACIDENTE', 'pais', "BRASIL", "tipo")
        df = pd.DataFrame(data.items(), columns=['Incidente', 'Quantidade'])
        values = "Quantidade"
        names = "Incidente"
        figure = DataHandler().make_figure(df[:10], values, names, title)
        figures.append(figure)
        title = 'Acidentes e incidentes na aviação civil brasileira'
        data = DataHandler().get_2collumn_by_condition_group(self.dataframe, 'classificacao', 'ACIDENTE', 'pais', "BRASIL", "tipo")
        df = pd.DataFrame(data.items(), columns=['Incidente', 'Quantidade'])
        figure = DataHandler().make_figure(df[:10], values, names, title)
        figures.append(figure)
    
    def make_scatter(self, dataframe: pd.DataFrame, title: str):
        ...
    
    def make_bar(self, dataframe: pd.DataFrame, title: str):
        ...

    def make_chart(self, flag: str):
        if flag == "scatter":
            return self.make_scatter()
        elif flag == "bar":
            return self.make_bar()
        elif flag == "pie":
            return self.make_pie()

class DataConstants:


    def __init__(self) -> None:
        self.city_df = DataHandler.get_data_frame('data/municipios.csv')
        self.states_df = DataHandler.get_data_frame('data/estados.csv')
        self.ocurrency_df = DataHandler.get_data_frame('data/ocorrencia.csv')
        self.aircraft_df = DataHandler.get_data_frame('data/aeronave.csv')
    
    def __normalize_citys(self)->pd.DataFrame:
        self.city_df = DataHandler.inherit_conditional_collumn(self.city_df, self.states_df, 'uf', 'codigo_uf')
        self.city_df = DataHandler.normalize_collumn_str(self.city_df, 'nome')
        return self.city_df
        
    def __adjust_locality(self):
        condition = self.ocurrency_df["localidade"]=="***"
        self.ocurrency_df.loc[condition, "localidade"] = self.ocurrency_df[condition]["uf"]
        condition = self.ocurrency_df["uf"]=="***"
        self.ocurrency_df = self.ocurrency_df.drop(self.ocurrency_df[condition].index)

        condition = self.ocurrency_df["localidade"]=="NAO IDENTIFICADA"
        self.ocurrency_df.loc[condition, "localidade"] = self.ocurrency_df[condition]["uf"]
        return self.ocurrency_df
    
    def __drop_country(self):
        condition = self.ocurrency_df["pais"]!="BRASIL"
        self.ocurrency_df = self.ocurrency_df.drop(self.ocurrency_df[condition].index)
        return self.ocurrency_df
    
    def __get_latitude(self, city_name: str):
        try:
            return self.city_df[self.city_df["nome"]==city_name]["latitude"].values[0]
        except:
            return self.states_df[self.states_df["uf"]==city_name]["latitude"].values[0]
    

    def __get_longitude(self, city_name: str):
        try:
            return self.city_df[self.city_df["nome"]==city_name]["longitude"].values[0]
        except:
            return self.states_df[self.states_df["uf"]==city_name]["longitude"].values[0]

    def __make_lat_long_df(self):
        self.city_df = self.__normalize_citys()
        self.ocurrency_df = DataHandler.normalize_collumn_str(self.ocurrency_df, 'localidade')
        self.ocurrency_df = self.__adjust_locality()
        self.ocurrency_df = self.__drop_country()
        self.ocurrency_df["latitude"] = self.ocurrency_df["localidade"].apply(lambda x: self.__get_latitude(x))
        self.ocurrency_df["longitude"] = self.ocurrency_df["localidade"].apply(lambda x: self.__get_longitude(x))
        return self.ocurrency_df


    def pre_process(self):
        self.main_dataframe = self.__make_lat_long_df()
        self.main_dataframe = self.__add_principal_collumns()
        return self.main_dataframe
    
    def __add_principal_collumns(self):
        self.main_dataframe = DataHandler.inherit_conditional_collumn(self.main_dataframe, self.aircraft_df, 'tipo_motor', "codigo_ocorrencia")
        self.main_dataframe = DataHandler.inherit_conditional_collumn(self.main_dataframe, self.aircraft_df, 'equipamento', "codigo_ocorrencia")
        self.main_dataframe = DataHandler.inherit_conditional_collumn(self.main_dataframe, self.aircraft_df, 'quantidade_motores', "codigo_ocorrencia")
        self.main_dataframe = DataHandler.inherit_conditional_collumn(self.main_dataframe, self.aircraft_df, 'nivel_dano', "codigo_ocorrencia")
        self.main_dataframe = DataHandler.inherit_conditional_collumn(self.main_dataframe, self.aircraft_df, 'fase_operacao', "codigo_ocorrencia")
        self.main_dataframe = DataHandler.inherit_conditional_collumn(self.main_dataframe, self.aircraft_df, 'categoria_aviacao', "codigo_ocorrencia")
        return self.main_dataframe

class DataHandler:

    
    @classmethod
    def get_data_frame(cls, file_path: str)-> pd.DataFrame:
        return pd.read_csv(file_path, sep=',')

    @classmethod
    def get_collumn_by_condition(cls, data_frame: pd.DataFrame, collumn_name: str, condition: str)-> pd.DataFrame:
        return data_frame[data_frame[collumn_name] == condition]
    
    def get_collumn_by_condition_group(cls, data_frame: pd.DataFrame, collumn_name: str, condition: str, group: str)-> dict:
        series = data_frame[data_frame[collumn_name] == condition]
        grouped_series = series.groupby(group)
        series_values = grouped_series.size().sort_values(ascending=False)
        return series_values
    
    @classmethod
    def get_2collumn_by_condition_group(cls, data_frame: pd.DataFrame, 
                                        collumn_name: str, condition: str, 
                                        collumn2: str, condition2: str, 
                                        group: str)-> dict:
        series = data_frame[(data_frame[collumn_name] == condition) & (data_frame[collumn2] == condition2)]
        grouped_series = series.groupby(group)
        series_values = grouped_series.size().sort_values(ascending=False)
        return series_values

    @classmethod
    def inherit_conditional_collumn(cls, data_frameA: pd.DataFrame, data_frameB: pd.DataFrame, collumn_name: str, by_condition: str)-> pd.DataFrame:
        data_frameA[collumn_name] = data_frameA[by_condition].apply(lambda x: data_frameB[data_frameB[by_condition] == x][collumn_name].values[0])
        return data_frameA


    @classmethod
    def series_to_dataframe(cls, series: pd.Series, collumn_names: list)-> pd.DataFrame:
        return pd.DataFrame(series.items(), columns=collumn_names)
    
    @classmethod
    def normalize_collumn_str(cls, data_frame: pd.DataFrame, collumn_name: str)-> pd.DataFrame:
        data_frame[collumn_name] = data_frame[collumn_name].apply(lambda x: unidecode(x).upper())
        return data_frame


    @classmethod
    def time_series_dataframe(cls, data_frame: pd.DataFrame):
        dataframe = pd.DataFrame({"classificacao": dataframe["classificacao"], "ocorrencia_dia": dataframe['dia_ocorrencia']})
        dataframe['ocorrencia_dia'] = pd.to_datetime(dataframe['ocorrencia_dia'])
        dataframe['ocorrencia_dia'] = dataframe['ocorrencia_dia'].dt.year
        dataframe = dataframe.groupby(['ocorrencia_dia', 'classificacao']).size().unstack()
        return data_frame
    
    @classmethod
    def make_figure(cls, data_frame: pd.DataFrame, values: str, names: str, title: str):
        figure = px.pie(data_frame, values=values, names=names, title=title)
        return figure

if __name__=="__main__":
    app = DataConstants()
    df = app.make_lat_long_df()
    print(df.head())
