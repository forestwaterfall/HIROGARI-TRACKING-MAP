
#! env python
# -*- coding: utf-8 -*-

import os
import sys
import wx
from func import HTM

if __name__ == '__main__':
    app = wx.App(False)
    frame = HTM(None)
    frame.Show(True)
    app.MainLoop()
