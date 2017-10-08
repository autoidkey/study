#coding:utf-8
import time
import math
import sys
import argparse
import cPickle as pickle
import numpy as np
from chainer import cuda,Variable,FunctionSet
import chainer.functions as F
from charRNN import CharRNN,make_initial_state

#arguments
parser = argparse.ArgumentParser()

parser.add_argument('--model', type=str,required=True)
parser.add_argument('--vocabulary', type=str,required=True)

parser.add_argument('--seed', type=int,default=123)
parser.add_argument('--sample', type=int,default=-1) #
parser.add_argument('--primetext', type=str,default='')
parser.add_argument('--length', type=int,default=20) #2000
parser.add_argument('--gpu', type=int,default=-1)

args = parser.parse_args()
np.random.seed(args.seed)

#load vocab
vocab = pickle.load(open(args.vocabulary,'rb'))
ivocab = {}
for c,i in vocab.items():
	ivocab[i] = c

args.primetext = args.primetext.decode('utf-8')

model = pickle.load(open(args.model, 'rb'))
#n_units = model.embed.W.data.shape[1] #
n_units = 128 #cptrain参照

if args.gpu >= 0:
	#cuda.get_device(args.gpu).use()
	cuda.init(args.gpu)
	model.to_gpu()

#initialize generator
state = make_initial_state(n_units,batchsize=1,train=False)
if args.gpu >= 0:
	for key,value in state.items():
		value.data = cuda.to_gpu(value.data)

prev_char = np.array([0],dtype=np.int32)
if args.gpu >=0:
	prev_char = cuda.to_gpu(prev_char)

if len(args.primetext) > 0:
	print("prime:",args.primetext)
	for i in args.primetext :
		#sys.stdout.write(i)
		print i
		prev_char = np.ones((1,1),dtype=np.float32) * vocab[i]
		if args.gpu >= 0:
			prev_char = cuda.to_gpu(prev_char)

		state, prob = model.predict(prev_char, state)
		#index = np.argmax(cuda.to_cpu(prob.data))
		#sys.stdout.write(ivocab[index])

print ""
print "roop start"
for i in xrange(args.length):
	#print 'prev:',prev_char.data
	state, prob = model.predict(prev_char,state)

	if args.sample > 0:
		print "prob"
		probability = cuda.to_cpu(prob.data)[0].astype(np.float64)
		probability /= np.sum(probability)
		index = np.random.choice(range(len(probability)),p=probability)
	else :
		index = np.argmax(cuda.to_cpu(prob.data))
	#print "result:"
	sys.stdout.write(ivocab[index])
	#print ""

	prev_char = np.array([[index]],dtype=np.float32)
	#print "prev2:",prev_char.data
	if args.gpu >= 0:
		prev_char = cuda.to_gpu(prev_char)
else :
	print ""


#python sample.py --model charrnn_... --vocabulary data/vocab.bin --primetext "ex"
