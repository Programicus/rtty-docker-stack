#!/bin/bash

#local script I have for convience functions
if [ -f ~/.local/scripts/.bashrc ]; then
    source ~/.local/scripts/.bashrc
fi

#findpi is defined above, but this block can be avoided by setting the appropriate env vars
if [[ -z $RASPBERRY_IP  ]] || [[ -z $RASPBERRY_UNAME ]] ; then
	findpi
fi

function remote() {
	ssh ${RASPBERRY_UNAME}@${RASPBERRY_IP} "cd node_red;${*}"
}
