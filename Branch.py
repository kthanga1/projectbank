import threading
import grpc
import customers_pb2
import customers_pb2_grpc
from concurrent import futures
import multiprocessing
import sys
import os
import jsonstore
import socket
import time
import datetime
import asyncio
from grpc_reflection.v1alpha import reflection
from grpc_health.v1 import health
from grpc_health.v1 import health_pb2
from grpc_health.v1 import health_pb2_grpc
from grpc import aio

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

        self.lock = threading.Lock()

    # TODO: students are expected to process requests from both Client and Branch
    async def MsgDelivery(self, request, context):
        # request = next(request_iterator)
        print('Execute {} at Branch {} '.format(request.interface, self.id))
        if request.interface == "withdraw":
            resp = await self.Withdraw(request, context)
        elif request.interface == "deposit":
            resp = await self.Deposit(request, context)
        elif request.interface == "query":
            resp = await self.Query(request, context)
        elif request.interface == "propagate_deposit":
            resp = self.Update_Deposit(request, context)
        elif request.interface == "propagate_withdraw":
            resp = self.Update_Withdraw(request, context)
        return resp

    async def Withdraw(self, request, context):
        print('Branch {} -- Current balance  {} withdraw {}'.format(self.id, self.balance, request.money))
        self.update_balance(request.money, 'withdraw')
        print('New balance  {} '.format(self.balance))
        # Constructing protobuf response
        response = customers_pb2.EventResponse(id=self.id, status="recv")
        response.respData.append(customers_pb2.InterfaceResponse(interface=request.interface,
                                                                 result="success"))
        await self.Propagate_Withdraw(request, context)
        return response

    async def Deposit(self, request, context):
        print('Branch {} -- Current balance  {} deposit {}'.format(self.id, self.balance, request.money))
        self.update_balance(request.money, 'deposit')
        print('New balance  {} '.format(self.balance))
        # Constructing protobuf response
        response = customers_pb2.EventResponse(id=self.id, status="recv")
        response.respData.append(customers_pb2.InterfaceResponse(interface=request.interface,
                                                                 result="success"))

        await self.Propagate_Deposit(request, context)
        return response

    async def Query(self, request, context):
        print('Query balance of branch {}'.format(self.id))
        time.sleep(3)
        try:
            self.lock.acquire(blocking=True)
            money = self.balance
        finally:
            self.lock.release()
        response = customers_pb2.EventResponse(id=self.id, status="recv")
        # Constructing protobuf response
        response.respData.append(customers_pb2.InterfaceResponse(interface=request.interface,
                                                                 result="success", money=money))
        return response

    async def Propagate_Deposit(self, request, context):
        print('Propagating deposit to other branches {}'.format(request.money))
        for stub in self.stubList:
            propagate_req = customers_pb2.Event(id=request.id, interface="propagate_deposit", money=request.money)
            resp = await self.stubList[stub].MsgDelivery(propagate_req)
            print('Propagated deposit  {} balance to branch {} '.format(request.money, stub))

    async def Propagate_Withdraw(self, request, context):
        print('Propagating withdraw to other branches {}'.format(request.money))
        for stub in self.stubList:
            propagate_req = customers_pb2.Event(id=request.id, interface="propagate_withdraw", money=request.money)
            resp = await self.stubList[stub].MsgDelivery(propagate_req)
            print('Propagated withdraw  {} balance to branch {} '.format(request.money, stub))

    def Update_Deposit(self, request, context):
        self.update_balance(request.money, 'deposit')
        return customers_pb2.ResponseStatus(result=customers_pb2.SUCCESS)

    def Update_Withdraw(self, request, context):
        self.update_balance(request.money, 'withdraw')
        return customers_pb2.ResponseStatus(result=customers_pb2.SUCCESS)

    async def InitStubs(self, request, context):
        status = customers_pb2.ResponseStatus(result=customers_pb2.FAILURE)
        try:
            idports = request.idports
            for idport in idports:
                if idport.id is not self.id:
                    channel = grpc.aio.insecure_channel('localhost:{}'.format(idport.portNo))
                    self.stubList[idport.id] = customers_pb2_grpc.BranchStub(channel)

            if len(self.stubList) > 0:
                status.result = customers_pb2.Result.SUCCESS
            print('Customer stub list initialized in Branches')
        except Exception as excp:
            print(excp)
        return status

    def update_balance(self, money, action):
        print(f'update deposit {money}')
        try:
            self.lock.acquire(blocking=True)
            if action == 'withdraw':
                self.balance = self.balance - money
            elif action == 'deposit':
                self.balance = self.balance + money
        finally:
            self.lock.release()
        print(f'balance{self.balance}')
        return self.balance


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
async def _wait_forever(server):
    try:
        while True:
            time.sleep(datetime.timedelta(days=1).total_seconds())
    except KeyboardInterrupt:
        await server.stop(1)


# Create multiple branch processes
def create_branch_processes(port, branch_id, balance, branches):
    sys.stdout.flush()
    workers = []
    bind_address = 'localhost:{}'.format(port)

    worker = multiprocessing.Process(target=create_branch_async,
                                     args=(bind_address, port, branch_id, balance, branches),
                                     name='Branch_{}'.format(branch_id))

    workers.append(worker)
    worker.start()
    print('starting branch {} server in address {}, PID - {}'.format(branch_id, bind_address, worker.pid))
    return worker.pid


def create_branch_async(bind_address, port, branch_id, balance, branches):
    print(bind_address)
    asyncio.run(start_server(bind_address, port, branch_id, balance, branches))


async def start_server(bind_address, port, branch_id, balance, branches):
    """Start a server in a subprocess."""
    server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10, ))
    customers_pb2_grpc.add_BranchServicer_to_server(Branch(branch_id, balance, branches), server)
    health_servicer = health.HealthServicer(experimental_non_blocking=True,
                                            experimental_thread_pool=futures.ThreadPoolExecutor(max_workers=1))
    health_pb2_grpc.add_HealthServicer_to_server(health_servicer, server)

    services = tuple(service.full_name for service in customers_pb2.DESCRIPTOR.services_by_name.values()) \
               + (reflection.SERVICE_NAME, health.SERVICE_NAME)

    reflection.enable_server_reflection(services, server)
    server.add_insecure_port(bind_address)
    await server.start()
    # Mark all services as healthy.
    overall_server_health = ""
    for service in services + (overall_server_health,):
        health_servicer.set(service, health_pb2.HealthCheckResponse.SERVING)

    await server.wait_for_termination()


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
