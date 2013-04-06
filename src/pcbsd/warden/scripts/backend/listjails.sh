#!/bin/sh
# Prints a listing of the installed jails
######################################################################

# Source our functions
PROGDIR="/usr/local/share/warden"

# Source our variables
. ${PROGDIR}/scripts/backend/functions.sh

# Check if we have any jails
if [ ! -d "${JDIR}" ]
then
  echo "Error: No jails found!"
  exit 4
fi

line()
{
  len="${1}"

  i=0 
  while [ "${i}" -lt "${len}" ] ; do
    i=`expr ${i} + 1`
    echo -n '-' 
  done
  echo 
}

lineline=0
VERBOSE="${1}"

# Prints a listing of the available jails
printf "%-24s%-12s%-12s%-12s\n" HOST AUTOSTART STATUS TYPE
line "75"

cd ${JDIR}

for i in `ls -d .*.meta 2>/dev/null`
do
  AUTO="Disabled" 
  STATUS="<unknown>"

  if [ ! -e "${i}/id" ] ; then continue ; fi

  ID="`cat ${i}/id 2>/dev/null`"
  HOST="`cat ${i}/host 2>/dev/null`"

  #
  # IPv4 networking
  # 
  IPS4=
  IP4=`cat ${i}/ipv4 2>/dev/null`
  if [ -e "${i}/alias-ipv4" ] ; then
    while read line
    do
      IPS4="${IPS4} ${line}" 
    done < "${i}/alias-ipv4"
  fi

  BRIDGEIPS4=
  BRIDGEIP4=`cat ${i}/bridge-ipv4 2>/dev/null`
  if [ -e "${i}/alias-bridge-ipv4" ] ; then
    while read line
    do
      BRIDGEIPS4="${BRIDGEIPS4} ${line}" 
    done < "${i}/alias-bridge-ipv4"
  fi

  GATEWAY4=`cat ${i}/defaultrouter-ipv4 2>/dev/null`

  #
  # IPv6 networking
  # 
  IPS6=
  IP6=`cat ${i}/ipv6 2>/dev/null`
  if [ -e "${i}/alias-ipv6" ] ; then
    while read line
    do
      IPS6="${IPS6} ${line}" 
    done < "${i}/alias-ipv6"
  fi

  BRIDGEIPS6=
  BRIDGEIP6=`cat ${i}/bridge-ipv6 2>/dev/null`
  if [ -e "${i}/alias-bridge-ipv6" ] ; then
    while read line
    do
      BRIDGEIPS6="${BRIDGEIPS6} ${line}" 
    done < "${i}/alias-bridge-ipv6"
  fi

  GATEWAY6=`cat ${i}/defaultrouter-ipv6 2>/dev/null`

  # Check if we are autostarting this jail
  if [ -e "${i}/autostart" ] ; then
    AUTO="Enabled"
  fi
 
  # Figure out the type of jail
  if [ -e "${i}/jail-portjail" ] ; then
    TYPE="portjail"
  elif [ -e "${i}/jail-pluginjail" ] ; then
    TYPE="pluginjail"
  elif [ -e "${i}/jail-linux" ] ; then
    TYPE="linuxjail"
  else
    TYPE="standard"
  fi

  JAILNAME=`echo ${i}|sed -E 's|^.(.+).meta|\1|'`

  ${PROGDIR}/scripts/backend/checkstatus.sh ${JAILNAME} 2>/dev/null
  if [ "$?" = "0" ]
  then
    STATUS="Running"
  else
    STATUS="Stopped"
  fi

  if [ "${VERBOSE}" = "YES" ] ; then
    cat<<__EOF__ 

ID: ${ID}
HOST: ${HIST}
IP4: ${IP4}
ALIASIP4: ${IPS4}
BRIDGEIP4: ${BRIDGEIP4}
ALIASBRIDGEIP4: ${BRIDGEIPS4}
DEFAULTROUTER4: ${GATEWAY4}
IP6: ${IP6}
ALIASIP6: ${IPS6}
BRIDGEIP6: ${BRIDGEIP6}
ALIASBRIDGEIP6: ${BRIDGEIPS6}
DEFAULTROUTER6: ${GATEWAY6}
AUTOSTART: ${AUTOSTART}
STATUS: ${STATUS}
TYPE: ${TYPE}

__EOF__

  else
    printf "%-24s%-12s%-12s%-12s\n" ${HOST} ${AUTO} ${STATUS} ${TYPE}
  fi
done

