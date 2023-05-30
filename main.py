from kivy.config import Config
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

from datetime import date, datetime
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.clock import Clock
from layout import Layout
from roadmap import Roadmap, About
import layout as lo
import global_var as gv
import csv
import json
import os


class NewFilePopup(lo.Popup):
    def __init__(self, on_confirm, on_cancel):
        super().__init__()
        self.title = "Enter CSV File Name"
        self.size_hint = (0.7, 0.5)

        self.file_name = None

        list_view = lo.FileChooserListView(multiselect=False, filters=['*.csv'])
        self.text_input = lo.TextInput(multiline=False, on_text_validate=self.handle_validate)

        confirm_button = lo.Button(text='Confirm')
        confirm_button.bind(on_release=lambda button: self.handle_confirm(on_confirm))
        cancel_button = lo.Button(text='Cancel')
        cancel_button.bind(on_release=lambda button: self.handle_cancel(on_cancel))

        total_layout = lo.BoxLayout(orientation='vertical')
        layout = lo.BoxLayout(orientation='horizontal', size_hint=(1, None), height=lo.dp(30))
        layout.add_widget(lo.Label(text='Enter a new file name:'))
        layout.add_widget(self.text_input)
        total_layout.add_widget(list_view)
        total_layout.add_widget(layout)
        button_box=lo.BoxLayout(size_hint=(1, None), height=lo.dp(50))
        button_box.add_widget(confirm_button)
        button_box.add_widget(cancel_button)
        total_layout.add_widget(button_box)
        
        self.content = total_layout

    def get_current_folder(self, file_chooser):
        current_folder = file_chooser.path
        print("Current Folder:", current_folder)

    def handle_confirm(self, on_confirm):
        new_file_name = self.text_input.text
        on_confirm(new_file_name)
        self.file_name = os.path.join(self.content.children[-1].path, new_file_name+'.csv')
        self.dismiss()

    def handle_cancel(self, on_cancel):
        on_cancel()
        self.dismiss()
    
    def handle_validate(self, instance):
        self.file_name = os.path.join(self.content.children[-1].path, instance.text+'.csv')
        self.dismiss()

class TopBar(lo.BoxLayout, lo.BaseWidget):
    def __init__(self, top_id, **kwargs):
        super().__init__(**kwargs)
        # self.id = id
        self.size_hint_y = None
        self.pos_hint={'center_x': 0.5, 'top': 1}
        self.height = lo.dp(50)
        self.dragging = False
        self.drag_pos = None

    def on_parent(self, instance, par):
        label = lo.Label(text=f'Skullz working their asses off for Eren the Measly v{gv.VER_INFO}', halign='left', text_size=(gv.APP_WIDTH*0.48, None))
        self.add_widget(label)
        self.add_widget(lo.Label(text='Today: ' + str(gv.TODAY.strftime("%d.%m.%Y")), size_hint_x=0.2))
        self._update_label = lo.Label(text='Last Updated: ', size_hint_x=0.2)
        self.add_widget(self._update_label)
        self.add_widget(lo.Button(text='Import Collection (.CSV)', size_hint_x=0.3, on_press=self.open_file))
        self.add_widget(lo.Button(text='Export Collection (.CSV)', size_hint_x=0.3, on_press=self.export_file))

        script_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(script_dir, "current_values.json")
        with open(file_path) as file:
            values = json.load(file)
        gv.AVAX = float(values['AVAX'])
        gv.DAYS = int(values['DAYS'])
        gv.FLSH = float(values['FLSH'])
        gv.RFLSH = float(values['RFLSH'])
        gv.WD_COST = float(values['WD_COST'])
        gv.DATE_UPDATED = datetime.strptime(values['DATE_UPDATED'], "%Y-%m-%d %H:%M:%S.%f").date()
        self.update_update_date()

    def update_update_date(self):
        self._update_label.text = f'Last Updated: {gv.DATE_UPDATED.strftime("%d.%m.%Y")}'

    def open_file(self, button):
        file_selector = gv.FileSelectorPopup(filter='csv', on_selection=self.handle_popup_dismiss)
        file_selector.bind(on_dismiss=self.handle_popup_dismiss)
        file_selector.open()

    def handle_popup_dismiss(self, instance):        
        if instance.selected_file:
            with open(instance.selected_file, encoding='utf-8') as csv_file:
                csv_content = csv_file.read()
                csv_delimiter = csv.Sniffer().sniff(csv_content).delimiter
                csv_file.seek(0)                
                csv_reader = csv.reader(csv_file, delimiter=csv_delimiter)
                
                file_header = next(csv_reader)
                correct_header = ['Collection', 'SkullzID', 'Rarity', 'image_loc']
                
                if file_header != correct_header:
                    error_popup = lo.Popup()
                    error_popup.title = "CSV Header Error"
                    error_popup.size_hint = (0.5, 0.2)
                    
                    error_message = lo.Label(text=f'The selected CSV file needs to have {correct_header} as its starting row!')
                    error_button = lo.Button(text='OK', on_press=lambda instance: error_popup.dismiss())
                    error_box = lo.BoxLayout(orientation='vertical')
                    error_box.add_widget(error_message)
                    error_box.add_widget(error_button)

                    error_popup.content = error_box
                    error_popup.open()
                gv.COLLECTION = []
        
                for row in csv_reader:
                    gv.COLLECTION.append({'Collection': row[0], 'SkullzID': row[1], 'Rarity': row[2], 'image_loc': row[3]})
            script_dir = os.path.dirname(os.path.abspath(__file__))
            file_path = os.path.join(script_dir, "current_collection.json")
            with open(file_path, 'w') as file:
                json.dump(gv.COLLECTION, file)
            squads = []
            self.create_json(squads)
            self.parent.children[0].children[1].children[0].children[0].children[2].populate_squads(squads)
            self.parent.children[0].children[1].children[0].children[0].children[0].children[0].populate_grid(gv.COLLECTION)

    def export_file(self, button):
        def on_confirm(new_file_name):
            print("New file name:", new_file_name)

        def on_cancel():
            print("New file creation canceled")

        popup = NewFilePopup(on_confirm=on_confirm, on_cancel=on_cancel)
        popup.bind(on_dismiss=self.handle_export)
        popup.open()

    def handle_export(self, instance):

        field_names = gv.COLLECTION[0].keys()

        with open(instance.file_name, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=field_names)

            writer.writeheader()
            writer.writerows(gv.COLLECTION)


class Tabs(TabbedPanel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.id = 'tabs'
        self.do_default_tab = False
        self.tab_pos = 'bottom_left'

        self._tab1 = Layout()
        self._tab1_item = TabbedPanelItem(text='Collection')
        self._tab1_item.add_widget(self._tab1)
        self._tab2_item = TabbedPanelItem(text='My Wallets')

        self._tab3 = Roadmap()
        self._tab3_item = TabbedPanelItem(text='Roadmap')
        self._tab3_item.add_widget(self._tab3)

        self._tab4 = About()
        self._tab4_item = TabbedPanelItem(text='About')
        self._tab4_item.add_widget(self._tab4)

        Clock.schedule_once(self.switch_tab)

        self.bind(current_tab=self.on_tab_click)

    def on_parent(self, instance, par):
        self.add_widget(self._tab1_item)
        self.add_widget(self._tab2_item)
        self.add_widget(self._tab3_item)
        self.add_widget(self._tab4_item)

        self._tab2_item.disabled = True
        self._tab3_item.disabled = False
        self._tab4_item.disabled = False
        
    def switch_tab(self, dt):
        self.switch_to(self.tab_list[3])

    def on_tab_click(self, instance, value):
        # if value == self._tab1_item:
        self.regenerate_tab1_content()

    def regenerate_tab1_content(self):
        self._tab1_item.content.clear_widgets()
        # self._tab2_item.content.clear_widgets()
        self._tab3_item.content.clear_widgets()
        self._tab4_item.content.clear_widgets()
        

class MainTabLayout(lo.BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'

    def on_parent(self, instance, par):
        self.add_widget(TopBar(top_id='top_bar'))
        self.add_widget(Tabs())


class ErenSkullz(App):
    def build(self):
        Window.size = (gv.APP_WIDTH, gv.APP_HEIGHT)
        Window.borderless = False
        Window.left = (Window.width - Window.size[0]) / 2 + lo.dp(50)
        Window.top = (Window.height - Window.size[1]) / 2 + lo.dp(50)

        layout = MainTabLayout()

        return layout


if __name__ == '__main__':
    app = ErenSkullz()
    app.run()
