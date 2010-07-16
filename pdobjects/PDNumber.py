# -*- coding: utf-8 -*-
from pymt import *
from pdbox import *
from utils import *
import topd

class PDNumber(PDBox):
    def __init__(self, **kwargs):
        kwargs.setdefault('n_lets', (1,1))
        kwargs.setdefault('widget', MTButton(size=(80,40)))
        super(PDNumber, self).__init__(**kwargs)
        self.widget.label = '0'
        self._lasty = 0
        #topd
        #posx, posy = kwargs.get('pos')
        #self.pdobject = topd.Number(self.pdpatch, posx, posy)
        self.pdobject = topd.Number(self.pdpatch)

    def on_touch_move(self, touch):
        super(PDNumber, self).on_touch_move(touch)
        #FIXME: do this using gesture?
        if self.widget.state == 'down':
            y = touch.y - self._lasty
            if y > 0:
                self.value += 1
                self.pdobject.increment()
            elif y < 0:
                self.value -= 1
                self.pdobject.decrement()
        self._lasty = touch.y
        #FIXME: aceitar mais de 1 outlet
        self.outlets[0].value = self.value

    def get_value(self):
        return float(self.widget.label)
    def set_value(self, value):
        if not isinstance(value, str):
            self.widget.label = str(value)
        #FIXME: aceitar mais de 1 outlet
        if self.outlets[0]:
            self.outlets[0].value = value
    value = property(get_value, set_value)

