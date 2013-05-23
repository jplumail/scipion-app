'''
Created on May 8, 2013

@author: laura
'''
import unittest, sys
from pyworkflow.manager import Manager
from pyworkflow.em import *
from pyworkflow.em.packages.xmipp3 import *
from PIL import Image

class TestXmippPreprocessMicrographs(unittest.TestCase):

    def setUp(self):
        
        # Create or load project
        projName = 'tests'
        manager = Manager()
        self.proj = manager.createProject(projName) # Now it will be loaded if exists

        # Parameters required by the import 
        samplingRate = 1.237
        voltage = 300
        pattern = "/home/laura/Scipion_Projects/SmallData/*.mrc"
                
        self.protImport = ProtImportMicrographs(pattern=pattern, samplingRate=samplingRate, voltage=voltage)
        self.proj.launchProtocol(self.protImport, wait=True)
        # check that input micrographs have been imported (a better way to do this?)
        self.assertFalse(self.protImport.outputMicrographs is None, 'imported micrographs failed')
        
    def testDownsampling(self):
        # test downsampling a set of micrographs
        downFactor = 2
        protDown = XmippProtPreprocessMicrographs(doDownsample=True, downFactor=downFactor)
        protDown.inputMicrographs.set(self.protImport.outputMicrographs)
        self.proj.launchProtocol(protDown, wait=True)
        
        # check that output micrographs have double sampling rate than input micrographs
        self.assertTrue(protDown.outputMicrographs.samplingRate.get() == self.protImport.outputMicrographs.samplingRate.get()*downFactor, "Micrographs uncorrectly downsampled")
        
    def testCrop(self):
        # test crop on a set of micrographs
        cropPixels = 100
        protCrop = XmippProtPreprocessMicrographs(doCrop=True, cropPixels=cropPixels)
        protCrop.inputMicrographs.set(self.protImport.outputMicrographs)
        self.proj.launchProtocol(protCrop, wait=True)
        
        # check that output micrographs have been correctly croped
        # FIXME: I DONT KNOW HOW TO CHECK IMAGE SIZE ON PIXELS
#        for i_mic in self.protImport.outputMicrographs:
#            i_fn = i_mic.getFileName()
#            #i_fs = os.path.getsize(i_fn)
#            i_fnp = self.get_num_pixels(i_fn)
#            for o_mic in protCrop.outputMicrographs:
#                o_fn = o_mic.getFileName()
#                if os.path.basename(o_fn) == os.path.basename(i_fn):
#                    #o_fs =  os.path.getsize(o_fn)
#                    o_fnp = self.get_num_pixels(o_fn)
#                    self.assertTrue((i_fnp - self.cropPixels) == o_fnp, "Micrograph uncorrectly cropped")
#                    break

            
        #self.assertTrue(protCrop.outputMicrographs.samplingRate.get() == self.protImport.outputMicrographs.samplingRate.get()*self.downFactor, "Micrographs uncorrectly downsampled")

    def testCTF(self):
        # test ctf a set of micrographs
        protCTF = XmippProtCTFMicrographs()
        protCTF.inputMicrographs.set(self.protImport.outputMicrographs)
        self.proj.launchProtocol(protCTF, wait=True)
        
        self.assertTrue(self.checkCTFModels(protCTF.outputMicrographs), 'CTF model does not exists')
        
    def checkCTFModels(self, micSet):
        # check that output micrographs have CTF model
        #TODO: implement a better way to check that CTFModel exists
        if micSet.hasCTF:
            return True
        
    def get_num_pixels(self, fn):
        width, height = Image.open(fn).size
        return width*height
    
class TestXmippExtractParticles(unittest.TestCase):

    def setUp(self):
        # Create or load project
        projName = 'tests'
        manager = Manager()
        self.proj = manager.createProject(projName) # Now it will be loaded if exists

        # Parameters required by the import 
        samplingRate = 1.237
        voltage = 300
        pattern = "/home/laura/Scipion_Projects/SmallData/*.mrc"
        
        # Parameters for the tests
        self.downFactor = 2
        self.cropPixels = 100
        
        # Perform the import micrographs
        self.protImport = ProtImportMicrographs(pattern=pattern, samplingRate=samplingRate, voltage=voltage)
        self.proj.launchProtocol(self.protImport, wait=True)
        # check that input micrographs have been imported (a better way to do this?)
        self.assertFalse(self.protImport.outputMicrographs is None, 'imported micrographs failed')
        
        # Perform the import coordinates

class TestXmippTiltedMicrographs(unittest.TestCase):        
    
    def setUp(self):
        # Create or load project
        projName = 'tests'
        manager = Manager()
        self.proj = manager.createProject(projName) # Now it will be loaded if exists

        # Parameters required by the import 
        samplingRate = 1
        voltage = 200
        pattern = "/home/laura/Scipion_Projects/TiltedData/*.mrc"        

        # Perform the import micrographs
        self.protImport = ProtImportMicrographs(pattern=pattern, samplingRate=samplingRate, 
                                                voltage=voltage, tiltPairs=True)
        self.proj.launchProtocol(self.protImport, wait=True)
        # check that input micrographs have been imported (a better way to do this?)
        self.assertFalse(self.protImport.outputMicrographs is None, 'imported micrographs failed')
        
    def testPreprocess(self):
        # test downsampling a set of micrographs
        downFactor = 2
        protDown = XmippProtPreprocessMicrographs(doDownsample=True, downFactor=downFactor)
        protDown.inputMicrographs.set(self.protImport.outputMicrographs)
        self.proj.launchProtocol(protDown, wait=True)
        
        # Assert true if output micrographs have tiltedPair relationship
        self.assertTrue(protDown.outputMicrographs.hasTiltPairs(), "Downsampled micrographs have tilted pairs")
        
        md = xmipp.MetaData()
        md.readBlock(protDown.outputMicrographs.getFileName(), 'TiltedPairs')
        
        # Assert true if output metadata has TiltedPairs block
        self.assertFalse(md.isEmpty(), 'TiltedPairs block is empty')

if __name__ == "__main__":
    #suite = unittest.TestLoader().loadTestsFromTestCase(TestXmippPreprocessMicrographs)
    suite = unittest.TestLoader().loadTestsFromName('test_protocols.TestXmippTiltedMicrographs.testPreprocess')
    unittest.TextTestRunner(verbosity=2).run(suite)