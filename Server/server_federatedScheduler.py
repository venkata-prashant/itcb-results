#!/usr/bin/python           # This is server.py file                                                                                                                                                                           
import gc
import socket
import pygraphviz as pgv
import queue 
from _thread import *
import threading
import copy
import json
import datetime
import os
import timeit
import getopt
import sys
import time
import random

from os import listdir
from os.path import isfile, join
from math import ceil
from _symtable import FREE



executableObjectName = ["ammunition", "binarysearch", "bitcount", "bitnoic", "bsort", "complex_updates", "cosf", "countnegative", "cubic", "deg2rad", "dijkstra", "epic", "fac", "fft", "filterbank", "fir2dim", "fmref", "iir", "insertsort", "isqrt", "jfdctint", "lift", "lms", "ludcmp", "matrix1", "md5", "minver", "mpeg2", "ndes", "petrinet", "pm", "powerwindow", "prime", "quicksort", "rad2deg", "recursion", "rijndael_enc", "rijndael_dec", "sha", "st", "statemate", "susan"]

#
#   Data object that corresponds to the request message sent be the server to the
#       client
#
class requestData:
    objectID = 0
    noOfThreads = 0
    execTime = 0
    frequency = 0
    forLoopIter=0
    #self, objid = 2, threads = 1, exectime = 0.339, freq = 1
    def __init__(self, objid =2, threads=1, exectime=0.339, freq=1, itr=0):
        self.objectID = objid
        self.noOfThreads = threads
        self.exectime = exectime
        self.frequency = freq
        self.forLoopIter=itr
 
#
#   Data object that corresponds to the reply message sent be the client to the
#       server
#
class replyData:
    objectID = 0
    noofCycles = 0
    actualExecTime = 0
    
    def __init__(self, objid = 0, cyclecount = 0, actexecTime = 0):
        #print(actexecTime)
        self.objectID = objid
        self.noofCycles = cyclecount
        self.actualExecTime = float(actexecTime)

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
    obj.__dict__ = json.loads(repstr)
    return obj

#
#   Create an arbitrary file name that the Tacle Bench program can save its
#       instruction cycle count onto
#
def createFileName(objid):
    curTime = datetime.datetime.now()
    filename = "../results/" + str(objid) + "_" + curTime.strftime("%m_%d_%H_%M_%S") + ".txt"
    return filename

# updates the ready queue with currently readynodes. 
def update_queue():
    global readyQueue
    global g_copy
    #print(g_copy.nodes())
    for (node, values) in g_copy.in_degree_iter():
        if (values==0) and (node not in client_task.values()) and (node.attr['visited']=='False'):
            curr_node=g_copy.get_node(node)
            curr_node.attr['visited']=True;
            readyQueue.put(node)
            #print('Readynode: ',node)

# listener program for each client  
def clientListener(c,lock):
        global g
        global g_copy
        global g_result
        global executed_tasklist
        while True:
            data=''
            try:
                data=c.recv(1024)
            except:
                c.close();
            if not data:
                break   
            if data: 
                lock.acquire()
                
                try:
                    
                    #print(data.decode('ascii'),'client',clients.index(c))
                    node=client_task[c];
                    reply_obj=convertJSONToReplyObj(data.decode('ascii'))
                    curr_node=g_result.get_node(node);
                    curr_node.attr['act_exec']=reply_obj.actualExecTime;
                    curr_node.attr['dist']=reply_obj.noofCycles;
                    curr_node.attr['cycle_count']=reply_obj.noofCycles
                    if g_copy.has_node(node): 
                        g_copy.remove_node(node)
                        update_queue();
                        cID=clients.index(c)
                        executed_tasklist[cID].append(node)
                            
                    
                    freeClients[cID]=1
                finally: 
                    lock.release()
        c.close()
        
#returns the toposort of the graph in a list
def toposort(g_result):
    g_copy = g_result.copy()
    stack = []
    while len(g_copy.nodes()) > 0:
        for node in g_copy.nodes():
            if g_copy.in_degree(node) == 0:
                stack.append(g_result.get_node(node.get_name()))
                g_copy.delete_node(node)
                break
                
    return stack
 
 #returns the critical path value   
def criticalPath(g_result,topoList):
    critical=[]
    for node in topoList:
        curr_node=g_result.get_node(node)
        dist_curr=float(curr_node.attr['dist'])
        for neighbors in g_result.itersucc(node):
            dist_succ= float(neighbors.attr['dist'])
            exec_succ=float(neighbors.attr['cycle_count'])
            if dist_succ<(dist_curr+exec_succ):
                dist_succ=dist_curr+exec_succ
                neighbors.attr['dist']=dist_succ
                critical.append(dist_succ);
    if len(critical)>0:
        
        return max(critical)
    else:
        print("Empty list")
        print(topoList)

def run_dag(g,num_iter,filename,lock,nC,useM):
    global freeClients
    global readyQueue
    global g_copy
    global g_result
    global executed_tasklist
    C=int(g.node_attr['workload'])
    L=int(g.node_attr['cpathlen'])
    D=int(g.node_attr['deadline'])
    
    outfilename= filename[:-4]+'.csv'
    
    for cID in range(0, nC):
        freeClients[cID]=0
    
    m_req= ceil((C-L)/(D-L))
    print("m_req", m_req)
    
    if not useM:
        m_req=nC
    
    max_m = m_req if m_req <= nC else nC
    for cID in range(0, max_m):
        freeClients[cID]=1    #only set free to required num of clients
    
    
    for iter_n in range(0,num_iter):
        g_copy=g.copy()   #create a copy of g and assign it to g_copy
        g_result=g.copy()
        executed_tasklist = []
        gc.collect()

	
        for i in range (0, nC):
            new = []                                
            executed_tasklist.append(new)
        
        for c in clients:        #reset the client_task dict
            client_task[c]=0
        
        for node in g.nodes():
            node.attr['marked']=False
            node.attr['visited']=False
            node.attr['act_exec']=0
            node.attr['dist']=0
            node.attr['cycle_count']=0
        
        for node in g_copy.nodes():
            node.attr['marked']=False
            node.attr['visited']=False;
            node.attr['act_exec']=0
            node.attr['dist']=0
            node.attr['cycle_count']=0
            
        for node in g_result.nodes():
            node.attr['marked']=False
            node.attr['visited']=False
            node.attr['act_exec']=0
            node.attr['dist']=0
            node.attr['cycle_count']=0
        
        update_queue()      #get the first node in ready queue
        #while there are still nodes to execute    
        while g_copy.number_of_nodes() >0:
            
            while not readyQueue.empty() and 1 in freeClients:
                node= readyQueue.get()
                cID=freeClients.index(1) #get index of freeClient 
                c= clients[cID];
                if (node not in client_task.values()) and (g_copy.has_node(node)):
                    node_obj=g_copy.get_node(node);
                    obj= int(node_obj.attr['object'])
                    exec_time =node_obj.attr['wcet']
                    forloop_iter = 0
                    threads= int(node_obj.attr['threads'])
                    freq = 0
                    command= convertObjToJson(requestData(obj,threads,exec_time,freq,forloop_iter))
                    
                    c.send(command.encode("ascii"))
                    
                    client_task[c]=node;
                    lock.acquire()
                    try:
                        freeClients[cID]=0;
                    finally:
                        lock.release()

            
        
    
        topologist=toposort(g_result)
    
        for list in executed_tasklist:
            for i in range(0, len(list)-1):
                g_result.add_edge(list[i],list[i+1])
    
    
        g_result.write('./resultDotFiles/'+filename[:-4]+'_'+str(iter_n)+'.dot')

    
        is_sched=0;
        critical_path=criticalPath(g_result, topologist)
        if(critical_path<D):
            is_sched=1;
        file=open("./output/" + outfilename,'a')
        file.write('%.4f , %d, %d\n' %(critical_path, D, is_sched))
        file.close()

def usage():
    print("Options: \n\t-h/--help\t\tThis message\n\t-m/--usemaxMcores\t\tUse only M clients to execute a DAG\n\t-n/--numofclients\t\tServer will wait for the specified number of clients to connect before executing.\n")
       
def Main():
    
    
    global g
    global g_copy
    global freeClients
    filepath = './DagTasks'
    onlyfiles = [f for f in listdir(filepath) if isfile(join(filepath, f))]
    num_iter=100
    num_clients = 0
    #If useMcores is true, the server will use only M clients to schedule a task. Otherwise it will use all the clients
    useMcores = True
    
    
    host = "" 
    port = 12350
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host, port)) 
    print("socket binded to port", port) 
    s.listen(4) 
    print("socket is listening") 
    
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hmn:", ["help", "usemaxMcores","numofclients"])
    except getopt.GetoptError as err:
        print(str(err))
        usage()
        sys.exit(2)
    
    for o,a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit()
        if o in ("-m","--usemaxMcores"):
            useMcores = True
        if o in ("-n","--numofclients"):
            num_clients = int(a)
    
    
    # a loop to connect NUM_CLIENT clients
    client_id=0;
    num_nodes=len(g.nodes())
    lock=threading.Lock() 
    NUMCLIENT=num_clients                                                    
    for i in range (0, NUMCLIENT):                               
        new = []                                
        executed_tasklist.append(new) 
    
    
    while client_id<NUMCLIENT:   
        c, addr = s.accept() 
        clients.append(c);
        client_task[c]=0;
        freeClients.append(0)  #connect to all clients but set as busy first
        print('Connected to :', addr[0], ':', addr[1] , 'Client ID',client_id)
        start_new_thread(clientListener, (c,lock)) 
        client_id= client_id+1
    
    
    for filename in onlyfiles:
        if str(filename).endswith('dot'):
                print(filename)
                new_absfilename = filepath + "/" + filename
                g = pgv.AGraph(new_absfilename)
                run_dag(g,num_iter,filename,lock,num_clients,useMcores)
        
    
    for c in clients:
        c.send('end'.encode("ascii"))
        c.close()
    s.close() 

clients = list()  # list of clients
client_task = {}  # dictionary to hold (client, currently executing tasks) pair.
freeClients = []  # list to indicate which client is free , 1 means free, 0 means busy
NUMCLIENT = 1  # Controls the number of clients.
executed_tasklist = []
filepath = './DagTasks'
onlyfiles = [f for f in listdir(filepath) if isfile(join(filepath, f))]

g = pgv.AGraph()  # reads input from dot flie.
g_copy = pgv.AGraph()  # create an empty graph, this will be populated with g's nodes and edges in each iteration.
g_result=pgv.AGraph()

readyQueue = queue.Queue()

if __name__ == '__main__': 
    Main()
