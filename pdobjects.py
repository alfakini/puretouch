# -*- coding: utf-8 -*-
from pymt import *
from pdbox import *
import time
from utils import *
import topd

class PDObject(PDBox):
    def __init__(self, **kwargs):
        kwargs.setdefault('n_lets', (0,0))
        #FIXME: Pymt with bug, i think the bug is in mtlabel, but i don't know how to solve it
        #kwargs.setdefault('widget', MTTextInput(size=(100,30), autowidth=True))
        kwargs.setdefault('widget', MTTextInput(size=(100,30)))
        super(PDObject, self).__init__(**kwargs)
        self.widget.push_handlers(self.on_text_validate)
        #self.widget.push_handlers(self.on_text_change)

    def on_text_validate(self, *largs):
        self.label, self.parameters = (lambda x: (x[0], x[1:]))(self.widget.label.split(' '))
        pdobjs = objects_config()
        if self.label in pdobjs:
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

        print self.label, self.parameters
        #self.pdobject.edit(self.widget.label)
    
    '''def on_text_change(self, *largs):
        #super(PDObject, self).on_text_change(*largs)
        print self.widget.width
        print self.width
        #self.widget.width += 4
    '''
    def get_value(self):
        return float(self.widget.label)
    def set_value(self, value):
        pass
    value = property(get_value, set_value)

class PDBang(PDBox):
    def __init__(self, **kwargs):
        kwargs.setdefault('n_lets', (1,1))
        kwargs.setdefault('widget', MTButton(size=(40,40)))
        super(PDBang, self).__init__(**kwargs)
        self.widget.push_handlers(self.on_press)
        self.widget.push_handlers(self.on_release)
        self.widget.label = 'B'
        self._lastvalue = None

    def on_press(self, *largs):
        #FIXME: aceitar mais de 1 outlet
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

class PDToggle(PDBox):
    def __init__(self, **kwargs):
        kwargs.setdefault('n_lets', (1,1))
        kwargs.setdefault('widget', MTToggleButton(size=(40,40)))
        super(PDToggle, self).__init__(**kwargs)
        self.widget.push_handlers(self.on_press)
        self.widget.push_handlers(self.on_release)
        self.widget.label = 'T'
        self._state = 0
    def on_press(self, *largs):
        print 'on_press'

    def on_release(self, *largs):
        print 'on_release'

    def get_value(self):
        return self.widget.state
    def set_value(self, value):
        if isinstance(value, float) or isinstance(value, int):
            self._state = (1 if value else 0)
        else:
            if value == 'down':
                self._state+=1

        if not self._state % 2:
            self.widget.state = 'normal'
            self.widget.dispatch_event('on_release', None)
        else:
            self.widget.state = 'down'
            self.widget.dispatch_event('on_press', None)

        #FIXME: aceitar mais de 1 outlet
        if self.outlets[0]:
            self.outlets[0].value = self.value
    value = property(get_value, set_value)

class PDNumber(PDBox):
    def __init__(self, **kwargs):
        kwargs.setdefault('n_lets', (1,1))
        kwargs.setdefault('widget', MTButton(size=(80,40)))
        super(PDNumber, self).__init__(**kwargs)
        self.widget.label = '0'
        self._lasty = 0

    def on_touch_move(self, touch):
        super(PDNumber, self).on_touch_move(touch)
        #FIXME: do this using gesture?
        if self.widget.state == 'down':
            y = touch.y - self._lasty
            if y > 0:
                self.value += 1
            elif y < 0:
                self.value -= 1
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

#====================================================================


class PDMessage(object):
    def __init__(self):
        pass

class PDSymbol(object):
    def __init__(self):
        pass

class PDComment(PDBox):
    def __init__(self, pdpatch, **kwargs):
        kwargs.setdefault('n_lets', (0,0))
        kwargs.setdefault('widget', MTTextInput(size=(100,30)))

        super(PDComment, self).__init__(**kwargs)

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
