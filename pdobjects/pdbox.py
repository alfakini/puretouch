# -*- coding: utf-8 -*-
from pymt import *
from math import fabs
import utils
import topd

additional_css = '''
.let {
    bg-color: rgb(68, 170, 40, 150);
}
.box {
    bg-color: rgb(100, 100, 100, 40);
}
'''
css_add_sheet(additional_css)

class PDConnection(MTWidget):
    def __init__(self,  **kwargs):
        super(PDConnection, self).__init__(**kwargs)
        self.source = kwargs.get('source')
        self.outlet = kwargs.get('outlet')
        self.target = kwargs.get('target')
        self.inlet = kwargs.get('inlet')
        self.state = 'temp'
        self.line_width = 15

    def on_touch_down(self,touch):
        if touch.is_double_tap:
            x1, y1 = self.outlet.to_window(*self.outlet.pos)
            x2, y2 = self.inlet.to_window(*self.inlet.pos)
            y, x = touch.y, utils.line(x1+10,y1+7,x2+10,y2+7)(touch.x)
            if(fabs(x - y) < self.line_width/2):
                self.remove()

    def draw(self):
        outlet = self.outlet.to_window(self.outlet.x, self.outlet.y)
        outlet = (outlet[0] + 10, outlet[1] + 7)
        if self.state == 'temp':
            set_color(1, 0, 0, 0.6) 
            drawLine([outlet[0], outlet[1], self.inlet.x, self.inlet.y], width=self.line_width)
        else:
            inlet = self.inlet.to_window(self.inlet.x, self.inlet.y)
            inlet = (inlet[0] + 10, inlet[1] + 7)
            set_color(0.8, 0.8, 0.0, 0.6)
            drawLine([outlet[0], outlet[1], inlet[0], inlet[1]], width=self.line_width)

    def remove(self):
        self.parent.pdpatch.disconnect(self.source.pdobject, self.outlet.index, self.target.pdobject, self.inlet.index)
        self.parent.remove_widget(self)


class Let(MTRectangularWidget):
    def __init__(self, **kwargs):
        kwargs.setdefault('size', (20, 15))
        kwargs.setdefault('cls', ('let'))

        super(Let, self).__init__(**kwargs)

        self.index = kwargs.get('index')
        self._value = None

    def apply_css(self, styles):
        if 'bg-color' in styles:
            self.background = styles.get('bg-color')
            super(Let, self).apply_css(styles)

    def draw(self):
        set_color(*self.background)
        drawRectangle(pos=self.pos, size=self.size)

class Inlet(Let):
    def __init__(self, **kwargs):
        super(Inlet, self).__init__(**kwargs)
        self.source_outlet = None #O outlet de referência

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            obj = self.parent.parent
            patch = obj.parent
            connection = obj.parent.connections[touch.id]
            connection.inlet = self
            connection.target = obj
            connection.outlet.target_inlet = self # Liga este inlet ao source outlet
            self.source_outlet = connection.outlet # Liga o sourch outlet a este inlet
            connection.state = 'connected'
            connection.target.bring_to_front()
            connection.source.bring_to_front()
            patch.pdpatch.connect(connection.source.pdobject, connection.outlet.index, obj.pdobject, self.index)
            touch.ungrab(self)

    def get_value(self):
        return self._value
    def set_value(self, value):
        self._value = value
        self.parent.parent.value = value #atualiza o valor do widget, ex: Slider, Button, etc
    value = property(get_value, set_value)

class Outlet(Let):
    def __init__(self, **kwargs):
        super(Outlet, self).__init__(**kwargs)
        self.target_inlet = None #O inlet alvo
        self.connection = None

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return False
        touch.grab(self)
        obj = self.parent.parent
        self.patch = obj.parent
        self.connection =  PDConnection(source=obj, outlet=self, target=None, inlet=touch)
        self.patch.connections[touch.id] = self.connection
        self.patch.add_widget(self.connection)
        return True

    def on_touch_up(self, touch):
        if not touch.grab_current == self:
            return False
        connections = self.patch.connections
        if connections[touch.id].inlet == touch:
            self.connection = None
            self.patch.remove_widget(connections[touch.id])
        touch.ungrab(self)

    def get_value(self):
        return self._value
    def set_value(self, value):
        self._value = value
        if self.target_inlet: #Se possuir um inlet alvo, atualiza seu valor
            self.target_inlet.value = value
    value = property(get_value, set_value)

class PDBox(MTScatterWidget):
    def __init__(self, **kwargs):
        kwargs.setdefault('cls', ('box'))
        if 'pdpatch' in kwargs:
            self.pdpatch = kwargs.get('pdpatch')
        if 'widget' in kwargs:
            self.widget = kwargs.get('widget')
            self.widget.y += 15
            kwargs.setdefault('size', (self.widget.width, self.widget.height + 30))
        super(PDBox, self).__init__(**kwargs)

        #self.push_handlers(self.on_move)

        self.pdobject = None
        self.add_widget(self.widget)
        self.connections = []

        #FIXME: não é necessário pois temos inlet_box e outlet_box
        self.inlets = []
        self.outlets = []
        
        #Add inlets
        self.inlet_box = MTBoxLayout(pos=(0, self.height-15), orientation='horizontal', spacing=4)
        self.add_widget(self.inlet_box)
        for i in range(kwargs.get('n_lets')[0]):
            inlet = Inlet(index=i)
            self.inlets.append(inlet) 
            self.inlet_box.add_widget(inlet)  

        #Add outlets
        self.outlet_box = MTBoxLayout(pos=(0, 0), orientation='horizontal', spacing=4)
        self.add_widget(self.outlet_box) 
        for i in range(kwargs.get('n_lets')[1]):
            outlet = Outlet(index=i)
            self.outlets.append(outlet) 
            self.outlet_box.add_widget(outlet)  
    
    def on_touch_down(self,touch):
        super(PDBox, self).on_touch_down(touch)
        if self.collide_point(*touch.pos):
            touch.grab(self)
            if touch.is_double_tap:
                #topd
                self.pdobject.delete()
                for outlet in self.outlets:
                    if outlet.connection:
                        outlet.connection.remove()
                self.parent.remove_widget(self)
            return True

    def on_touch_up(self,touch):
        super(PDBox, self).on_touch_up(touch)
        if touch.grab_current == self:
            if self.collide_point(*touch.pos):
                self.pdobject.move(touch.x, touch.y)
            touch.ungrab(self)

    def apply_css(self, styles):
        if 'bg-color' in styles:
            self.background = styles.get('bg-color')
            super(PDBox, self).apply_css(styles)

    def draw(self):
        set_color(*self.background)
        drawRectangle(pos=(0,0), size=self.size)
