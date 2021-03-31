import grpc
import customers_pb2
import customers_pb2_grpc
import jsonstore
import grpc
import sys
import time
import multiprocessing
from multiprocessing import Queue

customer_list = {}
customerPortList = customers_pb2.CustNodes()
outQueue = Queue()

class Customer:
    def __init__(self, id, events):
        # unique ID of the Customer
        self.id = id
        # events from the input
        self.events = events
        # a list of received messages used for debugging purpose
        self.recvMsg = list()
        # pointer for the stub
        self.stub = None


    # TODO: students are expected to create the Customer stub
    def createStub(self, port):
        channel = grpc.insecure_channel('localhost:{}'.format(port), options=(('grpc.enable_http_proxy', 0),))
        self.stub = customers_pb2_grpc.BranchStub(channel)

    # TODO: students are expected to send out the events to the Bank
    def executeEvents(self, outQueue):
        print('Executing {}'.format(self.id))
        for event in self.events:
            if event.interface == 'deposit':
                print('Starting Event {} ->  deposit money in Branch {} by customer {}'.format(event.id, self.id, self.id))
                resp = self.stub.Deposit(event)
                print(resp)
                self.recvMsg.append(resp)
                if resp.status != 'recv':
                    print('Event {} -> Failed to Deposit money into Branch {} by customer {}'.format(event.id, self.id, self.id))
            elif event.interface == 'withdraw' :
                print('Starting Event {} -> withdraw money from Branch {} by customer {}'.format(event.id, self.id, self.id))
                resp = self.stub.Withdraw(event)
                print(resp)
                self.recvMsg.append(resp)
                if resp.status != 'recv':
                    print('Event {} -> Failed to Deposit money into Branch {} by customer {}'.format(event.id, self.id, self.id))
            elif event.interface == 'query' :
                print('Event {} ->  Querying balance from Branch {} by customer {}'.format(event.id, self.id , self.id))
                time.sleep(3)
                resp = self.stub.Query(event)
                if len(self.recvMsg) > 0:
                    self.recvMsg[0].respData.extend(resp.respData)
                else:
                    self.recvMsg.append(resp)
        outQueue.put(self.recvMsg)



# Create multiple customer processes according to the customer input
def create_customer_processes():
    sys.stdout.flush()
    workers = []
    for customer in customer_list:
        worker = multiprocessing.Process(target=customer_list[customer].executeEvents,args=([outQueue,]))
        workers.append(worker)

    for worker in workers:
        worker.start()
    worker.join()
    results = [outQueue.get() for worker in workers]

    return results


def init_customers(customers, branchports):
    for customer in customers:
        customernode = Customer(customer.id, customer.events)
        customernode.createStub(branchports[str(customer.id)])
        customer_list[customer.id] = customernode
        # add pair of customer id and port number for creating customer stubs within each branch
        nodeport = customerPortList.idports.add()
        nodeport.id=customer.id
        nodeport.portNo = branchports[str(customer.id)]


def initstublist_branches():
    for customer_id in customer_list:
        response = customer_list[customer_id].stub.InitStubs(customerPortList)
        print("Initializing Branch stubs --> {}".format("Success" if response.result == 1 else "Failure"))


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Excepted arguments: Customer.py $input_file_name ")
        exit()
    filename = sys.argv[1]
    inputreq = jsonstore.read_input(filename)
    portlist = jsonstore.read_portlist()

    # start an equal number of customers as branches.
    init_customers(inputreq[1], portlist)

    # fetch the list of branch server ports.
    initstublist_branches()
    # Execute customer processes and invoke the event messages in random, Cust{id} to B{id}
    results = create_customer_processes()

    if jsonstore.write_output(results) == 1:
        print("Output written to file --> output.json")

