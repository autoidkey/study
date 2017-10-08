#coding: utf-8
import time
import math
import sys
import argparse
import cPickle as pickle
import copy
import os
import codecs
import numpy as np
from chainer import cuda, Variable,FunctionSet,optimizers
import chainer.functions as F
from charRNN import CharRNN, make_initial_state

#input data
def load_data(args):
	vocab = {}
	print('%s/input2.txt'%args.data_dir)
	words = codecs.open('%s/input_001.txt' % args.data_dir, 'rb','UTF-8').read()
	'''
	dat=[]
	for l in open('%s/input2.txt' % args.data_dir).readlines():
		#print l[:-1]
		#data = eval(l[:-1])
		data = l[:-1]
		dat.append(data)
		#dat.append(l[:-1])
	'''

	#words = dat
	#print words
	#dataset = np.ndarray((1,1),dtype = np.float32)
	dataset = np.ndarray((len(words),1),dtype = np.float32)
	#dataset = np.ndarray((len(words)),dtype = np.float32)
	for i,word in enumerate(words):
		if word not in vocab:
			vocab[word] = len(vocab)
			#print i,word
		dataset[i] = vocab[word]
		#dataset[i] = word
		#dataset.update({i:word})
	print 'corpus length', len(words)
	print 'vocab size ::' ,len(vocab)
	return dataset, words, vocab

#argmuents
parser = argparse.ArgumentParser()
parser.add_argument('--data_dir', type =str, default='data/tinyshakespeare')
parser.add_argument('--checkpoint_dir', type =str, default='cv')
parser.add_argument('--gpu', type =int, default=0)
parser.add_argument('--rnn_size', type =int, default=128)
parser.add_argument('--learning_rate', type =float, default=2e-3)
parser.add_argument('--learning_rate_decay', type =float, default=0.97)
parser.add_argument('--learning_rate_decay_after', type =int, default=10)
parser.add_argument('--decay_rate', type =float, default=0.95)
parser.add_argument('--dropout', type =float, default=0.10)
parser.add_argument('--seq_length', type =int, default=50)
parser.add_argument('--batchsize', type =int, default=5000)
parser.add_argument('--epochs', type =int, default=50)
parser.add_argument('--grad_clip', type =int, default=5)
parser.add_argument('--init_from', type =str, default='')

#too long...

args = parser.parse_args()
if not os.path.exists(args.checkpoint_dir):
	os.mkdir(args.checkpoint_dir)

#基礎変数
n_epochs = args.epochs
n_units = args.rnn_size #128
batchsize = args.batchsize
bprop_len = args.seq_length
grad_clip = args.grad_clip

# データのロード
train_data, words, vocab = load_data(args)
pickle.dump(vocab, open('%s/vocab.bin'%args.data_dir,'wb'))
#sys.exit()

#モデル呼び出し
if len(args.init_from) > 0:
	model = pickle.load(open(args.init_from,'rb'))
else :
	model = CharRNN(len(vocab),n_units)

#どーでもいい
if args.gpu >= 0 :
	#cuda.get_device(args.gpu).use()
	cuda.init(args.gpu)
	model.to_gpu()

#RNNモデルセット
optimizer = optimizers.RMSprop(lr = args.learning_rate,alpha=args.decay_rate,eps=1e-8)
optimizer.setup(model)


whole_len = train_data.shape[0]
print 'whole_len:', whole_len
jump = whole_len/batchsize
print 'jump:', jump
epoch = 0
start_at = time.time()
cur_at = start_at
#初期化
state = make_initial_state(n_units,batchsize=batchsize)
#print state
#損失計算
if args.gpu >= 0:
	accum_loss = Variable(cuda_zeros(()))
	for key,value in state.items():
		value.data = cuda.to_gpu(value.data)
else : 
	accum_loss = Variable(np.zeros((),dtype = np.float32))


print 'going to train {} iterations'. format(jump*n_epochs)
#学習roop
for i in xrange(jump*n_epochs):
	#making batch add int32
	#毎回異なるものが代入 50パターン
	x_batch = np.array([train_data[(jump*j + i)%whole_len]
		for j in xrange(batchsize)], dtype=np.float32)
	y_batch = np.array([train_data[(jump*j + i + 1)%whole_len]
		for j in xrange(batchsize)], dtype=np.int32)
	new_y_b = np.ndarray(batchsize,dtype=np.int32)
	for k in range(batchsize):
		new_y_b[k] = y_batch[k][0]
	y_batch = new_y_b

	#print 'xbatch', x_batch
	#print len(x_batch)
	#print 'ybatch', y_batch #y_batch[0][0]
	#print new_y_b,new_y_b[5],new_y_b[10]


	if args.gpu >= 0:
		x_batch = cuda.to_gpu(x_batch)
		y_batch = cuda.to_gpu(y_batch)

	#learning
	state, loss_i = model.forward_one_step(x_batch,y_batch,state,dropout_ratio=args.dropout)
	accum_loss += loss_i

	if (i + 1) % bprop_len == 0: # Run truncate BPTT
		now = time.time()
		print '{}/{}, train_loss = {}, time = {:.2f}'.format((i+1)/bprop_len, jump, accum_loss.data/bprop_len, now-cur_at)
		cur_at = now
		#更新
		optimizer.zero_grads()
		accum_loss.backward()
		accum_loss.unchain_backward()
		if args.gpu >= 0:
			accum_loss = Variable(cuda.zeros(()))
		else :
			accum_loss = Variable(np.zeros((),dtype = np.float32))

		optimizer.clip_grads(grad_clip)
		optimizer.update()

	if (i + 1) % 10000 == 0:
		fn = ('%s/charrnn_epoch_%.2f.chainermodel' % (args.checkpoint_dir,float(i)/jump))
		pickle.dump(copy.deepcopy(model).to_cpu(),open(fn,'wb'))
		print i,"/", jump*n_epochs

	if (i + 1) % jump == 0:
		epoch += 1

		if epoch >= args.learning_rate_decay_after :
			optimizer.lr *= args.learning_rate_decay
			print 'decayed learning rate by a factor {} to {}'.format(args.learning_rate_decay,optimizer.lr)

	sys.stdout.flush()

#python cptrain.py -data_dir data

