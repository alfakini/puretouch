# -*- coding: utf-8 -*-
from pymt import *
from pdbox import *
from utils import *
import topd

class PDToggle(PDBox):
    def __init__(self, **kwargs):
        kwargs.setdefault('n_lets', (1,1))
        kwargs.setdefault('widget', MTToggleButton(size=(40,40)))
        super(PDToggle, self).__init__(**kwargs)
        self.widget.push_handlers(self.on_press)
        self.widget.push_handlers(self.on_release)
        self.widget.label = 'T'
        self._state = 0
        #topd
        #posx, posy = kwargs.get('pos')
        #self.pdobject = topd.Toggle(self.pdpatch, posx, posy)
        self.pdobject = topd.Toggle(self.pdpatch)

    def on_press(self, *largs):
        self._state += 1
        if self._state % 2:
            self.pdobject.on()
        else:
            self.pdobject.off()
        if self.outlets[0]:
            self.outlets[0].value = self.value

    def on_release(self, *largs):
        pass

    def get_value(self):
        return self.widget.state
    def set_value(self, value):
        if isinstance(value, float) or isinstance(value, int):
            self._state = (1 if value else 0)

        if self._state % 2:
            self.widget.state = 'down'
            self.pdobject.on()
        else:
            self.widget.state = 'normal'
            self.pdobject.off()

        if self.outlets[0]:
            self.outlets[0].value = self.value
            #self.widget.dispatch_event('on_press', None)
            #self.widget.dispatch_event('on_release', None)

        #FIXME: aceitar mais de 1 outlet
    value = property(get_value, set_value)





