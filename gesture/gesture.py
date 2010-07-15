from pymt import *

#Based on http://github.com/alcides/wallmanager/blob/master/mtmenu/gesture/gesture_list.py
#Doc: http://pymt.txzone.net/docs/api/api-pymt.gesture.html

GESTURES = {'down': [(1,2), (1,1)], 
           'up': [(1,1), (1,2)], 
           'right': [(1,1), (2,1)], 
           'left': [(2,1), (1,1)]}

#FIXME: Singleton
class GestureDB(GestureDatabase):
    def __init__(self):
        super(GestureDB, self).__init__()

        for key, value in GESTURES.iteritems():
            g = Gesture()
            g.label = key
            g.id = key
            g.add_stroke(point_list=value)
            g.normalize()
            self.add_gesture(g)

class Gestures(MTGestureWidget):
    def __init__(self, **kwargs):
        gdb = GestureDB()
        super(Gestures, self).__init__(**kwargs)

    def on_gesture(self, gesture, touch):
        try:
            score, best = gdb.find(gesture, minscore=.5)
        except Exception, e:
            return

        print best.id
        return best.id
            


