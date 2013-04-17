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
This sub-package will contains Xmipp3.0 specific protocols
"""


from pyworkflow.em import *  
from pyworkflow.em.packages.xmipp3.data import *
from xmipp import MetaData, MDL_MICROGRAPH

class XmippProtImportMicrographs(ProtImportMicrographs):
    pass


class XmippProtParticlePicking(ProtParticlePicking):
    pass

class XmippProtAlign(ProtAlign):
    pass


class XmippProtClassify(ProtClassify):
    pass


class XmippProtAlignClassify(ProtAlignClassify):
    pass

# Group of converter fuction 

def convertSetOfMicrographs(setOfMics, filename):
        """Method to convert from a general set of micrographs to Xmipp set of micrographs"""
        if type(setOfMics) is XmippSetOfMicrographs:
            return setOfMics
        md = MetaData()

        for mic in setOfMics:
            objId = md.addObject()
            md.setValue(MDL_MICROGRAPH, mic.getFileName(), objId)

        md.write(filename)
        
        micsOut = XmippSetOfMicrographs()
        micsOut.setFileName(filename)
        micsOut.copyInfo(setOfMics)
        
        return micsOut
