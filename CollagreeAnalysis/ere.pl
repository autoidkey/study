#!/usr/bin/perl


my @files = glob("errdist_X_*.csv");

foreach $file (@files) {
    my $delta = 1;
    my $sum = 0;
    open(IN, "$file");
    while(<IN>) {
	s/\s+$//;
	my @tokens = split(",");
	if ($tokens[0] !~ /V1/) {
	    $sum += $tokens[0] * $tokens[1] / $delta;
	}
    }
    close(IN);
    if ($file =~ /_(X_.+?).csv/) {
	print "$1,$sum\n";
    }
}

