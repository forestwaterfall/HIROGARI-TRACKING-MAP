# -*- coding: utf-8 -*-

import wx
import wx.xrc
import wx.adv

class MyFrame1 ( wx.Frame ):

    def __init__( self, parent ):
        wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = 'HIROGARI TRACKING MAP', pos = wx.DefaultPosition, size = wx.Size( 600,380 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

        self.SetSizeHints( wx.Size( 600,380 ), wx.DefaultSize )

        self.wSizer1 = wx.BoxSizer( wx.VERTICAL)
        self.settingSizer = wx.WrapSizer(wx.HORIZONTAL, wx.WRAPSIZER_DEFAULT_FLAGS)
        self.wSizer3 = wx.WrapSizer( wx.HORIZONTAL, wx.WRAPSIZER_DEFAULT_FLAGS )

        self.m_staticText1 = wx.StaticText( self, wx.ID_ANY, u"HIROGARI Tracking Map", wx.DefaultPosition, wx.DefaultSize, style = wx.TE_CENTER )
        self.m_staticText1.Wrap( -1 )

        self.m_staticText1.SetFont( wx.Font( 16, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, wx.EmptyString ) )

        self.wSizer3.Add( self.m_staticText1, 0, wx.ALL, 10 )


        self.settingSizer.Add( self.wSizer3, 1, wx.EXPAND, 5 )

        self.wSizer2 = wx.WrapSizer( wx.HORIZONTAL, wx.WRAPSIZER_DEFAULT_FLAGS )

        mode_choiceChoices = ['Designate', 'Real Time' ]
        self.mode_choice = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.Size( -1,-1 ), mode_choiceChoices, 0 )
        self.mode_choice.SetSelection( 1 )
        self.wSizer2.Add( self.mode_choice, 0, wx.ALL, 5 )

        self.track_date = wx.adv.DatePickerCtrl( self, wx.ID_ANY, wx.DefaultDateTime, wx.DefaultPosition, wx.DefaultSize, wx.adv.DP_DEFAULT )
        self.wSizer2.Add( self.track_date, 0, wx.ALL, 5 )

        self.track_time = wx.adv.TimePickerCtrl( self, wx.ID_ANY, wx.DefaultDateTime, wx.DefaultPosition, wx.DefaultSize, wx.adv.TP_DEFAULT )
        self.wSizer2.Add( self.track_time, 0, wx.ALL, 5 )

        self.show_button = wx.Button( self, wx.ID_ANY, u"SHOW", wx.DefaultPosition, wx.Size( 60,-1 ), 0 )
        self.wSizer2.Add( self.show_button, 0, wx.ALL, 5 )


        self.settingSizer.Add( self.wSizer2, 1, wx.EXPAND, 5 )
        self.wSizer1.Add(self.settingSizer, 1, wx.EXPAND, 0)

        self.mapSizer = wx.BoxSizer( wx.VERTICAL)
        self.tracking_map = wx.StaticBitmap( self, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize, 0 )


        self.mapSizer.Add( self.tracking_map, 0, wx.ALL, 5 )
        self.wSizer1.Add(self.mapSizer, 1, wx.ALIGN_CENTER, 0)

        self.SetSizer( self.wSizer1 )
        self.Layout()

        self.Centre( wx.BOTH )

    def __del__( self ):
        pass
