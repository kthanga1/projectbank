import grpc
import customers_pb2
import customers_pb2_grpc
from concurrent import futures
import multiprocessing
import sys
import os
import socket
import jsonstore
import atexit
import time
import datetime

_ONE_DAY = datetime.timedelta(days=1)
_branches = []
_customers = []
pidList = []
portList = {}


class Branch(customers_pb2_grpc.BranchServicer):
    def __init__(self, id, balance, branches):
        # unique ID of the Branch
        self.id = id
        # replica of the Branch's balance
        self.balance = balance
        # the list of process IDs of the branches
        self.branches = branches
        # the list of Client stubs to communicate with the branches
        # modified it to list for mapping stubs to branch ids
        self.stubList = {}
        # a list of received messages used for debugging purpose
        self.recvMsg = list()
        # iterate the processID of the branches

        # TODO: students are expected to store the processID of the branches
        self.processId = os.getpid()

    # TODO: students are expected to process requests from both Client and Branch
    def MsgDelivery(self, request, context):
        print('{} branch balance with {} '.format(request.interface, request.money))
        if request.interface == "withdraw":
            self.balance = self.balance - request.money
        elif request.interface == "deposit":
            self.balance = self.balance + request.money
        return customers_pb2.ResponseStatus(result=customers_pb2.SUCCESS)

    def Withdraw(self, request, context):
        print('Current balance  {} withdraw {}'.format(self.balance, request.money))
        if request.interface == "withdraw":
            self.balance = self.balance - request.money
        print('New balance  {} '.format(self.balance))
        # Constructing protobuf response
        response = customers_pb2.EventResponse(id=self.id, status="recv")
        innerResp = response.respData.add()
        innerResp.interface = request.interface
        innerResp.result = "success"
        self.Propagate_Withdraw(request, context)
        return response

    def Deposit(self, request, context):
        print('Current balance  {} deposit {}'.format(self.balance, request.money))
        if request.interface == "deposit":
            self.balance = self.balance + request.money
        print('New balance  {} '.format(self.balance))
        # Constructing protobuf response
        response = customers_pb2.EventResponse(id=self.id, status="recv")
        innerResp = response.respData.add()
        innerResp.interface = request.interface
        innerResp.result = "success"
        self.Propagate_Deposit(request, context)
        return response

    def Query(self, request, context):
        print('Query balance of branch {}'.format(self.id))
        response = customers_pb2.EventResponse(id=self.id, status="recv")
        # Constructing protobuf response
        innerResp = response.respData.add()
        innerResp.interface = request.interface
        innerResp.result = "success"
        innerResp.money = self.balance

        return response

    def Propagate_Deposit(self, request, context):
        print('Propagating deposit to other branches {}'.format(request.money))
        for stub in self.stubList:
            resp = self.stubList[stub].MsgDelivery(request)
            print('Propagated deposit  {} balance to branch {} '.format(request.money, stub))
        return resp

    def Propagate_Withdraw(self, request, context):
        print('Propagating withdraw to other branches {}'.format(request.money))
        for stub in self.stubList:
            resp = self.stubList[stub].MsgDelivery(request)
            print('Propagated withdraw  {} balance to branch {} '.format(request.money, stub))
        return resp

    def InitStubs(self, request, context):
        status = customers_pb2.ResponseStatus(result=customers_pb2.FAILURE)
        idports = request.idports
        for idport in idports:
            if idport.id is not self.id:
                channel = grpc.insecure_channel('localhost:{}'.format(idport.portNo),
                                                options=(('grpc.enable_http_proxy', 0),))
                self.stubList[idport.id] = customers_pb2_grpc.BranchStub(channel)
        if len(self.stubList) > 0:
            status.result = customers_pb2.Result.SUCCESS
        print('Customer stub list initialized in Branches')
        return status


# Grpc example code to find an available port
def get_free_loopback_tcp_port():
    if socket.has_ipv6:
        tcp_socket = socket.socket(socket.AF_INET6)
    else:
        tcp_socket = socket.socket(socket.AF_INET)
    tcp_socket.bind(('', 0))
    address_tuple = tcp_socket.getsockname()
    tcp_socket.close()
    return address_tuple[1]

# Grpc example code to wait forever for 1 day
def _wait_forever(server):
    try:
        while True:
            time.sleep(_ONE_DAY.total_seconds())
    except KeyboardInterrupt:
        server.stop(1)


# Create multiple branch processes
def create_branch_processes(port, branch_id, balance, branches):
    sys.stdout.flush()
    workers = []
    bind_address = 'localhost:{}'.format(port)

    worker = multiprocessing.Process(target=start_server,
                                     args=(bind_address, port, branch_id, balance, branches),
                                     name='Branch_{}'.format(branch_id))

    workers.append(worker)
    worker.start()
    print('starting branch {} server in address {}, PID - {}'.format(branch_id, bind_address, worker.pid))
    return worker.pid



def start_server(bind_address, port, branch_id, balance, branches):
    """Start a server in a subprocess."""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=2, ))
    customers_pb2_grpc.add_BranchServicer_to_server(Branch(branch_id, balance, branches), server)
    server.add_insecure_port(bind_address)
    server.start()
    # server.wait_for_termination()
    _wait_forever(server)



def spinbranches(branch_ids, branch_list):
    # Input paramteres include list of branch id's and branch input list incl money
    for branch in branch_list:
        port = get_free_loopback_tcp_port()
        portList[branch.id] = port
        pid = create_branch_processes(port, branch.id, branch.balance, branch_ids)
        pidList.append(pid)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Excepted arguments: $input_file_name ")
        exit()

    filename = sys.argv[1]
    inputreq = jsonstore.read_input(filename)
    spinbranches(inputreq[2], inputreq[3])  # Pass branchlist, branchid array and port no
    print(portList)
    status = jsonstore.write_portlist(portList)
    if len(pidList) > 0 and status is True:
        print("Launched servers successfully")
    else:
        print("Launching servers failed")
