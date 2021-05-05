import wx
import io
import gui_class
import numpy as np
import ephem
import time
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import os
import copy
from PIL import Image, ImageOps
from geopy.distance import geodesic
import math
from pyorbital.orbital import Orbital
import threading
import sys
import subprocess

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

proj_lib = os.path.join(resource_path('.\\lib'))
os.environ["PROJ_LIB"] = proj_lib
print(proj_lib)

from mpl_toolkits.basemap import Basemap
import datetime
import time
import requests

def get_tle(cat_id='47930'):
    url = "https://celestrak.com/satcat/tle.php?CATNR=47930"
    r = requests.post(url)
    TLE = r.text.split("\r\n")[:3]
    return TLE

TLE = get_tle()

def scale_bitmap(bitmap, width, height):
    """ 画像のリサイズ """
    image = wx.ImageFromBitmap(bitmap)
    image = image.Scale(width, height, wx.IMAGE_QUALITY_HIGH)
    result = wx.BitmapFromImage(image)
    return result


north = 85
south = -70
east = 180
west = -180

m = Basemap(projection='mill', area_thresh=1000.0, llcrnrlat=south, urcrnrlat=north, llcrnrlon=west, urcrnrlon=east)

def _pydate2wxdate(date):
    assert isinstance(date, (datetime.datetime, datetime.date))
    tt = date.timetuple()
    dmy = (tt[2], tt[1]-1, tt[0])
    return wx.DateTimeFromDMY(*dmy)

def _wxdate2pydate(date):
    assert isinstance(date, wx.DateTime)
    if date.IsValid():
        ymd = map(int, date.FormatISODate().split('-'))
        return datetime.date(*ymd)
    else:
        return None


class HTM( gui_class.MyFrame1 ):
    def __init__( self, parent ):
        gui_class.MyFrame1.__init__( self, parent )
        self.ratio = 40
        self.last_runtime = time.time()
        self.map_plot_thread(datetime.datetime.utcnow(), TLE)
        self.Bind(wx.EVT_SIZE, self.set_mapratio)
        self.Bind(wx.EVT_IDLE, self.main)
        self.flag_changesize = False
        self.flag_update = False
        self.last_tle_update = time.time()
        self.input_time = datetime.datetime.utcnow()
        self.show_button.Bind(wx.EVT_BUTTON,self.onTimeChange)
        self.mode = 0
        self.Image = wx.Image(resource_path('loading.png'))
        self.wxImage = wx.Bitmap(self.Image)
        self.TLE_update_count = 1
        self.flag_exit = False
        subprocess.Popen("taskkill /F /IM loading.exe",shell=True)
        self.Bind(wx.EVT_CLOSE, self.closehandler)


    def loading(self):
        self.Image = wx.Image(resource_path('loading.png'))
        self.wxImage = wx.Bitmap(self.Image)
        self.wxImage_re = scale_bitmap(self.wxImage, int(16*self.ratio), int(9*self.ratio))
        self.tracking_map.SetBitmap(self.wxImage_re)

    def closehandler(self,event):
        self.Destroy()

    def main(self, event):
        event.RequestMore(True)
        global TLE
        modechange = False
        if self.mode == 0 and self.mode_choice.GetSelection() == 1:
            self.loading()
            modechange = True
        if time.time() - self.last_tle_update > 3600*8*self.TLE_update_count:
            TLE = get_tle()
            self.TLE_update_count += 1
        if time.time() - self.last_runtime > 0.1 and self.flag_changesize:
            self.set_mapratio(event)
            self.flag_changesize = False
        if (time.time() - self.last_runtime> 1 and self.mode_choice.GetSelection()==1) or modechange:
            self.last_runtime = time.time()
            if not self.thread_map.is_alive():
                self.map_plot_thread(datetime.datetime.utcnow(), TLE)
        self.mode = self.mode_choice.GetSelection()

    def get_time(self):
        track_wxdate = self.track_date.GetValue()
        hour, minute, second = self.track_time.GetTime()
        date = _wxdate2pydate(track_wxdate)
        year = date.year
        month = date.month
        day = date.day
        dt = datetime.datetime(year, month, day, hour, minute, second)
        dt -= datetime.timedelta(hours=9)
        return dt

    def onTimeChange(self,event):
        modechange = False
        if self.mode_choice.GetSelection()==1:
            self.mode_choice.SetSelection(0)
            modechange = True
        global TLE
        plt.close()
        self.loading()
        time = self.get_time()
        if not modechange:
            self.map_plot_thread(time, TLE)

    def set_mapratio(self,event):
        self.flag_changesize = True
        size = self.GetSize()
        x = size[0]
        y = x*9/16 + 100
        self.SetSize(x,y)
        size2 = self.wSizer1.GetSize()
        size = self.wSizer1.GetSize()
        size_t = self.m_staticText1.GetSize()
        size_m = self.mode_choice.GetSize()
        header_y = 0
        header_y += self.wSizer3.GetSize()[1]
        header_y += self.wSizer3.GetSize()[1]
        x = size[0]
        y = size[1]  - size_t[1] - size_m[1]
        if y*16/9 > x:
            self.ratio = x/16
        else:
            self.ratio = y/9
        if time.time() - self.last_runtime > 0.01:
            self.last_runtime = time.time()
            self.wxImage_re = scale_bitmap(self.wxImage, int(16*self.ratio), int(9*self.ratio))
            self.tracking_map.SetBitmap(self.wxImage_re)


            self.SetSizer( self.wSizer1 )
            self.Layout()

    def map_plot_thread(self, time, TLE):
        self.thread_map = threading.Thread(target = self.map_plot, args=(time,TLE))
        self.thread_map.start()

    def map_plot(self, time, TLE):
        start_mode = self.mode_choice.GetSelection()
        m = Basemap(projection='mill', area_thresh=1000.0, llcrnrlat=south, urcrnrlat=north, llcrnrlon=west, urcrnrlon=east)
        #m.shadedrelief()
        im = Image.open(resource_path('default_map.png'))
        m.imshow(im, alpha=1)
        m.nightshade(time+datetime.timedelta(hours=10))
        #m.drawcoastlines()
        # 一分ごとの人工衛星の位置をプロット
        time_list = []
        for t in range(-10,100):
            time_list.append(time+datetime.timedelta(minutes=t))
        for t in time_list:
            satellite = ephem.readtle(TLE[0], TLE[1], TLE[2])
            satellite.compute(t)
            latitude = satellite.sublat / ephem.degree
            longitude = satellite.sublong / ephem.degree -150
            if longitude<-180:
                longitude+=360
            x1,y1 = m(longitude, latitude)
            m.plot(x1, y1, marker=".", markersize=1, c='blue')
        if self.mode_choice.GetSelection() != start_mode:
            if self.mode_choice.GetSelection():
                time = datetime.datetime.utcnow()
            else:
                time = self.get_time()
            self.map_plot(time, TLE)
            return 0
        satellite = ephem.readtle(TLE[0], TLE[1], TLE[2])
        satellite.compute(time)
        latitude = satellite.sublat / ephem.degree
        longitude = satellite.sublong / ephem.degree -150
        if longitude<-180:
            longitude+=360
        earth_radius = 6371000.
        sat_loc = (latitude, longitude)
        # define the position of the satellite
        orbit = Orbital(TLE[0], line1=TLE[1], line2=TLE[2])
        lon_dum, lat_dum, altitude = orbit.get_lonlatalt(time)
        print(altitude)
        position = [altitude*1000, latitude, longitude]

        radius = math.degrees(math.acos(earth_radius / (earth_radius + position[0])))
        print(longitude)
        x1,y1 = m(longitude, latitude)
        m.plot(x1, y1, marker="*", markersize=5, c='red')
        if longitude<-90:
            diff = longitude - (-180)
            m = Basemap(projection='mill', area_thresh=1000.0, llcrnrlat=south, urcrnrlat=north, llcrnrlon=0, urcrnrlon=360)
            m.tissot(diff, latitude, radius, 100, facecolor='white', alpha=0.5)
            m = Basemap(projection='mill', area_thresh=1000.0, llcrnrlat=south, urcrnrlat=north, llcrnrlon=-360, urcrnrlon=0)
            m.tissot(diff, latitude, radius, 100, facecolor='white', alpha=0.5)
        elif longitude > 90:
            diff = longitude - 180
            m = Basemap(projection='mill', area_thresh=1000.0, llcrnrlat=south, urcrnrlat=north, llcrnrlon=0, urcrnrlon=360)
            m.tissot(diff, latitude, radius, 100, facecolor='white', alpha=0.5)
            m = Basemap(projection='mill', area_thresh=1000.0, llcrnrlat=south, urcrnrlat=north, llcrnrlon=-360, urcrnrlon=0)
            m.tissot(diff, latitude, radius, 100, facecolor='white', alpha=0.5)
        else:
            m.tissot(longitude, latitude, radius, 100, facecolor='white', alpha=0.5)
        plt.gca().spines['right'].set_visible(False)
        plt.gca().spines['top'].set_visible(False)
        plt.gca().spines['left'].set_visible(False)
        plt.gca().spines['bottom'].set_visible(False)
        plt.subplots_adjust(left=0, right=1, bottom=0, top=1)
        buf = io.BytesIO()
        plt.savefig(buf,format='png', dpi = 300, transparent = False, bbox_inches = 'tight', pad_inches = 0)
        #plt.savefig('map.png',format='png', dpi = 600, transparent = False, bbox_inches = 'tight', pad_inches = 0)
        plt.close()
        buf.seek(0)
        self.output_map = buf
        if self.mode_choice.GetSelection() != start_mode:
            if self.mode_choice.GetSelection():
                time = datetime.datetime.utcnow()
            else:
                time = self.get_time()
            self.map_plot(time, TLE)
            return 0

        self.Image = wx.Image(buf, wx.BITMAP_TYPE_ANY)
        self.wxImage = wx.Bitmap(self.Image) #画像リサイズ対象=wx.Bitmap
        self.wxImage_re = scale_bitmap(self.wxImage, int(16*self.ratio), int(9*self.ratio))
        self.tracking_map.SetBitmap(self.wxImage_re)
