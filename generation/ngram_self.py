#coding: utf-8
#2017/1/26 sc 
import sys
import MeCab
import math
import search_hint_ex as she
#print(sys.getdefaultencoding()) #pythonの文字コード
#print(sys.stdout.encoding) #標準出力の文字コード

def ngram_char(array) :
	n_min = 2 
	n_max = 5 
	count = {} #出現回数
	#words = []
	
	for string in array:
		charlist = list(string)
		print(charlist)
		#print(len(charlist))
		for i in range(n_min,n_max + 1):
			start = 0
			while True:
				if start + i <= len(charlist):
					word_array = charlist[start:start + i]
					word = ''.join(word_array)
					#print(word)
					#words.append(word)
					if word in  count:
						count[word] += 1
					else : 
						count[word] = 1
					start += 1
				else :
					break
		
	#for k,v in sorted(count.items(),key = lambda x:x[1],reverse=True):
	#    print(k,v)  #出現回数を表示
	return count

def ngram_word(array) : #単にngramで抜き出す
	n_min = 1 
	n_max = 5 
	count = {} #出現回数
	word_array = []
	
	for string in array: #発言単位
		m = MeCab.Tagger ("-Ochasen")
		me = m.parse(string)
		word_array = me.split("\n") #リスト化
		#print(array) #単語 : 品詞 /行
		
		words = []
		for info in word_array: #単語単位
			arr = info.split("\t")
			if arr[0] == "EOS" or arr[0] == "":
				continue
			else :    
				words.append(arr[0]) #単語だけに
				
		for i in range(n_min,n_max + 1):
			start = 0
			while True:
				if start + i <= len(words):
					word_array = words[start:start + i]
					word = ''.join(word_array)
					#print(word_array)
					if word in  count:
						count[word] += 1
					else : 
						count[word] = 1
					start += 1
				else :
					break
		
	#for k,v in sorted(count.items(),key = lambda x:x[1],reverse=True):
		#print(k,v)  #出現回数を表示
	return count

#頻出単語の計算 ok 
def ngram_fre_con_word(array,nmin) : #内容語ngramで抜き出す
	n_min = nmin
	n_max = 5 
	count = {} #出現回数
	pos_array = []
	pos = {} #単語:[原型,品詞]
	context_words = ["名詞","動詞","副詞","形容詞"]
	error_pos = ["接尾","接頭"]
	
	sentences = []
	for doc in array :
		sents = she.symbol_check(doc)
		sentences += sents
	#print(sentences)

	for string in sentences: #発言単位
		m = MeCab.Tagger ("-Ochasen")
		me = m.parse(string)
		pos_array = me.split("\n") #リスト化
		#print(pos_array) #[単語\t品詞, ...]
		
		words = []
		for info in pos_array: #形態素単位
			arr = info.split("\t")
			if arr[0] == "EOS" or arr[0] == "":
				continue
			else :    
				words.append(arr[0]) #単語だけに
				if arr[0] in pos :
					continue
				else :
					pos[arr[0]] = [arr[2],arr[3]]
		#print("words:\n",words)
		#print("pos:\n",pos)
		
			
		for i in range(n_min,n_max + 1): #ngramにかける
			start = 0
			while True:
				active1 = False
				active2 = False
				if start + i <= len(words):
					#内容語か判定
					s_pos_type = pos[words[start]][1].split("-")
					e_pos_type = pos[words[start + i - 1]][1].split("-")
					#print(pos_type)
					#始まりの形態素
					if s_pos_type[0] in context_words : 
						active1 = True
						if s_pos_type[1] == "接尾" or s_pos_type[1] == "非自立":
							active1 = False
					elif s_pos_type[0] == "接頭詞" :
						active1 = True
					#終わりの形態素
					if e_pos_type[0] == "名詞" : 
						active2 = True
					'''    
					if e_pos_type[0] in context_words : 
						active2 = True
					'''
						#接頭語はおかしいが自動的に省いてる
						
					#ngramで取り出し            
					if active1 and active2 :
						word_array = words[start:start + i] #startからstart+i-1を取り出す
						#末尾を原型へ
						word_array[-1] = pos[word_array[-1]][0]
						word = ''.join(word_array)
						#print(word_array)
						#出現数カウント
						if word in  count:
							count[word] += 1
						else : 
							count[word] = 1
					#次へ        
					start += 1
				else :
					#print("break")
					break
		
	#for k,v in sorted(count.items(),key = lambda x:x[1],reverse=True):
	 #   print(k,v)  #出現回数を表示
	return count

#文書に対するtf値を求める
def ngram_tf_con_word(document,nmin) :
	n_min = nmin
	n_max = 5 
	count = {} #出現回数
	all_word_num = 0 #そう単語数
	pos_array = []
	pos = {} #単語:[原型,品詞]
	context_words = ["名詞","動詞","副詞","形容詞"]
	error_pos = ["接尾","接頭"]
	
	m = MeCab.Tagger ("-Ochasen")
	me = m.parse(document)
	pos_array = me.split("\n") #リスト化
	#print(pos_array) #[単語\t品詞, ...]
		
	words = []
	for info in pos_array: #形態素単位
		arr = info.split("\t")
		if arr[0] == "EOS" or arr[0] == "":
			continue
		else :    
			words.append(arr[0]) #単語だけに
			if arr[0] in pos :
				continue
			else :
				pos[arr[0]] = [arr[2],arr[3]]
	#print("words:\n",words)
	#print("pos:\n",pos)
	
	for i in range(n_min,n_max + 1): #ngramにかける
		start = 0
		while True:
			active1 = False
			active2 = False
			if start + i <= len(words):
				#内容語か判定
				s_pos_type = pos[words[start]][1].split("-")
				e_pos_type = pos[words[start + i - 1]][1].split("-")
				#print(pos_type)
				#始まりの形態素
				if s_pos_type[0] in context_words : 
					active1 = True
					if s_pos_type[1] == "接尾" :
						active1 = False
				elif s_pos_type[0] == "接頭詞" :         
					active1 = True
						
				#終わりの形態素    
				if e_pos_type[0] in context_words : 
					active2 = True    
					#接頭語はおかしいが自動的に省いてる
						
				#ngramで取り出し            
				if active1 and active2 :
					word_array = words[start:start + i] #startからstart+i-1を取り出す
					#末尾を原型へ
					word_array[-1] = pos[word_array[-1]][0]
					word = ''.join(word_array)
					#print(word_array)
					#出現数カウント
					if word in  count:
						count[word] += 1
					else : 
						count[word] = 1
				#次へ        
				start += 1
				all_word_num += 1
			else :
				#print("break")
				break
				
	#文書そう単語数を分母にかける
	for k in count.keys() :
		count[k] *= 1 / all_word_num 
		
	return count

#IDF計算
def ngram_idf_con_word(array,nmin) :  
	n_min = nmin
	n_max = 5 
	idf = {} #辞書
	pos_array = []
	pos = {} #単語:[原型,品詞]
	context_words = ["名詞"] #,"動詞","副詞","形容詞"
	error_pos = ["接尾"] #接頭詞は品詞
	appear_flag = {} #文書中で現れたか
	
	for string in array: #発言単位
		m = MeCab.Tagger ("-Ochasen")
		me = m.parse(string)
		pos_array = me.split("\n") #リスト化
		#print(pos_array) #単語 : 品詞 /行
		
		for key in appear_flag.keys() : #フラグ初期化
			appear_flag[key] = False
			#print(key)
		
		words = []
		for info in pos_array: #単語単位
			arr = info.split("\t")
			if arr[0] == "EOS" or arr[0] == "":
				continue
			else :    
				words.append(arr[0]) #単語だけに
				if arr[0] in pos :
					continue
				else :
					pos[arr[0]] = [arr[2],arr[3]]
		#print("words:\n",words)
		#print("pos:\n",pos)
		
		for i in range(n_min,n_max + 1): #ngramにかける
			start = 0
			while True:
				active1 = False
				active2 = False
				#ここに最小nが1の時の処理
				if start + i <= len(words):
					#内容語か判定
					s_pos_type = pos[words[start]][1].split("-")
					e_pos_type = pos[words[start + i - 1]][1].split("-")
					#print(s_pos_type)
					#始まりの形態素
					if s_pos_type[0] in context_words : 
						active1 = True
						if s_pos_type[1] == "接尾" or s_pos_type[1] == "非自立" :
							active1 = False
					elif s_pos_type[0] == "接頭詞" :         
						active1 = True
						
					#終わりの形態素    
					if e_pos_type[0] in context_words : 
						active2 = True
						
						#接頭語はおかしいが自動的に省いてる
						
					#ngramで取り出し            
					if active1 and active2 :
						word_array = words[start:start + i] #startからstart+i-1を取り出す
						#末尾を原型へ
						word_array[-1] = pos[word_array[-1]][0]
						word = ''.join(word_array)
						#print(word_array)
						#出現数カウント
						if word not in idf:
							idf[word] = 1
							appear_flag[word] = True
						else :
							if not appear_flag[word] :
								idf[word] += 1
								#print(word)
								appear_flag[word] = True
					#次へ        
					start += 1
				else :
					#print("break")
					break
		
	#for k,v in sorted(idf.items(),key = lambda x:x[1],reverse=True):
	 #print(k,v)  #出現回数を表示
	
	#idf値計算
	for key in idf.keys() :
		idf[key] = math.log(len(array) / idf[key]) + 1
		
	return idf

#手がかりが何もない時の処理
def ngram_other(context,nmin) :
	n_min = nmin
	n_max = 5 
	pos_array = []
	pos = {} #単語:[原型,品詞]
	context_words = ["名詞","動詞","副詞","形容詞"]
	error_pos = ["接尾","接頭"]
	phrase = []

	m = MeCab.Tagger ("-Ochasen")
	me = m.parse(context)
	pos_array = me.split("\n") #リスト化
	pos_array.pop()
	pos_array.pop()
	#print(pos_array) #単語 : 品詞 /行

	words = []
	for info in pos_array: #形態素単位
		arr = info.split("\t")
		words.append(arr[0]) #単語だけに
		if arr[0] in pos :
			continue
		else :
			#ngramが対応する辞書
			pos[arr[0]] = [arr[2],arr[3]]
	#print("words:\n",words)
	#print("pos:\n",pos)

	#ngramにかける
	for i in range(n_min,n_max + 1): 
		start = 0
		while True:
			active1 = False
			active2 = False
			if start + i <= len(words):
				#内容語か判定
				s_pos_type = pos[words[start]][1].split("-")
				e_pos_type = pos[words[start + i - 1]][1].split("-")
				#print(pos_type)
				#始まりの形態素
				if s_pos_type[0] in context_words : 
					active1 = True
					if s_pos_type[1] == "接尾" or s_pos_type[1] == "非自立":
						active1 = False
				elif s_pos_type[0] == "接頭詞" :
					active1 = True
				#終わりの形態素
				if e_pos_type[0] == "名詞" : 
						active2 = True
				'''    
				if e_pos_type[0] in context_words : 
					active2 = True
				'''
				#接頭語はおかしいが自動的に省いてる
						
				#ngramで取り出し            
				if active1 and active2 :
					word_array = words[start:start + i] 
					#startからstart+i-1を取り出す
					#末尾を原型へ
					word_array[-1] = pos[word_array[-1]][0]
					word = ''.join(word_array)
					#print(word_array)
					phrase.append(word)
				#次へ        
				start += 1
			else :
				#これ以上調べられない時
				#print("break")
				break
	return phrase


	
def tf_idf(tf,idf) :
	#tf,idf : 辞書
	tfidf = {}
	for k,v in tf.items() :
		if k in idf.keys() :
			tfidf[k] = v * idf[k]
	
	return tfidf
	
	
def display(dic) : #降順ソートして表示
	svalue = sorted(dic.items(), key=lambda x: x[1],reverse = True)
	adv = []    
	for i in range(10) :
		adv.append(svalue[i])
	print(adv)
	

def max_value(dic) :
	max_word = []
	max_val = float("-inf")
	for v in dic.values() :
		if v > max_val :
			max_val = v
	
	for k in dic.keys() :
		if dic[k] == max_val :
			max_word.append(k)
			
	print([max_word,max_val])
	
def fre_words(dic,filta) :
	fre = [] #頻出単語
	max_count = max(dic.values()) #最大出現数
	under_count = max_count - filta #フィルタの範囲
	
	#print("最大出現数",max_count)
	
	for count in reversed(range(under_count,max_count + 1)) : 
		for k,v in dic.items():
			if count == v:
				fre.append([k,v])
	
	return fre #リスト

if __name__ == '__main__':
	#st = ["私はリンゴが好き","リンゴは青くない","リンゴジュースは美味しい","私はバナナが嫌い","バナナとリンゴは果物だ"]
	#pre_con = ["【論点まとめ】「児童福祉・児童虐待への対応」についての議論のまとめです。児童福祉、特に児童虐待に対しての問題提起がなされました。","実際に、主任児童委員になって気づくことがたくさんあります。サポーター会議の在り方、民生子ども課の役割、保健所との連携、もちろん主任児童委員の役割も含めて、とにかく、話すこと。少しでも気にある家庭があったら、関係者が集まって話し合うこと。そして図式化すること。そこから、各関係者の仲間意識とどうしたら解決に結びつかが見えてくるかもしれません。児童養護施設のイメージもかえないと。本当の一時保護ができるように。"]
	#pre_con = ["リンゴバナナ","リンゴみかんバナナ","バナナバナナみかん"]
	pre_con = ["私の地域では、町内会がありますが。本当に機能していないと思います。町内会費払っているけど、町内で何かをやっていることなんてありません。他の地域では、学区一斉清掃なる取り組み、町内会ぐるみの防災訓練など。子供会は町内の取り組みです。でも子供がいない家庭では関わりがないです。子供会は良くお祭りごとをやっていますが。町内のつながりを深めることにより、防犯防災、そして、外国人がいたら手助け、高齢者や障害を持つ方のこえかけ。Naoさんが言うとおりです。でもうまくやっている町内もあると思います。どう違いがあるのかと思いました。古くからいる方がオープンにするか、しないかの違いなのでしょうか・・","町内会で、役員などは強制するが、活動は活発でないんです。また、働いている世代は、年長者さんとの時間を合わせることができません。ある役目は、正月や年末は絶対とか。朝のごみだし見回りは絶対とか・・でも働いていたら絶対無理なんですよね。そういう頑固たる対応ではやめようと思うはずです。それに見合う地域ぐるみの活動があればいいですが、所詮役員だけというか・・・ですから若い方は入らないということになるのではないかと思います。"]
	fre = ngram_fre_con_word(pre_con,2)
	tf = ngram_tf_con_word(pre_con[-1],1)
	idf = ngram_idf_con_word(pre_con,1)
	tfidf = tf_idf(tf,idf) #正確には違う
	print("fre")
	word = fre_words(fre,0)
	print(word)
	#print("tf")
	#print(tf)
	#print("idf")
	#max_value(idf)
	#print("tfidf")
	#max_value(tfidf)
	'''
	text = "高次元多関節機構を用いた研究がある。"
	phrase = ngram_other(text,2)
	print(phrase)
	'''

	
#頻出単語探索方法
#1.ngramで頻出文字列を抽出


#12/20メモ
#tf値と頻出を勘違い
#tf値は文書ごとの単語で出る
#ここでは最後の文書のtfだけでよさげ

#point
#arr[i,j]ではi番目からj-1番目までを取り出す
#