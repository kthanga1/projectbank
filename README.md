# CSE-531 gRPC Project - distributed bank


## Built With

The project uses the below main libraries and languages.
* [Python 3.8.7](https://www.python.org/downloads/release/python-380/)
* [grpcio](https://grpc.io/docs/languages/python/quickstart/)
* [grpcio-tools](https://grpc.io/docs/languages/python/quickstart/)
* [Protobuf](https://developers.google.com/protocol-buffers)

## Installation requirements
The installation steps followed the docs available in https://grpc.io/docs/languages/python/quickstart/ to setup python virtual 
environment and grpc libraries for this project. 
After you setup the python system-wide or in virtual environment; run the following commands:
```python -m pip install grpcio```
```python -m pip install grpcio-tools```


## Steps to execute:

1. Clone the source to local folder. It consists of the proto file to generate the message file and services.
2. Execute the command to run protobuf compiler to generate the Protobuf message file and Services or run `init.py` that generates proto service and protobuf files.  
   ``python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. ./customers.proto``
3. Copy the input json to customers.json file. The sample customers.json provided is available in the source folder.
4. Run the below command to create branch processes and start the grpc server:
``python -m Branch customers.json``
5. Run command to run the customer requests: `python -m Customer customers.json`
6. Onec customer script executes, the output will be written to `output.json` file.


## <b>Input sample:</b> 

```json
[
  {
    "id" : 1,
    "type" : "customer",
    "events" :  [{ "id": 1, "interface":"query", "money": 400 }]
  },
  {
    "id" : 2,
    "type" : "customer",
    "events" :  [{ "id": 2, "interface":"deposit", "money": 170 },{ "id": 3, "interface":"query", "money": 400 }]
  },
  {
    "id" : 3,
    "type" : "customer",
    "events" :  [{ "id": 4, "interface":"withdraw", "money": 70 },{ "id": 5, "interface":"query", "money": 400 }]
  },
  {
    "id" : 1,
    "type" : "branch",
    "balance" : 400
  },
  {
    "id" : 2,
    "type" : "branch",
    "balance" : 400
  },
  {
    "id" : 3,
    "type" : "branch",
    "balance" : 400
  }
]
```
## <b>Output sample:</b>

```json
{
  "id": 1,
  "status": "recv",
  "respData": [
    {
      "interface": "query",
      "result": "success",
      "money": 500
    }
  ]
}{
  "id": 2,
  "status": "recv",
  "respData": [
    {
      "interface": "deposit",
      "result": "success"
    },
    {
      "interface": "query",
      "result": "success",
      "money": 500
    }
  ]
}{
  "id": 3,
  "status": "recv",
  "respData": [
    {
      "interface": "withdraw",
      "result": "success"
    },
    {
      "interface": "query",
      "result": "success",
      "money": 500
    }
  ]
}
```






