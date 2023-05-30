from datetime import date, timedelta, datetime
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
import json
import global_var as gv
import os
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

    def create_json_col(widget, col = gv.COLLECTION):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(script_dir, "current_collection.json")
        with open(file_path, 'w') as col_file:
            json.dump(col, col_file)
        with open(file_path) as collection_file:
            gv.COLLECTION = json.load(collection_file)


class InputRow(BoxLayout, BaseWidget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.spacing = gv.SPACING
        self.padding = gv.PADDING
        self.is_validating = False
        self.total = 0
        
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
        
        self._curr_values = Label(text=self.update_string('init'))

    def update_string(self, status):
        if status == 'init':
            date_update = str(datetime.combine(gv.DATE_UPDATED, datetime.min.time()))+'.00'
        else:
            date_update = str(gv.TODAY)

        values = {'AVAX': gv.AVAX, 'DAYS': gv.DAYS, 'FLSH': gv.FLSH, 'RFLSH': gv.RFLSH, 'WD_COST': gv.WD_COST, 'DATE_UPDATED': date_update}

        script_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(script_dir, "current_values.json")
        with open(file_path, 'w') as file:
            json.dump(values, file)

        updated_string = f'Last Updated --     AVAX: {float(gv.AVAX):0>6,.2f}     Days: {int(gv.DAYS):0>2}     FLSH: {float(gv.FLSH):0>11,.2f}     rFLSH: {float(gv.RFLSH):0>11,.2f}     Claim Cost: {float(gv.WD_COST):,.5f} AVAX          Total Squad Cost: {self.total} rFLSH'
        if len(updated_string) > 165:
            updated_string = f'Last Updated --     AVAX: {float(gv.AVAX):0>6,.2f}     Days: {int(gv.DAYS):0>2}     FLSH: {float(gv.FLSH):0>11,.2f}     rFLSH: {float(gv.RFLSH):0>11,.2f}     Claim Cost: {float(gv.WD_COST):,.5f} AVAX     Total Squad Cost: {self.total} rFLSH'
        return updated_string

    def calculate_total(self, button):
        self.total = 0
        for i in range(gv.SQUAD_1):
            self.total += gv.SQUAD_COST[i]
        for i in range(gv.SQUAD_2):
            self.total += gv.SQUAD_COST[i] + gv.SQUAD_COST[-1]*2
        for i in range(gv.SQUAD_3):
            self.total += gv.SQUAD_COST[i] + gv.SQUAD_COST[-1]*6
        
        self._curr_values.text = self.update_string('init')

    def on_parent(self, instance, par):
        box_inside_1 = BoxLayout(orientation='horizontal', size_hint_y = None, height=dp(50))
        avax_label = Label(text='AVAX to Spend: ', size_hint_y=None, height=dp(50), halign='right', valign='middle', text_size=(dp(gv.APP_WIDTH/11), None), size_hint_x=None, width=dp(gv.APP_WIDTH/11))
        avax_input = NumberInput(type_val='float', hint_text='AVAX to spend...', multiline=False, padding = [dp(5), dp(16), dp(5), dp(15)], size_hint_x=None, width=dp(250), on_text_validate=lambda instance: self.input_validate(instance.text, 'avax'))
        box_inside_1.add_widget(avax_label)
        box_inside_1.add_widget(avax_input)

        flsh_label = Label(text='FLSH: ', size_hint_y=None, height=dp(50), halign='right', valign='middle', text_size=(dp(gv.APP_WIDTH/20), None), size_hint_x=None, width=dp(gv.APP_WIDTH/20))
        box_inside_1.add_widget(flsh_label)
        flsh_input = NumberInput(type_val='float', hint_text='FLSH...', multiline=False, padding = [dp(5), dp(16), dp(5), dp(15)], size_hint_x=None, width=dp(250), on_text_validate=lambda instance: self.input_validate(instance.text, 'flsh'))
        box_inside_1.add_widget(flsh_input)

        box_inside_1.add_widget(self._curr_values)
        # box_inside_1.add_widget(Button(text='Refresh', size_hint_x=None, width=dp(70), on_press=self.calculate_total))

        box_inside_2 = BoxLayout(orientation='horizontal', size_hint_y = None, height=dp(50))
        freq_label = Label(text='Claim Frequency: (days) ', size_hint_y=None, height=dp(50), halign='right', valign='middle', text_size=(dp(gv.APP_WIDTH/11), None), size_hint_x=None, width=dp(gv.APP_WIDTH/11))
        freq_input = NumberInput(type_val='int', hint_text='Claim Frequency in days...', multiline=False, padding = [dp(5), dp(16), dp(5), dp(15)], size_hint_x=None, width=dp(250), on_text_validate=lambda instance: self.input_validate(instance.text, 'days'))
        box_inside_2.add_widget(freq_label)
        box_inside_2.add_widget(freq_input)

        rflsh_label = Label(text='rFLSH: ', size_hint_y=None, height=dp(50), halign='right', valign='middle', text_size=(dp(gv.APP_WIDTH/20), None), size_hint_x=None, width=dp(gv.APP_WIDTH/20))
        box_inside_2.add_widget(rflsh_label)
        rflsh_input = NumberInput(type_val='float', hint_text='rFLSH...', multiline=False, padding = [dp(5), dp(16), dp(5), dp(15)], size_hint_x=None, width=dp(250), on_text_validate=lambda instance: self.input_validate(instance.text, 'rflsh'))
        box_inside_2.add_widget(rflsh_input)

        self._sq1_total_gain = 0
        self._sq2_total_gain = 0
        self._sq3_total_gain = 0

        self._sq1_claim_gain = 0
        self._sq2_claim_gain = 0
        self._sq3_claim_gain = 0

        self._sq1 = 0
        self._sq2 = 0
        self._sq3 = 0

        self.calculate_squad_costs()

        prediction_1a = f'[i]Gain in {gv.DAYS} day(s) (FLSH)[/i] -- Squad 1: {self._sq1_claim_gain} Squad 2: {self._sq2_claim_gain} Squad 3: {self._sq3_claim_gain} Total: {self._sq1_claim_gain+self._sq2_claim_gain+self._sq3_claim_gain-gv.WD_COST}'
        prediction_1b = f'[i]Date of next slot[/i] -- Squad 1: {self._sq1}  Squad 2: {self._sq2}  Squad 3: {self._sq3}'

        box_inner_2 = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(50), size_hint_x=None, width=dp(gv.APP_WIDTH/2))
        box_inner_2_inner_1 = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(25), size_hint_x=None, width=dp(gv.APP_WIDTH/4))
        self._prediction_1a_label = Label(text=prediction_1a, size_hint_y=None, height=dp(25), halign='left', valign='middle', text_size=(dp(gv.APP_WIDTH/2.8)-gv.SPACING*85, None), size_hint_x=None, width=dp(gv.APP_WIDTH/2.8), markup=True)
        self._prediction_1b_label = Label(text=prediction_1b, size_hint_y=None, height=dp(25), halign='left', valign='middle', text_size=(dp(gv.APP_WIDTH/2.8)-gv.SPACING*85, None), size_hint_x=None, width=dp(gv.APP_WIDTH/2.8), markup=True)
        box_inner_2_inner_1.add_widget(self._prediction_1a_label)
        
        prediction_2a = f'rFLSH converting on {(gv.TODAY+timedelta(days=1)).strftime("%d.%m.%Y")}: {float(gv.FLSH)*0.01} rFLSH'
        prediction_2b = f'Current FLSH: {gv.CURR_FLSH}               Current rFLSH: {gv.CURR_RFLSH}'

        box_inner_2_inner_2 = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(25), size_hint_x=None, width=dp(gv.APP_WIDTH/4))
        box_inner_2_inner_2.add_widget(self._prediction_1b_label)
        self._prediction2a_label = Label(text=prediction_2a, size_hint_y=None, height=dp(25), halign='left', valign='middle', text_size=(dp(gv.APP_WIDTH/3)-gv.SPACING*85, None), size_hint_x=None, width=dp(gv.APP_WIDTH/3), markup=True)
        self._prediction2b_label = Label(text=prediction_2b, size_hint_y=None, height=dp(25), halign='left', valign='middle', text_size=(dp(gv.APP_WIDTH/3)-gv.SPACING*85, None), size_hint_x=None, width=dp(gv.APP_WIDTH/3), markup=True)
        box_inner_2_inner_1.add_widget(self._prediction2a_label)
        box_inner_2_inner_2.add_widget(self._prediction2b_label)

        box_inner_2.add_widget(box_inner_2_inner_1)
        box_inner_2.add_widget(box_inner_2_inner_2)
        box_inside_2.add_widget(box_inner_2)

        box_inside_3 = BoxLayout(orientation='horizontal', size_hint_y = None, height=dp(50))
        cost_label = Label(text='Claim Cost (AVAX): ', size_hint_y=None, height=dp(50), halign='right', valign='middle', text_size=(dp(gv.APP_WIDTH/11), None), size_hint_x=None, width=dp(gv.APP_WIDTH/11))
        cost_input = NumberInput(type_val='float', hint_text='Claim Cost in AVAX...', multiline=False, padding = [dp(5), dp(16), dp(5), dp(15)], size_hint_x=None, width=dp(250), on_text_validate=lambda instance: self.input_validate(instance.text, 'cost'))

        box_inside_3.add_widget(cost_label)
        box_inside_3.add_widget(cost_input)
        
        prediction_3 = ''
        prediction_4 = ''

        box_inner_2 = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(50), size_hint_x=None, width=dp(gv.APP_WIDTH/4))
        box_inner_2.add_widget(Label(text=prediction_3, size_hint_y=None, height=dp(25), halign='left', valign='middle', text_size=(dp(gv.APP_WIDTH/1.65)-gv.SPACING*10, None), size_hint_x=None, width=dp(gv.APP_WIDTH/1.65), markup=True))
        box_inner_2.add_widget(Label(text=prediction_4, size_hint_y=None, height=dp(25), halign='left', valign='middle', text_size=(dp(gv.APP_WIDTH/1.65)-gv.SPACING*10, None), size_hint_x=None, width=dp(gv.APP_WIDTH/1.65), markup=True))

        box_inner_3 = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(50), size_hint_x=None, width=dp(gv.APP_WIDTH/5))
        box_inner_inner_1 = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(25), size_hint_x=None, width=dp(gv.APP_WIDTH/10))
        box_inner_inner_2 = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(25), size_hint_x=None, width=dp(gv.APP_WIDTH/10))
        box_inner_inner_1.add_widget(Label(text='[i]Next Slot Costs (rFLSH)[/i]', markup=True, size_hint_y=None, height=dp(25), halign='center', valign='middle', text_size=(dp(gv.APP_WIDTH/10), None), size_hint_x=None, width=dp(gv.APP_WIDTH/10)))
        self._sq1_next = Label(text=f'Squad 1: {gv.SQUAD1_NEXT}', size_hint_y=None, height=dp(25), halign='center', valign='middle', text_size=(dp(gv.APP_WIDTH/10), None), size_hint_x=None, width=dp(gv.APP_WIDTH/10))
        box_inner_inner_1.add_widget(self._sq1_next)
        box_inner_3.add_widget(box_inner_inner_1)
        self._sq2_next = Label(text=f'Squad 2: {gv.SQUAD2_NEXT}', size_hint_y=None, height=dp(25), halign='center', valign='middle', text_size=(dp(gv.APP_WIDTH/10), None), size_hint_x=None, width=dp(gv.APP_WIDTH/10))
        self._sq3_next = Label(text=f'Squad 3: {gv.SQUAD3_NEXT}', size_hint_y=None, height=dp(25), halign='center', valign='middle', text_size=(dp(gv.APP_WIDTH/10), None), size_hint_x=None, width=dp(gv.APP_WIDTH/10))
        box_inner_inner_2.add_widget(self._sq2_next)
        box_inner_inner_2.add_widget(self._sq3_next)
        box_inner_3.add_widget(box_inner_inner_2)
        box_inside_3.add_widget(box_inner_3)
        box_inside_3.add_widget(box_inner_2)

        self.add_widget(box_inside_1)
        self.add_widget(box_inside_2)
        self.add_widget(box_inside_3)
        self.calculate_total(self)
        self.height = sum(w.height+gv.SPACING for w in self.children)

    def update_values(self):
        self._sq1_next.text = f'Squad 1: {gv.SQUAD1_NEXT}'
        self._sq2_next.text = f'Squad 2: {gv.SQUAD2_NEXT}'
        self._sq3_next.text = f'Squad 3: {gv.SQUAD3_NEXT}'
        self.calculate_squad_costs()
        self._prediction_1a_label.text = f'[i]Gain in {gv.DAYS} day(s) (FLSH)[/i] -- Squad 1: {self._sq1_claim_gain} Squad 2: {self._sq2_claim_gain} Squad 3: {self._sq3_claim_gain} Total: {self._sq1_claim_gain+self._sq2_claim_gain+self._sq3_claim_gain-gv.WD_COST}'
        self._prediction_1b_label.text = f'[i]Date of next slot[/i] -- Squad 1: {self._sq1}  Squad 2: {self._sq2}  Squad 3: {self._sq3}'

    def calculate_squad_costs(self):
        self._sq1_total_gain = 0
        self._sq2_total_gain = 0
        self._sq3_total_gain = 0

        for skull in gv.SQUADS:
            col = skull['skullz'].split('_')[0]
            id = skull['skullz'].split('_')[1]
            for nft in gv.COLLECTION:
                if nft['Collection'] == col and nft['SkullzID'] == id:
                    if skull['squad'] == 1:
                        self._sq1_total_gain += gv.GAIN[nft['Rarity']]
                    if skull['squad'] == 2:
                        self._sq2_total_gain += gv.GAIN[nft['Rarity']]
                    if skull['squad'] == 3:
                        self._sq3_total_gain += gv.GAIN[nft['Rarity']]
                    break
        self._total_gain = self._sq1_total_gain + self._sq2_total_gain + self._sq3_total_gain

        gv.CURR_FLSH = gv.FLSH
        gv.CURR_RFLSH = gv.RFLSH
        
        if type(gv.DATE_UPDATED) == datetime:
            cmp = gv.TODAY.date() > gv.DATE_UPDATED.date()
        else:
            cmp = gv.TODAY.date() > gv.DATE_UPDATED

        if cmp:
            dates = (gv.TODAY.date() - gv.DATE_UPDATED.date()).days
            
            while dates > 0:
                gv.CURR_RFLSH = gv.CURR_RFLSH + gv.FLSH*0.01
                dates -= 1
            
            gv.CURR_FLSH = gv.FLSH - (gv.CURR_RFLSH-gv.RFLSH)

        self._days_needed_1 = 0
        self._days_needed_2 = 0
        self._days_needed_3 = 0

        if gv.SQUAD1_NEXT != 'No slots left':
            if gv.CURR_RFLSH > float(gv.SQUAD1_NEXT):
                self._sq1_claims = 'Ready'
            else:
                rflsh_needed = gv.SQUAD1_NEXT - gv.CURR_RFLSH
                if rflsh_needed * 100 < gv.CURR_FLSH:
                    self._days_needed_1 = (int((gv.CURR_FLSH/rflsh_needed)/0.01)/gv.DAYS)
                    self._sq1_claims = 0
                else:
                    i = gv.DAYS
                    one_claim_flsh = gv.CURR_FLSH
                    while i > 0:
                        multiplier = 1 + 0.01*i
                        if multiplier > 2.0:
                            multiplier = 2.0
                        one_claim_flsh += self._total_gain * multiplier
                        i -= 1
                    one_claim_flsh -= gv.WD_COST

                    after_one_claim_rflsh = one_claim_flsh*0.01+gv.CURR_RFLSH
                    claim = 1
                    self._days_needed_1 += 1
                    while after_one_claim_rflsh < rflsh_needed:
                        after_one_claim_rflsh += one_claim_flsh*0.01
                        self._days_needed_1 += 1
                        claim += 1
                    self._sq1_claims = claim
        else: 
            self._sq1_claims = 'All slots open'
        
        if type(self._sq1_claims) == int:
            self._sq1 = (gv.TODAY.date()+timedelta(days=(self._sq1_claims*gv.DAYS+self._days_needed_1))).strftime("%d.%m.%Y")
        else:
            self._sq1 = self._sq1_claims

        if gv.SQUAD2_NEXT != 'No slots left':
            if gv.CURR_RFLSH > float(gv.SQUAD2_NEXT):
                self._sq2_claims = 'Ready'
            else:
                rflsh_needed = gv.SQUAD2_NEXT - gv.CURR_RFLSH
                if rflsh_needed * 100 < gv.CURR_FLSH:
                    self._days_needed_2 = (int((gv.CURR_FLSH/rflsh_needed)/0.01)/gv.DAYS)
                    self._sq2_claims = 0
                else:
                    i = gv.DAYS
                    one_claim_flsh = gv.CURR_FLSH
                    while i > 0:
                        multiplier = 1 + 0.01*i
                        if multiplier > 2.0:
                            multiplier = 2.0
                        one_claim_flsh += self._total_gain * multiplier
                        i -= 1
                    one_claim_flsh -= gv.WD_COST

                    after_one_claim_rflsh = one_claim_flsh*0.01+gv.CURR_RFLSH
                    claim = 1
                    self._days_needed_2 += 1
                    while after_one_claim_rflsh < rflsh_needed:
                        after_one_claim_rflsh += one_claim_flsh*0.01
                        self._days_needed_2 += 1
                        claim += 1
                    self._sq2_claims = claim
        else: 
            self._sq2_claims = 'All slots open'

        if type(self._sq2_claims) == int:
            self._sq2 = (gv.TODAY.date()+timedelta(days=(self._sq2_claims*gv.DAYS+self._days_needed_2))).strftime("%d.%m.%Y")
        else:
            self._sq2 = self._sq2_claims

        if gv.SQUAD3_NEXT != 'No slots left':
            if gv.CURR_RFLSH > float(gv.SQUAD3_NEXT):
                self._sq3_claims = 'Ready'
            else:
                rflsh_needed = gv.SQUAD3_NEXT - gv.CURR_RFLSH
                if rflsh_needed * 100 < gv.CURR_FLSH:
                    self._days_needed_3 = (int((gv.CURR_FLSH/rflsh_needed)/0.01)/gv.DAYS)
                    self._sq3_claims = 0
                else:
                    i = gv.DAYS
                    one_claim_flsh = gv.CURR_FLSH
                    while i > 0:
                        multiplier = 1 + 0.01*i
                        if multiplier > 2.0:
                            multiplier = 2.0
                        one_claim_flsh += self._total_gain * multiplier
                        i -= 1
                    one_claim_flsh -= gv.WD_COST

                    after_one_claim_rflsh = one_claim_flsh*0.01+gv.CURR_RFLSH
                    claim = 1
                    self._days_needed_3 += 1
                    while after_one_claim_rflsh < rflsh_needed:
                        after_one_claim_rflsh += one_claim_flsh*0.01
                        self._days_needed_3 += 1
                        claim += 1
                    self._sq3_claims = claim
        else: 
            self._sq3_claims = 'All slots open'
        
        if type(self._sq3_claims) == int:
            self._sq3 = (gv.TODAY.date()+timedelta(days=(self._sq3_claims*gv.DAYS+self._days_needed_3))).strftime("%d.%m.%Y")
        else:
            self._sq3 = self._sq3_claims

        self._sq1_claim_gain = 0
        self._sq2_claim_gain = 0
        self._sq3_claim_gain = 0

        i = gv.DAYS
        while i > 0:
            multiplier = 1 + 0.01*i
            if multiplier > 2.0:
                multiplier = 2.0
            self._sq1_claim_gain += self._sq1_total_gain * multiplier
            self._sq2_claim_gain += self._sq2_total_gain * multiplier
            self._sq3_claim_gain += self._sq3_total_gain * multiplier
            i -= 1    
    
    def input_validate(self, text, type):
        if not self.is_validating:
            self.is_validating = True
            if type == 'avax':
                gv.AVAX = float(text)
            elif type == 'flsh':
                gv.FLSH = float(text)
            elif type == 'days':
                gv.DAYS = int(text)
            elif type == 'rflsh':
                gv.RFLSH = float(text)
            elif type == 'cost':
                gv.WD_COST = float(text)
            
            self._curr_values.text = self.update_string('')
            self.calculate_squad_costs()
            gv.DATE_UPDATED = gv.TODAY
            self.update_values()
            self.is_validating = False
