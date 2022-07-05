#!/bin/bash

spath="/home/vmguest"
sshkey_path="/home/$spath/.secrets"
sshkey="adminkey"

for md5 in "$spath/pfscl/md5s/"*
do
	output=$(md5sum -c --quiet "$md5")
	if [[ -z "$output" ]]; then
		:
	else
		host=$(echo "$md5" | cut -d'.' -f 1,2,3 | awk -F/ '{print $NF}')
		scp -i $sshkey_path/$sshkey admin@$host:/cf/conf/config.xml $host-config.xml
		time=$(date +%F_%R:%S_%:::z)
		cp $host-config.xml $spath/pfscl/config-archive/$host/$host-config-$time.xml
		python3 $spath/pfscl/pfconfedit.py --publickey $spath/.getssl/$host/$host.crt --privatekey $spath/.getssl/$host/$host.key --config $spath/pfscl/$host-config.xml
		sleep 2
		scp -i $sshkey_path/$sshkey $spath/pfscl/$host-config.xml admin@$host:/cf/conf/config.xml
		ssh -i $sshkey_path/$sshkey admin@$host rm /tmp/config.cache
		mkdir -p $spath/pfscl/config-archive/$host
		time=$(date +%F_%R:%S_%:::z)
		mv $host-config.xml $spath/pfscl/config-archive/$host/$host-config-$time.xml
		md5sum $spath/.getssl/$host/$host.crt > $spath/pfscl/md5s/$host.crt.md5
	fi
done
