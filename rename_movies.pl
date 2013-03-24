#!/usr/bin/perl
use strict;
use warnings;

my $movie_dir = "/Users/xz/Downloads/movies";

my @movies = `ls $movie_dir`;
foreach (@movies) {
	chomp;
	next if not /^\[/;
	my ($to) = $_ =~ /^\[[^]]+\][\.\s]+(.*)$/;
	print "renaming $_ -> $to\n";
	`cd $movie_dir ; mv $_ $to`;
}
