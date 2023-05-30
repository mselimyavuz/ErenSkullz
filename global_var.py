import json
import os
from datetime import date, datetime
from kivy.metrics import dp
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.textinput import TextInput

VER_INFO = "1.0"
TODAY = datetime.today()
DATE_UPDATED = 0

APP_WIDTH = dp(1920)
APP_HEIGHT = dp(1000)
ITEM_HEIGHT = dp(50)
SPACING = dp(1)
PADDING = dp(1)
GAIN = {'Legendary': 80, 'Epic': 40, 'Rare': 20, 'Common': 10}
SQUAD_COST = [0, 333, 666, 1333, 2666, 5222]
RARITY_ORDER = ['Common', 'Rare', 'Epic', 'Legendary']

AVAX = 0
DAYS = 0
FLSH = 0
RFLSH = 0
WD_COST = 0
CURR_FLSH = 0
CURR_RFLSH = 0

SQUAD_1 = 0
SQUAD_2 = 0
SQUAD_3 = 0

script_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_dir, "current_squads.json")

with open(file_path) as squads_file:
    SQUADS = json.load(squads_file)

for skull in SQUADS:
    if skull['squad'] == 1:
        SQUAD_1 += 1
    elif skull['squad'] == 2:
        SQUAD_2 += 1
    elif skull['squad'] == 3:
        SQUAD_3 += 1

file_path = os.path.join(script_dir, "current_collection.json")

with open(file_path) as collection_file:
    COLLECTION = json.load(collection_file)

if 6 - SQUAD_1 > 0:
    SQUAD1_NEXT = SQUAD_COST[SQUAD_1]
else:
    SQUAD1_NEXT = 'No slots left'
if 6 - SQUAD_2 > 0:
    SQUAD2_NEXT = SQUAD_COST[SQUAD_2] + SQUAD_COST[-1]*2
else:
    SQUAD2_NEXT = 'No slots left'
if 6 - SQUAD_3 > 0:
    SQUAD3_NEXT = SQUAD_COST[SQUAD_3] + SQUAD_COST[-1]*6
else:
    SQUAD3_NEXT = 'No slots left'


class NumberInput(TextInput):
    def __init__(self, type_val, **kwargs):
        super().__init__(**kwargs)
        self.type_val = type_val

    def insert_text(self, substring, from_undo=False):
        if self.type_val == 'int':
            allowed_chars = '0123456789'
        else:
            allowed_chars = '0123456789.'
        filtered_substring = ''.join([char for char in substring if char in allowed_chars])
        return super().insert_text(filtered_substring, from_undo=from_undo)

    def on_text_validate(self):
        if self.type_val == 'float':
            try:
                float(self.text)
            except ValueError:
                self.text = ""
                self.hint_text = "You entered an invalid value."
        print(self.text)
    
    def text_validate(self, instance):
        self.on_text_validate()


class FileSelectorPopup(Popup):
    def __init__(self, filter, on_selection):
        super().__init__()
        self.title = "Select your collections CSV file"
        self.size_hint = (0.7, 0.5)

        self.selected_file = None
        
        if filter == 'csv':
            filters = ['*.csv']
        elif filter == 'img':
            filters = ['*.jpg', '*.jpeg', '*.png']
        
        main_box = BoxLayout(orientation='vertical')
        list_view = FileChooserListView(on_selection=on_selection, multiselect=False, filters=filters)
        list_view.bind(on_submit=self.handle_double_click)
        button_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        ok_button = Button(text='Select', on_press=self.handle_selection)
        cancel_button = Button(text='Cancel', height=dp(50), on_press=self.dismiss_popup)
        button_box.add_widget(ok_button)
        button_box.add_widget(cancel_button)

        main_box.add_widget(list_view)
        main_box.add_widget(button_box)

        self.content = main_box

    def dismiss_popup(self, instance):
        self.dismiss()
    
    def handle_selection(self, button):
        self.selected_file = self.content.children[1].selection[0]
        self.dismiss_popup(self)
    
    def handle_double_click(self, instance, selection, touch):
        if selection:
            self.selected_file = selection[0]
            self.dismiss_popup(instance)