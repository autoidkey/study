#coding:utf-8
#2017/1/17 ho
import CaboCha
import re
import predicate_arg_structure as pas

#array = 先行文脈リスト

#think表現の前を抽出リストの前ほど優先度高
def search_think_expression(document) : #clauses
	think = ["思う","感じる","考える"]
	expression = [["と","助詞","格助詞","引用","*","*","*","と","ト","ト"],["を","助詞,格助詞,一般,*,*,*,を,ヲ,ヲ"]] #をはまた考える
	stopper = ["読点","句点"]    
	think_sentences = []
	count = -1
	exist = False
	usedex = [] 

	#print(document)
	sentences = symbol_check(document)
	
	#print(sentences)
	for sentence in sentences :
		clauses = seperate_clause(sentence)
		end_point = -len(clauses)
		clause = clauses #保険
		count = -1
		exist = False

		while True :
			#後ろから探す
			cla = clause[count] #[文節説明,[その要素,...]]
			if exist :
				print("exist")
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
						think_sentences[-1] = word[0] + think_sentences[-1]
					#print(think_sentences)
					count += -1    
			else :
				#探す処理
				out_end = cla[1][0] #文節頭の要素(思うとかで１文節使用しているから)
				array = out_end.split(",") #要素の属性をリスト化
				#think要素があるか
				if array[-3] in think :
					#print(array[-3])
					think_sentences.append("")
					exist = True
					usedex.append(array[-3])
					#thinkの直前の要素判定
					if count - 1 < end_point :
						think_sentences.pop()
						break
					next_cla = clause[count - 1]
					words = pas.morph_array(next_cla[1][-1])
					if words == expression[0] :
						#と　を削除
						clause[count - 1][1].pop()
						#print(clause[count - 1][1])
						if len(clause[count - 1][1]) == 0:
							break
				count += -1
		
			if count < end_point :
				break
	
	if len(think_sentences) == 0:
		print("nothing thinking")
	else :
		nothing = 0
		#print(think_sentences)
	return (usedex,think_sentences)

def search_importance(document) : #clause
	importance = ["重要","必要","大事","大切",	"必須"]
	#sep = ["句点","読点"]
	imp_sentences = [] #表現を含む文
	imp_flag = False
	one_sen = ""
	end = False #文末かどうか
	usedex = []
	
	sentences = symbol_check(document)

	for sen in sentences :
		for impor in importance :
			if impor in sen :
				#句点について
				sep = sen.split("、")
				if len(sep) > 1:
					for s in reversed(sep) :
						if impor in s :
							#表現が現れている方を代入
							sent = s
				else :
					sent = sen

				sep_txt = sent.rsplit(impor,1)
				extr = sep_txt[0]
				imp_sentences.append(extr)
				usedex.append(impor)				

	#print(imp_sentences)
#-----------------------------------------------  
	important_thing = [] #その内容
	thing = ["こと","事","の"]
	bp = False
	
	for imp_sen in imp_sentences :
		bp = False
		cla = seperate_clause(imp_sen)
		for context in cla: #[,[]]
			for com in context[1] :
				word = pas.morph_array(com) #文中の形とそれ以外
				if word[0] in thing and word[2] == "非自立":
					print("TRUE：",word[0])
					important_thing.append(one_sen)
					#print(important_thing)
					one_sen = ""
					bp = True
					break
				else :    
					one_sen = one_sen + word[0]
					#print(one_sen)
			
			if bp :
				break
		else :
			#print("else")
			#print(important_thing)
			text = ""
			
			num = imp_sentences.index(imp_sen)
			imp = imp_sen.split(usedex[num])
			if imp[0] != "" :
				#前部分にあるとき
				cla = pas.seperate_clause(imp[0])
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
				important_thing.append(text)
				text = ""

			else :
				#後ろ部分にあるとき
				cla = seperate_clause(imp[1])
				#mitei

	
	if len(important_thing) == 0:
		print("nothing important")
	else :
		nothing = 0
		#print(important_thing)
	
	return (usedex,important_thing)

#句読点に対応できてない
def search_esp_expression(document) :
	#名詞では、いいの・ではない・ない・から、名詞、。。して、。。しなけれ、名詞は
	esps = ["ないでしょうか","でしょうかね","ではありません","いただきたい","ばならない","どうでしょう","いいですね"]
	esp_sen = []
	usedex = []
	'''
	doc = document
	for ten in sep :
		doc = doc.replace(ten,"|")
	#文単位に分割
	sentences = doc.split("|")
	#print(sentences)
	if sentences[-1] == "":
		sentences.pop()
	'''
	sentences = symbol_check(document)
	for sen in sentences :
		for esp in esps :
			if esp in sen :
				#句点について
				sep = sen.split("、")
				if len(sep) > 1:
					#後ろ部分を採用
					sent = sep[-1]
				else :
					sent = sen

				sep_txt = sent.rsplit(esp,1)
				extr = sep_txt[0]
				esp_sen.append(extr)
				usedex.append(esp)
				

	if len(esp_sen) == 0:
		print("nothing esp")
	
	return (usedex,esp_sen)

def symbol_check(document) :
	#文内かっこの処理がまだ
	symbol = ["。","？","！"]
	mark = ["？","！"]
	sentences = []
	string = ""
	#[[[info],[morph]],....]
	#係り受け解析
	if isinstance(document,str):
		clauses = seperate_clause(document)
	else:
		clauses = document

	for acla in clauses :
		for morph in acla[1] :
			#1形態素
			word = pas.morph_array(morph)
			#文書中の記号の判別
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
	
	
if __name__ == '__main__':
	print("input string:")
	sentence = input()
	#clause = seperate_clause(sentence)
	#search_end_verb_text(clause)
	print("------think----------------")
	sentences = search_think_expression(sentence)
	print(sentences)
	print("---------importance---------------")
	thing = search_importance(sentence)
	print(thing)
	print("---------esp-expression---------------")
	esp = search_esp_expression(sentence)
	print(esp)

	sc  = symbol_check(sentence)
	print(sc)

    
	#if len(sentences[1]) == 0 

#文の最後の文節の中で一番後ろの内容語を取り出す
#思う、感じる、考えるなどは優先する

'''
ないでしょうか　でしょうかね　ありませんか　ていただきたい　ばならない　どうでしょうか　 -- この表現も使用

重要
抽出部分は名詞が多い[こととか]


think

'''