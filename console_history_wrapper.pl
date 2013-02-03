#!/usr/bin/perl -w

use strict;
use warnings;
use Term::ReadKey;
use IO::Handle;

ReadMode 4;

while (1) {
	my $c = ReadKey(-1);
	print "$c" if defined $c;
	autoflush STDOUT 1;
	sleep 0.01;
}
