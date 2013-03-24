#!/usr/bin/perl -w

# we are converting all the movie files into mp4 files

use strict;
use warnings;
use Term::ANSIColor;
use constant FONT => "red bold";

my $MOVIE_DIR = "/Users/xz/Music/iTunes/iTunes Media/Home Videos/";
my @SUPPORTS = qw/rmvb/;
my $cmd = "ls " . join " ", map "*.$_", @SUPPORTS;
my @targets = map {substr $_, 0, -1} `cd '$MOVIE_DIR'; $cmd`;
my $target_suffix = "mp4";

sub _list_support() {
	print "Current supported types: ";
	print foreach (@SUPPORTS);
	print "\n";
}

sub _confirm_convert() {
	local $\ = "\n";
	print "Listing files:";
	print " |-- " . colored $_, FONT foreach (@targets);
	print colored "Are you sure to convert all these files to *.$target_suffix? (yes/no) ", "bold";
	my $val = <>;
	die "Stopping convert! " if not grep /yes/i, $val;
}

sub _do_convert($) {
	my $from = shift;
	my $to = $from;
	$to =~ s/\.[^.]+$/.$target_suffix/;
	print "Converting file $from -> $to... \n";
	`HandBrakeCLI -i '$from' -o '$to' 1>&2`;
	die "Failed convert file $from!" if $?;
}

_list_support();
_confirm_convert();
_do_convert($_) foreach (@targets);
print colored "ALL " . scalar @targets . " files converted! Enjoy!\n", FONT;
