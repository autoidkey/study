#!/usr/bin/perl

my %hash = ();
open(IN, "ngram_ig_posi_category.csv");
while(<IN>) {
    s/\s+$//;
    my @tokens = split(/,/);
    my $ngram = $tokens[1];
    my $tags_str = $tokens[2];
    my @tags = split(/ /, $tags_str);
    foreach $tag (@tags) {
	my $ref = $hash{$tag};
	if (!$ref) {
	    $hash{$tag} = [];
	    $ref = $hash{$tag};
	}
	push(@$ref, $ngram);
    }
}

close(IN);

foreach $tag (keys(%hash)) {
    my $ref = $hash{$tag};
    print "$tag\n";
    foreach $ngram (@$ref) {
	print "  $ngram\n";
    }
}
