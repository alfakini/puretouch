# -*- coding: utf-8 -*-
from pymt import *
from pdpatch import *
import os

if __name__ == "__main__":
    #os.system('pd topd/recebe.pd & sleep 2000')
    window = MTWindow()
    patch = PDPatch(size=window.size)
    window.add_widget(patch)
    runTouchApp()
