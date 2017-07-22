#utf-8
#2017/2/25 sc
import predicate_arg_structure as pas
import MeCab
#メカブで述語を解析して分岐

#末尾の原型と品詞を返す
def mekabuka_last(string) :
	#内容語のみ
	get = ["名詞","動詞","形容詞"]
	m = MeCab.Tagger ("-Ochasen")
	me = m.parse(string)
	mek = me.split("\n")
	mek.pop()
	mek.pop()
	#print(mek)
	mekabu = []
	meka = mek[-1] #末尾の要素
	mekab = meka.split("\t")
	pos = mekab[3].split("-")
	'''
	for meka in mek :
		mekab = meka.split("\t")
		pos = mekab[3].split("-")
		if pos[0] in get :
			if not (pos[0] == "名詞" and pos[1] == "非自立") :
				mekabu.append(mekab[2])
	'''

	return [mekab[2],pos]

def gene_dig(pre_arg,ex) :
	pre = pre_arg[0]
	args = pre_arg[1] #[[[josi1],[josi2]],[arg1,arg2]]
	q_string = ""
	digs = ["どのよう","具体的","として"]

	for i in reversed(range(0,len(args[0]))) :
		q_string += args[1][i] + args[0][i][0] 
	else :
		q_string += pre + "とありますが"
		
		if ex == "どのよう":
			q_string += "具体的にアイデアはありますか?"
		else :
			q_string += "どのようなものが考えられますか?"
	print("dig")
	return q_string

def gene_q_fre(word) :
	q_string = word + "というワードがよく出てきますが具体的になにができるのでしょうか？"
	return q_string

def gene_filters(pre_arg) :
	#順序より何の格が出ているかが重要
	#3項=> 2項 => と見つからない時に制度を下げていく
	pre = pre_arg[0]
	args = pre_arg[1] #[[[josi1],[josi2]],[arg1,arg2]]
	useable = ["は","も","が","を","に","と","で","にとって","から"]
	ff = ["が","を","と","で","も","は","に","にとって","から"]
	sf = [["に","を"],["で","が"],["で","を"],["に","が"],["にとって","に"],["を","で"],["も","が"],["は","を"]] #["s","f"]の組み
	tf = [["が","に","を"],["は","に","を"],["も","を","で"],["で","が","に"],["が","を","から"],["は","にとって","に"],["も","が","を"],["に","が","から"]]
	other = ["こそ","に関して","ば","にとって","ながら"]
	digs = ["どのよう","具体的","として"] #何
	q_string = ""

	pos = mekabuka_last(pre)
	#print(pos)

	#項が存在しないとき
	if len(args) == 0 :
		#print("nothing argment")
		pos = mekabuka_last(pre)
		if pos[1][0] == "名詞" :
			q_string = pre + "とはどういうものなのですか？"
		else :
			q_string = pre + "とはどういうことですか？"
		return q_string



	#掘り下げ表現を含む時
	for arg in args[1] :
		for dig in digs :
			if dig in arg :
				return gene_dig(pre_arg,dig)

	#係助詞処理 には　でも　などの処理
	for arg in args[0] :
		#(は、も)など
		if arg[1] == "係助詞" :
			arg_num = args[0].index(arg)
			#対応する項
			ml = mekabuka_last(args[1][arg_num])
			if ml[1][1] == "格助詞" :
				new_arg = args[1][arg_num].rsplit(ml[0],1)
				args[1][arg_num] = new_arg[0]
				args[0][arg_num] = [ml[0],ml[1][1]]

	#女子そのものを抽出
	pops = []
	for pop in args[0] :
		pops.append(pop[0])
	#print(pops)


	#ここから格構造処理
	num = len(pops)
	#print(num)
	if num == 0 :
		#名詞のとき?
		q_string = args[1][0] + pre + "とはどのようなものでしょうか?"
		return q_string

	q_string = ""
	if 'ば' in pops :
		#**ばがあるとき　戦闘とは限らない
		print("ba")
		for i in range(num) :
			q_string += args[1][i] + pops[i] 
		q_string = "なぜ" + q_string + pre + "のですか？"
	else :
		f_flag = True
		s_flag = True
		t_flag = True

		#項と述語を代入
		for i in range(num) :
			q_string += args[1][i] + pops[i]
		q_string += pre

		#フィルタリング
		if contain(pops,tf) :
			#３条件
			q_string = t_pop_gene(q_string,pops,tf)
		elif contain(pops,sf) :
			#2条件
			q_string = s_pop_gene(q_string,pops,sf)
		elif contain(pops,ff) :
			#1条件 
			q_string = f_pop_gene(q_string,pops,ff)
		else : 
			#論外
			#print("other match")
			q_string = "なぜ" + q_string + "なのでしょうか？"

	return q_string

def contain(pops,filta) :
	c = filta[0]
	if isinstance(c,str) :
		#fのみ
		#述語に近い方優先
		for pop in reversed(pops) :
			if pop in filta :
				return True
		return False
	elif isinstance(c,list) :
		#s,t
		for comb in filta :
			p_set = set(pops)
			c_set = set(comb)
			match = p_set & c_set
			if match == c_set :
				return True

		return False
	else :
		print("eroor")
		return False

def add_arg_pre(num,pre,args) :
	string = ""
	for i in range(num):
		string += args[1][i] + args[0][i][0]
	string += pre

	return string

def f_pop_gene(string,pops,filta):
	j = consist_impro(pops,filta)
	if j == "が" :
		print("ga")
		string = "どのように" + string + "のですか？"
		#string = "どのように" + string + "とお思いですか？"
	elif j == "を" :
		print("wo")
		#string = "どのようにすれば" + string + "のですか？"
		string = "どのように" + string + "のですか？"
	elif j == "と" :
		print("to")
		string = "どのように" + string + "のですか？"
	elif j == "で" :
		print("de")
		string = "どんな" + string + "のですか？"
	elif j == "も" :
		print("mo")
		string = "どのように" + string + "のですか？"
		#どのようにして
	elif j == "は" :
		print("ha")
		string = "なぜ" + string + "のですか？"
	elif j == "に" :
		print("ni")
		string = "なぜ" + string + "のですか？"
	elif j == "にとって" :
		print("nitotte")
		string = "" + string + "のですか？"
	elif j == "から" :
		print("kara")
		string = "どのように" + string + "のですか？"
	else :
		print("other1")

	return string

def s_pop_gene(string,pops,filta) :
	#基本的に入れ替えても使えそう
	j = consist_impro(pops,filta)
	if j == {"に","を"} :
		print("niwo")
		string = "どのように" + string + "のですか？"
		#string = "どのように" + string + "とお思いですか？"
	elif j == {"で","が"} :
		print("dega")
		string = "どのように" + string + "のですか？"
	elif j == {"で","を"} :
		print("dewo")
		string = "どのように" + string + "のですか？"
	elif j == {"に","が"} :
		print("niga")
		#string = "どのように" + string + "のですか？"
		string = "なぜ" + string + "のですか？"
	elif j == {"も","が"} :
		print("もga")
		#string = "どのように" + string + "のですか？"
		string = "どうすれば" + string + "のですか？"
	elif j == {"は","を"} :
		print("hawo")
		string = "なぜ" + string + "のですか？"
	else :
		print("other2")
	return string

def t_pop_gene(string,pops,filta) :
	j = consist_impro(pops,filta)
	if j == {"が","に","を"} :
		string = "どうすれば" + string + "のですか？"
	elif j == {"は","に","を"} :
		#string = "どのように" + string + "と考えられますか？"
		string = "どのように" + string + "のですか？"
	elif j == {"も","を","で"} :
		string = "どのように" + string + "のですか？"
		#string = "どのように" + string + "のでしょうか？"
	elif j == {"で","が","に"} :
		string = "どのように" + string + "のですか？"
		#string = "どのように" + string + "でしょうか？"
	elif j == {"が","を","から"} :
		string = "なぜ" + string + "のですか？"
	elif j == {"は","にとって","に"} :
		string = "なぜ" + string + "のですか？"
	elif j == {"も","が","を"} :
		string = "どのように" + string + "のですか？"
	else :
		print("other3")

	return string

def consist(pops,mat) :
	#女子　と　マッチ対象
	if isinstance(mat,str) :
		#fのみ
		#述語に近い方優先
		for pop in reversed(pops) :
			if pop == mat :
				return True
		return False
	elif isinstance(mat,list) :
		#s,t
		p_set = set(pops)
		c_set = set(mat)
		match = p_set & c_set
		#print(match)
		if match == c_set :
			return True
		return False
	else :
		print("eroor")
		return False

def consist_impro(pops,filta):
	c = filta[0]
	if isinstance(c,str) :
		#fのみ
		#述語に近い方優先
		for pop in reversed(pops) :
			if pop in filta :
				return pop
		return "#"
	elif isinstance(c,list) :
		#s,t
		for comb in filta :
			p_set = set(pops)
			c_set = set(comb)
			match = p_set & c_set
			if match == c_set :
				return c_set

		return ["#"]
	else :
		print("eroor")
		return "#"

if __name__ == '__main__' :
	text = "法整備を含めた検討がまだまだ足りない"
	#clauses = pas.seperate_clause(text)
	#pre_is_veradj(clauses,"4")
	#gene_q(['入れる', [[['は','係助詞'], ['が','格助詞']], ['ソフト面での基盤整備に', '力']]])
	#gene_qq(['集まる', [[['も', '係助詞'], ['から', '格助詞'], ['が', '格助詞']], ['地域の自立のために', '市民', '関心']]])
	#string = gene_qq(['場', [[], ['だからこそ行政区分を超えた議論の']]])
	#string = gene_qq(['つなげる', [[['を', '格助詞'], ['に', '格助詞']], ['本', '次の活動']]])
	#string = gene_qq(['注意する', []])
	#string = gene_filters(['有用', [[['ば', '接続助詞'], ['にとって', '格助詞']], ['与えられるようであれ', '尚都市']]])
	#string = gene_filters(['目指す', [[['も', '係助詞'], ['が', '接続助詞'], ['を', '格助詞']], ['名駅周辺', 'そうです', '栄など低層の建物が並ぶところも統一した雰囲気のある景観']]])
	string = gene_filters(['目指す', [[['も', '係助詞'], ['から', '格助詞']], ['名駅周辺', '栄など低層の建物が並ぶところも統一した雰囲気のある景観']]])
	
	print(string)





'''
係助詞
[は]、[も]、こそ、でも、xしか、xさえ、xだに
格助詞
[が]、Xの、[を]、[に]、へ、[と]、から、Xより、[で]

*共通
ために(は) で　格助詞「に(は)」がヒット
掘り下げ表現が出ている場合はそのまま使用

1.述語項構造から生成
2.名詞から作成

方針
が系はどのようにで
を格はどのようにしてで

'''
