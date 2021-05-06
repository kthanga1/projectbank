import customers_pb2
import customers_pb2_grpc
import jsonstore
import grpc
import sys
import time
import concurrent.futures
import asyncio
from grpc import aio
customerPortList = customers_pb2.CustNodes()
port_list = []
out_list = []


class Customer():
    def __init__(self, id, events):
        # unique ID of the Customer
        self.id = id
        # events from the input
        self.events = events
        # a list of received messages used for debugging purpose
        self.recvMsg = list()
        # pointer for the stub
        self.stub = None

        self.name = None


    # TODO: students are expected to create the Customer stub
    def createStub(self, port):
        channel = grpc.aio.insecure_channel('localhost:{}'.format(port))
        self.stub = customers_pb2_grpc.BranchStub(channel)


    # TODO: students are expected to send out the events to the Bank
    async def executeEvents(self):
        print('Executing process {}'.format(self.id))
        for event in self.events:
            print('Event {} ->  Querying balance from Branch {} by customer {}'.format(event.id, self.id , self.id))
            resp = await self.stub.MsgDelivery(event)
            if len(self.recvMsg) > 0:
                self.recvMsg[0].respData.extend(resp.respData)
            else:
                self.recvMsg.append(resp)

async def init_stubs(stub):
    response = await stub.InitStubs(customerPortList, wait_for_ready=False)
    return response

# Create multiple customer processes according to the customer input
async def init_customers(customer):
    # for customer in customers:
    customernode = Customer(customer.id, customer.events)
    customernode.createStub(port_list[str(customer.id)])
    response = await customernode.stub.InitStubs(customerPortList)
    await customernode.executeEvents()
    return customernode


def start_async(customers):
    customerNode = asyncio.run(init_customers(customers))
    return customerNode.recvMsg


def custom_port_pair(customers):
    for cust in customers:
        nodeport = customerPortList.idports.add()
        nodeport.id = cust.id
        nodeport.portNo = port_list[str(cust.id)]


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Excepted arguments: Customer.py $input_file_name ")
        exit()
    filename = sys.argv[1]
    inputreq = jsonstore.read_input(filename)
    port_list = jsonstore.read_portlist()
    # start an equal number of customers as branches.

    inputCustJson = inputreq[1]
    # fetch the list of branch server ports.
    custom_port_pair(inputreq[1])


    with concurrent.futures.ProcessPoolExecutor() as executor:
        futureresults = executor.map(start_async, inputreq[1])
        for ascompleted in futureresults:
            out_list.append(ascompleted[0])







    if jsonstore.write_output(out_list) == 1:
        print("Output written to file --> output.json")

