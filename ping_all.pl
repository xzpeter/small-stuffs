#!/usr/bin/perl
use strict;
use warnings;

my $ip_pre="192.168.1.";
my $cnt = 0;

for my $i (100..130) {
	my $ip = $ip_pre.$i;
	print "\rtesting IP $ip...";
	my $result = system("ping -c 1 -t 1 $ip_pre$i > /dev/null 2>&1");
	if (!$result) {
		print "found good!\n";
		$cnt++;
	}
}
print "\r". (" "x40) ."\rDone. $cnt devices found.\n";
