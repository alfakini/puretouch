# -*- coding: utf-8 -*-
from pymt import *
from pdobjects import *
from utils import randpos
import topd

class PDPatch(MTWidget):
    def __init__(self, **kwargs):
        super(PDPatch, self).__init__(**kwargs) #MTInnerWindow

        #topd
        self.pdpatch = topd.Patch()
        self.pdpatch.dsp(0)

        #connections between the boxes outlets and inlets
        self.connections = {}

        #menu to create objects
        self.menu_widget = MTSidePanel(side='left', align='bottom')
        self.create_menu_button('object', self.create_object)
        self.create_menu_button('bang', self.create_bang)
        self.create_menu_button('toggle', self.create_toggle)
        self.create_menu_button('number', self.create_number)
        self.create_menu_button('vslider', self.create_vslider)
        self.add_widget(self.menu_widget)

        #other patch controls
        self.dsp_button = MTToggleButton(label='DSP OFF', size=(80,30), pos=(self.width-80,self.height-30))
        self.dsp_button.push_handlers(on_press=self.dsp)
        self.add_widget(self.dsp_button)

    def dsp(self, touch):
        if self.dsp_button.label == 'DSP ON':
            self.pdpatch.dsp(0)
            self.dsp_button.label = 'DSP OFF'
        else: 
            self.pdpatch.dsp(1)
            self.dsp_button.label = 'DSP ON'
        self.dsp_button.update_label()

    def create_menu_button(self, l, func, *args):
        m = MTButton(label=l, size=(80,40))
        m.push_handlers(on_press=func)
        self.menu_widget.add_widget(m)

    def create_object(self, touch):
        self.add_widget(PDObject(pdpatch=self.pdpatch, pos=(self.width/2, self.height/2)))

    def create_number(self, touch):
        self.add_widget(PDNumber(pdpatch=self.pdpatch, pos=(self.width/2, self.height/2)))

    def create_bang(self, touch):
        self.add_widget(PDBang(pdpatch=self.pdpatch, pos=(self.width/2, self.height/2)))

    def create_vslider(self, touch):
        self.add_widget(PDVSlider(pdpatch=self.pdpatch, pos=(self.width/2, self.height/2)))

    def create_toggle(self, touch):
        self.add_widget(PDToggle(pdpatch=self.pdpatch, pos=(self.width/2, self.height/2)))


