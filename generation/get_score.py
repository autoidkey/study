import re
import sys #command line
import csv
import MeCab
import codecs
import take_impor_verb as tiv

def context_info(lis) :
	sents = lis[3]
	seps = ['。','？','?']
	for sep in seps :
		sents = sents.replace(sep,".")
		sen = sents.split(".")
		sen.pop()

	info = [lis[2],sen]
	#print(info)
	return info

def mekabuka(string) :
	#内容語のみ
	get = ["名詞","動詞","形容詞"]
	m = MeCab.Tagger ("-Ochasen")
	me = m.parse(string)
	mek = me.split("\n")
	mek.pop()
	mek.pop()
	#print(mek)
	mekabu = []
	for meka in mek :
		mekab = meka.split("\t")
		pos = mekab[3].split("-")
		if pos[0] in get :
			if not (pos[0] == "名詞" and pos[1] == "非自立") :
				mekabu.append(mekab[2])

	return mekabu

def mekabuka_par(array,dic,key) :
	#内容語のみ
	print("array:",array)
	get = ["名詞","動詞","形容詞"]
	m = MeCab.Tagger ("-Ochasen")
	for string in array :
		print(string)
		me = m.parse(string[0])
		mek = me.split("\n")
		mek.pop()
		mek.pop() #EOS
		#print(mek)
		mecab= []
		for meka in mek :
			mekab = meka.split("\t")
			pos = mekab[3].split("-")
			if pos[0] in get :
				if not (pos[0] == "名詞" and pos[1] == "非自立") :
					mecab.append(mekab[2])
					if key in dic :
						dic[key] += 1
					else :
						dic[key] = 1

	if key in dic :
		print("cooc[%s]:" % key,dic[key])	

	return mecab

def comparer(list1,list2):
	num = False
	for l1 in list1 :
		if l1 in list2 :
			num = True
			break
	return num

def cal_perc(dic1,dic2) :
	#dic1/dic2
	score = {}
	ex_mole = {}
	ex_deno = {}
	expre = ["思う","考える","感じる"]

	for key in dic2.keys() :
		if key in dic1 :
			#print("key:",key)
			key_arr = mekabuka(key)
			#print(key_arr)
			
			if len(key_arr) == 0 :
				key_arr.append("none")
				#continue
			

			if key_arr[0] in expre :
				if key_arr[0] in ex_mole :
					ex_mole[key_arr[0]] += dic1[key]
				else :
					ex_mole[key_arr[0]] = dic1[key]

				if key_arr[0] in ex_deno :
					ex_deno[key_arr[0]] += dic2[key]
				else :
					ex_deno[key_arr[0]] = dic2[key]
			else :
				score[key] = dic1[key]/dic2[key]

	for ex in expre :
		if ex in ex_deno :
			score[ex] = ex_mole[ex]/ex_deno[ex]

	return score

#get score from all csv
def get_score(args) :
	pro = {}
	ave = {} 
	ap_q = {}
	cooc = {}
	dist = {}
	hint = ["思う","思います","思っています","考える","考えます","考えています","感じる","感じます","感じています","重要","大切","大事","必要","ないでしょうか","でしょうかね","ではありません","いただきたい","ばならない","どうでしょう","いいですね"]
	type1 = ["思う","思います","思っています","考える","考えます","考えています","感じる","感じます","感じています"]
	type2 = ["重要","大切","大事","必須","必要"]
	type3 = ["ないでしょうか","でしょうかね","ではありません","いただきたい","ばならない","どうでしょう","いいですね"]
	for cs in args :
		print(cs," loading...")
		f = codecs.open(cs,'r','shift_jis')
		dr = csv.reader(f)
		#print("dr: ", dr )

		idfacires = []
		for row in dr :
			idfacires.append(row)  #id,faci,remark  
		f.close()
		#print(idfacires)

		for one in idfacires :
			remark = context_info(one)
			#print(remark)
			if remark[0] == "false" : 
				#not faci
				for sen in remark[1] :
					#search hint
					for ex in hint : 
						#find hint
						if ex in sen :
							#print(sen,":",ex)
							#ここ全然違う wと共起するAはtivと同じ感じで抽出							
							
							if ex in type1 :
								#print("think")
								#print(sen)
								clause = tiv.seperate_clause(sen)
								finder = tiv.search_think_expression(clause)
							elif ex in type2 :
								print(ex)
								#print("impor")
								#print(sen)
								clause = tiv.seperate_clause(sen)
								finder = tiv.search_importance(clause)
							elif ex in type3 :
								#print("other")
								print(sen)
								#sep from right
								sep_ex = sen.rsplit(ex,1)
								if "、" in sep_ex[0] :
									sep_conm = sep_ex[0].split("、")
									finder = [sep_conm[-1]]
								else :
									finder = [sep_ex[0]]
								#print(finder)

							distance = 0
							#findrが空の時
							if finder[0] == '':
								continue
							#compare par faci
							list_par = mekabuka_par(finder,cooc,ex)
							present = idfacires.index(one)
							end = len(idfacires)
							for i in range(present + 1,end) :
								distance += 1
								if idfacires[i][2] == "true" :
									list_faci = mekabuka(idfacires[i][3])
									#共起するか
									apper = comparer(list_par,list_faci)
									if apper :
										#dist
										if ex in dist :
											dist[ex] += distance
										else :
											dist[ex] = distance
										#ap_q
										if ex in ap_q :
											ap_q[ex] += 1
										else :
											ap_q[ex] = 1
										break
									else :
										distance -= 1
								else :
									continue
	print("ファシリテータに現れた:",ap_q)
	print("共起:",cooc)
	print("距離合計:",dist)
	pro = cal_perc(ap_q,cooc)
	print("pro:",pro)
	ave = cal_perc(dist,ap_q)
	print("ave:",ave)
	#return (mole,deno)
	for k in pro.keys() :
		score = pro[k] * ave[k]
		print(k," : ",score)

if __name__  == '__main__' :
	args = sys.argv #filename,arg1,arg2...
	del args[0]
	get_score(args)
