# **************************************************************************
# *
# * Authors:     J.M. De la Rosa Trevin (jmdelarosa@cnb.csic.es)
# *
# * Unidad de  Bioinformatica of Centro Nacional de Biotecnologia , CSIC
# *
# * This program is free software; you can redistribute it and/or modify
# * it under the terms of the GNU General Public License as published by
# * the Free Software Foundation; either version 2 of the License, or
# * (at your option) any later version.
# *
# * This program is distributed in the hope that it will be useful,
# * but WITHOUT ANY WARRANTY; without even the implied warranty of
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# * GNU General Public License for more details.
# *
# * You should have received a copy of the GNU General Public License
# * along with this program; if not, write to the Free Software
# * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
# * 02111-1307  USA
# *
# *  All comments concerning this program package may be sent to the
# *  e-mail address 'jmdelarosa@cnb.csic.es'
# *
# **************************************************************************
"""
This module contains all configuration
settings and gui general functions 
"""
import os, sys
import Tkinter as tk
import tkFont

from pyworkflow.object import OrderedObject
from pyworkflow.utils.path import findResource

"""
Some GUI CONFIGURATION parameters
"""
cfgFontName = "Verdana"
cfgFontSize = 10  

#TextColor
cfgCitationTextColor = "dark olive green"
cfgLabelTextColor = "black"
cfgSectionTextColor = "blue4"
#Background Color
cfgBgColor = "light grey"
cfgLabelBgColor = "white"
cfgHighlightBgColor = cfgBgColor
cfgButtonFgColor = "white"
cfgButtonActiveFgColor = "white"
cfgButtonBgColor = "#7D0709"
cfgButtonActiveBgColor = "#A60C0C"
cfgEntryBgColor = "lemon chiffon" 
cfgExpertLabelBgColor = "light salmon"
cfgSectionBgColor = cfgButtonBgColor
#Color
cfgListSelectColor = "DeepSkyBlue4"
cfgBooleanSelectColor = "white"
cfgButtonSelectColor = "DeepSkyBlue2"
#Dimensions limits
cfgMaxHeight = 650
cfgMaxWidth = 800
cfgMaxFontSize = 14
cfgMinFontSize = 6
cfgWrapLenght = cfgMaxWidth - 50


class Config(OrderedObject):
    pass

def saveConfig(filename):
    from pyworkflow.mapper import SqliteMapper
    from pyworkflow.object import String, Integer
    
    mapper = SqliteMapper(filename)
    o = Config()
    for k, v in globals().iteritems():
        if k.startswith('cfg'):
            if type(v) is str:
                value = String(v)
            else: 
                value = Integer(v)
            setattr(o, k, value)
    mapper.insert(o)
    mapper.commit()
            
   
"""
FONT related variables and functions 
"""
def setFont(fontKey, update=False, **opts):
    """Register a tkFont and store it in a globals of this module
    this method should be called only after a tk.Tk() windows has been
    created."""
    if not hasFont(fontKey) or update:
        globals()[fontKey] = tkFont.Font(**opts)
    
def hasFont(fontKey):
    return fontKey in globals()

def aliasFont(fontAlias, fontKey):
    """Set a fontAlias as another alias name of fontKey"""
    g = globals()
    g[fontAlias] = g[fontKey] 
    
def setCommonFonts():
    """Set some predifined common fonts.
    Same conditions of setFont applies here."""
    setFont('fontNormal', family=cfgFontName, size=cfgFontSize)
    aliasFont('fontButton', 'fontNormal')
    setFont('fontBold', family=cfgFontName, size=cfgFontSize, weight='bold')
    setFont('fontLabel', family=cfgFontName, size=cfgFontSize+1, weight='bold')

def changeFontSizeByDeltha(font, deltha, minSize=-999, maxSize=999):
    size = font['size']
    new_size = size + deltha
    if new_size >= minSize and new_size <= maxSize:
        font.configure(size=new_size)
            
def changeFontSize(font, event, minSize=-999, maxSize=999):
    deltha = 2
    if event.char == '-':
        deltha = -2
    changeFontSizeByDeltha(font, deltha, minSize, maxSize)

"""
IMAGE related variables and functions 
"""

def getImage(imageName, imgDict=None, tk=True):
    """ Search for the image in the RESOURCES path list. """
    if imageName is None:
        return None
    from pyworkflow.utils.path import findResource
    if imgDict is not None and imageName in imgDict:
        return imgDict[imageName]
    imagePath = findResource(imageName)
    image = None
    if imagePath:
        from PIL import Image, ImageTk
        image = Image.open(imagePath)
        if tk:
            image = ImageTk.PhotoImage(image)
        if imgDict is not None:
            imgDict[imageName] = image
    return image

def getPILImage(imageXmipp, dim=None):
    from PIL import Image
    image = Image.fromarray(imageXmipp.getData())
    img = image.convert('RGB')
    if dim:
        size = int(dim), int(dim)
        img.thumbnail(size, Image.ANTIALIAS)
    return img

"""
Windows geometry utilities
"""
def getGeometry(win):
    ''' Return the geometry information of the windows
    It will be a tuple (width, height, x, y)
    '''
    return win.winfo_reqwidth(), win.winfo_reqheight(), win.winfo_x(), win.winfo_y()

def centerWindows(root, dim=None, refWindows=None):
    """Center a windows in the middle of the screen 
    or in the middle of other windows(refWindows param)"""
    root.update_idletasks()
    if dim is None:
        gw, gh, gx, gy = getGeometry(root)
    else:
        gw, gh = dim
    if refWindows:
        rw, rh, rx, ry = getGeometry(refWindows)
        x = rx + (rw - gw) / 2
        y = ry + (rh - gh) / 2 
    else:
        w = root.winfo_screenwidth()
        h = root.winfo_screenheight()
        x = (w - gw) / 2
        y = (h - gh) / 2
        
    root.geometry("%dx%d+%d+%d" % (gw, gh, x, y))
    
def configureWeigths(widget):
    """This function is a shortcut to a common
    used pair of calls: rowconfigure and columnconfigure
    for making childs widgets take the space available"""
    widget.columnconfigure(0, weight=1)
    widget.rowconfigure(0, weight=1)
    
    
class Window():
    """Class to manage a Tk windows.
    It will encapsulates some basic creation and 
    setup functions. """
    
    def __init__(self, title, masterWindow=None, weight=True, minsize=(500, 300),
                 icon=None):
        """Create a Tk window.
        title: string to use as title for the windows.
        master: if not provided, the windows create will be the principal one
        weight: if true, the first col and row will be configured with weight=1
        minsize: a minimum size for height and width
        icon: if not None, set the windows icon
        """
        if masterWindow is None:
            Window._root = self
            self.root = tk.Tk()
            self._images = {}
        else:
            self.root = tk.Toplevel(masterWindow.root)
            self._images = masterWindow._images
            
        self.root.withdraw()
        self.root.title(title)
        
        if weight:
            configureWeigths(self.root)
        if not minsize is None:
            self.root.minsize(minsize[0], minsize[1])
        if not icon is None:
            path = findResource(icon)          
            abspath = os.path.abspath(path)
            self.root.iconbitmap("@" + abspath)
            
        self.root.protocol("WM_DELETE_WINDOW", self._onClosing)
        self.master = masterWindow
        setCommonFonts()
        
    def desiredDimensions(self):
        """This method should be used by subclasses
        to calculate desired dimensions"""
        return None
    
    def show(self, center=True):
        """This function will enter in the Tk mainloop"""
        if center:
            if self.master is None:
                refw = None
            else:
                refw = self.master.root
            centerWindows(self.root, dim=self.desiredDimensions(),
                          refWindows=refw)
        self.root.deiconify()
        self.root.focus_set()
        self.root.mainloop()
        
    def close(self):
        self.root.destroy()
        
    def _onClosing(self):
        """Do some cleanning before closing"""
        if self.master is None: 
            pass
        else:
            self.master.root.focus_set()
        self.close()
        
    def getImage(self, imgName):
        return getImage(imgName, self._images)
    
    def createMainMenu(self, menuConfig):
        """Create Main menu from a given configuration"""
        menu = tk.Menu(self.root)
        self._addMenuChilds(menu, menuConfig)
        self.root.config(menu=menu)
            
    def _addMenuChilds(self, menu, menuConfig):
        """Helper function for creating main menu"""
        for sub in menuConfig:
            if len(sub):
                submenu = tk.Menu(self.root, tearoff=0)
                menu.add_cascade(label=sub.text.get(), menu=submenu)
                self._addMenuChilds(submenu, sub)
            else:
                menu.add_command(label=sub.text.get(), compound=tk.LEFT,
                                 image=self.getImage(sub.icon.get()))
