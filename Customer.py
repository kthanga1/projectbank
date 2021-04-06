import grpc
import customers_pb2
import customers_pb2_grpc
import jsonstore
import grpc
import sys
import time
import concurrent.futures


customerPortList = customers_pb2.CustNodes()
port_list = []
out_list = []


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
    def executeEvents(self):
        print('Executing process {}'.format(self.id))
        for event in self.events:
            print('Event {} ->  Querying balance from Branch {} by customer {}'.format(event.id, self.id , self.id))
            # if event.interface == 'query':
            #     time.sleep(3)
            resp = self.stub.MsgDelivery(event)
            if len(self.recvMsg) > 0:
                self.recvMsg[0].respData.extend(resp.respData)
            else:
                self.recvMsg.append(resp)

# Create multiple customer processes according to the customer input
def init_customers(customer):
    customernode = Customer(customer.id, customer.events)
    customernode.createStub(port_list[str(customer.id)])
    # add pair of customer id and port number for creating customer stubs within each branch
    response = customernode.stub.InitStubs(customerPortList)
    print("Initializing Branch stubs --> {}".format("Success" if response.result == 1 else "Failure"))
    customernode.executeEvents()
    return customernode.recvMsg


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

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_results = executor.map(init_customers, inputreq[1])
        for when_completed in future_results:
            out_list.append(when_completed[0])


    if jsonstore.write_output(out_list) == 1:
        print("Output written to file --> output.json")

