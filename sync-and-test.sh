#!/bin/bash

#local script I have for convience functions
if [ -f ~/.local/scripts/.bashrc ]; then
    source ~/.local/scripts/.bashrc
fi

#findpi is defined above, but this block can be avoided by setting the appropriate env vars
if [[ -z $RASPBERRY_IP  ]] || [[ -z $RASPBERRY_UNAME ]] ; then
	findpi
fi

rsync -az --delete --exclude='.git/' --exclude='sync-and-test.sh' . ${RASPBERRY_UNAME}@${RASPBERRY_IP}:~/node_red
function remote() {
	ssh ${RASPBERRY_UNAME}@${RASPBERRY_IP} "cd node_red;${*}"
}


remote docker-compose down
remote docker-compose build
(remote docker-compose up) & (sleep 10s; xdg-open "http://${RASPBERRY_IP}:1880")