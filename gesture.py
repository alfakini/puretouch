from pymt import *

def gesture_add_default(gdb):
    
    # Circle
    g = gdb.str_to_gesture('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')
    g.label = 'Circle'
    g.id = 'circle'
    gdb.add_gesture(g)

class MTGestureDetector(MTGestureWidget):
    def __init__(self, gdb, **kwargs):
        super(MTGestureDetector, self).__init__(**kwargs)
        self.gdb = gdb 

def on_gesture(self, gesture, x, y):
    try:
        score, best = self.gdb.find(gesture)
    except Exception, e:
        return

if __name__ == '__main__':
    # Create and fill gesture database
    gdb = GestureDatabase()
    gesture_add_default(gdb)
    
    w = getWindow()
    #w.add_widget(PanalWidget())
    g = MTGestureDetector(gdb)
    w.add_widget(g)
    runTouchApp()
