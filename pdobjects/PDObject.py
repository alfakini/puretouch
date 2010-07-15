# -*- coding: utf-8 -*-
from pymt import *
from pdbox import *
from utils import *
from topd import Object

class PDObject(PDBox):
    def __init__(self, **kwargs):
        kwargs.setdefault('n_lets', (0,0))
        #FIXME: Pymt with bug, i think the bug is in mtlabel, but i don't know how to solve it
        #kwargs.setdefault('widget', MTTextInput(size=(100,30), autowidth=True))
        kwargs.setdefault('widget', MTTextInput(size=(100,30)))
        super(PDObject, self).__init__(**kwargs)
        self.widget.push_handlers(self.on_text_validate)
        posx, posy = kwargs.get('pos')
        #topd
        self.pdobject = Object(self.pdpatch, '', posx, posy)

    def on_text_validate(self, *largs):
        self.label, self.parameters = (lambda x: (x[0], x[1:]))(self.widget.label.split(' '))
        pdobjs = objects_config()
        if self.label in pdobjs:
            #topd
            self.pdobject.edit(self.widget.label)
            lets = pdobjs[self.label]
            self.inlet_box.spacing = (self.width - 20*lets[0])/float((lets[0]-1))
            for i in range(lets[0]):
                inlet = Inlet(index=i, patch=self.parent)
                self.inlets.append(inlet)
                self.inlet_box.add_widget(inlet)

            self.outlet_box.spacing = (self.width - 20*lets[1])/float((lets[1]-1))
            for i in range(lets[1]):
                outlet = Outlet(index=i, patch=self.parent)
                self.outlets.append(outlet)
                self.outlet_box.add_widget(outlet)
            return
        self.widget.label = '##'

    '''def on_text_change(self, *largs):
        #super(PDObject, self).on_text_change(*largs)
        print self.widget.width
        print self.width
        #self.widget.width += 4
    '''

    def get_value(self):
        return float(self.widget.label)
    def set_value(self, value):
        #FIXME: How do this?
        pass
    value = property(get_value, set_value)

