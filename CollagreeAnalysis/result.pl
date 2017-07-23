#!/usr/bin/perl

#use Encode;

my $dir = $ARGV[0];
my %ngram2avg = ();
open(IN, "${dir}_avg.csv");
while(<IN>) {
    s/\s+$//;
    my @tokens = split(/,/);
    $ngram2avg{$tokens[0]} = $tokens[1];
}
close(IN);
 
my @files = glob("$dir/*.csv");

#open(OUT, ">$dir.csv");
foreach $file (@files) {
    print STDERR "$file\n";
    my $ngram = $file;
    $ngram =~ s/.csv$//;
    $ngram =~ s/^$dir\///;
    #Encode::from_to($ngram, "utf8", "sjis");
    
    open(OUT_R, " | R --vanilla > tmp.txt"); 
    print OUT_R "data <- as.matrix(read.csv(\"$file\", header=FALSE))\n";
    print OUT_R "cor.test(data[,1],data[,2])\n";
    close(OUT_R);

    open(IN, "tmp.txt");
    my $result = join("", <IN>); 
    if ($result =~ /cor\s+([\d\.\-\+E]+)\s+>/) { 
	print "$ngram,$1,$ngram2avg{$ngram}\n";
    } 
    close(IN);
}

#close(OUT);
