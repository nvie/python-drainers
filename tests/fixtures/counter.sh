#!/bin/sh
i=0
while [ $i -lt 30 ]; do
	if [ $(($i % 10)) -eq 0 ]; then
		sleep 1
	fi
	echo $(($i+1))
	i=$(($i+1))
done
