#!/usr/bin/perl -w
use strict;
use warnings;
use Data::Dumper;

my %size_trans = (
	"b" => 1,
	"k" => 1<<10,
	"m" => 1<<20,
	"g" => 1<<30,
	"t" => 1<<40,
	);
my ($file_name, $file_size);

sub usage ()
{
	my $usage ="usage:
		$0 <NAME> <SIZE>

		NAME is the file name to be generated, please no blank
		SIZE is the file size to be generated, can be 10, 10M/m, 10G/g, etc.
";
	print $usage;
    exit 0;
}

if (scalar @ARGV < 2) {
	usage
}

my $progress = 0;
sub update_progress ($$)
{
	my $done = int 100*$_[0]/$_[1];
	return if $done <= $progress;
	print "\rCreating file... \%$done";
}

$file_name = $ARGV[0];
$file_size = $ARGV[1];

$file_size =~ /^(\d+)/;
my $size_n = $1;
my $c = lc substr($file_size, -1, 1);
$file_size = ($size_n *= $size_trans{$c});

print "file name: $file_name\n";
print "file size: $file_size ($ARGV[1])\n";

# confirm
print "\nAre you sure to create this file? (y/n) ";
my $ans = <STDIN>;
exit 0 if "n" eq lc substr($ans, 0, 1);

# do the creation
open my $file, ">", "$file_name" or die "cannot create file";
my $t = "0123456789abcdef"x32;
my $l = length $t;
my $n = $file_size;
while ($n > 0) {
	print $file $t;
	$n -= $l;
	update_progress($file_size-$n, $file_size);
}
close $file;
print "\nfile $file_name generated!\n";
