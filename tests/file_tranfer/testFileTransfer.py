"""
Created on Apr 9, 2013

@author: antonio
"""
import unittest
#from fileTransfer.fileTransfer import FileTransfer
from file_transfer.fileTransfer import *

class TestFileTransfer(unittest.TestCase):

    sourceFilesCase1 = None
    targetFilesCase1 = None
    gatewayHostsCase1 = None
    hostsPaswordsCase1 = None
    operationIdCase1 = None 
    numberTrialsCase1 = None
    fileTransfer = None
    forceOperationCase1 = None

    def setUp(self):
        self.fileTransferProces = FileTransfer()
        self.sourceFilesCase1 = {"1":"/home/antonio/Documents/Scipion/ScipionTestFiles/1212_00029.xmp", "2":"/home/antonio/Documents/Scipion/ScipionTestFiles/1212_00036.xmp"}
        self.targetFilesCase1 = {"1":["apoza@glassfishdev.cnb.csic.es:/home/apoza/testFileTransfer/testFile1.xmp"], "2":["apoza@glassfishdev.cnb.csic.es:/home/apoza/testFileTransfer/testFile2.xmp"]}
        self.hostsPaswordsCase1 = {"apoza@glassfishdev.cnb.csic.es":"BF6fYiFYiYD"}
        self.operationIdCase1 = 1 
        self.numberTrialsCase1 = 1
        self.forceOperationCase1 = False
    
    def tearDown(self):
        filePaths = getTargetFilePathList(self.targetFilesCase1)
        self.fileTransferProces.deleteFiles(filePaths, self.hostsPaswordsCase1, gatewayHosts=self.gatewayHostsCase1, operationId=self.operationIdCase1, numberTrials=self.numberTrialsCase1, forceOperation=False)
        self.fileTransferProces.deleteDirectories(["apoza@glassfishdev.cnb.csic.es:/home/apoza/testFileTransfer"], self.hostsPaswordsCase1, gatewayHosts=self.gatewayHostsCase1, operationId=self.operationIdCase1, numberTrials=self.numberTrialsCase1, forceOperation=False)
        
    def testSimpleLocalToRemoteFileTranfer(self):
        self.fileTransferProces.transferFiles(self.sourceFilesCase1, self.targetFilesCase1, self.hostsPaswordsCase1, gatewayHosts=self.gatewayHostsCase1, operationId=self.operationIdCase1, numberTrials=self.numberTrialsCase1, forceOperation=False);
        filePaths = getTargetFilePathList(self.targetFilesCase1)
        passTest = len(self.fileTransferProces.checkFiles(filePaths, self.hostsPaswordsCase1, gatewayHosts=self.gatewayHostsCase1, operationId=self.operationIdCase1, numberTrials=self.numberTrialsCase1, forceOperation=self.forceOperationCase1)) == 0
        self.assertTrue(passTest)
    


if __name__ == "__main__":
    #import sys;sys.argv = ["", "Test.testName"]
    unittest.main()