import customers_pb2
import json
from google.protobuf import json_format



def read_input(path):
    #parse the json and identify customer and branch list
    #Will only accept equal and corresponding number of customer branches.
    customerlist = []
    branchlist = []
    branchids = []
    customerids = []
    with open(path) as input_json:
        for item in json.load(input_json):
            if item["type"] == 'customer':
                customer = json_format.Parse(json.dumps(item), customers_pb2.CustomersI())
                customerlist.append(customer)
                customerids.append(item["id"])
            elif item["type"] == 'branch':
                customer = json_format.Parse(json.dumps(item), customers_pb2.CustomersI())
                branchlist.append(customer)
                branchids.append(item["id"])
            else:
                print("Bad type")
    if len(customerlist) == len(branchlist):
        for i in range(len(customerlist)):
            if customerlist[i].id is not branchlist[i].id:
                print('Expected corresponding number of customers to branches')
    return customerids, customerlist , branchids, branchlist


def write_output(results):
    with open('output.json', 'w') as file:
        for result in results:
            file.writelines(json_format.MessageToJson(result[0]))
        return 1


def write_portlist(ports):
    with open('portlist.json', 'w') as file:
        json.dump(ports, file)
        return True


def read_portlist():
    portlist = []
    with open('portlist.json') as file:
        portlist = json.load(file)
    return portlist