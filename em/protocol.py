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
Protocols related to EM
"""
import os
import shutil
from pyworkflow.object import String, Float
from pyworkflow.protocol import Protocol
from pyworkflow.protocol.params import *
from pyworkflow.em import SetOfMicrographs


class DefImportMicrographs(Form):
    """Create the definition of parameters for
    the ImportMicrographs protocol"""
    def __init__(self):
        Form.__init__(self)
    
        self.addSection(label='Input')
        self.addParam('pattern', StringParam, label="Pattern")
        self.addParam('tiltPairs', BooleanParam, default=False, important=True,
                   label='Are micrographs tilt pairs?')
        
        self.addSection(label='Microscope description')
        self.addParam('voltage', FloatParam, default=200,
                   label='Microscope voltage (in kV)')
        self.addParam('sphericalAberration', FloatParam, default=2.26,
                   label='Spherical aberration (in mm)')
        self.addParam('samplingRateMode', EnumParam, default=0,
                   label='Sampling rate mode',
                   choices=['From image', 'From scanner'])
        self.addParam('samplingRate', FloatParam,
                   label='Sampling rate (A/px)', condition='samplingRateMode==0')
        self.addParam('magnification', IntParam, default=60000,
                   label='Magnification rate', condition='samplingRateMode==1')
        self.addParam('ScannedPixelSize', FloatParam,
                   label='Scanned pixel size', condition='samplingRateMode==1')
        


class ProtImportMicrographs(Protocol):
    """Protocol to import a set of micrographs in the project"""
    _definition = DefImportMicrographs()
    
    def __init__(self, **args):
        Protocol.__init__(self, **args)         
        
    def _defineSteps(self):
        self._insertFunctionStep('importMicrographs', self.pattern.get(), self.tiltPairs.get(),
                                self.voltage.get(), self.sphericalAberration.get(),
                                self.samplingRate.get())
        
    def importMicrographs(self, pattern, tiltPairs, voltage, sphericalAberration, samplingRate):
        """Copy micrographs matching the filename pattern
        Register other parameters"""
        from glob import glob
        files = glob(pattern)
        if len(files) == 0:
            raise Exception('importMicrographs:There is not files matching pattern')
        path = self._getPath('micrographs.txt')
        micSet = SetOfMicrographs(value=path)
        micSet.microscope.voltage.set(voltage)
        micSet.microscope.sphericalAberration.set(sphericalAberration)
        micSet.samplingRate.set(samplingRate)
        micSet.tiltPairs.set(tiltPairs)
        for f in files:
            dst = self._getPath(os.path.basename(f))            
            shutil.copyfile(f, dst)
            micSet.append(dst)
        
        micSet.writeToFile(path)
        self._defineOutputs(micrograph=micSet)
        outFiles = micSet._files + [path]
        
        return outFiles
        

class ProtCTFMicrographs(Protocol):
    pass


class ProtPreprocessMicrographs(Protocol):
    pass


class ProtParticlePicking(Protocol):
    pass


class ProtAlign(Protocol):
    pass


class ProtClassify(Protocol):
    pass


class ProtAlignClassify(Protocol):
    pass
