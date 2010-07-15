# -*- coding: utf-8 -*-
from pymt import *
import topd

additional_css = '''
.let {
    bg-color: rgb(68, 170, 40, 150);
}

.box {
    bg-color: rgb(100, 100, 100, 30);
}
'''

css_add_sheet(additional_css)

class PDConnection(MTWidget):
    def __init__(self,  **kwargs):
        self.source = kwargs.get('source')
        self.outlet = kwargs.get('outlet')
        self.target = kwargs.get('target')
        self.inlet = kwargs.get('inlet')
        self.state = 'temp'

        super(PDConnection, self).__init__(**kwargs)

    def on_touch_down(self,touch):
        if touch.is_double_tap:
            x1,y1,x2,y2 = self.source.x, self.source.y, self.target.x, self.target.y
            print x1, y1, x2, y2

            if self.line_collision_with_point(x1, y1, x2, y2, touch.x, touch.y):
                self.parent.remove_widget(self)

    def on_draw(self):
        outletx, outlety = self.outlet.to_window(self.outlet.x, self.outlet.y)
        if self.state == 'temp':
            set_color(1, 0, 0, 1) 
            drawLine([outletx, outlety, self.inlet.x, self.inlet.y], width=15)
        else:
            inletx, inlety = self.inlet.to_window(self.inlet.x, self.inlet.y)
            set_color(1, 1, 0, 1)
            drawLine([outletx, outlety, inletx, inlety], width=15)
            
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
            connection = obj.parent.connections[touch.id]
            connection.inlet = self
            connection.target = obj
            connection.outlet.target_inlet = self # Liga este inlet ao source outlet
            self.source_outlet = connection.outlet # Liga o sourch outlet a este inlet
            connection.state = 'connected'
            connection.target.bring_to_front()
            connection.source.bring_to_front()
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

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return False
        touch.grab(self)
        obj = self.parent.parent
        self.patch = obj.parent
        self.patch.connections[touch.id] = PDConnection(source=obj, outlet=self, target=None, inlet=touch)
        self.patch.add_widget(self.patch.connections[touch.id])
        return True

    def on_touch_up(self, touch):
        if not touch.grab_current == self:
            return False
        connections = self.patch.connections
        if connections[touch.id].inlet == touch:
            self.patch.remove_widget(connections[touch.id])
        touch.ungrab(self)

    def get_value(self):
        return self._value
    def set_value(self, value):
        self._value = value
        if self.target_inlet: #Se possuir um inlet alvo, atualiza seu valor
            print '[OUTLET]: ', value, self
            self.target_inlet.value = value
    value = property(get_value, set_value)

class PDBox(MTScatterWidget):
    def __init__(self, **kwargs):

        if 'pdpatch' in kwargs:
            self.pdpatch = kwargs.get('pdpatch')
        print self.pdpatch

        kwargs.setdefault('cls', ('box'))
        if 'widget' in kwargs:
            self.widget = kwargs.get('widget')
            self.widget.y += 15
            kwargs.setdefault('size', (self.widget.width, self.widget.height + 30))

        super(PDBox, self).__init__(**kwargs)

        self.add_widget(self.widget)
        self.connections = []

        #FIXME: não é necessário pois temos inlet_box e outlet_box
        self.inlets = []
        self.outlets = []
        
        #Add inlets
        self.inlet_box = MTBoxLayout(pos=(0, self.height-15), orientation='horizontal', spacing=4)
        self.add_widget(self.inlet_box)
        for i in range(kwargs.get('n_lets')[0]):
            inlet = Inlet(index=i, patch=self.parent)
            self.inlets.append(inlet) 
            self.inlet_box.add_widget(inlet)  

        #Add outlets
        self.outlet_box = MTBoxLayout(pos=(0, 0), orientation='horizontal', spacing=4)
        self.add_widget(self.outlet_box) 
        for i in range(kwargs.get('n_lets')[1]):
            outlet = Outlet(index=i, patch=self.parent)
            self.outlets.append(outlet) 
            self.outlet_box.add_widget(outlet)  
    
    def apply_css(self, styles):
        if 'bg-color' in styles:
            self.background = styles.get('bg-color')
            super(PDBox, self).apply_css(styles)

    def draw(self):
        set_color(*self.background)
        drawRectangle(pos=(0,0), size=self.size)
