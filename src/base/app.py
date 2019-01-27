from ..gui.kivy_gui.gui_app import KivyGuiApp


class App:
    def __init__(self):
        self.gui = KivyGuiApp()

    def start(self):
        self.gui.run()
