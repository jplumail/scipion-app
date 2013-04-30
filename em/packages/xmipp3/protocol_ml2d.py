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
This sub-package contains wrapper around ML2D Xmipp program
"""


from pyworkflow.em import *  
from pyworkflow.utils import *  
import xmipp
from data import *


class XmippDefML2D(Form):
    """Create the definition of parameters for
    the XmippProtML2D protocol"""
    def __init__(self):
        Form.__init__(self)
    
        self.addSection(label='Input')
        self.addParam('inputImages', PointerParam, label="Input images", important=True, 
                      pointerClass='SetOfImages',
                      help='Select the input images from the project.'
                           'It should be a SetOfImages class')        
        self.addParam('doGenerateReferences', BooleanParam, default=True,
                      label='Generate references (or classes) ?', 
                      help='If you set to <No>, you should provide references images'
                           'If <Yes>, the default generation is done by averaging'
                           'subsets of the input images.')
        self.addParam('numberOfReferences', IntParam, default=3, condition='doGenerateReferences',
                      label='Number of references:',
                      help='Number of references to be generated.')
        self.addParam('referenceImages', PointerParam, condition='not doGenerateReferences',
                      label="Reference image(s)", 
                      pointerClass='SetOfImages',
                      help='Image(s) that will serve as class references')
        
        self.addSection(label='MLF-specific parameters', questionParam='doMlf')        
        self.addParam('doMlf', BooleanParam, default=False,
                      label='Use MLF2D instead of ML2D')
        self.addParam('doCorrectAmplitudes', BooleanParam, default=True,
                      label='Use CTF-amplitude correction inside MLF?',
                      help='If set to <Yes>, the input images file should contains'
                           'the CTF information for each image.'
                           'If set to <No>, provide the images pixel size in Angstrom.')
        self.addParam('areImagesPhaseFlipped', BooleanParam, default=True,
                      label='Are the images CTF phase flipped?',
                      help='You can run MLF with or without having phase flipped the images.')        
        self.addParam('highResLimit', IntParam, default=20,
                      label='High-resolution limit (Angstroms)',
                      help='No frequencies higher than this limit will be taken into account.'
                           'If zero is given, no limit is imposed.')
        
        self.addSection(label='Advanced parameters', questionParam='showAdvanced')        
        self.addParam('showAdvanced', BooleanParam, default=False,
                      label='Show advanced parameters')
        self.addParam('doMirror', BooleanParam, default=True,
                      label='Also include mirror in the alignment?',
                      help='Including the mirror transformation is useful if your particles'
                           'have a handedness and may fall either face-up or face-down on the grid.'
                           )
        self.addParam('doFast', BooleanParam, default=True, condition='not doMlf',
                      label='Use the fast version of this algorithm?',
                      help='For details see:\n'
                           '<Scheres et al., Bioinformatics, 21 (Suppl. 2), ii243-ii244>\n'
                           '[http://dx.doi.org/10.1093/bioinformatics/bti1140]'
                           )        
        self.addParam('doNorm', BooleanParam, default=False,
                      label='Refine the normalization for each image?',
                      help='This variant of the algorithm deals with normalization errors.'
                           'For more info see (and please cite):\n'
                           '<Scheres et. al. (2009) J. Struc. Biol., Vol 166, Issue 2, May 2009>\n'
                           '[http://dx.doi.org/10.1016/j.jsb.2009.02.007]'
                           )             
        # Advance or expert parameters
        self.addParam('maxIters', IntParam, default=100, expertLevel=LEVEL_ADVANCED,
                      label='Maximum number of iterations',
                      help='If the convergence has not been reached after this number'
                           'of iterations, the process will be stopped.')   
        self.addParam('psiStep', FloatParam, default=5.0, expertLevel=LEVEL_ADVANCED,
                      label='In-plane rotation sampling (degrees)',
                      help='In-plane rotation sampling interval (degrees).')          
        self.addParam('stdNoise', FloatParam, default=1.0, expertLevel=LEVEL_EXPERT,
                      label='Std for pixel noise',
                      help='Expected standard deviation for pixel noise.')               
        self.addParam('stdOffset', FloatParam, default=3.0, expertLevel=LEVEL_EXPERT,
                      label='Std for origin offset',
                      help='Expected standard deviation for origin offset (pixels).')   
        
        
class XmippProtML2D(ProtAlign, ProtClassify):
    """ Protocol to preprocess a set of micrographs in the project. """
    _definition = XmippDefML2D()
    _label = 'Xmipp ML2D'

    def getId(self):
        progId = "ml"
        if self.doMlf:
            progId += "f" 
        return progId   
         
    def _defineSteps(self):
        """ Define main steps of the ML2D protocol. """
        self._insertMLStep()
        
    def _convertImages(self, attrName):
        """ Convert from input images (pointed by attrName)
        to Xmipp set of images """
        inputImgs = getattr(self, attrName).get() # This should be the pointer to images
        fn = self._getTmpPath(attrName + '_images.xmd')
        xmippImgs = convertFromSetOfImages(inputImgs, fn)
        if xmippImgs != inputImgs:
            return [fn]
        
    def _insertMLStep(self):
        """ Mainly prepare the command line for call ml(f)2d program"""
        progId = self.getId()
        
        program = "xmipp_%s_align2d" % progId

        restart = False
        
        prefix = '%s2d' % progId
        oroot = self._getPath(prefix)
        params = ' -i %s --oroot %s' % (self.ImgMd, oroot)
        # Number of references will be ignored if -ref is passed as expert option
        if self.DoGenerateReferences:
            params += ' --nref %d' % self.NumberOfReferences
        else:
            params += ' --ref %s' % self.RefMd
        
        if (self.DoFast and not self.DoMlf):
            params += ' --fast'
        if (self.NumberOfThreads > 1  and not self.DoMlf):
            params += ' --thr %i' % self.NumberOfThreads
        if (self.DoMlf):
            if not self.DoCorrectAmplitudes:
                params += ' --no_ctf'                    
            if (not self.ImagesArePhaseFlipped):
                params += ' --not_phase_flipped'
            if (self.HighResLimit > 0):
                params += ' --limit_resolution 0 %f' % self.HighResLimit
            params += ' --sampling_rate %f' % self.SamplingRate
        if self.MaxIters != 100:
            params += " --iter %d" % self.MaxIters

        # Dictionary with boolean options and the cmd options
        booleanDict = {'doMirror': '--mirror', 'doNorm': '--norm'}
        #Add all boolean options if true
        for k, v in booleanDict.iteritems():
            if getattr(self, k):
                params += " " + v

        self.insertRunJobStep(program, params, 
                              [self.getFilename(k) for k in ['images', 'classes']])
                
    def createOutput(self, IOTable):
        
        mdOut = "Micrographs@" + self._getPath("micrographs.xmd")    
        micSet = XmippSetOfMicrographs(mdOut)
            
        # Add micrographs to the set           
        for i, v in IOTable.iteritems():
            micSet.append(XmippMicrograph(v))
            #TODO: Handle Tilted micrographs
#            if tiltPairs:
#                MD.setValue(xmipp.MDL_MICROGRAPH_TILTED,IOTable[fnMicrographTilted],objId)
#                MD.setValue(xmipp.MDL_MICROGRAPH_TILTED_ORIGINAL,fnMicrographTilted,objId)
        micSet.write()
        # Create the SetOfMicrographs object on the database
        micSet.copyInfo(self.inputMics)
        
        if self.doDownsample.get():
            micSet.samplingRate.set(self.inputMics.samplingRate.get()*self.downFactor.get())

        self._defineOutputs(outputMicrographs=micSet)
