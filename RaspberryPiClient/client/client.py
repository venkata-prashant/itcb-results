import socket 
import importlib
import json
import datetime
import os
import timeit
import getopt
import sys
import time
import random
 
#
# executableObjectName maps object ID to the executable name
# Example:
# objectID = 1 implies the executable object is binarysearch
#
executableObjectName = ["ammunition", "binarysearch", "bitcount", "bitonic", "bsort", "cjpeg_transupp", "cjpeg_wrbmp" ,"complex_updates", "cosf", "countnegative", "cubic", "deg2rad", "dijkstra", "epic", "fac", "fft", "filterbank", "fir2dim", "fmref", "iir", "insertsort", "isqrt", "jfdctint", "lift", "lms", "ludcmp", "matrix1", "md5", "minver", "mpeg2", "ndes", "petrinet", "pm", "powerwindow", "prime", "quicksort", "rad2deg", "recursion", "rijndael_dec", "rijndael_enc", "sha", "st", "statemate", "susan"]

#
#   Data object that corresponds to the request message sent be the server to the client
#
class requestData:
    objectID = 0
    noOfThreads = 0
    execTime = 0
    frequency = 0
    forLoopIter = 0
    
    def __init__(self, objid= 2, threads =1, exectime=.339, freq = 1, itr=0):
        self.objectID = objid
        self.noOfThreads = threads
        self.exectime = exectime
        self.frequency = freq
        self.forLoopIter = itr
 
#
#   Data object that corresponds to the reply message sent be the client to the server
#
class replyData:
    objectID = 0
    noofCycles = 0
    actualExecTime = 0
    
    def __init__(self, objid = 0, cyclecount = 0, actexecTime=0):
        self.objectID = objid
        self.noofCycles = cyclecount
        self.actualExecTime = actexecTime

#
#   Method that converts a data object to an equivalent JSON string
#
def convertObjToJson(obj):
    s = json.dumps(obj.__dict__)
    return s

#
#   Method that converts a JSON string corresponding to request data object to its
#       object representation
#
def convertJSONToReqObj(reqstr):
    obj = requestData()
    obj.__dict__ = json.loads(reqstr)
    return obj

#
#   Method that converts a JSON string corresponding to reply data object to its
#       object representation
#
def convertJSONToReplyObj(repstr):
    obj = replyData()
    obj.__dic__ = json.loads(repstr)
    return obj

#
#   Create an arbitrary file name that the Tacle Bench program can save its
#       instruction cycle count onto
#
def createFileName(objid):
    curTime = datetime.datetime.now()
    filename = "../results/" + str(objid) + "_" + curTime.strftime("%m_%d_%H_%M_%S") + "_" + str(random.randint(1, 1000)) + ".txt"
    return filename

#
#   Executes an object on a designated core and computes its execution time in terms of number of cycles.
#   Returns the execution time and cycle count values as a JSON string.
#
def execObject(reqmsg, coreID, instCycleCount):
    reqObj = convertJSONToReqObj(reqmsg)
    filename = createFileName(reqObj.objectID)
    execString = "sudo nice -n -20 taskset -c " + str(coreID) + " ../obj/" + executableObjectName[int(reqObj.objectID)] + " -n " + str(reqObj.noOfThreads) + " -s " + filename
    if instCycleCount == 1:
            execString = execString + " -i"
    
    print(execString)
    starttime = time.time()
    os.system(execString)
    endTime = time.time()
    elapsed_time = endTime - starttime;
    
    f = open(filename, "r+")
    print(filename)
    contents = f.read()
    contents= contents.replace(',','')
    contents=contents.strip()
    cycleCount = int(contents)
    print(contents)
    f.write("%f ," % elapsed_time)
    f.close()
    retobj = replyData(reqObj.objectID, cycleCount, elapsed_time)
    retString = convertObjToJson(retobj)
    print(retString)
    return retString
    
    
def usage():
    print("Options: \n\t-h/--help\t\tThis message\n\t-c/--core\t\tExecute this program on a the specified core\n\t-e/--execcore\t\tExecute the C program on the specified core\n\t-i/--instcyclecount\tCount the instruction cycles\n\t-s/ --serverIPaddress\tIP address of the server\n\t-p/ --serverPort\tPort Number of the server")


def Main(): 
    host = '192.168.1.69'
    port = 12349
    
    execCore = 0
    instCycleCount = 0
    core = []
    
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hic:e:s:p:", ["help", "instcyclecount","core", "execcore","serverIPaddress","serverPort"])
    except getopt.GetoptError as err:
        print(str(err))
        usage()
        sys.exit(2)
    
    for o,a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit()
        if o in ("-c","--core"):
            core.append(int(a))
            os.sched_setaffinity(0, core)
        if o in ("-e","--execcore"):
            execCore = int(a)
        if o in ("-i","--instcyclecount"):
            instCycleCount = 1
        if o in ("-s","--serverIPaddress"):
            host = a
        if o in ("-p","--serverPort"):
            port = int(a)
    
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM) 
    s.connect((host,port))
    
    while True: 
            message='';
            data = s.recv(1024)
            if data.decode('ascii')=='end':
                break; 
            if data:
              message=execObject(data.decode('ascii'), execCore, instCycleCount)
               
            if len(message)>0:
                s.sendall(message.encode('ascii'))
         
    s.close() 
   
if __name__ == '__main__': 
    Main() 
