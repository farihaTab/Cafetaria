"""
The task is to simulate an M/M/k system with a single queue.
Complete the skeleton code and produce results for three experiments.
The study is mainly to show various results of a queue against its ro parameter.
ro is defined as the ratio of arrival rate vs service rate.
For the sake of comparison, while plotting results from simulation, also produce the analytical results.
"""

import heapq
import random
import matplotlib.pyplot as plt
from decimal import Decimal

"""
        mean interarrival time 30 seconds
        group size 1,2,3,4 probability 0.5,0.3,0.1,0.1
        simulation ends 90min after
        3 customer route 
            i. hot-food , drinks, cashier   0.80    ST-U(50,120)    ACT-U(20,40)
            ii. sandwich, drinks, cashier   0.15    ST-U(60,180)    ACT-U(5,15)
            iii. drinks, cashier            0.05    ST-U(5,20)      ACT-U(5,10)
        #cashier = 2 - 3    can have multiple server
        #hotfood = 1 - h    always one-to-one service
        #sandwitch = 1 - s  always one-to-one service
"""
class Customer:
    def __init__(self, no, custType, currService):
        self.custNo = no
        self.custType = custType
        self.currService = currService

        self.arrivalTime = None

        self.hotfoodQTime = None
        self.hotfoodSTime = None
        self.sandwichQTime = None
        self.sandwichSTime = None
        self.drinksQTime = None
        self.drinksSTime = None
        self.cashierQTime = None
        self.cashierSTime = 0.0

        self.cashierNo = None

    def __repr__(self):
        return 'custNo. ',self.custNo,' arr: ',self.arrivalTime,'q: ',self.queueTime,'serv: ',self.serviceTime

# Parameters
class Params:
    def __init__(self, lambd, hotfoodServer, sandwitchServer, cashier):
        self.lambd = lambd
        self.cashier = cashier
        self.hotfoodServer = hotfoodServer
        self.sandwichServer = sandwitchServer


# States and statistical counters
class States:
    def __init__(self, hotfoodServer, sandwitchServer, cashier):
        # States
        self.cashierQ = [[] for _ in range(cashier)]
        self.hotfoodQ = []
        self.sandwichQ = []

        # Statistics
        self.maxHotfoodQdelay = 0.0
        self.maxSandwichQdelay = 0.0
        self.maxCashierQdelay = 0.0
        self.avgHotfoodQdelay = 0.0
        self.avgSandwichQdelay = 0.0
        self.avgCashierQdelay = 0.0

        self.maxHotfoodQlength = 0.0
        self.maxSandwichQlength = 0.0
        self.maxCashierQlength = 0.0
        self.avgHotfoodQlength = 0.0
        self.avgSandwichQlength = 0.0
        self.avgCashierQlength = 0.0

        self.avgTotalQdelayCust1 = 0.0
        self.maxTotalQdelayCust1 = 0.0
        self.avgTotalQdelayCust2 = 0.0
        self.maxTotalQdelayCust2 = 0.0
        self.avgTotalQdelayCust3 = 0.0
        self.maxTotalQdelayCust3 = 0.0

        self.avgTotalQdelay = 0.0 # found by weighting their individual
                                    # avg yoal delays by their respectibe pribabiltiyes of occurance
        self.avgCustInSystem = 0.0
        self.maxCustInSystem = 0.0

        self.totalCust1 = 0
        self.totalCust2 = 0
        self.totalCust3 = 0

        self.prevEvent = None

    def update(self, sim, event): # ekhane ei parameter gula update korbo
        if event.eventType == 'DEPARTURE':
            print 'updating for DEPARTURE ',event.customer.custNo
            if (event.customer.custType == 1 and event.customer.currService == 1): # hotfood
                self.avgHotfoodQdelay += event.customer.hotfoodQTime
                if (self.maxHotfoodQdelay < event.customer.hotfoodQTime):
                    self.maxHotfoodQdelay = event.customer.hotfoodQTime
            elif (event.customer.custType == 2 and event.customer.currService == 2): #sandwich
                self.avgSandwichQdelay += event.customer.sandwichQTime
                if (self.maxSandwichQdelay < event.customer.sandwichQTime):
                    self.maxSandwichQdelay = event.customer.sandwichQTime
            # no queue in drinks
            elif (( event.customer.custType == 1 and event.customer.currService == 3 )
                  or (event.customer.custType == 2 and event.customer.currService == 3)
                  or (event.customer.custType == 3 and event.customer.currService == 2)): #cashier
                self.avgCashierQdelay += event.customer.cashierQTime
                if (self.maxCashierQdelay < event.customer.cashierQTime):
                    self.maxCashierQdelay = event.customer.cashierQTime

                if (event.customer.custType == 1):
                    totalDelay = event.customer.hotfoodQTime+event.customer.drinksQTime+event.customer.cashierQTime
                    self.avgTotalQdelayCust1 += totalDelay
                    if (self.maxTotalQdelayCust1 < totalDelay):
                        self.maxTotalQdelayCust1 += 1
                elif (event.customer.custType == 2):
                    totalDelay = event.customer.sandwichQTime+event.customer.drinksQTime+event.customer.cashierQTime
                    self.avgTotalQdelayCust2 += totalDelay
                    if (self.maxTotalQdelayCust2 < totalDelay):
                        self.maxTotalQdelayCust2 += 1
                elif (event.customer.custType == 3):
                    totalDelay = event.customer.drinksQTime+event.customer.cashierQTime
                    self.avgTotalQdelayCust3 += totalDelay
                    if (self.maxTotalQdelayCust3 < totalDelay):
                        self.maxTotalQdelayCust3 += 1



        elif event.eventType == 'ARRIVAL':
            if event.customer.custType == 4:
                return
            print 'updating for ARRIVAL ',event.customer.custNo
            if (event.customer.currService == 1):
                if (event.customer.custType == 1):
                    self.totalCust1 += 1
                elif (event.customer.custType == 2):
                    self.totalCust2 += 1
                else:
                    self.totalCust3 += 1

        # self.avgQlength = self.avgQlength + len(self.queue)*(event.eventTime - self.prevEventTime)
        prevEventTime = 0.0
        if (self.prevEvent == None):
            prevEventTime = 0.0
        else:
            prevEventTime = self.prevEvent.eventTime
        self.avgHotfoodQlength += len(self.hotfoodQ)*(event.eventTime - prevEventTime)
        self.avgSandwichQlength += len(self.sandwichQ)*(event.eventTime - prevEventTime)
        cashierQLen = 0
        for i in range(sim.params.cashier):
            cashierQLen += len(self.cashierQ[i])
        self.avgCashierQlength += cashierQLen*(event.eventTime - prevEventTime)

        if(self.maxHotfoodQlength < len(self.hotfoodQ)):
            self.maxHotfoodQlength = len(self.hotfoodQ)
        if(self.maxSandwichQlength < len(self.sandwichQ)):
            self.maxSandwichQlength = len(self.sandwichQ)
        if(self.maxCashierQlength < cashierQLen):
            self.maxCashierQlength = cashierQLen

        custInSystem = len(self.hotfoodQ)+len(self.sandwichQ)+cashierQLen
        if (sim.hotfoodServerBusy):
            custInSystem += 1
        if sim.sandwichServerBusy:
            custInSystem += 1
        for i in range(sim.params.cashier):
            if sim.cashierBusy[i]:
                custInSystem += 1
        self.avgCustInSystem += custInSystem
        if self.maxCustInSystem < custInSystem:
            self.maxCustInSystem = custInSystem
        self.prevEvent = event


    def finish(self, sim):
        # self.maxHotfoodQdelay = 0.0
        # self.maxSandwichQdelay = 0.0
        # self.maxCashierQdelay = 0.0
        totalCust = self.totalCust1 + self.totalCust2 +self.totalCust3
        self.avgHotfoodQdelay /= self.totalCust1
        self.avgSandwichQdelay /= self.totalCust2
        self.avgCashierQdelay /= totalCust

        # self.maxHotfoodQlength = 0.0
        # self.maxSandwichQlength = 0.0
        # self.maxCashierQlength = 0.0
        self.avgHotfoodQlength /= sim.now()
        self.avgSandwichQlength /= sim.now()
        self.avgCashierQlength /= sim.now()

        self.avgTotalQdelayCust1 /= self.totalCust1
        # self.maxTotalQdelayCust1 = 0.0
        self.avgTotalQdelayCust2 /= self.totalCust2
        # self.maxTotalQdelayCust2 = 0.0
        self.avgTotalQdelayCust3 /= self.totalCust3
        # self.maxTotalQdelayCust3 = 0.0

        self.avgTotalQdelay = 0.8* self.avgTotalQdelayCust1 + 0.15* self.avgTotalQdelayCust2 + 0.05* self.avgTotalQdelayCust3# found by weighting their individual
                                # avg yoal delays by their respectibe pribabiltiyes of occurance
        self.avgCustInSystem /= sim.now()
        # self.maxCustInSystem = 0.0

        # self.totalCust1 = 0
        # self.totalCust2 = 0
        # self.totalCust3 = 0

        # return
        # self.util = self.util / sim.now()
        # self.avgQdelay = self.avgQdelay /self.served
        # self.avgQlength = self.avgQlength /sim.now() #todo: k diye gun dite hobe


    def printResults(self, sim):
        print 'SIMULATION RESULTS: '
        print 'Params: lambda = %lf, hotfood server = %d, sandwich server = %d cashier = %d' % (sim.params.lambd, sim.params.hotfoodServer, sim.params.sandwichServer, sim.params.cashier)
        print 'avg delay in hotfood queue: %lf' % (self.avgHotfoodQdelay)
        print 'avg delay in sandwich queue: %lf' % (self.avgSandwichQdelay)
        print 'avg delay in cashier queue: %lf' % (self.avgCashierQdelay)
        print 'max delay in hotfood queue: %lf' % (self.maxHotfoodQdelay)
        print 'max delay in sandwich queue: %lf' % (self.maxSandwichQdelay)
        print 'max delay in cashier queue: %lf' % (self.maxCashierQdelay)

        print 'avg length in hotfood queue: %lf' % (self.avgHotfoodQlength)
        print 'avg length in sandwich queue: %lf' % (self.avgSandwichQlength)
        print 'avg length in cashier queue: %lf' % (self.avgCashierQlength)
        print 'max length in hotfood queue: %lf' % (self.maxHotfoodQlength)
        print 'max length in sandwich queue: %lf' % (self.maxSandwichQlength)
        print 'max length in cashier queue: %lf' % (self.maxCashierQlength)

        print 'avg total delay for customer type 1: %lf' % (self.avgTotalQdelayCust1)
        print 'avg total delay for customer type 2: %lf' % (self.avgTotalQdelayCust2)
        print 'avg total delay for customer type 3: %lf' % (self.avgTotalQdelayCust3)
        print 'max total delay for customer type 1: %lf' % (self.maxTotalQdelayCust1)
        print 'max total delay for customer type 2: %lf' % (self.maxTotalQdelayCust2)
        print 'max total delay for customer type 3: %lf' % (self.maxTotalQdelayCust3)

        print 'overall avg total delay for all customers: %lf' % (self.avgTotalQdelay)

        print 'time-avg total number of customer in system: %lf' % (self.avgCustInSystem)
        print 'max total number of customer in system: %lf' % (self.maxCustInSystem)




        # print 'av: %lf' % (self.avgQlength)
        # print 'MMk Average customer delay in queue: %lf' % (self.avgQdelay)
        # print 'MMk Time-average server utility: %lf' % (self.util)

class Event:
    def __init__(self, sim):
        self.eventType = None
        self.sim = sim
        self.eventTime = None

    def process(self, sim):
        raise Exception('Unimplemented process method for the event!')

    def __repr__(self):
        return self.eventType


class StartEvent(Event):
    def __init__(self, eventTime, sim):
        print 'Start Event scheduled'
        self.eventTime = eventTime
        self.eventType = 'START'
        self.sim = sim

    def process(self, sim):
        x=sim.streamInterarrival.expovariate(sim.params.lambd)
        x = round(x,0)
        print 'x ', x
        for i in range(sim.findGroupSize()):
            # new customer in cafeteria
            customer = Customer(sim.custNo,sim.findCustomerType(),1)
            customer.arrivalTime = self.eventTime+x
            sim.scheduleEvent(ArrivalEvent(self.eventTime+x,sim,customer))
        sim.scheduleEvent(ArrivalEvent(self.eventTime+x,sim,Customer(0,4,1)))
        #sim.scheduleEvent(ExitEvent(90*60, sim))


class ExitEvent(Event):
    def __init__(self, eventTime, sim):
        print 'Exit Event scheduled'
        self.eventTime = eventTime
        self.eventType = 'EXIT'
        self.sim = sim

    def process(self, sim):
        None


class ArrivalEvent(Event):
    def __init__(self, eventTime, sim, customer):
        self.eventTime = eventTime
        self.eventType = 'ARRIVAL'
        self.sim = sim
        if customer.currService==1:
            sim.custNo = sim.custNo + 1
        self.customer = customer
        # self.customer.arrivalTime = eventTime

    def process(self, sim):
        print self.customer.custNo, ' arrived for ', self.customer.custType,' ',self.customer.currService
        if self.customer.custType == 4: #if this is a group arrival
            #schedule next arrival
            x = sim.streamInterarrival.expovariate(sim.params.lambd)
            x = round(x, 0)
            print 'x ',x, ' ', self.eventTime + x
            if self.eventTime+x >= 90*60:
                return
            for i in range(sim.findGroupSize()):
                # new customer in cafeteria
                # generate customer type and set curr task to first task
                customer = Customer(sim.custNo, sim.findCustomerType(), 1)
                customer.arrivalTime = self.eventTime+x
                sim.scheduleEvent(ArrivalEvent(self.eventTime + x, sim, customer))
            sim.scheduleEvent(ArrivalEvent(self.eventTime + x, sim, Customer(0, 4, 1)))
            return

        if self.customer.custType == 1 and self.customer.currService == 1: # if arrival at hot-food service
            if not sim.hotfoodServerBusy: # if server free
                # make the server busy
                sim.hotfoodServerBusy = True
                # set queue time at hotfood 0 for this customer and gather statistics
                self.customer.hotfoodQTime = 0.0
                # schedule a departure event for this job
                hotfoodSTime = sim.streamHotfoodST.uniform(50.0/sim.params.hotfoodServer,120.0/sim.params.hotfoodServer)
                self.customer.hotfoodSTime = hotfoodSTime
                sim.scheduleEvent(DepartureEvent(sim.now() + hotfoodSTime, sim, self.customer))
                # calculate accumulated cost at cashier for this service
                accumulatedTime = sim.streamHotfoodACT.uniform(20.0,40.0)
                self.customer.cashierSTime += accumulatedTime
            else:
                #print 'server busy ', len(sim.states.queue)
                # add customer to queue
                # self.customer.hotfoodQTime = sim.now()  # apatoto line e daranor time ta save kore rakhi
                sim.states.hotfoodQ.append(self.customer)
        elif (( self.customer.custType == 1 and self.customer.currService == 2 )
            or (self.customer.custType == 2 and self.customer.currService == 2)
            or (self.customer.custType == 3 and self.customer.currService == 1)): # if arrival at drinks service
            # in drinks we have infinite servers, so server always free
            # set queue time at drinks 0 for this customer and gather statistics
            self.customer.drinksQTime = 0.0
            # schedule a departure event for this job
            drinksSTime = sim.streamDrinksST.uniform(5.0 , 20.0)
            self.customer.drinksSTime = drinksSTime
            sim.scheduleEvent(DepartureEvent(sim.now() + drinksSTime, sim, self.customer))
            # calculate accumulated cost at cashier for this service
            accumulatedTime = sim.streamDrinksACT.uniform(5.0, 15.0)
            self.customer.cashierSTime += accumulatedTime
        elif (self.customer.custType == 2 and self.customer.currService == 1): # if arrival at sandwich service
            if not sim.sandwichServerBusy: # if server free
                # make the server busy
                sim.sandwichServerBusy = True
                # set queue time at sancwich 0 for this customer and gather statistics
                self.customer.sandwichQTime = 0.0
                # schedule a departure event for this job
                sandwichSTime = sim.streamSandwichST.uniform(60.0/sim.params.sandwichServer,180.0/sim.params.sandwichServer)
                self.customer.sandwichSTime = sandwichSTime
                sim.scheduleEvent(DepartureEvent(sim.now() + sandwichSTime, sim, self.customer))
                # calculate accumulated cost at cashier for this service
                accumulatedTime = sim.streamSandwichACT.uniform(5.0,15.0)
                self.customer.cashierSTime += accumulatedTime
            else:
                # print 'server busy ', len(sim.states.queue)
                # add customer to queue
                # self.customer.sandwichQTime = sim.now()#apatoto line e daranor time ta save kore rakhi
                sim.states.sandwichQ.append(self.customer)
        else: # if arrival at cashier
            freeCashier = sim.getFreeCashier()
            if (freeCashier == None): #if all server busy
                print 'cashier busy'
                minIdx = 0
                min = 0
                for i in range(sim.params.cashier):
                    if(min > len(sim.states.cashierQ[i])):
                        min = len(sim.states.cashierQ[i])
                        minIdx = i

                # add customer to shortest queue
                # self.customer.cashierQTime = sim.now()  # apatoto line e daranor time ta save kore rakhi
                self.customer.cashierNo = minIdx
                sim.states.cashierQ[minIdx].append(self.customer)
            else:
                # make the server busy
                print 'cashier free'
                sim.cashierBusy[freeCashier] = True
                # set queue time at sancwich 0 for this customer and gather statistics
                self.customer.cashierQTime = 0.0
                # set cashierNo in customer
                self.customer.cashierNo = freeCashier
                # schedule a departure event for this job
                sim.scheduleEvent(DepartureEvent(sim.now() + self.customer.cashierSTime, sim, self.customer))


class DepartureEvent(Event):
    def __init__(self, eventTime, sim, cust):
        self.eventTime = eventTime
        self.eventType = 'DEPARTURE'
        self.sim = sim
        self.customer = cust

    def process(self, sim):
        print self.customer.custNo , ' departed from ', self.customer.custType,' ',self.customer.currService

        if self.customer.custType == 1 and self.customer.currService == 1: # hotfood service
            if len(sim.states.hotfoodQ) == 0: # if hotfood queue empty
                print 'queue empty'
                # make a server idle
                sim.hotfoodServerBusy = False
            else:
                # remove a customer from queue
                cust = sim.states.hotfoodQ.pop(0)
                print 'hotfood queue not empty. first in line ', cust.custNo
                # set queuetime for popped customer
                cust.hotfoodQTime = self.eventTime - cust.arrivalTime
                # set service time for popped customer
                hotfoodSTime = sim.streamHotfoodST.uniform(50.0 / sim.params.hotfoodServer, 120.0 / sim.params.hotfoodServer)
                cust.hotfoodSTime = hotfoodSTime
                # schedule departure for removed customer
                sim.scheduleEvent(DepartureEvent(sim.now() + hotfoodSTime, sim, cust))

                #if more task tobe done for customer who left queue
                #update currTask
                self.customer.currService += 1
                #invoke arrival event for this new task
                # todo: update statistics
                ArrivalEvent(sim.now(),sim,self.customer).process(sim)
        elif (self.customer.custType == 2 and self.customer.currService == 1):
            if len(sim.states.sandwichQ) == 0:  # if sandwich queue empty
                print 'queue empty'
                # make a server idle
                sim.sandwichServerBusy = False
            else:
                # remove a customer from queue
                cust = sim.states.sandwichQ.pop(0)
                print 'sandwich queue not empty. first in line ', cust.custNo
                # set queuetime for popped customer
                cust.sandwichQTime = self.eventTime - cust.arrivalTime
                # set service time for popped customer
                sandwichSTime = sim.streamSandwichST.uniform(60.0 / sim.params.sandwichServer, 180.0 / sim.params.sandwichServer)
                cust.sandwichSTime = sandwichSTime
                # schedule departure for removed customer
                sim.scheduleEvent(DepartureEvent(sim.now() + sandwichSTime, sim, cust))

                # if more task tobe done for customer who left queue
                # update currTask
                self.customer.currService += 1
                # invoke arrival event for this new task
                ArrivalEvent(sim.now(), sim, self.customer).process(sim)
        elif (( self.customer.custType == 1 and self.customer.currService == 2 )
            or (self.customer.custType == 2 and self.customer.currService == 2)
            or (self.customer.custType == 3 and self.customer.currService == 1)): # if departure from drinks
            #None
            # if more task tobe done for customer who left queue
            # update currTask
            self.customer.currService += 1
            # invoke arrival event for this new task
            ArrivalEvent(sim.now(), sim, self.customer).process(sim)
        else: # if departure from cashier
            cashierNo = self.customer.cashierNo
            if len(sim.states.cashierQ[cashierNo])==0: # if queue empty
                print 'queue empty'
                # make a server idle
                sim.cashierBusy[cashierNo] = False
            else:
                # remove a customer from queue
                cust = sim.states.cashierQ[cashierNo].pop(0)
                print 'cashier queue not empty. first in line ', cust.custNo
                # set queuetime for popped customer
                print 'event time ',self.eventTime
                if(cust.custType == 1):
                    cust.cashierQTime = self.eventTime - \
                                        (cust.arrivalTime+cust.hotfoodQTime+cust.hotfoodSTime +cust.drinksSTime)
                    print cust.arrivalTime,' ',cust.hotfoodQTime,' ',cust.hotfoodSTime ,' ',cust.drinksSTime
                elif(cust.custType == 2):
                    cust.cashierQTime = self.eventTime - \
                                        (cust.arrivalTime+cust.sandwichQTime+cust.sandwichSTime+cust.drinksSTime)
                    print cust.arrivalTime,' ',cust.sandwichQTime,' ',cust.sandwichSTime,' ',cust.drinksSTime
                elif(cust.custType == 3):
                    cust.cashierQTime = self.eventTime - (cust.arrivalTime+cust.drinksSTime)
                    print cust.arrivalTime+cust.drinksSTime
                print 'cashierQTime ',cust.cashierQTime

                # set service time for popped customer
                # service time set previously
                # schedule departure for removed customer
                sim.scheduleEvent(DepartureEvent(sim.now() + cust.cashierSTime, sim, cust))

                # if more task tobe done for customer who left queue
                # no more task left




class Simulator:
    def __init__(self, seed):
        self.eventQ = []
        self.simclock = 0
        self.seed = seed
        self.params = None
        self.states = None

        self.cashier = None #cashier state busy or idle
        self.custNo = 0
        self.end = 100

        self.streamInterarrival = random.Random()
        self.streamGroupSize = random.Random()
        self.streamRouteChoice = random.Random()
        self.streamHotfoodST = random.Random()
        self.streamSandwichST = random.Random()
        self.streamDrinksST = random.Random()
        self.streamHotfoodACT = random.Random()
        self.streamSandwichACT = random.Random()
        self.streamDrinksACT = random.Random()

    def initialize(self):
        print 'initializing ...'
        self.simclock = 0
        self.scheduleEvent(StartEvent(0, self))

    def configure(self, params, states):
        self.params = params
        self.states = states

        self.cashierBusy = [ False for _ in range(params.cashier)]
        self.hotfoodServerBusy = False
        self.sandwichServerBusy = False




    def now(self):
        return self.simclock

    def scheduleEvent(self, event):
        heapq.heappush(self.eventQ, (event.eventTime, event))

    def findGroupSize(self):
        group = self.streamGroupSize.random()
        if group < 0.5:
            group = 1
        elif group < 0.5 + 0.3:
            group = 2
        elif group < 0.5 + 0.3 + 0.1:
            group = 3
        else:
            group = 4
        print 'group size ',group
        return group

    def findCustomerType(self):
        type = self.streamRouteChoice.random();
        if type < 0.8:
            type = 1;
        elif type < 0.8 + 0.15:
            type = 2;
        else:
            type = 3;
        return type

    def getFreeCashier(self):
        for i in range(self.params.cashier):
            if not self.cashierBusy[i]:
                return i;
        return None

    def run(self):
        random.seed(self.seed)
        self.initialize()

        while len(self.eventQ) > 0:
            time, event = heapq.heappop(self.eventQ)

            print event.eventTime, 'Event', event
            if event.eventType == 'EXIT':
                break
            # if self.now() > 90:#apatoto
            #     break

            if self.states != None:
                self.states.update(self, event)

            # print event.eventTime, 'Event', event
            self.simclock = event.eventTime
            event.process(self)

        self.states.finish(self)

    def printResults(self):
        self.states.printResults(self)

    def getResults(self):
        return self.states.getResults(self)


def experiment1():
    # seed = 101
    # sim = Simulator(seed)
    # sim.configure(Params(1.0/30.0, 1, 1, 2), States(1,1,2))
    # sim.run()
    # sim.printResults()

    avgQDelayCashier = []
    avgQDelayHotfood = []
    avgQDelaySandwich = []
    steps = 5

    # normal
    seed = 101

    avgQDelayC = 0.0
    avgQDelayH = 0.0
    avgQDelayS = 0.0
    for i in range(steps):
        sim = Simulator(seed)
        sim.configure(Params(1.0 / 30.0, 1, 1, 2), States(1, 1, 2))
        sim.run()
        sim.printResults()
        avgQDelayC += sim.states.avgCashierQdelay
        avgQDelayH += sim.states.avgHotfoodQdelay
        avgQDelayS += sim.states.avgSandwichQdelay
    avgQDelayC /= float(steps)
    avgQDelayH /= float(steps)
    avgQDelayS /= float(steps)
    avgQDelayCashier.append(avgQDelayC)
    avgQDelayHotfood.append(avgQDelayH)
    avgQDelaySandwich.append(avgQDelayS)

    # varying five employees

    avgQDelayC = 0.0
    avgQDelayH = 0.0
    avgQDelayS = 0.0
    for i in range(steps):
        sim = Simulator(seed)
        sim.configure(Params(1.0 / 30.0, 1, 1, 3), States(1, 1, 3))
        sim.run()
        sim.printResults()
        avgQDelayC += sim.states.avgCashierQdelay
        avgQDelayH += sim.states.avgHotfoodQdelay
        avgQDelayS += sim.states.avgSandwichQdelay
    avgQDelayC /= float(steps)
    avgQDelayH /= float(steps)
    avgQDelayS /= float(steps)
    avgQDelayCashier.append(avgQDelayC)
    avgQDelayHotfood.append(avgQDelayH)
    avgQDelaySandwich.append(avgQDelayS)

    avgQDelayC = 0.0
    avgQDelayH = 0.0
    avgQDelayS = 0.0
    for i in range(steps):
        sim = Simulator(seed)
        sim.configure(Params(1.0 / 30.0, 2, 1, 2), States(2, 1, 2))
        sim.run()
        sim.printResults()
        avgQDelayC += sim.states.avgCashierQdelay
        avgQDelayH += sim.states.avgHotfoodQdelay
        avgQDelayS += sim.states.avgSandwichQdelay
    avgQDelayC /= float(steps)
    avgQDelayH /= float(steps)
    avgQDelayS /= float(steps)
    avgQDelayCashier.append(avgQDelayC)
    avgQDelayHotfood.append(avgQDelayH)
    avgQDelaySandwich.append(avgQDelayS)

    avgQDelayC = 0.0
    avgQDelayH = 0.0
    avgQDelayS = 0.0
    for i in range(steps):
        sim = Simulator(seed)
        sim.configure(Params(1.0 / 30.0, 1, 2, 2), States(1, 2, 2))
        sim.run()
        sim.printResults()
        avgQDelayC += sim.states.avgCashierQdelay
        avgQDelayH += sim.states.avgHotfoodQdelay
        avgQDelayS += sim.states.avgSandwichQdelay
    avgQDelayC /= float(steps)
    avgQDelayH /= float(steps)
    avgQDelayS /= float(steps)
    avgQDelayCashier.append(avgQDelayC)
    avgQDelayHotfood.append(avgQDelayH)
    avgQDelaySandwich.append(avgQDelayS)

    # varying six employees

    avgQDelayC = 0.0
    avgQDelayH = 0.0
    avgQDelayS = 0.0
    for i in range(steps):
        sim = Simulator(seed)
        sim.configure(Params(1.0 / 30.0, 2, 2, 2), States(2, 2, 2))
        sim.run()
        sim.printResults()
        avgQDelayC += sim.states.avgCashierQdelay
        avgQDelayH += sim.states.avgHotfoodQdelay
        avgQDelayS += sim.states.avgSandwichQdelay
    avgQDelayC /= float(steps)
    avgQDelayH /= float(steps)
    avgQDelayS /= float(steps)
    avgQDelayCashier.append(avgQDelayC)
    avgQDelayHotfood.append(avgQDelayH)
    avgQDelaySandwich.append(avgQDelayS)

    avgQDelayC = 0.0
    avgQDelayH = 0.0
    avgQDelayS = 0.0
    for i in range(steps):
        sim = Simulator(seed)
        sim.configure(Params(1.0 / 30.0, 2, 1, 3), States(2, 1, 3))
        sim.run()
        sim.printResults()
        avgQDelayC += sim.states.avgCashierQdelay
        avgQDelayH += sim.states.avgHotfoodQdelay
        avgQDelayS += sim.states.avgSandwichQdelay
    avgQDelayC /= float(steps)
    avgQDelayH /= float(steps)
    avgQDelayS /= float(steps)
    avgQDelayCashier.append(avgQDelayC)
    avgQDelayHotfood.append(avgQDelayH)
    avgQDelaySandwich.append(avgQDelayS)

    avgQDelayC = 0.0
    avgQDelayH = 0.0
    avgQDelayS = 0.0
    for i in range(steps):
        sim = Simulator(seed)
        sim.configure(Params(1.0 / 30.0, 1, 2, 3), States(1, 2, 3))
        sim.run()
        sim.printResults()
        avgQDelayC += sim.states.avgCashierQdelay
        avgQDelayH += sim.states.avgHotfoodQdelay
        avgQDelayS += sim.states.avgSandwichQdelay
    avgQDelayC /= float(steps)
    avgQDelayH /= float(steps)
    avgQDelayS /= float(steps)
    avgQDelayCashier.append(avgQDelayC)
    avgQDelayHotfood.append(avgQDelayH)
    avgQDelaySandwich.append(avgQDelayS)

    # seven employees

    avgQDelayC = 0.0
    avgQDelayH = 0.0
    avgQDelayS = 0.0
    for i in range(steps):
        sim = Simulator(seed)
        sim.configure(Params(1.0 / 30.0, 2, 2, 3), States(2, 2, 3))
        sim.run()
        sim.printResults()
        avgQDelayC += sim.states.avgCashierQdelay
        avgQDelayH += sim.states.avgHotfoodQdelay
        avgQDelayS += sim.states.avgSandwichQdelay
    avgQDelayC /= float(steps)
    avgQDelayH /= float(steps)
    avgQDelayS /= float(steps)
    avgQDelayCashier.append(avgQDelayC)
    avgQDelayHotfood.append(avgQDelayH)
    avgQDelaySandwich.append(avgQDelayS)

    print str(avgQDelayCashier)[1:-1]
    print str(avgQDelayHotfood)[1:-1]
    print str(avgQDelayHotfood)[1:-1]

    cashier = avgQDelayCashier.index(min(avgQDelayCashier))
    hotfood =  avgQDelayHotfood.index(min(avgQDelayHotfood))
    sandwich = avgQDelaySandwich.index(min(avgQDelaySandwich))

    print cashier
    print hotfood
    print sandwich

    if (cashier == 0 or cashier == 2 or cashier == 3 or cashier == 4): # 2 cashiers
        print 'recommended #cashiers: 2'
    else:
        print 'recommended #cashiers: 3'

    if(hotfood==0 or hotfood== 1 or hotfood==3  or hotfood==6 ):# 1 hotfood
        print  'recommended #hotfood services 1'
    else:
        print  'recommended #hotfood services 1'

    if(sandwich == 0 or sandwich == 1 or sandwich == 2 or sandwich == 5):
        print 'recommended #sandwich services 1'
    else:
        print 'recommended #sandwich services 2'



    # max_ = max(util)
    # bestWRTutil = util.index(max_util)
    #
    # min_avgQlength = min(avgQlength)
    # bestWRTQlength = avgQlength.index(min_avgQlength)
    #
    # min_avgQdelay = min(avgQDelay)
    # bestWRTQDelay = avgQDelay.index(min_avgQdelay)


def main():
    experiment1()
#    experiment2()
#    experiment3()


if __name__ == "__main__":
    main()

