#!/bin/bash

host=""
cango=false
spath="/home/$(whoami)"

while (( $# >= 1 )); do
	case $1 in
	-h) host=$2 cango=true;;
	*) break;
	esac;
	shift
done

if [[ "$cango" = 'false' ]]; then
	echo "-h is a required argument. Please supply it.";
	exit;
fi

if ! [[ -d $spath/.getssl/$host ]]; then
	getssl -c $host
fi
mkdir -p $spath/pfscl/md5s
touch $spath/.getssl/$host/$host.crt
md5sum $spath/.getssl/$host/$host.crt > $spath/pfscl/md5s/$host.crt.md5

