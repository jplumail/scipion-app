import sys

from pyworkflow.manager import Manager
from pyworkflow.project import *
from pyworkflow.em import *
from pyworkflow.em.packages.xmipp3 import *

projName = sys.argv[1]

manager = Manager()
proj = manager.createProject(projName) # Now it will be loaded if exists

from tests.tester import *

#prot = MyProtocol(name="test3", n=2, workingDir=proj.getPath('Runs', 'T3'))
#proj.launchProtocol(prot)

prot2 = ProtImportMicrographs(workingDir=proj.getPath('Runs', 'Import1'), 
                              pattern="/home/laura/Scipion_Projects/InputData/*.mrc", sampling=1, voltage=200)
proj.launchProtocol(prot2)

l = proj.mapper.select(classname='SetOfMicrographs')
#l = proj.mapper.getAll()

for p in l:
    p.printAll()

prot3 = XmippProtPreprocessMicrographs(workingDir=proj.getPath('Runs', 'PreprocessDown'), inputMicrographs=l[0], 
                                       doDownsample=True, downFactor=2)


proj.launchProtocol(prot3)

prot4 = XmippProtPreprocessMicrographs(workingDir=proj.getPath('Runs', 'PreprocessCrop'), inputMicrographs=l[0], 
                                       doCrop=True, cropPixels=10)


proj.launchProtocol(prot4)

prot5 = XmippProtPreprocessMicrographs(workingDir=proj.getPath('Runs', 'PreprocessLog'), inputMicrographs=l[0], 
                                       doLog=True)


proj.launchProtocol(prot5)

prot6 = XmippProtPreprocessMicrographs(workingDir=proj.getPath('Runs', 'PreprocessRemove'), inputMicrographs=l[0], 
                                       doRemoveBadPix=True)


proj.launchProtocol(prot6)

l = proj.mapper.select(classname='SetOfMicrographs')
#l = proj.mapper.getAll()

for p in l:
    p.printAll()
