import bisect
import builder
import random

print("Begin")


class Simulator(object):
    def __init__(self, topology =  "chord", strategy = "static"):
        self.nodeIDs = []   # the (super)nodes
        self.workerIDs = [] # the nodes and sybils 
        self.pool = []
        self.nodes = {}  # (id: int, Node: object)
        
        
        self.numNodes = 1000
        self.numTasks = 1000000
        self.churnRate = 0.01 # chance of join/leave per tick per node
    
        self.perfectTime = self.numTasks/self.numNodes
        
        self.numDone = 0
        self.time = 0
        
        self.nodeIDs = builder.createStaticIDs(self.numNodes)
        self.addToPool(self.numNodes)
        
        print("Creating Nodes")
        for id in self.nodeIDs:
            n = SimpleNode(id)
            self.nodes[id] = n
            
        
        
        print("Creating Tasks")
        for key in [next(builder.generateFileIDs()) for _ in range(self.numTasks)]:
            id, _ = self.whoGetsFile(key)
            self.nodes[id].addTask(key)
        self.topology =  topology 
    
    def whoGetsFile(self, key : int):
        i =  bisect.bisect_left(self.nodeIDs, key) # index of node closest without going over
        if i == len(self.nodeIDs):
            i = 0 
        return self.nodeIDs[i], i        
      
    
    def doTick(self):
        assert(len(self.nodeIDs)  ==  len(set(self.nodeIDs)))
        self.churnNetwork()
        self.performWork()
        self.time += 1    
    
    def churnNetwork(self):
        """
        figure out who is leaving and store it
        figure out who is joining and store it
        for each leaving node,
            remove it
            collect tasks
        reassign tasks
        
        for each joining
            add new node
            reassign tasks from affected nodes
            
        generate new ids and add them to pool
        
        """
        leaving = []
        joining = []
        for nodeID in self.nodeIDs:
            if random.random() < self.churnRate:
                leaving.append(nodeID)
        for j in self.pool:
            if random.random() < self.churnRate:
                joining.append(j)
                self.pool.remove(j)
        
        tasks = []
        
        for l in leaving:
            tasks += self.removeNode(l)
        self.reallocateTasks(tasks)
        
        for j in joining:
            # assert(len(self.nodeIDs)  ==  len(set(self.nodeIDs)))
        
            index  = bisect.bisect_left(self.nodeIDs, j)
            succ = None
            if index == len(self.nodeIDs): 
                succ =  self.nodes[self.nodeIDs[0]]
            else:
                succID = self.nodeIDs[index]
                succ =  self.nodes[succID]                
            # if j in self.nodeIDs:
            #    continue
            
            # assert(j not in self.nodeIDs)
            
            
            self.nodeIDs.insert(index, j)            
            
            newNode = SimpleNode(j)
            self.nodes[j] = newNode
            
            tasks = succ.tasks[:]
            succ.tasks = []
            
            for task in tasks:
                if newNode.id < succ.id:
                    if task <= newNode.id:
                        newNode.addTask(task)
                    else:
                        succ.addTask(task)
                else:
                    if task > succ.id and  task < newNode.id:
                        newNode.addTask(task)
                    else:
                        succ.addTask(task)
            
        self.addToPool(len(leaving))
        
            
    def addToPool(self, num):
        for _ in range(num):
            x = next(builder.generateFileIDs())
            assert(x not in self.nodeIDs)
            self.pool.append(x)

    def removeNode(self, key):
        tasks = self.nodes[key].tasks[:]
        self.nodeIDs.remove(key)
        del(self.nodes[key])
        return tasks
        
    def reallocateTasks(self, tasks):
        for task in tasks:
            id, _  = self.whoGetsFile(task)
            self.nodes[id].addTask(task)
        
    
    def performWork(self):
        for n in self.nodeIDs:
            workDone = self.nodes[n].doWork()
            if workDone:  # if the node finished a task
                self.numDone += 1
    
    def simulate(self):
        while(self.numDone < self.numTasks):
            self.doTick()
            print(self.time, self.numDone, len(self.nodeIDs), len(self.pool), len(self.pool) + len(self.nodeIDs) )
        print(str(self.numTasks) + " done in " + str(self.time) + " ticks.")
        print(self.perfectTime)
        
        # maxNode =max(self.nodes.values(), key= lambda x: len(x.done))
        # print(len(maxNode.done))
    
    

class SimpleNode(object):
    def __init__(self, id):
        self.id = id
        self.tasks = []
        self.done = []
    
    def doWork(self):
        if len(self.tasks) > 0:
            x = self.tasks.pop()
            self.done.append(x)
            return True
        return False
    
    def addTask(self,task):
        self.tasks.append(task)




class Task(object):
    def __init__(self, key, size=1):
        self.key = key
        self.size = size
        

class Result(object):
    results = []
    
    def combine(self, other) -> None:
        self.results = self.results + other.results



s = Simulator()
s.simulate()    
