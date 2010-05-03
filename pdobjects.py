# -*- coding: utf-8 -*-
from pymt import *
import topd

class PDConnection(MTWidget):
    def __init__(self, source, outlet, target, inlet,  **kwargs):
        super(PDConnection, self).__init__(**kwargs)

        self.source = source
        self.outlet = outlet
        self.target = target
        self.inlet = inlet
        self.state = 'temp'

    def on_draw(self):
        outletx, outlety = self.outlet.to_window(self.outlet.x, self.outlet.y)
        if self.state == 'temp':
            set_color(1, 0, 0, 1) 
            drawLine([outletx, outlety, self.inlet.x, self.inlet.y], width=15)
        else:
            inletx, inlety = self.inlet.to_window(self.inlet.x, self.inlet.y)
            set_color(1, 1, 0, 1)
            drawLine([outletx, outlety, inletx, inlety], width=15)
            
    def on_touch_down(self,touch):
        if touch.is_double_tap:
            x1,y1,x2,y2 = self.source_box.x, self.source_box.y, self.target_box.x, self.target_box.y
            print x1, y1, x2, y2

            if self.line_collision_with_point(x1, y1, x2, y2, touch.x, touch.y):
                self.parent.remove_widget(self)

    def line_collision_with_point(self, x1, y1, x2, y2, x, y):
        '''From studioimaginaire'''
        # If line is vertical
        if x1 == x2:
            print y, y1, y2
            _max = max(y1,y2)
            _min = min(y1,y2)
            if y > _min and y < _max:
                return True
            else:
                return False
        m = float((y2 - y1)) / float((x2 - x1))
        b = y1 - m*x1
        result = abs(int(y) - int(m * x + b))

        if result < 10:
            return True
        else:
            return False

#TODO: A verificação de ligação outlet>inlet pode ser feita usando os métodos on_touch_down, on_touch_up, verificando no patch se o touch colide com algum #inlet
class PDLet(MTRectangularWidget):
    def __init__(self, **kwargs):
        kwargs.setdefault('color', (1,1,1))
        kwargs.setdefault('size', (20, 15))
        super(PDLet, self).__init__(**kwargs)

        self.state = 'normal'
        self.index = kwargs['index']
        self.pdobject = kwargs['pdobject']
        
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.state = 'touched'
            return True

    def on_touch_up(self, touch):
        if self.collide_point(touch.x, touch.y):
            self.state = 'touched'
            return True
        self.state = 'normal'  
 
class PDInlet(PDLet):
    def __init__(self, **kwargs):
        super(PDInlet, self).__init__(**kwargs)
        self.value = None

    def update_value(self, value):
        self.value = value

class PDOutlet(PDLet):
    def __init__(self, **kwargs):
        super(PDOutlet, self).__init__(**kwargs)
        self.value = None
        self.target = None #O inlet alvo

    def update_value(self, value):
        self.value = value
        if self.target: self.target.update_value(value)

class PDBox(MTScatterWidget):
    def __init__(self, n_inlets, n_outlets, widget, pdobject=None, **kwargs):
        kwargs.setdefault('size', (widget.width, widget.height + 30))
        super(PDBox, self).__init__(**kwargs)
        #Pymt Widget
        self.widget = widget
        self.widget.y += 15
        self.add_widget(self.widget)

        #topd
        self.pdobject = pdobject # topd object
        #self.pdpatch = pdpatch # referencia ao pdpatch

        #Connections, Inlets, Outlets
        self.connections = []
        self.inlets = []
        self.outlets = []
        
        #Add inlets
        self.inlet_box = MTBoxLayout(pos=(0, self.height-15), orientation='horizontal', spacing=4)
        for i in range(n_inlets):
            inlet = PDInlet(index=i, pdobject=self.pdobject)
            self.inlets.append(inlet) 
            self.inlet_box.add_widget(inlet)  
        self.add_widget(self.inlet_box)

        #Add outlets
        self.outlet_box = MTBoxLayout(pos=(0, 0), orientation='horizontal', spacing=4)
        for i in range(n_outlets):
            outlet = PDOutlet(index=i, pdobject=self.pdobject)
            self.outlets.append(outlet) 
            self.outlet_box.add_widget(outlet)  
        self.add_widget(self.outlet_box) 

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return False

        super(PDBox, self).on_touch_down(touch)

        for outlet in self.outlets:
            if outlet.state == 'touched':
                self.parent.connections[touch.id] = PDConnection(self, outlet, None, touch)
                self.parent.add_widget(self.parent.connections[touch.id])
        touch.grab(self)
        return True

    def on_touch_move(self, touch):
        super(PDBox, self).on_touch_move(touch)
        if not touch.grab_current == self:
            return False

        if touch.id in self.parent.temp_connections:
            self.parent.connections.touch = touch

        return True

    def on_touch_up(self, touch):
        super(PDBox, self).on_touch_up(touch)

        if self.collide_point(*touch.pos):
            if touch.id in self.parent.connections:
                for inlet in self.inlets:
                    if inlet.state == 'touched':
                        self.parent.connections[touch.id].target_box = self
                        self.parent.connections[touch.id].inlet = inlet
                        self.parent.connections[touch.id].outlet.target = inlet
                        self.parent.connections[touch.id].state = 'connected'
                        inlet.state = 'normal'

        if not touch.grab_current == self:
            return False

        if touch.id in self.parent.connections and self.parent.connections[touch.id].target_box == None: 
            self.parent.remove_widget(self.parent.connections[touch.id])
            del self.parent.connections[touch.id]
        touch.ungrab(self)
        return True
        
class PDObject(PDBox):
    def __init__(self, pdpatch, inlet_n, outlet_n, **kwargs):
        super(PDObject, self).__init__(inlet_n, outlet_n, MTTextInput(size=(100,30), autosize=True), **kwargs)

        #self.pd_object = topd.Object(self.parent.pdpatch, self.widget.label, self.x, self.y)
        self.widget.push_handlers(self.on_text_validate)
        self.widget.push_handlers(self.on_text_change)
        self.label = ''
        self.parameters = []
        self.width = self.widget.width
        self.pdobject = topd.Object(pdpatch, self.widget.label, self.x, self.y)

    def on_text_validate(self, *largs):
        self.label, self.parameters = (lambda x: (x[0], x[1:]))(self.widget.label.split(' '))
        self.pdobject.edit(self.widget.label)

    def on_text_change(self, *largs):
        self.width = max(100, self.widget.width)

    def on_update(self):
        if self.inlets[0].value: 
            self.widget.label = self.label + ' ' + str(self.inlets[0].value)
            self.pdobject.edit(self.widget.label)

class PDNumber(PDBox):
    def __init__(self, pdpatch, **kwargs):
        super(PDNumber, self).__init__(1, 1, MTButton(size=(80,40)),  **kwargs)
        self.widget.push_handlers(on_touch_move=self.button_touch_move)
        self.lasty = 0
        self.value = 0
        self.widget.label = '0'
        
    def button_touch_move(self, *largs):
        if self.widget.state == 'down':
            y = largs[0].y - self.lasty
            if y > 0:
                self.value += 1
            elif y < 0:
                self.value -= 1
        self.lasty = largs[0].y
        self.widget.label = str(self.value)

class PDMessage(object):
    def __init__(self):
        pass

class PDSymbol(object):
    def __init__(self):
        pass

class PDComment(PDBox):
    def __init__(self, pdpatch, **kwargs):
        super(PDComment, self).__init__(0,0, MTTextInput(size=(100,30), autowidth=True), **kwargs)
        self.widget.push_handlers(self.on_text_validate)
        self.parameters = []
        self.width = self.widget.width

    def on_text_validate(self, *largs):
        self.label, self.parameters = (lambda x: (x[0], x[1:]))(self.widget.label.split(' '))
        self.pdobject.edit(self.widget.label)

    #def on_text_change(self, *largs):
    #    self.wid
    #    self.width = self.widget.width
    
    #FIXME: :)
    #def on_update(self):
    #    if self.inlets[0].value: 
    #        self.widget.label = self.label + ' ' + str(self.inlets[0].value)

class PDHSlider(object):
    def __init__(self):
        pass

class PDVSlider(PDBox):
    def __init__(self, pdpatch, **kwargs):
        super(PDVSlider, self).__init__(1, 1, MTSlider(value_show=True), **kwargs)
        self.widget.push_handlers(self.on_value_change)
        self.pdobject = topd.VSlider(pdpatch, 100, 100)

    def on_value_change(self, *largs):
        self.outlets[0].update_value(largs[0])
        self.pdobject.increment()
        #enviar para o objeto pd que estiver ligado ao outlet

class PDBang(PDBox):
    def __init__(self, pdpatch, **kwargs):
        super(PDBang, self).__init__(1, 1, MTButton(size=(40,40)))
        self.widget.push_handlers(self.on_press)
        self.widget.push_handlers(self.on_release)
        self.widget.label = 'B'

    def on_press(self, *largs):
        print 'on_press'

    def on_release(self, *largs):
        print 'on_release'
    
class PDToggle(PDBox):
    def __init__(self, pdpatch, **kwargs):
        super(PDToggle, self).__init__(1, 1, MTToggleButton(size=(40,40)))
        self.widget.push_handlers(self.on_press)
        self.widget.push_handlers(self.on_release)
        self.widget.label = 'T'

    def on_press(self, *largs):
        print 'on_press'

    def on_release(self, *largs):
        print 'on_release'

class PDNumber2(object):
    def __init__(self):
        pass

class PDRadio(object):
    def __init__(self):
        pass

class PDHRadio(object):
    def __init__(self):
        pass

class PDVRadio(object):
    def __init__(self):
        pass

class PDVU(object):
    def __init__(self):
        pass

class PDCanvas(object):
    def __init__(self):
        pass

