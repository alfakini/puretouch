# -*- coding: utf-8 -*-
from pymt import *
from pdbox import *
from utils import *
import topd

class PDVSlider(PDBox):
    def __init__(self, **kwargs):
        kwargs.setdefault('n_lets', (1,1))
        kwargs.setdefault('widget', MTSlider(value_show=True))
        super(PDVSlider, self).__init__(**kwargs)
        self.widget.push_handlers(self.on_value_change)
        #topd
        posx, posy = kwargs.get('pos')
        self.pdobject = topd.VSlider(self.pdpatch, posx, posy)

    def on_value_change(self, value):
        self.pdobject.update(value)
        #FIXME: aceitar mais de 1 outlet
        self.outlets[0].value = value

    def get_value(self):
        return self.widget.value
    def set_value(self, value):
        if not isinstance(value, str):
            self.widget.value = value
        else:
            #FIXME: aceitar mais de 1 outlet
            self.outlets[0].value = value
    value = property(get_value, set_value)


