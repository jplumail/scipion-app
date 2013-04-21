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
This modules contains basic hierarchy
for EM data objects like: Image, SetOfImage and others
"""

from pyworkflow.object import *
from pyworkflow.mapper.sqlite import SqliteMapper


class EMObject(Object):
    """Base object for all EM classes"""
    def __init__(self, **args):
        Object.__init__(self, **args)
        
    def __str__(self):
        return str(self.get())


class Microscope(EMObject):
    """Microscope information"""
    def __init__(self, **args):
        EMObject.__init__(self, **args)
        self.magnification = Float(60000)
        self.voltage = Float(300)
        self.sphericalAberration = Float(1.2)
        

class Image(EMObject):
    """Represents an EM Image object"""
    def __init__(self, filename=None, **args):
        # Use the object value to store the filename
        args['value'] = filename
        EMObject.__init__(self, **args)
        self.samplingRate = Float()
        
    def getFormat(self):
        pass
    
    def getDataType(self):
        pass
        
    def getSamplingRate(self):
        pass
    
    def getDim(self):
        """Return image dimensions as tuple: (Ydim, Xdim)"""
        pass
    
    def getFileName(self):
        return self._objValue
    
    def setFileName(self, newFileName):
        self._objValue = newFileName
        
        
class Micrograph(Image):
    """Represents an EM Image object"""
    def __init__(self, filename=None, **args):
        Image.__init__(self, filename, **args)
        self.ctfModel = None
        
    def getMicroscope(self):
        pass
    
    def hasCTF(self):
        return self.ctfModel is not None


class TiltedPair(CsvList):
    """Store the id of the untilted and tilted micrographs"""
    def __init__(self, **args):
        CsvList.__init__(self, int, **args)
        

class SetOfImages(EMObject):
    """Represents a set of Images"""
    def __init__(self, filename=None, **args):
        # Use the object value to store the filename
        args['value'] = filename
        EMObject.__init__(self, **args)
        self.samplingRate = Float()
        self.scannedPixelSize = Float()
        
    def getSize(self):
        """Return the number of images"""
        pass
    
    def getFileName(self):
        return self._objValue
    
    def setFileName(self, newFileName):
        self._objValue = newFileName
        
        
    def append(self, image):
        """Add an image to the set"""
        pass
    
    
class SetOfMicrographs(SetOfImages):
    """Represents a set of Micrographs"""
    def __init__(self, filename=None, **args):
        SetOfImages.__init__(self, filename, **args)
        self._ctf = Boolean(args.get('ctf', False))
        self._tiltPairs = Boolean(args.get('tiltPairs', False))
        self.microscope = Microscope()
        self._micList = List(objName='Micrographs', objDoStore=False) # The micrograph list will be stored seperately
        self._pairList = List(objName='TiltPairs', objDoStore=False) 
        
    def getMicroscope(self, index=0):
        return self.microscope
    
    def hasTiltPairs(self):
        return self._tiltPairs.get()
    
    def hasCTF(self):
        """Return True if the SetOfMicrographs has associated a CTF model"""
        return self._ctf.get()
    
    def append(self, micrograph):
        """Add a micrograph to the set"""
        micrograph.samplingRate.set(self.samplingRate.get())
        self._micList.append(micrograph)        
    
    def __loadFiles(self):
        """Read files from text files"""
        mapper = SqliteMapper(self.getFileName(), globals())
        self._micList = mapper.selectFirst()
        
    def __iter__(self):
        """Iterate over the set of micrographs in a .txt file"""
        self.__loadFiles()
        for m in self._micList:
            yield m
        
    def iterPairs(self):
        """Iterate over the tilt pairs if is the case"""
        #FIXME, we need to store the real relation 
        # between micrographs
        # TODO: Validate number of micrographs is even for Tilt Pairs
        n = len(self._micList) / 2
        for i in range(n):
            mU = Micrograph()
            mU.setFileName(self._micList[2*i])
            mT = Micrograph()
            mT.setFileName(self._micList[2*i+1])
            yield (mU, mT)
        
    def write(self):
        """This method will be used to persist in a file the
        list of micrographs path contained in this Set
        path: output file path
        micrographs: list with the micrographs path to be stored
        """
        mapper = SqliteMapper(self.getFileName(), globals())
        mapper.insert(self._micList)
        for mic in self._micList:
            p = TiltedPair()
            p += [mic.getId(), 1]
            self._pairList.append(p)
        mapper.insert(self._pairList)
        mapper.commit()
        
    def copyInfo(self, other):
        """ Copy basic information (voltage, spherical aberration and sampling rate)
        from other set of micrographs to current one"""
        self.microscope.voltage.set(other.microscope.voltage.get())
        self.microscope.sphericalAberration.set(other.microscope.sphericalAberration.get())
        self.samplingRate.set(other.samplingRate.get())
        self.scannedPixelSize.set(other.scannedPixelSize.get())
        self._tiltPairs.set(other._tiltPairs.get())
        self._ctf.set(other._ctf.get())
    

class Coordinate(EMObject):
    """This class holds the (x,y) position and other information
    associated with a coordinate"""
    POS_CENTER = 0
    POS_TOPLEFT = 1
    
    def __init__(self, **args):
        self._micrograph = None
    
    def getPosition(self, mode=POS_CENTER):
        """Return the position of the coordinate.
        mode: select if the position is the center of the box
          or in the top left corner."""
        pass
    
    def getMicrograph(self):
        """Return the micrograph object to which
        this coordinate is associated"""
        return self._micrograph
    
    def setMicrograph(self, micrograph):
        """Set the micrograph to which this coordinate belongs"""
        self._micrograph = micrograph
    
    def getPair(self):
        """It should return the paired coordinate associate to self.
        If self is an untilted coordinate, getPaired will return the 
        tilted one and viceversa"""
        pass 
    
    
class SetOfCoordinates(EMObject):
    """Encapsulate the logic of a set of particles coordinates.
    Each coordinate has a (x,y) position and is related to a Micrograph
    The SetOfCoordinates can also have information about TiltPairs"""
    
    def __init__(self, **args):
        EMObject.__init__(self, **args)
        self._micrographsPointer = Pointer()
        self.boxSize = Integer()
    
    def getBoxSize(self):
        """Return the box size of the future particles.
        This can be None, since when the POS_CENTER mode is used,
        the box size is only relevant when extraction"""
        return self.boxSize.get()
    
    
    def setBoxSize(self, boxSize):
        """Set the box size of the future particles.
        This can be None, since when the POS_CENTER mode is used,
        the box size is only relevant when extraction"""
        self.boxSize.set(boxSize)
    
    def iterCoordinates(self):
        """Itearates over the whole set of coordinates.
        If the SetOfMicrographs has tilted pairs, the coordinates
        should have the information related to its paired coordinate."""
        pass
    
    def hasTiltPairs(self):
        """Returns True if the SetOfMicrographs has tilted pairs"""
        return self.getMicrographs().hasTiltPairs()
    
    def getMicrographs(self):
        """Returns the SetOfMicrographs associated with 
        this SetOfCoordinates"""
        return self._micrographsPointer.get()
    
    def setMicrographs(self, micrographs):
        """ Set the SetOfMicrograph associates with 
        this set of coordinates """
        self._micrographsPointer.set(micrographs)
        
    def getFileName(self):
        """ Get the metadata file with all all coordinates files for 
        this setOfCoordinates """
        return self._objValue
    
    def setFileName(self, newFileName):
        """ Set the metadata file with all all coordinates files for 
        this setOfCoordinates """
        self._objValue = newFileName
                
    
class CTFModel(EMObject):
    """Represents a generic CTF model"""
#TODO: See how this can be generic (no pointing to Xmipp labels
#    ctfParams = {
#                 "ctfSamplingRate":MDL_CTF_SAMPLING_RATE,
#                 "ctfVoltage":MDL_CTF_VOLTAGE,
#                 "ctfDefocusU":MDL_CTF_DEFOCUSU,
#                 "ctfDefocusV":MDL_CTF_DEFOCUSV,
#                 "ctfDefocusAngle":MDL_CTF_DEFOCUS_ANGLE,
#                 "ctfSphericalAberration":MDL_CTF_CS,
#                 "ctfQ0":MDL_CTF_Q0,
#                 "ctfK":MDL_CTF_K
#                }
    def __init__(self, **args):
        EMObject.__init__(self, **args)
        
        self.samplingRate = Float()
        self.defocusU = Float()
        self.defocusV = Float()
        self.defocusAngle = Float()
