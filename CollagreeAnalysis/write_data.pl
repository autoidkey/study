#!/usr/bin/perl

use Time::Local 'timelocal';
use Encode;

my $feat_file = "ig_catepred/feats.csv";
#my $feat_file = "ig_catepred/feats_selected.csv";

my $N_MIN = 3;
my $N_MAX = 6;
my $TIME_WINDOW = 10;  # 10 hours
my $FREQ_THRESH = 5;

my $ngram2freq = ();
#my $cate2freq = ();

my @faci_cates = ("_まとめ提示", "_言い換え", "_称賛", "_発言促進", "_挨拶", "_御礼", "_同意", "_問いかけ", "_OTHER", "_WAIT");
my @ids = ();
my %id2date = ();

my %key2feat = ();

my %ngram2cates = ();
read_cate();

my @all_ngrams = ();
my @feat_labels = ("timelag", "lastlen", "facinext", "precutt", "partnum");
read_feat();
push(@feat_labels, @faci_cates);


foreach $gdafile (@ARGV) {
    print STDERR "Processing $gdafile\n";
    count($gdafile); # GDAファイルを読んで説明変数を記録
}

# 後は標準出力に書き出すだけ
print "sucutt";
for (my $i = 0; $i < @feat_labels; $i++) {
    my $feat_label = $feat_labels[$i];
    print ",";
    print $feat_label;
}
print "\n";

foreach $id (@ids) {
    if (! $key2feat{"$id/precutt"}) { 
	$key2feat{"$id/precutt"} = 0;
	#next; 
    }
    print $key2feat{"$id/sucutt"};
    for (my $i = 0; $i < @feat_labels; $i++) {
	my $feat_label = $feat_labels[$i];
	print ",";
	my $key = "$id/$feat_label";
	my $feat = $key2feat{$key};
	if (length($feat) == 0) { 
	    $feat = 0; 
	}
	print $feat;
    }
    print "\n";
}



exit;
#--------------------

sub p_info { # 情報利得計算時に必要なp log p の関数
    my $p = $_[0];
    if ($p > 0) {
	return $p * log($p);
    } else {
	return 0;
    }
}

sub count {  # GDAファイルを読んで説明変数を記録する関数
    my $gda_file = $_[0];

    my %last_ngrams = ();
    my @file_ids = ();
    my $last_date = "";
    my $start_date = "";
    my $last_len = 0;
    my $last_id = "";
    my $is_faci_next = 0;
    my $last_empty_timelag = 0;
    my $precutt = 0;
    my %id2sucutt = ();
    my %part_hash = ();
    open(IN, $gda_file);

    while (my $ss = <IN>) { # 発言を1つずつ処理するループ
	if ($ss !~ /<ss /) {
	    next;
	}
	$ss =~ s/\s{2,}/ /g;
	my $date = get_date($ss);
	my $id = get_id($ss);
	my $who = get_who($ss);
	my @morphs = ();
	my @ngrams = ();
	if (! $start_date) {
	    $start_date = $date;
	}
	#print STDERR "date: $date\n";
	#print STDERR "ss: ", substr($ss, 0, 20), "\n";
	push(@ids, $id);
	push(@file_ids, $id);
	$id2date{$id} = $date;
	
	foreach $ngram (@all_ngrams) {
	    if ($last_ngrams{$ngram}) {
		$key2feat{"$id/$ngram"} = 1;
	    } else {
		$key2feat{"$id/$ngram"} = 0;
	    }
	}

	@ngrams = (); # 形態素N-gramを格納する配列
	while ($ss =~ s/<su.+?<\/su>//) { # 発言ssに含まれる文ごとのループ
	    my $su = $&;
	    @morphs = morph_array($su);
	    for (my $n = $N_MIN; $n <= $N_MAX; $n++) { # n = 3,4,5,6についてのループ
		push(@ngrams, ngram_array($n, @morphs)); # n個の形態素をつなげた形態素N-gramを追加
	    }

	    #print join(", ", @ngrams), "\n";
	}

	$key2feat{"$id/facinext"} = $is_faci_next; 
	if ($last_empty_timelag) {
	    my $lag = 0;
	    if ($last_date) {
		$lag = rand() * calc_lag($date, $last_date);
	    } else {
		$lag = rand() * calc_lag($date, $start_date);
	    }
	    $key2feat{"$last_id/timelag"} = $lag;
	    #print STDERR "@@@ $lag\n";
	}
	if ($last_date) {
	    my $lag = calc_lag($date, $last_date);
	    $key2feat{"$id/timelag"} = $lag;
	} else {
	    $last_empty_timelag = 1;
	}

	if (is_facili($ss)) { # ss がファシリテーター発言の場合
	    $is_faci_next = 1;
	    my %cate_hash = ();
	    foreach $ngram (@ngrams) {
		my $ref = $ngram2cates{$ngram};
		foreach $cate (@$ref) {
		    $cate_hash{$cate} = 1;
		    $key2feat{"$id/$cate"} = 1;
		}
	    }
	    if (! %cate_hash) {
		$cate_hash{"_OTHER"} = 1;
		$key2feat{"$id/_OTHER"} = 1;
	    }
	    foreach $negacate (@faci_cates) {
		if (! $cate_hash{$negacate}) {
		    $key2feat{"$id/$negacate"} = 0;
		}
	    }
	} else { # ss がファシリテーター発言でない場合
	    $key2feat{"$id/_WAIT"} = 1;
	    foreach $cate (@faci_cates) {
		if ($cate ne "_WAIT") {
		    $key2feat{"$id/$cate"} = 0;
		}
	    }
	    $last_date = $date;
	    $last_len = @morphs;
	    $is_faci_next = 0;
	    $precutt ++;
	    $part_hash{$who} = 1;
	    foreach $previd (@file_ids) {
		my $prevdate = $id2date{$previd};
		my $prevlag = calc_lag($date, $prevdate);
		#print STDERR "@@@ $prevlag\n";
		if ($prevlag <= $TIME_WINDOW) {
		    $id2sucutt{$previd} ++;
		} else {
		    #print STDERR "@@@ $prevlag\n";
		}
	    }
	    foreach $ngram (@ngrams) {
		$ngram2freq{$ngram} ++;
		$last_ngrams{$ngram} = 1;
	    }
	}

	$key2feat{"$id/lastlen"} = $last_len;
	$key2feat{"$id/precutt"} = $precutt; 
	$key2feat{"$id/partnum"} = keys(%part_hash);

    }

    # 最後に被説明変数を記録
    foreach $id (@file_ids) {
	if ($id2sucutt{$id}) {
	    $key2feat{"$id/sucutt"} = $id2sucutt{$id};
	} else {
	    $key2feat{"$id/sucutt"} = 0;
	}
     	#print STDERR "@@@ $id2sucutt{$id}\n";
     }
    $last_id = $id;
    close(IN);
}


sub calc_lag { # 時間差を計算
    my ($date, $faci_date) = @_;
    my $lag = to_unixtime($date) - to_unixtime($faci_date);
    #print STDERR "$date - $faci_date = $lag\n";
    return $lag / 3600;
}

sub to_unixtime { # 日付をUNIX Timeに変換
    my $dateTime = $_[0];
    if ($dateTime =~ /(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2})/) {
	my $year = $1 - 1900;
	my $mon = $2 - 1;
	my $day = $3;
	my $hour = $4;
	my $min = $5;
	my $sec = $6;
	my $utime = timelocal($sec, $min, $hour, $day, $mon, $year);
	#print STDERR "$dateTime -> $utime\n";
	return $utime;
    }
}

sub ngram_array { # 形態素N-gramのリストを作る関数
    my ($n, @morphs) = @_; # n: つなげる形態素の数，@morphs: 形態素のリスト
    my @ngrams = ();  
    my $len = @morphs;
    if ($len >= $n) {
	for(my $i = 0; $i < $len - $n + 1; $i++){  
	    my $ngram = ngram2str(@morphs[$i .. $i + $n - 1]);
	    if (! $ngram2n{$ngram}) {
		$ngram2n{$ngram} = $n;
	    }
	    push(@ngrams, $ngram);
	}
	return @ngrams;
    }

}


sub morph_array {
    my $gda = $_[0];
    my @morphs = ();
    while($gda =~ s/(<[^>]+ mph=[^>]+>[^<]+<\/[^>]+>)//) {
	my $morph = $1;
	push(@morphs, $morph);
    }
    return @morphs;
}

sub is_facili {
    my $ss = $_[0];
    return ($ss =~ /facilitation=\"true\"/);
}

sub ngram2str {
    my @morphs = @_;
    my $str = "";
    for (my $i = 0; $i < @morphs; $i++) {
	my $morph = $morphs[$i];
	my $surface = get_surface($morph);
	$str .= $surface;
	# if ($i < @morphs - 1) {
	#     my $surface = get_surface($morph);
	#     $str .= $surface;
	# } else {
	#     my $base = get_base($morph);
	#     $str .= $base;
	# }
    }
    return $str;
}

sub get_surface {
    my $morph = $_[0];
    if ($morph =~ /<[^>]+>([^<]+)</) {
	my $surface = $1;
	return $surface;
    }
}

sub get_base {
    my $morph = $_[0];
    if ($morph =~ /mph=\"mecab[^\"]+;([^;]+?);[^;]+?\"/) {
	my $base = $1;
	return $base;
    }
}

sub merge_hash {
    my ($orig_ref, $new_ref) = @_;
    foreach $ngram (%$new_ref) {
	$orig_ref->{$ngram} += $new_ref->{$ngram};
    }    
}


sub omit_dupli {
    my ($sorted_ref, $info_gain_ref) = @_;
    for (my $i = 0; $i < @$sorted_ref; $i++) {
	my $ngram = $sorted_ref->[$i];
	my $ig = $info_gain_ref->{$ngram};
	for (my $j = 0; $j <@$sorted_ref; $j++) {
	    my $ngram2 = $sorted_ref->[$j];
	    my $ig2 = $info_gain_ref->{$ngram2};
	    my $quoted = quotemeta($ngram2);
	    if ($ngram eq $ngram2 || $ngram !~ /$quoted/) {
		next;
	    } elsif ($j >= $i-5 || $ig2 <= $ig) {
		if ($j < $i) { $i--; }
		splice(@$sorted_ref, $j--, 1);
 	    }
	}
    }
}


sub read_cate {
    my $csv_file = "ngram_ig_posi_category.csv";
    open(IN, $csv_file);
    while(<IN>) {
	my @tokens = split(/,/);
	my $ngram = $tokens[1];
	my $catestr = $tokens[2];
	if ($catestr) {
	    #Encode::from_to($catestr, "sjis", "utf8");
	    my @cates = split(/ /, $catestr);
	    for (my $i = 0; $i < @cates; $i++) {
		$cates[$i] = "_$cates[$i]";
	    }
	    $ngram2cates{$ngram} = \@cates;
	}
    } 
    close(IN);
}

sub read_feat {
    open(IN, $feat_file);
    while(<IN>) {
	s/\s+$//;
	my @tokens = split(/,/);
	my $ngram = $tokens[0];
	push(@feat_labels, $ngram);
	push(@all_ngrams, $ngram);
    }
    close(IN);

}

sub get_date {
    my $ss = $_[0];
    if ($ss =~ /<ss[^>]* created=\"(.+?)\"/) {
	return $1;
    }
}

sub get_id {
    my $ss = $_[0];
    if ($ss =~ /<ss[^>]* id=\"(.+?)\"/) {
	return $1;
    }
}

sub get_who {
    my $ss = $_[0];
    if ($ss =~ /<ss[^>]* who=\"(.+?)\"/) {
	return $1;
    }
}

sub get_text_content {
    my $text = $_[0];
    $text =~ s/<[^>]+>//g;
    return $text;
}

