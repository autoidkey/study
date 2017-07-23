#coding :utf-8
#2017/2/9 sc
import CaboCha
import MeCab
import re
#import take_impor_verb as tiv
#import gene_q as gq

#文から述語と項を抽出
def pre_arg_str(text) :
	predicate = []
	#述語(名詞の中に形容動詞あり)
	pre_type = ["名詞",["動詞","形容詞"]]
	connection = ["連体化","接続助詞","並立助詞"] #接続型
	skip = False
	end_point = ["句点","一般"]
	
	#文節の三重リストへ
	clauses = seperate_clause(text) 
	
	arg_cla =[]
	end = ["","",""] #エラー対策
	cla_num = -1 #今ループ中の番号
	inter_pre =""
	if len(clauses) == 1 :
		#文節が一つの時
		subject = clauses[0][0][3].split("/") #[主辞,機能語]
		morphs = clauses[0][1][0:int(subject[0]) + 1] #述語部
		for m in reversed(morphs) :
			words = morph_array(m)
			inter_pre = words[0] + inter_pre
			#真っ白な項を作成

	else :
		#述語となる文節を後ろから探す
		for cla in reversed(clauses) :
			#subject = cla[0][3].split("/") #[主辞,機能語]
			if cla_num < -1 :
				#最後の文節以外の各文節末要素
				end = morph_array(cla[1][-1])
			
			if not end[2] in end_point and not skip :

				#述語であると思われる部分を抜き出す(主辞の前部分)
				#後ろの細かいのが欲しい時はここを変える
				#述語核の品詞
				pos_type = ""
				#num = cla_num
				while True :
					#print("pos:",pos_type)
					#print("cla:",clauses[num])
					subject = clauses[cla_num][0][3].split("/") #[主辞,機能語]
					morphs = clauses[cla_num][1][0:int(subject[0]) + 1] #述語部
					words_array = morph_array(morphs[int(subject[0])]) #述語核
				
					if pos_type != "":
						#2周目以降
						#文節末形態素
						last_m = morph_array(clauses[cla_num][1][-1])
						#print("last:",last_m)
						if not pos_type == words_array[1] or not last_m[2] in connection : 
							#接続詞でない時/瀕死違い
							cla_num += 1
							subject = clauses[cla_num][0][3].split("/") 
							morphs = clauses[cla_num][1][0:int(subject[0]) + 1] 
							words_array = morph_array(morphs[int(subject[0])]) 
							break
					else :
						#一週目
						pos_type = words_array[1]
						#名詞のとき(大丈夫?)
						if pos_type == "名詞" :
							for m in reversed(morphs) :
								words = morph_array(m)
								inter_pre = words[0] + inter_pre
							break
							
					un_mor = clauses[cla_num][1][int(subject[0])+1:] #非述語部
					#print("unmor:",un_mor)
					#非述語部
					for m in reversed(un_mor) :
						words = morph_array(m)
						inter_pre = words[0] + inter_pre
				
					#述語部
					for m in reversed(morphs) :
						words = morph_array(m)
						inter_pre = words[0] + inter_pre
					#num += -1
					#print("pre:",inter_pre)
					
					if - len(clauses) == cla_num :
						break
					else :
						cla_num += -1

				#------------------------------------------
				#print(words_array)
				#print(clauses[cla_num][0][1])
				#述語が名詞か動詞、形容詞かで分岐
				#述語の核?の部分から判断
				if words_array[1] in pre_type[0] :
					#print("noun")
					if words_array[2] == "非自立" : 
						new_text = text[:text.rfind(words_array[0])]
						inter_pre,arg_cla = pre_arg_str(new_text)
						break
					elif words_array[2] == "形容動詞語幹" :
						#ちょっと怪しい(名刺だけでも形容動詞の奴がある)
						if words_array[-3] == "可能" :
							w =  morph_array(clauses[cla_num - 1][1][0])
							if w[0] == "こと" :
								#「ことが可能」以下をカット
								#print("recursion")
								new_text = text[:text.rfind("こと")] 
								inter_pre,arg_cla = pre_arg_str(new_text)
								break
						else :
							arg_cla = pre_is_veradj(clauses,clauses[cla_num][0][1])
							skip = True
					else :    
						arg_cla = pre_is_noun(clauses,clauses[cla_num][0][1])
						skip = True
				elif words_array[1] in pre_type[1] :
					#print("verb")
					#こと○できるの時
					if words_array[-3] == "できる" :
						w =  morph_array(clauses[cla_num - 1][1][0])
						if w[0] == "こと" :
							#「ことができる」以下をカット
							#print("recursion")
							new_text = text[:text.rfind("こと")] 
							inter_pre,arg_cla = pre_arg_str(new_text)
							break
						else :
							#「交換できる」などの処理
							arg_cla = pre_is_veradj(clauses,clauses[cla_num][0][1])
							#print(arg_cla)
							skip = True
					else:
						arg_cla = pre_is_veradj(clauses,clauses[cla_num][0][1])
						#print(arg_cla)
						skip = True
				else :
					cla_num += -1
					continue
			elif end in end_point :
				#。や?とかが来た時
				break
			else : 
				cla_num += -1
				#print("skip")
				continue
			
	#暫定で述語を原型に
	#主辞以外もないと同士が変わる可能性あり
	inter_pre = pre_check(inter_pre)

	'''        
	argment = []
	for cla in arg_cla :
		string = ""
		for morph in cla[1] :
			words = morph.split("\t")
			word = words[0]
			string += word
		argment.append(string)    
	print(argment)
	'''
	
	
	#できる使用しても良くね?
	#skipは再帰のときbreakだとダメだから導入
	return [inter_pre,arg_cla]  #述語 項(リスト)
			
			
#項の抽出 変数=(三重リスト,文,述語の文節)
#項に名詞がない場合はおかしいはず
#とりあえずなんでも遡るようにする
def pre_is_noun(clauses,pre_num):
	# ***** noun 
	#argment = []
	sentences = []
	sentence = ""

	#遡れるだけ遡り述語とする
	for cla in reversed(clauses) : #[文節,[]]
		r =cla[0][2].split("D") #[係先,""] 
		#係先が述語の文節の時(直接述語にかかっている場合)
		#print(r)
		if r[0] == pre_num :
			#直接述語にかかっている項を記録
			#argment.insert(0,cla)
			cla_str = ""
			for m_info in cla[1] :
				morph = morph_array(m_info)
				cla_str += morph[0] #because arg
			#print("cla:",cla_str)
			sentence = cla_str + sentence

			sentence = prev_arg_check(clauses,cla,sentence)
			#print("sen:",sentence)
			#句点の処理 削除(削除か連結か)
			sep_sen = sentence.split("、")
			sentence = sep_sen[-1]
			#ここが微妙
	sentences.append(sentence)
	return [[],sentences]


#述語が動詞の時の項の処理
def pre_is_veradj(clauses,pre_num):
	# ***** verb 
	#argment = []
	sentences = []
	sentence = ""
	relation = []
	connection = ["連体化","接続助詞","並立助詞"] #接続型
	sep_flag = False
	brac = False
	for cla in reversed(clauses) : #[文節,[]]
		r =cla[0][2].split("D") #[係先,""]

		#括弧内処理
		#カッコ内は使用しない方が自然
		if brac :
			bra_str = ""
			for m_info in reversed(cla[1]) :
				morph = morph_array(m_info)
				bra_str = morph[0] + bra_str
				if morph[2] == "括弧開" :
					brac = False
					#print("bra end")
			sentence = bra_str + sentence

		#係先が述語の文節の時(直接述語にかかっている場合)
		#print(r)
		if r[0] == pre_num and not brac:
			#直接述語にかかっている項を記録
			#argment.insert(0,cla)
			#print(cla)
			cla_str = ""
			for m_info in cla[1] :
				morph = morph_array(m_info)
				if m_info == cla[1][-1] :
					#文節末の時
					#品詞で弾くならここを変更
					# relation check
					if morph[1] == "助詞" :
						#リセット
						relation.insert(0,[morph[0],morph[2]])
						sentences.insert(0,sentence)
						#print(sentence)
						sentence = ""
					elif morph[2] == "読点" :
						#かかる文末が読点終わりの時
						#cabochaの性質上仕方ない
						#print("toten")
						cla_str = ""
						sep_flag = True
					else :
						#まだわからん
						cla_str += morph[0]
				else :
					cla_str += morph[0] #because arg
					#括弧があるとき
					if morph[2] == "括弧閉" :
						brac = True
			sentence = cla_str + sentence
			#print(sentence)

			if not sep_flag and not brac :
				##文節先頭の形態素
				m = morph_array(cla[1][0])
				#print("m:",m)
			
				if m[2] == "非自立" :
					#非自立名詞の場合
					#print("prev")
					sentence = prev_arg_check(clauses,cla,sentence)
				else :  
					#普通の場合
					#古今文節遡りを強化
					arg_num = clauses.index(cla) - 1 #一つ前
					#接続型処理 
					while True :
						if arg_num > -1 :   
							#次以降の末尾の形態素
							m = morph_array(clauses[arg_num][1][-1])
							rr = clauses[arg_num][0][2].split("D") #[係先,""]
							if m[2] in connection or m[1] == "連体詞":
								#接続がある時
								if rr[0] == pre_num :
									#ただし述語にかかるなら別
									break
								cla_str = ""
								for m_info in clauses[arg_num][1] :
									morph = morph_array(m_info)
									cla_str += morph[0]
								sentence = cla_str + sentence
								arg_num += -1
								#print("connect")
							else :
								#print("nothing")
								#print(clauses[arg_num + 1][0])
								sentence = prev_arg_check(clauses,clauses[arg_num + 1],sentence)
								break
						else :
							#clausesの0番目にきたとき
							break
					#print("b: ",sentence)
	else :
		#項と助詞のズレを修正
		#print("insert:",sentences)
		sentences.insert(0,sentence)
		sentences.pop()
			
	
	#print(argment)
	#print("sen:",sentences)
	#print("rel:",relation)
	#return argment #三
	return [relation,sentences]

def prev_arg_check(clauses,cla,string):
	#clauses [[[文節説明],[形態素]],....]
	#print("prev")
	#係り元文節番号
	arg_num = int(cla[0][1])
	#元より前の文節から調べる
	for i in reversed(range(arg_num)) :
		r_cla = clauses[i]
		rela = r_cla[0][2].split("D")
		#係り先と係り元が一致
		if rela[0] == cla[0][1] :
			#print("re:",r_cla[1])
			#リストに追加
			#print("add:",r_cla)
			#argment.insert(0,r_cla)

			# clause end fun
			cla_str = ""
			for m_info in r_cla[1] :
				morph = morph_array(m_info)
				cla_str += morph[0] #because arg
			string = cla_str + string			

			#再帰
			string = prev_arg_check(clauses,r_cla,string)
	else :
		return string

#述語の操作
def pre_check(pre) :
	cut = ["て","べき","ですね","ても"]
	#てもしい
	for c in cut :
		if c in pre :
			if c == "て" :
				if not "ていない" in pre :
					pres = pre.split(c)
					#print("pres:",pres)
					pre = pres[0] 
			else :#あればカット
				pres = pre.split(c)
				#print("pres:",pres)
				pre = pres[0]
			#print("check") 
	new_pre = mekabu_origin(pre)
	return new_pre


def mekabu_origin(pre) :
	m = MeCab.Tagger ("-Ochasen")
	me = m.parse(pre)
	mek = me.split("\n")
	mek.pop()
	mek.pop()
	#print(mek)

	#超暫定例外処理 [感じ]

	#末尾を原型へ
	if len(mek) == 1 :
		meka = mek[0] 
		mekab = meka.split("\t")
		if mekab[0] == "感じ" :
			return "感じる"
		origin_pre = mekab[2]
	else :
		origin_pre = ""

		if len(mek) != 0 :
			katei = mek[-1].split("\t")
			if katei[-1] == "仮定形" and katei[-3] == "助動詞" :
				#仮定形はいらん
				mek.pop()
		for meka in mek :
			mekab = meka.split("\t")
			if meka == mek[-1] :
				#末形態素
				origin_pre += mekab[2]
			else :
				origin_pre += mekab[0]

	return origin_pre

#cabochaの出力結果をリスト化
def morph_array(string) :
	words_array = string.split(",")
	elem = words_array[0].split("\t")
	words_array[0] = elem[0]
	words_array.insert(1,elem[1])
	
	return words_array

def seperate_clause(text) : #文節をリスト化
	c = CaboCha.Parser()
	
	kabotya = c.parse(text)
	draw = kabotya.toString(CaboCha.FORMAT_TREE)
	lattice = kabotya.toString(CaboCha.FORMAT_LATTICE)
	#print(draw)        # 簡易 Tree 表示での出
	#print(lattice)   # 計算機に処理しやすいフォーマットで出力
	
	array = lattice.split("\n") #リスト化
	clauses = [] #[[文節,[その要素]],...]
	cn = -1
	
	for line in array:
		if re.match(r'EOS',line):
			#print("skip")
			break
		p_as = re.compile(r"\*")
		asterisk = p_as.match(line)
		#print(asterisk)
		if asterisk: #文節の番号の時
			cn += 1
			#print("number")
			info = line.split(" ") # *,番号,係先,主辞/機能語,係り受け値
			clauses.append([info]) 
			clauses[cn].append([]) #番号のリスト作成
		else : #文節の要素の場合
			#print("add")
			clauses[cn][1].append(line)
	'''
	for num in clauses :
		print(num[0])
		print(num[1])
	'''
	#print(clauses)
	return clauses
	
	
	

if __name__ == '__main__':
	#st = "法整備を含めた検討がまだまだ足りない"
	#st = "こうした緑と市内らしい緑とでは意味（役割？）が違いますね。"
	#st = "ここでかなりの被害者をすくなくすることができると"
	st ="児童養護施設のイメージもかえないと。本当の一時保護ができるように。"
	while True :
		print("input string or exit:")
		st = input()
		if st == "exit" :
			break
		c = CaboCha.Parser()
		kabotya = c.parse(st)
		draw = kabotya.toString(CaboCha.FORMAT_TREE)
		lattice = kabotya.toString(CaboCha.FORMAT_LATTICE)
		#print(draw)        # 簡易 Tree 表示での出
		print(lattice)   # 計算機に処理しやすいフォーマットで出力
		pas = pre_arg_str(st)
		print(pas)
		print("end")

'''
知識

日本語の性質的に述語は文の最後に来ることがほとんど


--------------------------
述語の処理

述語を含む文節の二重リストを取り出す
文節の説明　の　主辞/機能語　部分から述語(主辞?)を抽出
抽出は主事の番号から前の部分とする
述語の品詞で処理を分岐

----------------------------
項の処理
災害＝避難のイメージがものすごく強く（それ自体は間違っていないのですが・・）、”知らず知らずに持っている固定観念”や”災害のステレオタイプ”のようなものを崩していかなくてはならない
'''
