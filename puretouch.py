# -*- coding: utf-8 -*-

from pymt import *
from gesture import gesture_add_default
import topd
import os
import random

#TODO: Pensar melhor essa estrutura das connections, qual key usar? Usar uma lista?
#TODO: Jogar dentro do MTPatch
connections = {}

def randpos(width, height):
    return (random.randint(20, width-40), random.randint(40, height))

#FIXME: não atualizar tamanho dos objetos internos
class PDPatch(MTInnerWindow, topd.Patch):
    def __init__(self, gesture_db, **kwargs):
        super(PDPatch, self).__init__(**kwargs) #MTInnerWindow
        super(PDPatch, self).__init__() #topd.Patch
        
        #Gesture
        self.gesture_db = gesture_db
        self.detector = MTGestureWidget()
        self.detector.connect('on_gesture', self.on_gesture)
        self.add_widget(self.detector)

        menu = {'object': MTButton(label='object', size=(100,50)), 
                'message': MTButton(label='message', size=(100,50)),
                'vslide': MTButton(label='vslide', size=(100,50))}

        menu['object'].push_handlers(on_press=self.create_object)
        menu['vslide'].push_handlers(on_press=self.create_vslide)

        menu_widget = MTSidePanel(side='left', align='bottom')
        
        menu_widget.add_widget(menu['object'])
        menu_widget.add_widget(menu['vslide'])
        
        self.add_widget(menu_widget)

    def create_object(self, touch):
        self.add_widget(PDObject(1, 1, self, pos=randpos(self.width, self.height)))

    def create_vslide(self, touch):
        self.add_widget(PDWidget(1, 1, self, MTSlider(), pos=randpos(self.width, self.height)))

    #TODO: Selecionar objetos
    #TODO: Adicionar box
    def on_gesture(self, gesture, touch):
        ret = self.gesture_db.find(gesture)
        print self.gesture_db.gesture_to_str(gesture)
        
        try:
            score, best = self.gesture_db.find(gesture, minscore=.5)
            if best.id == 'circle':
                #TODO: Realizar teste verificando se objeto está dentro do circulo e seleciona para mover
                print "[MTPatch on_gesture] best.id == 'circle'"

        except Exception, e:
            print "[MTPatch on_gesture] exception"   

    def on_draw(self):

        super(PDPatch,self).on_draw() 

        global connections
        for connection in connections.values():
            if connection[0] == 'connected':
                pos_initial = connection[2]
                pos_final = connection[4]

                drawLine([pos_initial[0], pos_initial[1], pos_final[0], pos_final[1]], width = 1) 


#FIXME: Pode-se eliminar essa classe e deixar tudo nos inlets e outlets quando as connections forem deixadas no Patch
class PDLet(MTRectangularWidget):
    '''Abtração para os Inlets e Outlets'''

    def __init__(self, **kwargs):
        kwargs.setdefault('size', (20, 15))
        super(PDLet, self).__init__(**kwargs)
    	self.state = ('normal', None)

    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y):
            self.state = ('touched', touch.id, touch.pos)
            return True

    def on_touch_move(self, touch):
        if self.state[0] == 'touched' and self.state[1] == touch.id:
            self.state = ('touched', touch.id, touch.pos)
            return True

    def on_touch_up(self, touch):
        if self.collide_point(touch.x, touch.y):
            self.state = ('touched', touch.id, touch.pos)
            return True

        self.state = ('normal', None)


class PDInlet(PDLet):

    def __init__(self, **kwargs):
        super(PDInlet, self).__init__(**kwargs)
    
    #FIXME: Connections devem ser atualizadas no Patch
    def on_touch_move(self, touch):
        global connections
        for key in connections:
            if connections[key][3] == id(self):
                connections[key] = (connections[key][0],connections[key][1], connections[key][2], connections[key][3], 
                                    self.to_window(self.center[0], self.center[1]))
        super(PDInlet, self).on_touch_move(touch)
    

class PDOutlet(PDLet):

    def __init__(self, **kwargs):
        super(PDOutlet, self).__init__(**kwargs)

    #FIXME: Connections devem ser atualizadas no Patch
    def on_touch_move(self, touch):
        global connections
        for key in connections:
            if connections[key][1] == id(self):
                connections[key] = (connections[key][0],connections[key][1], 
                                    self.to_window(self.center[0], self.center[1]), connections[key][3], connections[key][4])
        super(PDOutlet, self).on_touch_move(touch)
      
          
#FIXME: usar MTDragable. MTScatter usa o ponto de referência no centro para as rotações, dificultando calculos.
#TODO: Fazer com que O Objeto seja dragable apenas quando selecionado. Isso ocorre com a gesture do circulo ao seu redor
class PDWidget(MTScatterWidget):

    def __init__(self, inlet_n, outlet_n, patch, obj, **kwargs):
        kwargs.setdefault('size', (obj.width, obj.height + 30))
        super(PDWidget, self).__init__(**kwargs)

        self.patch = patch
        self.object = obj
        self.add_widget(self.object)

        self.object.y += 15

        #inlets
        self.inlets = []
        space = 0
        for inlet in range(inlet_n):
            inlet = PDInlet(pos=(space, self.object.height + 15))
            self.inlets.append(inlet)
            self.add_widget(inlet)
            space += 25

        #outlets
        self.outlets = []
        space = 0
        for outlet in range(outlet_n):
            outlet = PDOutlet(pos=(space, 0))
            self.outlets.append(outlet)
            self.add_widget(outlet)
            space += 25

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return False

        self.cursor_point = touch.pos
        super(PDWidget, self).on_touch_down(touch)

        for outlet in self.outlets:
            if outlet.state[0] == 'touched':
                global connections
                connections[touch.id] = ('touched', id(outlet), outlet.to_window(outlet.x, outlet.y), None, None) 
     
        touch.grab(self)
        return True

    def on_touch_move(self, touch):
        self.cursor_point = touch.pos
        super(PDWidget, self).on_touch_move(touch)

        if not touch.grab_current == self:
            return False
        return True

    def on_touch_up(self, touch):
        super(PDWidget, self).on_touch_up(touch)

        if self.collide_point(*touch.pos):
            global connections
            if touch.id in connections:
                for inlet in self.inlets:
                    if inlet.state[0] == 'touched':
                        connection = connections[touch.id]
                        connections[touch.id] = ('connected', connection[1], connection[2], id(inlet), inlet.pos)

        if not touch.grab_current == self:
            return False
        touch.ungrab(self)
        return True

    def on_draw(self):     
        for outlet in self.outlets:
            if outlet.state[0] == 'touched':
                value = outlet.to_window(outlet.x, outlet.y)
                drawLine([value[0], value[1], self.cursor_point[0], self.cursor_point[1]], width=1)

        super(PDWidget, self).on_draw()

        global connections
        for connection in connections.values():
            if connection[0] == 'connected':
                pos_initial = connection[2]
                pos_final = connection[4]
                drawLine([pos_initial[0], pos_initial[1], pos_final[0], pos_final[1]], width = 1) 

        
class PDObject(PDWidget):

    def __init__(self, inlet_n, outlet_n, patch, **kwargs):
        super(PDObject, self).__init__(inlet_n, outlet_n, patch, MTTextInput(width=100, height=30), **kwargs)
        self.object.push_handlers(on_text_validate=self.mensagem)

    def mensagem(self, *largs):
        self.obj = topd.Object(self.patch, self.object.label, self.x, self.y)
    

if __name__ == "__main__":
    #os.system('pd topd/recebe.pd & sleep 300')

    gesture_db = GestureDatabase()
    gesture_add_default(gesture_db)
    patch = PDPatch(gesture_db)

    window = MTWindow()
    window.add_widget(patch)

    runTouchApp()

