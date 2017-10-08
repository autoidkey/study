#coding: utf-8
import numpy as np
from chainer import Variable, FunctionSet
import chainer.functions as F

class CharRNN(FunctionSet):
	# lstm5 + full1 のRNN 
	def __init__(self, n_vocab, n_units):
		super(CharRNN,self).__init__(
			l0 = F.Linear(1,n_units),
			l1_x = F.Linear(n_units,4*n_units),
			l1_h = F.Linear(n_units,4*n_units),
			l2_x = F.Linear(n_units,4*n_units),
			l2_h = F.Linear(n_units,4*n_units),
			l3_x = F.Linear(n_units,4*n_units),
			l3_h = F.Linear(n_units,4*n_units),
			l4_x = F.Linear(n_units,4*n_units),
			l4_h = F.Linear(n_units,4*n_units),
			l5_x = F.Linear(n_units,4*n_units),
			l5_h = F.Linear(n_units,4*n_units),
			l6 = F.Linear(n_units,n_vocab),
		)

		for param in self.parameters:
			param[:] = np.random.uniform(-0.08,0.08,param.shape)

	def forward_one_step(self,x_data,y_data,state,train=True,dropout_ratio=0.5) :
		x = Variable(x_data,volatile=not train)
		t = Variable(y_data,volatile=not train)
		#add int32？

		h0 = F.relu(self.l0(x))
		#print 'h0:', h0.data
		#print len(h0.data[0])
		h1_in = self.l1_x(F.dropout(h0,ratio= dropout_ratio,train= train)) + self.l1_h(state['h1'])
		c1,h1 = F.lstm(state['c1'],h1_in)
		#print 'h1:', h1_in.data
		#print len(h1_in.data[0])
		h2_in = self.l2_x(F.dropout(h1,ratio= dropout_ratio,train= train)) + self.l2_h(state['h2'])
		c2,h2 = F.lstm(state['c2'],h2_in)
		#print 'h2:', h2_in.data
		#print len(h2_in.data[0])
		h3_in = self.l3_x(F.dropout(h2,ratio= dropout_ratio,train= train)) + self.l3_h(state['h3'])
		c3,h3 = F.lstm(state['c3'],h3_in)
		#print 'h3:', h3_in.data
		#print len(h3_in.data[0])
		h4_in = self.l4_x(F.dropout(h3,ratio= dropout_ratio,train= train)) + self.l4_h(state['h4'])
		c4,h4 = F.lstm(state['c4'],h4_in)
		#print 'h4:', h4_in.data
		#print len(h4_in.data[0])
		h5_in = self.l5_x(F.dropout(h4,ratio= dropout_ratio,train= train)) + self.l5_h(state['h5'])
		c5,h5 = F.lstm(state['c5'],h5_in)
		#print 'h5:', h5_in.data
		#print len(h5_in.data[0])
		y = self.l6(F.dropout(h5,ratio=dropout_ratio,train=train))
		state = {'c1':c1,'h1':h1,'c2':c2,'h2':h2,'c3':c3,'h3':h3,'c4':c4,'h4':h4,'c5':c5,'h5':h5}
		
		#print '------------------	'
		#print y.data
		#print len(y.data[0]),len(y.data)
		#print t.data
		#print len(t.data[0]), len(t.data)
		

		#Expect: in_types[1].ndim == in_types[0].ndim - 1
		return state, F.softmax_cross_entropy(y,t)

	def predict(self,x_data,state):
		x = Variable(x_data,volatile=True)
		#print "x::",x.data

		h0 = F.relu(self.l0(x))
		h1_in = self.l1_x(h0) + self.l1_h(state['h1'])
		c1,h1 = F.lstm(state['c1'],h1_in)
		h2_in = self.l2_x(h1) + self.l2_h(state['h2'])
		c2,h2 = F.lstm(state['c2'],h2_in)
		h3_in = self.l3_x(h2) + self.l3_h(state['h3'])
		c3,h3 = F.lstm(state['c3'],h3_in)
		h4_in = self.l4_x(h3) + self.l4_h(state['h4'])
		c4,h4 = F.lstm(state['c4'],h4_in)
		h5_in = self.l5_x(h4) + self.l5_h(state['h5'])
		c5,h5 = F.lstm(state['c5'],h5_in)
		y = self.l6(h5)
		state = {'c1':c1,'h1':h1,'c2':c2,'h2':h2,'c3':c3,'h3':h3,'c4':c4,'h4':h4,'c5':c5,'h5':h5}

		return state, F.softmax(y)

def make_initial_state(n_units,batchsize=50,train=True):
	#return {name: Variable(np.zeros((batchsize,n_units),dtype=np.float32),volatile=not train)}
	result = {}
	s = ['c1','h1','c2','h2','c3','h3','c4','h4','c5','h5']
	for com in s :
		result.update({com: Variable(np.zeros((batchsize,n_units),dtype=np.float32),volatile=not train)})

	return result



