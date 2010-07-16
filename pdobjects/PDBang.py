# -*- coding: utf-8 -*-
from pymt import *
from pdbox import *
import topd

class PDBang(PDBox):
    def __init__(self, **kwargs):
        kwargs.setdefault('n_lets', (1,1))
        kwargs.setdefault('widget', MTButton(size=(40,40)))
        super(PDBang, self).__init__(**kwargs)
        self.widget.push_handlers(self.on_press)
        self.widget.push_handlers(self.on_release)
        self.widget.label = 'B'
        self._lastvalue = None
        #topd
        #posx, posy = kwargs.get('pos')
        #self.pdobject = topd.Bang(self.pdpatch, posx, posy)
        self.pdobject = topd.Bang(self.pdpatch)


    def on_press(self, *largs):
        #FIXME: aceitar mais de 1 outlet
        self.pdobject.bang()
        if self.outlets[0]:
            self.outlets[0].value = self.widget.state

    def on_release(self, *largs):
        if self.outlets[0]:
            self.outlets[0].value = self.widget.state

    def get_value(self):
        return self.widget.state
    def set_value(self, value):
        if value == 'down':
            self.widget.state = 'down'
            self.widget.dispatch_event('on_press', touch)
        if value == 'normal':
            self.widget.state = 'normal'
            self.widget.dispatch_event('on_release', touch)
        #FIXME: whitout visual feedback
        if isinstance(value, float) or isinstance(value, int):
            self.widget.state = 'down'
            self.widget.dispatch_event('on_press', touch)
            self.widget.state = 'normal'
            self.widget.dispatch_event('on_release', touch)
        #FIXME: aceitar mais de 1 outlet
        if self.outlets[0]:
            self.outlets[0].value = self.value
    value = property(get_value, set_value)

