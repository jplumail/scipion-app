"""
Created on Apr 9, 2013

@author: antonio
"""
import unittest
from utils.log import *

class TestScipionLog(unittest.TestCase):
      
    def testSimpleFileScipionLog(self):
        log = getGeneralLogger('pyworkflow.test.log.test_scipon_log')
        log.info('General info')
        log.debug('General debug')
        log.warning("General warning")
        
        log = getFileLogger('~/scipionLog/fileLog.log')
        log.info('File info!!!!!!')
        log.debug('File debug!!!!!!')
        log.warning("File warning!!!")
        
        log = getGeneralLogger('pyworkflow.test.log.test_scipon_log')
        log.error('General error')
        
        log = getFileLogger('~/scipionLog/fileLog.log')
        log.error('File error!!!!!!')
        
        self.assertTrue(True)  
        
    """
    config = {  'version': 1,              
                'disable_existing_loggers': False,
                'formatters': {
                    'standard': {
                        'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
                    },
                },
                'handlers': {
                    'default': {
                        'level':'INFO',    
                        'class':'logging.handlers.RotatingFileHandler',
                        'filename' : "/home/antonio/Documents/testScipion.log",
                        'maxBytes' : 100000,
                    },  
                },
                'loggers': {
                    '': {                  
                        'handlers': ['default'],        
                        'level': 'INFO',  
                        'propagate': True  
                    },
                }
            }
    logging.config.dictConfig(config)    
    """

if __name__ == "__main__":
    #import sys;sys.argv = ["", "Test.testName"]
    unittest.main()