# **************************************************************************
# *
# * Authors:     J.M. De la Rosa Trevin (jmdelarosa@cnb.csic.es)
# *              Laura del Cano         (ldelcano@cnb.csic.es)
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
This module handles process execution
"""
import sys

# The job should be launched from the working directory!
def runJob(log, programname, params,           
           numberOfMpi=1, numberOfThreads=1, runInBackground=False):

    command = buildRunCommand(log, programname, params,
                              numberOfMpi, numberOfThreads, runInBackground)
    if log is None:
        #TODO: printLog("Running command: %s" % greenStr(command),log)
        print "Running command: %s" % command
        pass

    from subprocess import call
    retcode = 1000
    try:
        #TODO: check differences and possibles improvements by using subprocess Python module
        retcode = call(command, shell=True, stdout=sys.stdout, stderr=sys.stderr)
        if log:
            #TODO: printLog("Process returned with code %d" % retcode,log)
            pass
        if retcode != 0:
            raise Exception("Process returned with code %d, command: %s" % (retcode,command))
    except OSError, e:
        raise Exception("Execution failed %s, command: %s" % (e, command))

    return retcode


def buildRunCommand(log, programname, params,
                    numberOfMpi, numberOfThreads, runInBackground):
    if numberOfMpi <= 1:
        command = programname + ' ' + params
    else:
        if programname.startswith('xmipp'):
            programname = programname.replace('xmipp', 'xmipp_mpi')
        paramsDict = {'nodes': numberOfMpi,
                      'command': "`which %(programname)s` %(params)s" % locals()
                      }
        hostConfig = loadHostConfig()
        command = hostConfig.mpiCommand.get() % paramsDict

    if runInBackground:
        command+=" &"

    return command


def loadHostConfig(host='localhost'):
    """ This function will load the execution host configuration.
    In there will be information to know how to launch MPI processes
    and how to submit jobs to the queue system if exists.
    """
    from pyworkflow.apps.config import ExecutionHostMapper, getConfigPath
    fn = getConfigPath('execution_hosts.xml')
    print 'fn', fn
    mapper = ExecutionHostMapper(fn)
    return mapper.selectAll()[0]

