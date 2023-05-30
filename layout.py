from kivy.app import App
from kivy.graphics import Color, Rectangle, Rotate
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
import csv
import json
import os
import global_var as gv
from calculations import InputRow
from global_var import NumberInput


class BaseWidget:
    def calculate_height(widget):
        spacing = 0
        if widget.spacing and type(widget.spacing) != list:
            spacing = widget.spacing
        return sum(w.height+spacing for w in widget.children)
    
    def create_json(widget, squads = gv.SQUADS):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(script_dir, "current_squads.json")
        with open(file_path, 'w') as squads_file:
            json.dump(squads, squads_file)
        with open(file_path) as squads_file:
            gv.SQUADS = json.load(squads_file)
        
        gv.SQUAD_1 = 0
        gv.SQUAD_2 = 0
        gv.SQUAD_3 = 0

        for skull in gv.SQUADS:
            if skull['squad'] == 1:
                gv.SQUAD_1 += 1
            elif skull['squad'] == 2:
                gv.SQUAD_2 += 1
            elif skull['squad'] == 3:
                gv.SQUAD_3 += 1
        
        if 6 - gv.SQUAD_1 > 0:
            gv.SQUAD1_NEXT = gv.SQUAD_COST[gv.SQUAD_1]
        else:
            gv.SQUAD1_NEXT = 'No slots left'
        if 6 - gv.SQUAD_2 > 0:
            gv.SQUAD2_NEXT = gv.SQUAD_COST[gv.SQUAD_2] + gv.SQUAD_COST[-1]*2
        else:
            gv.SQUAD2_NEXT = 'No slots left'
        if 6 - gv.SQUAD_3 > 0:
            gv.SQUAD3_NEXT = gv.SQUAD_COST[gv.SQUAD_3] + gv.SQUAD_COST[-1]*6
        else:
            gv.SQUAD3_NEXT = 'No slots left'

    def create_json_col(widget, col = gv.COLLECTION):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(script_dir, "current_squads.json")
        with open(file_path, 'w') as col_file:
            json.dump(col, col_file)
        with open(file_path) as collection_file:
            gv.COLLECTION = json.load(collection_file)


class CollectionItem(Label, BaseWidget):
    def __init__(self, col_id, **kwargs):
        super().__init__(**kwargs)
        # self.id = col_id
        self.size_hint_y = None
        self.height = gv.ITEM_HEIGHT


class ButtonWithID(Button, BaseWidget):
    def __init__(self, btn_id, **kwargs):
        super().__init__(**kwargs)
        # self.id = btn_id


class DropDownMenu(BoxLayout):
    def __init__(self, dd_id, skull, **kwargs):
        super().__init__(**kwargs)
        # self.id = dd_id
        self.squads = gv.SQUADS
        self.size_hint_y = None
        self.height = gv.ITEM_HEIGHT

        dropdown = DropDown()
        for option in ['Squad 1', 'Squad 2', 'Squad 3']:
            btn = Button(text=option, size_hint_y=None, height=dp(30), background_color=(0,0,0,0))
            btn.bind(on_press=lambda instance: setattr(self.main_button, 'text', instance.text))
            dropdown.add_widget(btn)

        with dropdown.canvas.before:
            Color(0, 0, 0, 1)
            self.dropdown_rect = Rectangle(pos=dropdown.pos, size=dropdown.size)

        dropdown.bind(pos=self.update_dropdown_rect, size=self.update_dropdown_rect)
        dropdown.bind(on_select=lambda instance, x: self.update_main_button(instance, x))
        dropdown.bind(on_touch_down=lambda instance, touch: dropdown.dismiss() if dropdown.collide_point(*touch.pos) else None)

        self.button_text = 'Select a squad...'
        for item in self.squads:
            if item['skullz'] == skull:
                self.button_text = f'Squad {item["squad"]}'

        self.main_button = ButtonWithID(btn_id='main_button', text=self.button_text, background_color=(0.3,0.5,1,1))
        self.main_button.bind(on_release=dropdown.open)

        self.add_widget(self.main_button)

        self.dropdown = dropdown

    def update_dropdown_rect(self, *args):
        self.dropdown_rect.pos = self.dropdown.pos
        self.dropdown_rect.size = self.dropdown.size

    def update_main_button(self, dropdown, value):
        self.main_button.text = value
        self.dropdown.select(value)
        self.dropdown.dismiss()
        

class CollectionGrid(GridLayout, BaseWidget):
    def __init__(self, grid_id, **kwargs):
        super().__init__(**kwargs)
        # self.id = id
        self.cols = 7
        self.spacing = gv.SPACING
        # self.padding = gv.PADDING
        self.size_hint_y = None
        self.squads = gv.SQUADS
        self.is_user_action = True

    def on_parent(self, instance, par):
        self.populate_grid(gv.COLLECTION)

    def update_scroll_view_height(self, instance, height):
        self.parent.height = height
    
    def populate_grid(self, grid=gv.COLLECTION):
        self.clear_widgets()
  
        for item in grid:
            self.add_widget(Image(source=os.path.join('img', item['image_loc']), size_hint_y= None, height=dp(50), size_hint_x=0.1))
            self.add_widget(CollectionItem(text=f"{item['Collection']} #{item['SkullzID']}", col_id=f"item_{item['Collection']}_{item['SkullzID']}", size_hint_x=0.25, text_size=(dp(500), dp(30)), halign='left', valign='center'))
            self.add_widget(Label(text=f"{item['Rarity']}", size_hint_x=0.15))
            self.add_widget(Button(text='+', size_hint_x=0.1, on_press=lambda instance: self.add_to_squad(instance, self.children.index(instance))))
            self.add_widget(Button(text='-', size_hint_x=0.1, on_press=lambda instance: self.remove_from_squad(instance, self.children.index(instance))))
            self.add_widget(DropDownMenu(size_hint_x=0.3, dd_id=f'dropdown_menu_{item["SkullzID"]}', skull=f"{item['Collection']}_{item['SkullzID']}"))
            self.add_widget(Button(text='Remove from collection', size_hint_x=0.1, on_press=lambda instance: self.remove_from_collection(instance, self.children.index(instance)), size_hint_y=None, height=dp(50)))
        
        self.height = sum(w.height + self.spacing[0] for w in self.children[::self.cols])
        self.bind(height=self.update_scroll_view_height)

    def remove_from_collection(self, instance, index):
        item_col = self.children[index+5].text.split(' ')[0]
        item_id = self.children[index+5].text.split(' ')[1][1:]
        self.new_collection = [skull for skull in gv.COLLECTION if not (skull['Collection'] == item_col and skull['SkullzID'] == item_id)]
        gv.COLLECTION = self.new_collection
        self.new_squads = [skull for skull in gv.SQUADS if not (skull['skullz'] == f"{item_col}_{item_id}")]
        button = self.parent.children[0].children[index+2]
        # button.parent.is_user_action = False
        button.dispatch('on_press')
        # button.parent.is_user_action = True

        self.create_json_col(self.new_collection)
        self.create_json(self.new_squads)
        self.parent.parent.children[2].populate_squads(gv.SQUADS)
        self.populate_grid(gv.COLLECTION)
        
    def add_to_squad(self, instance, index):
        item = f"{self.children[index+2].text.split(' ')[0]}_{self.children[index+2].text.split(' ')[1][1:]}"
        
        has_no_squad = True
        for skull in self.squads:
            if skull['skullz'] == item:
                has_no_squad = False
        
        dropdownmenu_selection = [child.main_button.text for child in self.children if type(child).__name__ == 'DropDownMenu' and self.children.index(child) == index-2][0]
        
        if dropdownmenu_selection != 'Select a squad...' and has_no_squad:
            self.show_popup(popup_type='add', index=index, item=item)
    
    def remove_from_squad(self, instance, index):
        item = f"{self.children[index+3].text.split(' ')[0]}_{self.children[index+3].text.split(' ')[1][1:]}"
        
        has_squad = False
        for skull in self.squads:
            if skull['skullz'] == item:
                has_squad = True

        dropdownmenu_selection = [child.main_button.text for child in self.children if type(child).__name__ == 'DropDownMenu' and self.children.index(child) == index-1][0]
        if dropdownmenu_selection != 'Select a squad...' and has_squad:
            self.show_popup(popup_type='remove', index=index, item=item)

    def show_popup(self, popup_type, index, item):
        if popup_type == 'add':
            offset_minus = 2
            adding = True
        else:
            offset_minus = 1
            adding = False
        offset_plus = self.cols-3-offset_minus
        for child in self.children:
            if type(child).__name__ == 'DropDownMenu' and self.children.index(child) == index-offset_minus:
                dropdown_menu = child
        dropdownmenu_selection = dropdown_menu.main_button.text
        new_squad = int(dropdownmenu_selection.split(' ')[1])
        skullz_name = self.children[index+offset_plus].text
        content = BoxLayout(orientation='vertical')

        skullz_with_squad = [skull['skullz'] for skull in self.squads]

        for child in self.parent.parent.children:
            if type(child).__name__ == 'SquadList':
                for grandchild in child.children:
                    if type(grandchild).__name__ != 'Button':
                        if grandchild.squad_num == new_squad:
                            target_squad = grandchild

        if popup_type == 'add' and target_squad.squad_empty > 0:
            content.add_widget(Label(text=f'You added {skullz_name} to {dropdownmenu_selection}'))
            if item in skullz_with_squad:
                for skull in self.squads:
                    if skull['skullz'] == item:
                        skull['squad'] = dropdownmenu_selection.split(' ')[1]
            else:
                self.squads.append({'skullz': item, 'squad': new_squad})
        elif popup_type == 'add' and target_squad.squad_empty <= 0:
            content.add_widget(Label(text=f'{dropdownmenu_selection} is full.'))
            dropdown_menu.main_button.text = 'Select a squad...'
        elif popup_type == 'remove':
            content.add_widget(Label(text=f'You removed {skullz_name} from {dropdownmenu_selection}'))
            dropdown_menu.main_button.text = 'Select a squad...'
            self.squads = [skull for skull in self.squads if skull['skullz'] != item]
        
        if int(dropdownmenu_selection.split(' ')[1]) == 1 and adding:
            gv.SQUAD_1 += 1
        elif int(dropdownmenu_selection.split(' ')[1]) == 1 and not adding:
            gv.SQUAD_1 -= 1
        elif int(dropdownmenu_selection.split(' ')[1]) == 2 and adding:
            gv.SQUAD_2 += 1
        elif int(dropdownmenu_selection.split(' ')[1]) == 2 and not adding:
            gv.SQUAD_2 -= 1
        elif int(dropdownmenu_selection.split(' ')[1]) == 3 and adding:
            gv.SQUAD_3 += 1
        elif int(dropdownmenu_selection.split(' ')[1]) == 3 and not adding:
            gv.SQUAD_3 -= 1

        gv.SQUADS = self.squads
        self.create_json(self.squads)
        self.parent.parent.children[-1].update_values()
        self.parent.parent.children[-1].calculate_total(self)
        target_squad.parent.populate_squads(self.squads)
        self.populate_grid(gv.COLLECTION)
        
        if self.is_user_action:
            button_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50), padding=dp(10))
            ok_button = Button(text='OK', size_hint=(None, None), size=(350, 50), background_color=(0,0,0,0))
            ok_button.bind(on_release=lambda instance: popup.dismiss())
            button_box.add_widget(ok_button)
            content.add_widget(button_box)

            popup = Popup(title='Selection', content=content, size_hint=(None, None), size=(400, 200))

            popup.open()


class CollectionScroll(ScrollView, BaseWidget):
    def __init__(self, scroll_id, **kwargs):
        super().__init__(**kwargs)
        # self.id = id
        self.bar_width = 10
        # self.size_hint_y = None
        # self.spacing = SPACING

    def on_parent(instance, self, par):
        collection_grid = CollectionGrid(grid_id='collection_grid')
        self.add_widget(collection_grid)


class Squad(BoxLayout, BaseWidget):
    def __init__(self, squad_id, **kwargs):
        super().__init__(**kwargs)
        # self.id = id
        self.squads = gv.SQUADS
        self.squad_id = squad_id
        self.orientation = 'vertical'
        self.squad_empty = 6
        self.squad_num = int(self.squad_id.split('_')[1])
        self.populate_squad(self.squads)

    def populate_squad(self, squads):
        self.clear_widgets()
        label = Label(text=f"{self.squad_id.split('_')[0].capitalize()} {self.squad_id.split('_')[1]}", size_hint_y=None, height=dp(50))
        self.add_widget(label)
        buttons = GridLayout(cols=3, spacing=gv.SPACING, padding=gv.PADDING)

        squad_count = 0
        self.squad_empty = 6
        for skull in squads:
            if skull['squad'] == int(self.squad_num):
                skullLayout = GridLayout(cols=1)
                for item in gv.COLLECTION:
                    if item['Collection'] == skull['skullz'].split('_')[0]:
                        if item['SkullzID'] == skull['skullz'].split('_')[1]:
                            nft_loc = item['image_loc']
                            if nft_loc == '':
                                nft_loc = 'dummy.jpeg'
                nft = Image(source=os.path.join('img', nft_loc), size_hint=(1, 1), allow_stretch=True)
                # nft.height = self.width / nft.image_ratio
                skullLayout.add_widget(nft)
                skullLayout.add_widget(Label(text=f"{skull['skullz'].split('_')[0]} #{skull['skullz'].split('_')[1]}", size_hint=(0.1, 0.2)))
                buttons.add_widget(skullLayout)
                self.squad_empty -= 1
                squad_count += 1
        while squad_count < 6:
            skullLayout = GridLayout(cols=1)
            nft = Image(source=os.path.join('img', 'dummy.jpeg'), size_hint=(1, 1), allow_stretch=True)
            # nft.height = self.width / nft.image_ratio
            skullLayout.add_widget(nft)
            skullLayout.add_widget(Label(text=f"Slot #{squad_count+1} Empty", size_hint=(0.1, 0.2)))
            buttons.add_widget(skullLayout)
            squad_count += 1

        self.add_widget(buttons)

        new_max = 0.3
        new_min = 0.2
        old_min = 0
        old_max = 1
        alpha = (new_max - new_min) * (int(self.squad_id.split('_')[1])%2 - old_min) / (old_max - old_min) + new_min
        self.change_bg_color(1, 1, 1, alpha)
    
    def change_bg_color(self, r, g, b, a):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(r, g, b, a) 
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size


class SquadList(BoxLayout, BaseWidget):
    def __init__(self, list_id, **kwargs):
        super().__init__(**kwargs)
        # self.id = id
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(300)
    
    def on_parent(self, instance, par):
        self.add_widget(Button(text='Max out\nall squads', size_hint_x=None, width=dp(80), on_press=self.max_out))
        self.add_widget(Squad(squad_id='squad_1'))
        self.add_widget(Squad(squad_id='squad_2'))
        self.add_widget(Squad(squad_id='squad_3'))
    
    def populate_squads(self, squads = gv.SQUADS):
        for child in self.children:
            if type(child).__name__ == 'Squad':
                child.populate_squad(squads)

    def max_out(self, instance):
        self.parent.children[1].children[2].dispatch('on_press')
        self.parent.children[1].children[2].dispatch('on_release')
        sort_func = lambda x: gv.RARITY_ORDER.index(x['Rarity'])

        sorted_col = sorted(gv.COLLECTION, key=sort_func, reverse=True)
        squad_list = []
        for i in range(18): 
            if i < 6:
                try:
                    skull_dict = {'skullz': f"{sorted_col[i]['Collection']}_{sorted_col[i]['SkullzID']}", 'squad': 1}
                    squad_list.append(skull_dict)
                except:
                    break
            elif i < 12 and i >= 6:
                try:
                    skull_dict = {'skullz': f"{sorted_col[i]['Collection']}_{sorted_col[i]['SkullzID']}", 'squad': 2}
                    squad_list.append(skull_dict)
                except:
                    break
            elif i < 18 and i >= 12:
                try:
                    skull_dict = {'skullz': f"{sorted_col[i]['Collection']}_{sorted_col[i]['SkullzID']}", 'squad': 3}
                    squad_list.append(skull_dict)
                except:
                    break

        self.create_json(squad_list)
        for child in self.children:
            if type(child).__name__ == 'Squad':
                child.populate_squad(squad_list)
        self.parent.children[0].children[0].populate_grid(gv.COLLECTION)
        self.parent.children[0].children[0].is_user_action = True


class TransparentButton(Button, BaseWidget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0, 0, 0, 0)
        self.size_hint_y = None
        self.height = dp(50)
        self.underline = True
        self.bind(on_press=lambda instance: setattr(self, 'color', (1,0,0,1)))
        self.bind(on_release=lambda instance: setattr(self, 'color', (1,1,1,1)))
        self.bind(on_release=self.change_text)
        self.needs_change = False
        self.does_exist = None
        if self.text not in ['Add All', 'Reset Squads']:
            self.needs_change = True
    
    def change_text(self, instance):
        if self.needs_change:
            splitted = self.text.split(' ')
            for child in self.parent.children:
                if type(child).__name__ == 'TransparentButton':
                    if child.text != self.text and child.needs_change:
                        try:
                            child_curr = child.text.split(' ')[1]
                            child.text = child.text.split(' ')[0]
                        except:
                            pass
            try:
                    curr_order = splitted[1]
                    self.does_exist = True
            except:
                self.does_exist = False
            
            if self.does_exist:
                if curr_order == '(a)':
                    self.text = splitted[0] + ' (d)'
                elif curr_order == '(d)':
                    self.text = splitted[0]
                    self.does_exist = False
            elif not self.does_exist:
                self.text = self.text + ' (a)'
                self.does_exist = True

class AddPopup(Popup, BaseWidget):
    def __init__(self):
        super().__init__()
        self.title = "Enter new Skull details"
        self.size_hint = (0.3, None)
        self.height = dp(450)

        self.new_dict = {}
        self._rarity = None

        main_box = BoxLayout(orientation='vertical')
        col_box = BoxLayout(size_hint_y=None, height=dp(30))
        col_label = Label(text='Collection:', halign='right', text_size=(gv.APP_WIDTH*0.050, None))
        self._col_input = TextInput(hint_text='Collection Name...', size_hint_x=None, width=dp(300))
        col_box.add_widget(col_label)
        col_box.add_widget(self._col_input)
        col_box.add_widget(Label())

        id_box = BoxLayout(size_hint_y=None, height=dp(30))
        id_label = Label(text='Skull ID:', halign='right', text_size=(gv.APP_WIDTH*0.050, None))
        self._id_input = NumberInput(type_val='int', hint_text='ID (only numbers)...', size_hint_x=None, width=dp(300))
        id_box.add_widget(id_label)
        id_box.add_widget(self._id_input)
        id_box.add_widget(Label())

        rarity_box = BoxLayout(size_hint_y=None, height=dp(30))
        rarity_label = Label(text='Rarity:', halign='right', text_size=(gv.APP_WIDTH*0.050, None))
        rarity_box.add_widget(rarity_label)

        button = Button(text='Select Rarity', size_hint=(None, None), size=(dp(300), dp(30)))
        button.bind(on_release=self.open_dropdown)
        
        dropdown = DropDown()
        dropdown.bind(on_select=self.dropdown_selected)
        dropdown.container.spacing = [0, 0]

        for i in ['Common', 'Rare', 'Epic', 'Legendary']:
            btn = Button(text=f'{i}', size_hint_y=None, height=dp(30))
            btn.bind(on_release=lambda btn: dropdown.select(btn.text))
            dropdown.add_widget(btn)
        with dropdown.canvas.before:
            Color(0, 0, 0, 1)
            self._dropdown_rect = Rectangle(pos=dropdown.pos, size=dropdown.size)
        dropdown.bind(pos=self.update_dropdown_rect, size=self.update_dropdown_rect)
        dropdown.bind(on_touch_down=lambda instance, touch: dropdown.dismiss() if dropdown.collide_point(*touch.pos) else None)

        rarity_box.add_widget(button)
        rarity_box.add_widget(dropdown)
        dropdown.dismiss()
        self._dropdown = dropdown
        self._button = button
        rarity_box.add_widget(Label())

        image_box = BoxLayout(size_hint_y=None, height=dp(30))
        image_label = Label(text='Image:', halign='right', text_size=(gv.APP_WIDTH*0.050, None))
        image_button = Button(text='Browse...', on_press=self.open_file, size_hint_x=None, width=dp(300))
        image_box.add_widget(image_label)
        image_box.add_widget(image_button)
        image_box.add_widget(Label())
        
        self._image_image_box = BoxLayout(size_hint_y=None, height=dp(200))
        self._img_name = 'dummy.jpeg'
        self._img_source = os.path.join('img', self._img_name)
        self._image_image = Image(source=self._img_source, size_hint_x=None, width=dp(300), allow_stretch=True)
        self._image_image_box.add_widget(Label(text='Current Image:', halign='right', text_size=(gv.APP_WIDTH*0.050, None)))
        self._image_image_box.add_widget(self._image_image)
        self._image_image_box.add_widget(Label())

        entry_box = BoxLayout(orientation='vertical')
        entry_box.add_widget(col_box)
        main_box.add_widget(Label(size_hint_y=None, height=dp(10)))
        entry_box.add_widget(id_box)
        main_box.add_widget(Label(size_hint_y=None, height=dp(10)))
        entry_box.add_widget(rarity_box)
        main_box.add_widget(Label(size_hint_y=None, height=dp(10)))
        entry_box.add_widget(image_box)
        main_box.add_widget(Label(size_hint_y=None, height=dp(10)))
        entry_box.add_widget(self._image_image_box)

        button_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        ok_button = Button(text='Add', on_press=self.on_submit)
        cancel_button = Button(text='Cancel', height=dp(50), on_press=self.dismiss)
        button_box.add_widget(ok_button)
        button_box.add_widget(cancel_button)

        main_box.add_widget(entry_box)
        main_box.add_widget(Label(size_hint_y=None, height=dp(10)))
        main_box.add_widget(button_box)

        self.content = main_box
    
    def update_dropdown_rect(self, *args):
        self._dropdown_rect.pos = self._dropdown.pos
        self._dropdown_rect.size = self._dropdown.size

    def open_dropdown(self, button):
        self._dropdown.open(button)
    
    def dropdown_selected(self, dropdown, text):
        self._rarity = text
        self._button.text = text

    def on_submit(self, button):
        if self._col_input.text == "":
            self._col_input.hint_text = 'Collection cannot be empty.'
        elif self._id_input.text == "":
            self._id_input.hint_text = 'ID cannot be empty.'
        elif not self._rarity:
            self._button.text = 'You need to select Rarity'
        else:
            col = self._col_input.text
            skull_id = self._id_input.text
            rarity = self._rarity
            img_loc = self._img_name
            self.new_dict = {'Collection': col, 'SkullzID': skull_id, 'Rarity': rarity, 'image_loc': img_loc}
            self.dismiss()

    def open_file(self, button):
        file_selector = gv.FileSelectorPopup(filter='img', on_selection=self.handle_popup_dismiss)
        file_selector.bind(on_dismiss=self.handle_popup_dismiss)
        file_selector.open()
    
    def handle_popup_dismiss(self, instance):        
        if instance.selected_file:
            self._img_source = instance.selected_file
            self._image_image_box.remove_widget(self._image_image)
            self._image_image_box.add_widget(Image(source=self._img_source, size_hint_x=None, width=dp(300), allow_stretch=True))
            self._img_name = os.path.basename(instance.selected_file)


class LabelRow(BoxLayout, BaseWidget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(50)
        
        self.add_widget(Label(text='', size_hint=(0.1, None), height=dp(50)))
        self.add_widget(TransparentButton(text='Skullz', size_hint=(0.25, None), height=dp(50), text_size=(dp(500), dp(30)), halign='left', valign='center', on_release=self.grid_sort))
        self.add_widget(TransparentButton(text='Rarity', size_hint=(0.15, None), height=dp(50), text_size=(dp(100), dp(30)), halign='center', valign='center', on_release=self.grid_sort))
        self.add_widget(TransparentButton(text='Add All', size_hint_x=0.1, on_press=self.add_all))
        self.add_widget(TransparentButton(text='Reset Squads',  size_hint_x=0.1, on_press=self.reset_squads))
        self.add_widget(Label(text='Squad selection', size_hint=(0.3, None), height=dp(50)))
        self.add_widget(Button(text='Add to collection', size_hint=(0.1, None), height=dp(50), on_press=self.add_to_collection))
    
    def grid_sort(self, instance):
        splitted = instance.text.split(' ')
        try:
            curr_order = splitted[1]
        except:
            curr_order = 'none'
        
        grid = self.parent.children[0].children[0]
        if splitted[0] == 'Skullz':
            sort_func = lambda x: (x['Collection'], x['SkullzID'])
        else:
            sort_func = lambda x: gv.RARITY_ORDER.index(x['Rarity'])

        if curr_order == 'none':
            grid.populate_grid(gv.COLLECTION)
        elif curr_order == '(a)':
            grid.populate_grid(sorted(gv.COLLECTION, key=sort_func, reverse=False))
        elif curr_order == '(d)':
            grid.populate_grid(sorted(gv.COLLECTION, key=sort_func, reverse=True))

    def add_to_collection(self, instance):
        popup = AddPopup()
        popup.bind(on_dismiss=self.handle_popup)
        popup.open()
    
    def handle_popup(self, instance):
        print(instance.new_dict)
        gv.COLLECTION.append(instance.new_dict)
        self.parent.children[0].children[0].populate_grid(gv.COLLECTION)
        self.create_json_col()
    
    def reset_squads(self, instance):
        grid = self.parent.children[0].children[0]
        squad_list = []
        for child in self.parent.children[2].children:
            if type(child).__name__ == 'Squad':
                child.populate_squad(squad_list)
        
        self.create_json(squad_list)
        grid.populate_grid(gv.COLLECTION)
    
    def add_all(self, instance):
        grid = self.parent.children[0].children[0]
        for child in grid.children:
            if type(child).__name__ == 'Button' and child.text == '+':
                child.parent.is_user_action = False
                child.dispatch('on_press')
                child.parent.is_user_action = True


class MainContent(BoxLayout, BaseWidget):
    def __init__(self, main_id, **kwargs):
        super().__init__(**kwargs)
        # self.id = id
        self.orientation = 'vertical'
    
    def on_parent(self, instance, par):
        self.add_widget(InputRow())
        self.add_widget(SquadList(list_id='squad_list'))
        self.add_widget(LabelRow())
        self.add_widget(CollectionScroll(scroll_id='collection_scroll'))
        # self.height = self.calculate_height()


class Layout(BoxLayout, BaseWidget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'

    def on_parent(self, instance, par):
        self.add_widget(MainContent(main_id='main_content'))
        # self.height = self.calculate_height()
        