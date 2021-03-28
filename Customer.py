import grpc
import customers_pb2
import customers_pb2_grpc
import jsonstore
import grpc
import sys
import time

customer_list = {}
customerPortList = customers_pb2.CustNodes()

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
    def executeEvents(self, query):
        for event in self.events:
            if event.interface == 'deposit' and query is False:
                print('Starting Event {} ->  deposit money in Branch {} by customer {}'.format(event.id, self.id, self.id))
                resp = self.stub.Deposit(event)
                print(resp)
                self.recvMsg.append(resp)
                if resp.status != 'recv':
                    print('Event {} -> Failed to Deposit money into Branch {} by customer {}'.format(event.id, self.id, self.id))
            elif event.interface == 'withdraw' and query is False:
                print('Starting Event {} -> withdraw money from Branch {} by customer {}'.format(event.id, self.id, self.id))
                resp = self.stub.Withdraw(event)
                print(resp)
                self.recvMsg.append(resp)
                if resp.status != 'recv':
                    print('Event {} -> Failed to Deposit money into Branch {} by customer {}'.format(event.id, self.id, self.id))
            elif event.interface == 'query' and query is True:
                print('Event {} ->  Querying balance from Branch {} by customer {}'.format(event.id, self.id , self.id))
                resp = self.stub.Query(event)
                if len(self.recvMsg) > 0:
                    self.recvMsg[0].respData.extend(resp.respData)
                else:
                    self.recvMsg.append(resp)
        return self.recvMsg


def executeEvents():
    for cust_id in customer_list:
        result = customer_list[cust_id].executeEvents(False)
    # Query the final responses with 3 sec wait
    time.sleep(3)
    for cust_id in customer_list:
        result = customer_list[cust_id].executeEvents(True)
        print(customer_list[cust_id].recvMsg)


def spincustomers(customers, branchports):
    for customer in customers:
        customernode = Customer(customer.id, customer.events)
        customernode.createStub(portlist[str(customer.id)])
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
    spincustomers(inputreq[1], portlist)
    # fetch the list of branch server ports.
    initstublist_branches()

    #Execute customer events and update the response to output file
    executeEvents()

    if jsonstore.write_output(customer_list) == 1:
        print("Output written to file --> output.json")

