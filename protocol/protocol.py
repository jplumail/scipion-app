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
This modules contains classes required for the workflow
execution and tracking like: Step and Protocol
"""

import datetime as dt
import pickle

from pyworkflow.object import OrderedObject, String, List, Integer, Boolean
from pyworkflow.utils.path import replaceExt, makePath, join, existsPath, cleanPath
from pyworkflow.utils.process import runJob

STATUS_LAUNCHED = "launched"  # launched to queue system
STATUS_RUNNING = "running"    # currently executing
STATUS_FAILED = "failed"      # it have been failed
STATUS_FINISHED = "finished"  # successfully finished
STATUS_WAITING = "waiting"    # waiting for user interaction


class Step(OrderedObject):
    """Basic execution unit.
    It should defines its Input, Output
    and define a run method"""
    def __init__(self, **args):
        OrderedObject.__init__(self, **args)
        self._inputs = []
        self._outputs = []
        self.status = String()
        self.initTime = String()
        self.endTime = String()
        self.error = String()
        self.isInteractive = Boolean(False)
        self.runStartsCallback = None # Used to monitor the Step Starts(Observer pattern)
        self.runFinishCallback = None # Used to monitor the Step Finish(Observer pattern)
        
    def _storeAttributes(self, attrList, attrDict):
        """Store all attributes in attrDict as 
        attributes of self, also store the key in attrList"""
        for key, value in attrDict.iteritems():
            attrList.append(key)
            setattr(self, key, value)
        
    def _defineInputs(self, **args):
        """This function should be used to define
        those attributes considered as Input"""
        self._storeAttributes(self._inputs, args)
        
    def _defineOutputs(self, **args):
        """This function should be used to specify
        expected outputs"""
        self._storeAttributes(self._outputs, args)
    
    def _preconditions(self):
        """Check if the necessary conditions to
        step execution are met"""
        return True
    
    def _postconditions(self):
        """Check if the step have done well its task
        and accomplish its results"""
        return True
    
    def _run(self):
        """This is the function that will do the real job.
        It should be override by sub-classes."""
        pass
    
    def run(self):
        """Do the job of this step"""
        self.initTime.set(dt.datetime.now())
        self.endTime.set(None)
        try:
            if not self.runStartsCallback is None:
                self.runStartsCallback(self)
            self._run()
            if self.isInteractive.get():
                # If the Step is interactive, after run
                # it will be waiting for use to mark it as DONE
                status = STATUS_WAITING
            else:
                status = STATUS_FINISHED
            self.status.set(status)
        except Exception, e:
            self.status.set(STATUS_FAILED)
            self.error.set(e)
            raise #only in development
        finally:
            self.endTime.set(dt.datetime.now())
            if not self.runFinishCallback is None:
                self.runFinishCallback(self)

class FunctionStep(Step):
    """This is a Step wrapper around a normal function
    This class will ease the insertion of Protocol function steps
    throught the function _insertFunctionStep"""
    def __init__(self, funcName=None, *funcArgs):
        """Receive the function to execute and the 
        parameters to call it"""
        Step.__init__(self)
        self.func = None # Function should be set before run
        self.funcName = String(funcName)
        self.funcArgs = funcArgs
        self.argsStr = String(pickle.dumps(funcArgs))
        
    def _run(self):
        resultFiles = self.func(*self.funcArgs)
        if resultFiles and len(resultFiles):
            missingFiles = existsPath(*resultFiles)
            if len(missingFiles):
                raise Exception('Missing files: ' + ' '.join(missingFiles))
            self.resultFiles = String(pickle.dumps(resultFiles))
    
    def _postconditions(self):
        """This type of Step, will simply check
        as postconditions that the result files exists"""
        if not hasattr(self, 'resultFiles'):
            return True
        files = pickle.loads(self.resultFiles.get())

        return len(existsPath(files)) == 0
    
    def __eq__(self, other):
        """Compare with other FunctionStep"""
        return (self.funcName == other.funcName and
                self.funcArgs == other.funcArgs and
                self.argsStr == other.argsStr)
        
            
class RunJobStep(FunctionStep):
    """This Step will wrapper the commonly used function runJob
    for launching specific programs with some parameters"""
    def __init__(self, programName=None, arguments=None, resultFiles=[]):
        FunctionStep.__init__(self, 'runJob', programName, arguments)
        # Define the function that will do the job and return result files
        self.func = self._runJob
        
    def _runJob(self, programName, arguments):
        """Wrap around runJob function"""
        runJob(None, programName, arguments)
        #TODO: Add the option to return resultFiles
             

MODE_RESUME = "resume"
MODE_RESTART = "restart"
MODE_CONTINUE = "continue"
         
                
class Protocol(Step):
    """The Protocol is a higher type of Step.
    It also have the inputs, outputs and other Steps properties,
    but contains a list of steps that are executed"""
    
    def __init__(self, **args):
        Step.__init__(self, **args)
        self.mode = String(args.get('mode', MODE_RESUME))
        self._steps = List() # List of steps that will be executed
        self.workingDir = args.get('workingDir', '.') # All generated files should be inside workingDir
        self.mapper = args.get('mapper', None)
        self._createVarsFromDefinition(**args)
        
    def _createVarsFromDefinition(self, **args):
        """This function will setup the protocol instance variables
        from the Protocol Class definition, taking into account
        the variable type and default values"""
        if hasattr(self, '_definition'):
            for paramName, param in self._definition.iterParams():
                # Create the var with value comming from args or from 
                # the default param definition
                var = param.paramClass(args.get(paramName, param.default.get()))
                setattr(self, paramName, var)
        else:
            print "FIXME: Protocol '%s' has not DEFINITION" % self.getClassName()
        
    
    def _getFilename(self, key, **args):
        return self._templateDict[key] % args
    
    def _store(self, *objs):
        if not self.mapper is None:
            if len(objs) == 0:
                self.mapper.store(self)
            else:
                for obj in objs:
                    self.mapper.store(obj)
            self.mapper.commit()
            
    def _defineSteps(self):
        """Define all the steps that will be executed."""
        pass
    
    def __insertStep(self, step):
        """Insert a new step in the list"""
        self._steps.append(step)
        step.runStartsCallback = self._stepStarted
        step.runFinishCallback = self._stepFinished
        
    def _getPath(self, *paths):
        """Return a path inside the workingDir"""
        return join(self.workingDir, *paths)

    def _getExtraPath(self, *paths):
        """Return a path inside the extra folder"""
        return self._getPath("extra", *paths)    
    
    def _getTmpPath(self, *paths):
        """Return a path inside the tmp folder"""
        return self._getPath("tmp", *paths)   
        
    def _insertFunctionStep(self, funcName, *funcArgs, **args):
        """Input params:
        funcName: the string name of the function to be run in the Step.
        *funcArgs: the variable list of arguments to pass to the function.
        **args: variable dictionary with extra params, NOT USED NOW
        """
        step = FunctionStep(funcName, *funcArgs)
        step.func = getattr(self, funcName)
        self.__insertStep(step)
        
    def _insertRunJobStep(self, progName, progArguments, resultFiles=[]):
        """Insert an Step that will simple call runJob function"""
        step = RunJobStep(progName, progArguments, resultFiles)
        self.__insertStep(step)
        
    def __backupSteps(self):
        """ Store the Steps list in another variable to prevent
        overriden of stored steps when calling _defineSteps function.
        This is need to later find in which Step will start the run
        if the RESUME mode is used"""
        self._steps.setStore(False)
        self._prevSteps = self._steps
        self._steps = List() # create a new object for steps
        
    def __findStartingStep(self):
        """ From a previous run, compare self._steps and self._prevSteps
        to find which steps we need to start at, skipping sucessful done 
        and not changed steps. Steps that needs to be done, will be deleted
        from the previous run storage"""
        if self.mode.get() == MODE_RESTART:
            return 0
        
        n = min(len(self._steps), len(self._prevSteps))
        
        for i in range(n):
            newStep = self._steps[i]
            oldStep = self._prevSteps[i]
            if (newStep != oldStep or 
                not oldStep._postconditions()):
                return i
            
        return n
    
    def __cleanStepsFrom(self, index):
        """ Clean from the persistence all steps in self._prevSteps
        from that index. After this function self._steps is updated
        with steps from self._prevSteps (<index) and self._prevSteps is 
        deleted since is no longer needed"""
        self._steps[:index] = self._prevSteps[:index]
        
        for oldStep in self._prevSteps[index:]:
            self.mapper.delete(oldStep)
            
        self._prevSteps = []
        
    def _stepStarted(self, step):
        """This function will be called whenever an step
        has started running"""
        print "STARTED: " + step.funcName.get()
    
    def _stepFinished(self, step):
        """This function will be called whenever an step
        has finished its run"""
        self.mapper.insertChild(self._steps, self._steps.getIndexStr(self.currentStep),
                         step, self.namePrefix)
        self.currentStep += 1
        self.mapper.commit()
        if step.status == STATUS_FAILED:
            raise Exception("Protocol failed: " + step.error.get())
        print "FINISHED: ", step.funcName.get()
    
    def _runSteps(self, startIndex):
        """ Run all steps defined in self._steps"""
        self._steps.setStore(True) # Set steps to be stored
        
        for step in self._steps[startIndex:]:
            step.run()
    
    def _run(self):
        self.__backupSteps() # Prevent from overriden previous stored steps
        self._defineSteps() # Define steps for execute later
        startIndex = self.__findStartingStep() # Find at which step we need to start
        self.__cleanStepsFrom(startIndex) # 
        
        self._store()
        paths = [self.workingDir, self._getExtraPath(), self._getTmpPath()]
        
        # Clean working path if in RESTART mode
        if self.mode.get() == MODE_RESTART:
            cleanPath(*paths)
        # Create workingDir, extra and tmp paths
        makePath(*paths)
        
        self._runSteps(startIndex)
        

    def run(self):
        self.currentStep = 1
        self.namePrefix = replaceExt(self._steps.getName(), self._steps.strId()) #keep 
        Step.run(self)
        outputs = [getattr(self, o) for o in self._outputs]
        #self._store(self.status, self.initTime, self.endTime, *outputs)
        self._store()
        print 'PROTOCOL FINISHED'


