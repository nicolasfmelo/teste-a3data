from PySide2.QtCore import QObject, Slot, Signal
import pandas as pd

from core.handler import DataHandler, DataConstants, ChartMaker
from view.view import View

class MainController:


    def __init__(self) -> None:
        self.chart_maker = ChartMaker()
        self.main_view = View()
        

    def run(self):
        self.main_view.run()