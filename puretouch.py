# -*- coding: utf-8 -*-
from pymt import *
from pdobjects import *
from pdpatch import *
from gesture import gesture_add_default
import os

if __name__ == "__main__":
    #os.system('pd topd/recebe.pd & sleep 300')

    window = MTWindow()
    gesture_db = GestureDatabase()
    gesture_add_default(gesture_db)
    patch = PDPatch(gesture_db, size=window.size)
    print patch.size
    #inner_window = MTInnerWindow()
    #inner_window.add_widget(patch)

    #window.add_widget(inner_window)
    window.add_widget(patch)

    runTouchApp()
