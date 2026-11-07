#!/usr/bin/env python3

import argparse
import base64
import random
import time

import grpc

import lab6_pb2
import lab6_pb2_grpc

IMAGE_FILE = 'Flatirons_Winter_Sunrise_edit_2.jpg'


def doAdd(stub, debug=False):
    reply = stub.Add(lab6_pb2.addMsg(a=5, b=10))
    if debug:
        print(reply)


def doRawImage(stub, debug=False):
    img = open(IMAGE_FILE, 'rb').read()
    reply = stub.RawImage(lab6_pb2.rawImageMsg(img=img))
    if debug:
        print(reply)


def doDotProduct(stub, debug=False):
    a = [random.random() for _ in range(100)]
    b = [random.random() for _ in range(100)]
    reply = stub.DotProduct(lab6_pb2.dotProductMsg(a=a, b=b))
    if debug:
        print(reply)


def doJsonImage(stub, debug=False):
    img = open(IMAGE_FILE, 'rb').read()
    encoded = base64.b64encode(img).decode('utf-8')
    reply = stub.JsonImage(lab6_pb2.jsonImageMsg(img=encoded))
    if debug:
        print(reply)


parser = argparse.ArgumentParser(description='gRPC client for measuring server operations')
parser.add_argument('host', help='IP address or hostname of the gRPC server')
parser.add_argument('cmd', choices=['add', 'rawImage', 'dotProduct', 'jsonImage'],
                    help='Operation to perform')
parser.add_argument('reps', type=int, help='Number of repetitions for measurement')
parser.add_argument('-p', '--port', type=int, default=50051, help='Server port (default: 50051)')
parser.add_argument('-d', '--debug', action='store_true', help='Print the response from the server')
args = parser.parse_args()

operations = {
    'add': doAdd,
    'rawImage': doRawImage,
    'dotProduct': doDotProduct,
    'jsonImage': doJsonImage,
}

channel = grpc.insecure_channel(f'{args.host}:{args.port}')
stub = lab6_pb2_grpc.Lab6Stub(channel)

print(f'Running {args.reps} reps against {args.host}:{args.port}')

func = operations[args.cmd]

start = time.perf_counter()
for x in range(args.reps):
    func(stub, debug=args.debug)
delta = ((time.perf_counter() - start) / args.reps) * 1000
print('Took', delta, 'ms per operation')
