from kivy.app import App


class AppGui(App):
    def __init__(self, name: str, **kwargs):
        super(AppGui, self).__init__(**kwargs)
        self.title = name
