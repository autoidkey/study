#coding:utf-8
#2017/2/9 sc
import CaboCha
import re
import predicate_arg_structure as pas

#複数ある先行文脈から手がかり表現を探索それを(表現,前部分)の形で抽出
def search_hint_ex(document,usedex,prep_sen,score) :
	type1 = ["思う","感じる","考える"]
	type2 = ["重要","大切","大事","必要","いいですね"]
	type3 = ["ないでしょうか","でしょうかね","ではありません","いただきたい","ばならない","どうでしょう"]
	#一時保存用
	hint_ar = [] #手がかり表現
	prep_ar = [] #前の部分
	#type1
	expression = [["と","助詞","格助詞","引用","*","*","*","と","ト","ト"],["は","助詞","係助詞","*","*","*","*","は","ハ","ワ"]]
	direct = ["を","助詞","格助詞","一般","*","*","*","を","ヲ","ヲ"] #をはまた考える
	stopper = ["読点","句点"]
	#type2
	#type3

	sentences = symbol_check(document)
	#print(sentences)
	for sen in sentences :
		hint_ar = []
		prep_ar = []

		#type1
		stopper = ["読点","句点"]
		clauses = seperate_clause(sen)
		end_point = -len(clauses)
		clause = clauses #保険
		count = -1
		exist = False

		if len(clauses) == 0 :
			continue

		while True :
			#後ろから探す
			cla = clause[count] #[文節説明,[その要素,...]]
			if exist :
				#print("think exist")
				#文字列生成処理
				out_top = cla[1][-1] #文節末の要素
				array = out_top.split(",")
				if array[1] in stopper : #文末が、か。
					#次の文へ
					exist = False
				else :
					for com in reversed(cla[1]) :
						word = com.split("\t") #文中の形とそれ以外に分割
						#print("add")
						prep_ar[-1] = word[0] + prep_ar[-1]
						#print(prep_ar)
					count += -1    
			else :
				#探す処理
				#print("s")
				out_end = cla[1][0] #文節頭の要素(思うとかで１文節使用しているから)
				#array = out_end.split(",") #要素の属性をリスト化
				array = pas.morph_array(out_end) #要素の属性をリスト化
				#think要素があるか
				if array[-3] in type1 :
					#表現が現れた時
					#print(array)
					prep_ar.append("")
					exist = True
					hint_ar.append(array[-3])
					#thinkの直前の要素判定
					if count - 1 < end_point :
						prep_sen.pop()
						break
					next_cla = clause[count - 1]
					#think表現の前部分を分析
					words = pas.morph_array(next_cla[1][-1])
					#print("w:",words)
					if words in expression :
						if words[0] == "は" :
							wordss = pas.morph_array(next_cla[1][-2])
							if wordss in expression :
								#とは　削除
								clause[count - 1][1].pop()
								clause[count - 1][1].pop()
						else :		
							#と　を削除
							clause[count - 1][1].pop()
							#print("rem: ",clause[count - 1][1])
						if len(clause[count - 1][1]) == 0:
							break
					#think表現が動詞として使用されるとき
					if words == direct :
						#print("direct")
						#prep_ar[-1] +=  array[0]
						for c in cla[1] :
							cm = pas.morph_array(c)
							prep_ar[-1] += cm[0]
							#print(prep_ar[-1])


				count += -1 #インデントあってる？
		
			if count < end_point :
				break

		#type2
		imp_sentences = []
		for impor in type2 :
			if impor in sen :
				#句点について
				sep = sen.split("、")
				if len(sep) > 1:
					#句点区切りがあるとき
					for s in reversed(sep) :
						if impor in s :
							#表現が現れている方を代入
							sent = s
				else :
					#ないとき
					sent = sen

				sep_txt = sent.rsplit(impor,1)
				extr = sep_txt[0]
				imp_sentences.append(extr)
				hint_ar.append(impor)

		if len(imp_sentences) != 0 :
			#[こと]とかを排除
			prep_ar = extract_imp_sen(imp_sentences,prep_ar,hint_ar)

		#type3
		for esp in type3 :
			if esp in sen :
				#句点について
				sep = sen.split("、")
				if len(sep) > 1:
					#後ろ部分を採用
					sent = sep[-1]
				else :
					sent = sen

				sep_txt = sent.rsplit(esp,1)
				#print("sep:",sep_txt)
				if esp == "ではありません" and sep_txt[1] == "":
					#否定で終わる時
					continue
				extr = sep_txt[0]
				prep_ar.append(extr)
				hint_ar.append(esp)

		#print("hint:",hint_ar)
		#print("prep:",prep_ar)
		if len(hint_ar) > 1 :
			#print("compare")
			#文中に複数の手がかり表現
			best_h = ""
			best_prep = "" 
			max_h = 0
			max_num = 0
			for i in range(len(hint_ar)) :
				#スコア最大
				if score[hint_ar[i]] > max_h :
					max_h = score[hint_ar[i]]
					best_h = hint_ar[i]
					max_num = i
				'''
				if len(prep_ar[i]) < min_p :
					min_p = len(prep_ar[i])
					shortest_prep = prep_ar[i]
				'''
			#対応する前部分を選択
			best_prep = prep_ar[max_num]
			for prep in prep_ar :
				if prep in best_prep :
					best_prep = prep

			usedex.append(best_h)
			prep_sen.append(best_prep)
		elif len(hint_ar) == 1 :
			usedex.append(hint_ar[0])
			prep_sen.append(prep_ar[0])

	#print("ex:",usedex)
	#print("pre:",prep_sen)

	return usedex,prep_sen



def extract_imp_sen(imp_s,pre_s,usedex) :
	thing = ["こと","事","の"]
	bp = False
	one_sen = ""

	for imp_sen in imp_s :
		bp = False
		cla = seperate_clause(imp_sen)
		for context in cla: #[,[]]
			for com in context[1] :
				word = pas.morph_array(com) #文中の形とそれ以外
				if word[0] in thing and word[2] == "非自立":
					#print("TRUE：",word[0])
					pre_s.append(one_sen)
					one_sen = ""
					bp = True
					break
				else :    
					one_sen = one_sen + word[0]
					#print(one_sen)
			
			if bp :
				break
		else :
			# [非自立名詞]が＊＊でないとき
			#print("else")
			text = ""
			
			num = imp_s.index(imp_sen)
			imp = imp_sen.split(usedex[num])
			if imp[0] != "" :
				#前部分にあるとき
				cla = seperate_clause(imp[0])
				for context in cla :
					#print(context)
					if context == cla[-1] :
						#最後のimporが現れる文節のみ
						subject = context[0][3].split("/") #syuji/jutugo
						#print(subject)
						morph = context[1][0:int(subject[0]) + 1]
						for m in morph :
							words = pas.morph_array(m)
							text += words[0] 
					else :
						for con in context[1] :
							words = pas.morph_array(con)
							text += words[0]
				#print(text)
				pre_s.append(text)
				text = ""

			else :
				#後ろ部分にあるとき
				print("behind")
				cla = seperate_clause(imp[1])

	return pre_s

def get_best_scorer(hint_ar,prep_ar) :
	#スコアを降順に並び替える
	#複数ある場合は後ろほど優先
	best_string = ""
	score_pro = {"思う":0.104,"考える":0.077,"感じる":0.135,"重要":0.06,"大切":0.086,"大事":0.056,"ないでしょうか":0.097,"でしょうかね":0.094,"ではありません":0.167,"いただきたい":0.145,"ばならない":0.121,"どうでしょう":0.082,'必要':0.085}
	score_dis = {"思う":3.825,"考える":3.973,"感じる":3.917,"重要":4.056,"大切":2.444,"大事":1,"ないでしょうか":5.378,"でしょうかね":3.182,"ではありません":7.25,"いただきたい":3.25,"ばならない":5.286,"どうでしょう":2.571,'必要':4.283}

	for k,v in reversed(sorted(score_pro.items(),key=lambda x:x[1])) :
		#print(k,":",v)
		if k in hint_ar :
			#print("find ",k)
			i = 0
			for hint in hint_ar :
				#後ろほど優先のため
				if hint == k :
					best_string =prep_ar[i]
				i += 1
			break

	return best_string			


def symbol_check(document) :
	symbol = ["。","？","！","?"]
	mark = ["？","！","?"]
	sentences = []
	string = ""
	#[[[info],[morph]],....]
	#係り受け解析
	clauses = seperate_clause(document)

	http = False
	for acla in clauses :
		for morph in acla[1] :
			#1形態素
			word = pas.morph_array(morph)
			##url処理
			if word[0] == "http" :
				#url処理
				http = True
				if string != "":
					sentences.append(string)
					string = ""
				break

			if http and word[2] == "数":
				http = False
				break

			#ここから普通の処理
			#文書中の記号の判
			if word[0] in symbol :
				if morph != acla[1][-1] and word[0] in mark:
					#形態素末でない時
					num = acla[1].index(morph)
					#次の文節形態素判別
					next_w = pas.morph_array(acla[1][num + 1])
					if next_w[1] == "助詞":
						#文中
						string += word[0]
					else : 
						#文区切り
						sentences.append(string)
						string = ""
				else :
					sentences.append(string)
					string = ""
			else :
				string += word[0]
				#print(string)
	#最後が記号で終わる場合
	if string != "":
		sentences.append(string)

	return sentences

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

if __name__ == '__main__' :
	usedex = []
	prep_sen = []
	score_pro = {"思う":0.104,"考える":0.077,"感じる":0.135,"重要":0.06,"大切":0.086,"大事":0.056,"ないでしょうか":0.097,"でしょうかね":0.094,"ではありません":0.167,"いただきたい":0.145,"ばならない":0.121,"どうでしょう":0.082,'必要':0.085}
	'''
	documents = ['意見を聞くことが重要である。あなたはそうは思わないのでしょうかね?話し合いも重要ではないでしょうか。私は思いますよ。','私はそうは思いません。そんなことより、行動することの方が大切ではありませんか？']
	for document in documents :
		usedex,prep_sen = search_hint_ex(document,usedex,prep_sen,score_pro)
	print("----------------------------------")
	print(usedex)
	print(prep_sen)

	'''	
	
	documents = []
	while True :
		print("input or exit or co:")
		document = input()
		if document == "exit" :
			break
		elif document == "co" :
			for document in documents :
				usedex,prep_sen = search_hint_ex(document,usedex,prep_sen,score_pro)
			print("----------------------------------")
			print(usedex)
			print(prep_sen)
			best = get_best_scorer(usedex,prep_sen)
			print(best)
			#初期化
			documents = []
			usedex = []
			prep_sen = []
		else : 
			documents.append(document)
	
	'''
	document = "僕は名古屋の自然というと、ビルが低層で空が広いとか、夜空を眺めると東京より星空が見えるという点。あとちょっと建物を登ると山並みがみえるという点だと思います。それに中部地方の農産物などからも自然を感じることができます。"
	sen = symbol_check(document)
	print(sen)
	'''





