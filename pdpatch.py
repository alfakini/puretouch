# -*- coding: utf-8 -*-
from pymt import *
from pdobjects import *
from utils import randpos
import topd

class PDPatch(MTWidget):
    def __init__(self, gesture_db, **kwargs):
        super(PDPatch, self).__init__(**kwargs) #MTInnerWindow

        #topd
        self.pdpatch = topd.Patch()
        self.pdpatch.dsp(0)
        #editmode() 1,0
        #send(fudi_msg)
        #clear()

        #gesture
        self.gesture_db = gesture_db
        self.detector = MTGestureWidget()
        self.detector.connect('on_gesture', self.on_gesture)
        #self.add_widget(self.detector)

        #connections between the boxes outlets and inlets
        self.connections = {}
        self.temp_connections = {}

        #patch menu to create objects
        self.menu_widget = MTSidePanel(side='left', align='bottom')
        self.create_menu_button('object', self.create_object)
        self.create_menu_button('bang', self.create_bang)
        self.create_menu_button('toggle', self.create_toggle)
        self.create_menu_button('number', self.create_number)
        self.create_menu_button('comment', self.create_comment)
        self.create_menu_button('vslider', self.create_vslider)
        self.create_menu_button('box_test', self.create_box_test)
        self.add_widget(self.menu_widget)

        #other patch controls
        self.dsp_button = MTButton(label='DSP OFF', size=(80,30), pos=(self.width-80,self.height-30))
        self.dsp_button.push_handlers(on_press=self.dsp)
        self.add_widget(self.dsp_button)

    #def find_connection(self, window_pos):
    #for mod in self.children:
    #    if mod.collide_point(*self.to_local(*window_pos)):
    #        for btn in mod.io_buttons:
    #            if btn.collide_point(*btn.to_widget(*window_pos)):
    #                return btn
    #return False

    def dsp(self, touch):
        if self.dsp_button.label == 'DSP ON':
            self.pdpath.dsp(0)
            self.dsp_button.label = 'DSP OFF'
        else: 
            self.pdpath.dsp(1)
            self.dsp_button.label = 'DSP ON'
        self.dsp_button.update_label()

    def create_menu_button(self, l, func, *args):
        m = MTButton(label=l, size=(80,40))
        m.push_handlers(on_press=func)
        self.menu_widget.add_widget(m)

    def create_box_test(self, touch):
        self.add_widget(PDBox(1, 1, pos=randpos(self.width, self.height)))


    def create_object(self, touch):
        self.add_widget(PDObject(self.pdpatch, 1, 1, pos=randpos(self.width, self.height)))

    def create_message(self, touch):
        pass

    def create_number(self, touch):
        self.add_widget(PDNumber(self.pdpatch, pos=randpos(self.width, self.height)))

    def create_symbol(self, touch):
        pass

    def create_comment(self, touch):
        self.add_widget(PDComment(self.pdpatch, pos=randpos(self.width, self.height)))

    def create_bang(self, touch):
        self.add_widget(PDBang(self.pdpatch, pos=randpos(self.width, self.height)))        

    def create_hslider(self, touch):
        pass

    def create_vslider(self, touch):
        self.add_widget(PDVSlider(self.pdpatch, pos=randpos(self.width, self.height)))

    def create_toggle(self, touch):
        self.add_widget(PDToggle(self.pdpatch, pos=randpos(self.width, self.height)))
    def create_number2(self, touch):
        pass

    def create_radio(self, touch):
        pass

    def create_hradio(self, touch):
        pass

    def create_vradio(self, touch):
        pass

    def create_vu(self, touch):
        pass

    def create_canvas(self, touch):
        pass

    def on_gesture(self, gesture, touch):
        ret = self.gesture_db.find(gesture)
        print self.gesture_db.gesture_to_str(gesture)
        
        try:
            score, best = self.gesture_db.find(gesture, minscore=.5)
            if best.id == 'circle':
                print "[MTPatch on_gesture] best.id == 'circle'"

        except Exception, e:
            print "[MTPatch on_gesture] exception"   
   
    #def on_draw(self):
    #    #for c in self.connections.values():
    #     #   c.on_draw()
    #    super(PDPatch, self).on_draw() 


