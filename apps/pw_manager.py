#!/usr/bin/env python

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
from inspect import isclass
from pyworkflow.utils.utils import prettyDate
"""
Main project window application
"""
import os
from os.path import join, exists
import sys
        
import Tkinter as tk
import ttk
import tkFont

import pyworkflow as pw
from pyworkflow.object import *
from pyworkflow.manager import Manager
from pyworkflow.mapper import SqliteMapper, XmlMapper
from pyworkflow.protocol import *
from pyworkflow.protocol.params import *
from config import *
from pyworkflow.em import *
import pyworkflow.gui as gui
from pyworkflow.gui.widgets import Button
from pyworkflow.gui.text import TaggedText
from pyworkflow.gui.dialog import askString, askYesNo, showError


def loadSubclasses():
    """This function will try to find
    all sub-classes of className located in
    the pyworkflow/protocol/packages/* path and made them
    available in the menu"""
    path = join(pw.HOME, 'em', 'packages')
    sys.path.append(path)
    folders = os.listdir(path)
    #print "path: ", path
    subclasses = {}
    for f in folders:
        if exists(join(path, f, '__init__.py')):
            m = __import__(f)
            for k, v in m.__dict__.iteritems():
                if isclass(v) and issubclass(v, Protocol):
                    subclasses[k] = v
    return subclasses
    
subclasses =  loadSubclasses()
    
def populateTree(tree, prefix, obj, level=0):
    text = obj.text.get()
    if text:
        key = '%s.%s' % (prefix, text)
        img = obj.icon.get()
        if img is None:
            img = ''
            pass
        else:
            img = self.getImage(img)
        item = tree.insert(prefix, 'end', key, text=text, image=img)
        
        if level < 3:
            tree.item(item, open=True)
        if not obj.isEmpty() and obj.action.hasValue():
            prot = globals().get(obj.action.get(), None)
            if not prot is None:
                tree.item(item, image=self.getImage('step.gif'))
                for k, v in subclasses.iteritems():
                    if not v is prot and issubclass(v, prot):
                        tree.insert(item, 'end', item+k, text=k, image=self.getImage('python_file.gif'))
                        
            else:
                raise Exception("Class '%s' not found" % obj.action.get())
    else:
        key = prefix
    
    for sub in obj:
        populateTree(tree, key, sub, level+1)
    
def getMapper(fn, classesDict):
    """Select what Mapper to use depending on
    the filename extension"""
    if fn.endswith('.xml'):
        return XmlMapper(fn, classesDict)
    elif fn.endswith('.sqlite'):
        return SqliteMapper(fn, classesDict)
    return None


    
def loadConfig(config, name):
    c = getattr(config, name) 
    fn = getConfigPath(c.get())
    if not os.path.exists(fn):
        raise Exception('loadMenuConfig: menu file "%s" not found' % fn )
    mapper = ConfigMapper(getConfigPath(fn), globals())
    menuConfig = mapper.getConfig()
    return menuConfig


class ManagerWindow(gui.Window):
    """Windows to manage projects"""
    def __init__(self, **args):
        gui.Window.__init__(self, "Projets", minsize=(600, 350), icon='scipion_bn.xbm', **args)
        # Load global configuration
        mapper = ConfigMapper(getConfigPath('configuration.xml'), globals())
        config = mapper.getConfig()
        self.projNameFont = tkFont.Font(size=12, family='verdana', weight='bold')
        self.projDateFont = tkFont.Font(size=8, family='verdana')
        self.projDelFont = tkFont.Font(size=8, family='verdana', weight='bold')
        self.manager = Manager()
        parent = self.root

        menuConfig = loadConfig(config, 'menu')
        self.createMainMenu(menuConfig)
        
        f = tk.Frame(parent, bg='white')
        f.columnconfigure(0, minsize=200)
        f.columnconfigure(1, minsize=400)
        f.rowconfigure(1, minsize=250)
        # Add logo
        logo = self.getImage('scipion_logo.gif')
        label = tk.Label(f, image=logo, borderwidth=0)
        label.grid(row=0, column=0, sticky='nw')
        # Add create project button
        #font = tkFont.Font(size=12, family='verdana')#, weight='bold')
        btn = Button(f, text='Create Project', command=self.createNewProject)
        btn.grid(row=1, column=0, sticky='new', padx=10, pady=10)
        
        lf = ttk.Labelframe(f, text='Current Projects')
        lf.grid(row=0, column=1, sticky='news', padx=10, pady=10, rowspan=2)
        text = TaggedText(lf, width=40, height=15, bd=0)
        text.grid(row=0, column=0, sticky='news')
        text.config(state=tk.DISABLED)
        gui.configureWeigths(lf)
        
        self.createProjectList(text)
        self.text = text
        f.rowconfigure(0, weight=1)
        f.rowconfigure(1, weight=1)
        f.columnconfigure(1, weight=1)
        f.grid(row=0, column=0, sticky='news')  

    def createProjectList(self, text):
        """Load the list of projects"""
        r = 0
        text.clear()
        parent = tk.Frame(text)    
        parent.columnconfigure(0, weight=1)
        
        for p in self.manager.listProjects():
            frame = self.createProjectLabel(parent, p)
            frame.grid(row=r, column=0, padx=10, pady=5, sticky='new')
            r += 1
        text.window_create(tk.INSERT, window=parent)
        
    def createProjectLabel(self, parent, projInfo):
        frame = tk.Frame(parent)
        label = tk.Label(frame, text=projInfo.projName, anchor='nw', 
                         justify=tk.LEFT, font=self.projNameFont, cursor='hand1')
        label.grid(row=0, column=0, padx=2, pady=2, sticky='nw')
        label.bind('<Button-1>', lambda e: self.openProject(projInfo.projName))
        dateLabel = tk.Label(frame, text='   Modified: ' + prettyDate(projInfo.mTime), font=self.projDateFont)
        dateLabel.grid(row=1, column=0)
        delLabel = tk.Label(frame, text='Delete project', font=self.projDelFont, cursor='hand1')
        delLabel.grid(row=1, column=1, padx=10)
        delLabel.bind('<Button-1>', lambda e: self.deleteProject(projInfo.projName))
        return frame
        
    def createNewProject(self):
        projName =  askString("Enter the project name", "Project Name:", self.root, 30)
        if not projName is None:
            self.manager.createProject(projName)
            self.createProjectList(self.text)
    
    def openProject(self, projName):
        projPath = self.manager.getProjectPath(projName)
        from pw_project import ProjectWindow
        projWindow = ProjectWindow(projPath, self)
        projWindow.show()
            
    def deleteProject(self, projName):
        if askYesNo("Confirm Project deletion", 
                    "Are you sure to <DELETE> project <%s>\n and all its <DATA>?" % projName, self.root):
            self.manager.deleteProject(projName)
            self.createProjectList(self.text)

if __name__ == '__main__':
    ManagerWindow().show()
    
