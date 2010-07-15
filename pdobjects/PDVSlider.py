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
        self.pdobject = topd.VSlider(self.pdpatch, 100, 100)

    def on_value_change(self, *largs):
        #FIXME: aceitar mais de 1 outlet
        self.outlets[0].value = largs[0]
        self.pdobject.increment()

    def get_value(self):
        return self.widget.value
    def set_value(self, value):
        if not isinstance(value, str):
            self.widget.value = value
        else:
            #FIXME: aceitar mais de 1 outlet
            self.outlets[0].value = value
    value = property(get_value, set_value)


