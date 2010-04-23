# -*- coding: utf-8 -*-

from pymt import *
from gesture import gesture_add_default
import topd
import os
import random

from utils import randpos

#TODO: usando doubletap e gestures para melhorar a interatividade
#TODO: tamanho do objeto cresce com o tamanho do texto digitado no teclado /pymt/examples/flowchart
#TODO: Não atualizar o tamanho dos objetos internos quando o patch é redimencionado 

class PDPatch(MTWidget):
    def __init__(self, gesture_db, **kwargs):
        super(PDPatch, self).__init__(**kwargs) #MTInnerWindow
        
        self.gesture_db = gesture_db
        self.detector = MTGestureWidget()
        self.detector.connect('on_gesture', self.on_gesture)
        self.add_widget(self.detector)

        self.connections = {}
        self.temp_connections = {}

        menu = {'object': MTButton(label='object', size=(100,50)), 
                'vslide': MTButton(label='vslide', size=(100,50))}
        menu['object'].push_handlers(on_press=self.create_object)
        menu['vslide'].push_handlers(on_press=self.create_vslide)
        menu_widget = MTSidePanel(side='left', align='bottom')
        menu_widget.add_widget(menu['object'])
        menu_widget.add_widget(menu['vslide'])

        self.add_widget(menu_widget)

    def create_object(self, touch):
        self.add_widget(PDObject(self, 1, 1, pos=randpos(self.width, self.height)))

    def create_vslide(self, touch):
        self.add_widget(PDBoxWidget(self, 1, 1, MTSlider(), pos=randpos(self.width, self.height)))

    def on_gesture(self, gesture, touch):
        ret = self.gesture_db.find(gesture)
        print self.gesture_db.gesture_to_str(gesture)
        
        try:
            score, best = self.gesture_db.find(gesture, minscore=.5)
            if best.id == 'circle':
                print "[MTPatch on_gesture] best.id == 'circle'"

        except Exception, e:
            print "[MTPatch on_gesture] exception"   
   
    def on_draw(self):
        for c in self.temp_connections.values():
            box, outlet, k, touch = c
            outletx, outlety = outlet.to_window(outlet.x, outlet.y)
            set_color(1, 0, 0, 1)
            drawLine([outletx, outlety, touch.x, touch.y], width=15)

        for c in self.connections.values():
            source_box, outlet, target_box, inlet = c
            outletx, outlety = outlet.to_window(outlet.x, outlet.y)
            inletx, inlety = inlet.to_window(inlet.x, inlet.y)
            set_color(1, 0, 0, 1)
            drawLine([outletx, outlety, inletx, inlety], width=15)

        super(PDPatch,self).on_draw() 


#FIXME: Pode-se eliminar essa classe e deixar tudo nos inlets e outlets quando as connections forem deixadas no Patch
class PDLet(MTRectangularWidget):
    '''Abstração para os Inlets e Outlets'''

    def __init__(self, value, **kwargs):
        kwargs.setdefault('size', (20, 15))
        super(PDLet, self).__init__(**kwargs)
        self.value = value
        self.state = 'normal'

    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y):
            self.state = 'touched'
            return True

    def on_touch_up(self, touch):
        if self.collide_point(touch.x, touch.y):
            self.state = 'touched'
            return True
        self.state = 'normal'


class PDInlet(PDLet):
    def __init__(self, value, **kwargs):
        super(PDInlet, self).__init__(value, **kwargs)
    

class PDOutlet(PDLet):
    def __init__(self, value, **kwargs):
        super(PDOutlet, self).__init__(value, **kwargs)


#FIXME: usar MTDragable. MTScatter usa o ponto de referência no centro para as rotações, dificultando calculos.
#TODO: Fazer com que O Objeto seja dragable apenas quando selecionado. Isso ocorre com a gesture do circulo ao seu redor
class PDBoxWidget(MTScatterWidget):
    def __init__(self, patch, inlet_n, outlet_n, widget, **kwargs):
        kwargs.setdefault('size', (widget.width, widget.height + 30))
        super(PDBoxWidget, self).__init__(**kwargs)

        self.patch = patch
        self.widget = widget
        self.add_widget(self.widget)

        self.widget.y += 15

        #inlets
        self.inlets = []
        space = 0
        for v in range(inlet_n):
            inlet = PDInlet(v, pos=(space, self.widget.height + 15))
            self.inlets.append(inlet)
            self.add_widget(inlet)
            space += 25

        #outlets
        self.outlets = []
        space = 0
        for v in range(outlet_n):
            outlet = PDOutlet(v, pos=(space, 0))
            self.outlets.append(outlet)
            self.add_widget(outlet)
            space += 25

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return False

        super(PDBoxWidget, self).on_touch_down(touch)

        for outlet in self.outlets:
            if outlet.state == 'touched':
                self.patch.temp_connections[touch.id] = (self, outlet, None, touch) 
     
        touch.grab(self)
        return True

    def on_touch_move(self, touch):
        super(PDBoxWidget, self).on_touch_move(touch)

        if not touch.grab_current == self:
            return False

        if touch.id in self.patch.temp_connections:
            c = self.patch.temp_connections[touch.id]
            self.patch.temp_connections[touch.id] = (c[0], c[1], None, touch)

        return True

    def on_touch_up(self, touch):
        super(PDBoxWidget, self).on_touch_up(touch)

        if self.collide_point(*touch.pos):
            if touch.id in self.patch.temp_connections:
                for inlet in self.inlets:
                    if inlet.state == 'touched':
                        source_box, source_outlet, x, y = self.patch.temp_connections[touch.id]
                        self.patch.connections[touch.id] = (source_box, source_outlet, self, inlet)
                        inlet.state = 'normal'

        if not touch.grab_current == self:
            return False
        if touch.id in self.patch.temp_connections: del self.patch.temp_connections[touch.id]
        touch.ungrab(self)
        return True

    def on_draw(self):     
        super(PDBoxWidget, self).on_draw()


class PDConnection(MTWidget):
    def __init__(self, source_box, outlet, target_box, inlet,  **kwargs):
        super(PDConnection, self).__init__(**kwargs)
        self.source_box = source_box
        self.outlet = outlet
        self.taget_box = target_box
        self.inlet = inlet
        self.state = 'temp'

    def on_draw(self):
        outletx, outlety = self.outlet.to_window(self.outlet.x, self.outlet.y)
        if self.state == 'temp':
            set_color(1, 0, 0, 1) 
            drawLine([outletx, outlety, self.target_box.x, self.target_box.y], width=15)
        else:
            inletx, inlety = inlet.to_window(inlet.x, inlet.y)
            set_color(1, 1, 0, 1)
            drawLine([outletx, outlety, inletx, inlety], width=15)


class PDObject(PDBoxWidget):
    def __init__(self, patch, inlet_n, outlet_n, **kwargs):
        super(PDObject, self).__init__(patch, inlet_n, outlet_n, MTTextInput(width=100, height=30), **kwargs)
        self.widget.push_handlers(on_text_validate=self.mensagem)

    def mensagem(self, *largs):
        pass
        #self.obj = topd.Object(self.patch, self.widget.label, self.x, self.y)
    

if __name__ == "__main__":
    #os.system('pd topd/recebe.pd & sleep 300')

    gesture_db = GestureDatabase()
    gesture_add_default(gesture_db)
    patch = PDPatch(gesture_db)
    inner_window = MTInnerWindow()
    inner_window.add_widget(patch)

    window = MTWindow()
    window.add_widget(inner_window)

    runTouchApp()

