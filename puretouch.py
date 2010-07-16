# -*- coding: utf-8 -*-
from pymt import *
from pdpatch import *
from pdobjects import *
import os

if __name__ == "__main__":
    #os.system('pd topd/recebe.pd & sleep 2000')
    window = MTWindow()
    patch = PDPatch(size=window.size)
    n1 = PDNumber(pdpatch=patch.pdpatch, pos=(100,100))
    n2 = PDNumber(pdpatch=patch.pdpatch, pos=(10,10))
    patch.add_widget(n1)
    patch.add_widget(n2)
    window.add_widget(patch)
    runTouchApp()
