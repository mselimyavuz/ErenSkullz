import layout as lo
import global_var as gv


class About(lo.BoxLayout, lo.BaseWidget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'

    def on_parent(self, instance, par):
        self.add_widget(lo.Label(text='This is an NFT collection management app. For personal use. It does not sync or anything. Pretty basic app to be honest. Created mostly for Eren.', size_hint_y=None, height=lo.dp(50)))

class Roadmap(lo.BoxLayout, lo.BaseWidget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'

    def on_parent(self, instance, par):
        self.add_widget(lo.Label(text='v1.5 -- Prettier graphics.', size_hint_y=None, height=lo.dp(50)))
        self.add_widget(lo.Label(text='v1.7 -- Multiple wallet collections.', size_hint_y=None, height=lo.dp(50)))
        self.add_widget(lo.Label(text='v2 -- Multiple wallet synchronisation.', size_hint_y=None, height=lo.dp(50)))