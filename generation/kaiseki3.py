#coding:UTF-8
#2017/1/17 ho
import MeCab
#import extract_fre_word as efw
import ngram_self as ns
import take_impor_verb as tiv
import search_hint_ex as she
import predicate_arg_structure as pas
import gene_q as gq


#utfファイルを読み込むとき
#pre = efw.extract_pre(file_name) #二重リスト 

#sts = ["私はリンゴが好き","リンゴは赤い","リンゴジュースは美味しい","私はバナナが嫌い","バナナとリンゴは果物だ"]

def kaiseki() :
	while True :
		pre_con = []
			
		while True :
			print("input or co:")
			document = input()
			if document == "co" :
				break
			else : 
				pre_con.append(document)
		print("ready to ok")
		print("length:", len(pre_con))

		fre = ns.ngram_fre_con_word(pre_con,2)
		print("fre")
		word = ns.fre_words(fre,0)
		print(word)

		q_flag = True
		if len(word) == 1 :
			if word[0][1] >= len(pre_con) :
				#頻出と判断
				q_string = gq.gene_q_fre(word[0][0])
				print(q_string)
				q_flag = False
			
		#-------------------------------------
		if q_flag :
			score_pro = {"思う":0.104,"考える":0.077,"感じる":0.135,"重要":0.06,"大切":0.086,"大事":0.056,"ないでしょうか":0.097,"でしょうかね":0.094,"ではありません":0.167,"いただきたい":0.145,"ばならない":0.121,"どうでしょう":0.082,'必要':0.085}
			score_dis = {"思う":3.825,"考える":3.973,"感じる":3.917,"重要":4.056,"大切":2.444,"大事":1,"ないでしょうか":5.378,"でしょうかね":3.182,"ではありません":7.25,"いただきたい":3.25,"ばならない":5.286,"どうでしょう":2.571,'必要':4.283}
			#のでしょうかワンチャン
					
			parts = []

			print("-------------she--------------")
			usedex = []
			prepsen = []
			for i in range(len(pre_con)) :
				document = pre_con[i]
				#([手がかり表現],[抽出部部分])
				#形態素の長さで採用
				usedex,prepsen = she.search_hint_ex(document,usedex,prepsen,score_pro)

			best  = she.get_best_scorer(usedex,prepsen)
			print(best)
				
			print("-----------pas-------------")
			parts = pas.pre_arg_str(best)
			print(parts)
			
			#parts = [[[josi1],[josi2]],[arg1,arg2]]
			print("---------gq-----------------")
			if len(parts[0]) == 0 and len(parts[1]) == 0 :
				#該当なし 直前のはつげんから質問生成 これでいいかわからん
				print("not find")
				context = pre_con[-1]
				sentences = she.symbol_check(context)
				print(sentences)
				parts = pas.pre_arg_str(sentences[-1])
				q_string = gq.gene_filters(parts)
				
			else :
				q_string = gq.gene_filters(parts)
				
			print(q_string)

		print("c (continue) or other (exit)")
		j = input()
		if j == "c" :
			continue
		else :
			break
		

if __name__ == '__main__':
	kaiseki()
		
	