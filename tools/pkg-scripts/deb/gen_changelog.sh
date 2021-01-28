#!/usr/bin/env bash

PROJECT='smithproxy-auth'
OPATH=`pwd`
SXPATH=$1
declare -A components
declare -A versions


SX_LOG="/tmp/${PROJECT}_log"

components[$SX_LOG]="${PROJECT}"

cd $SXPATH
git log --pretty=format:%s --oneline --output ${SX_LOG}_pre
versions[$SX_LOG]=`git describe --tags | sed -e 's/-[0-9a-z]*$'//`
cat ${SX_LOG}_pre | fmt -s --prefix="    " > ${SX_LOG}


echo "${PROJECT} (${versions[$SX_LOG]}) unstable; urgency=medium"
echo
echo
echo "    ${components[$f]}-${versions[$f]}"
echo
cat ${SX_LOG} | awk '{ print "    * ",$0 }'

echo
echo " -- Support <support@smithproxy.org>  `date -R`"
