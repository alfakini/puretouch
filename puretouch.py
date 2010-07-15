# -*- coding: utf-8 -*-
from pymt import *
from pdobjects import *
from pdpatch import *
import os

if __name__ == "__main__":
    #os.system('pd topd/recebe.pd & sleep 300')

    window = MTWindow()
    patch = PDPatch(size=window.size)
    
    patch.add_widget(PDBang(pdpatch=patch, pos=(300,200)))
    #inner_window = MTInnerWindow()
    #inner_window.add_widget(patch)

    #window.add_widget(inner_window)
    window.add_widget(patch)

    runTouchApp()
