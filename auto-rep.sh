#!/bin/bash

# this script will do some auto replacing work.

# CATUION: default, memset is replaced by EmcpalZeroMemory, check this
# using grep when not setting to zero, and use EmcpalFillMemory!

# declaring the rules
declare -a rules=(
"strcpy|csx_p_strcpy"
"strncpy|csx_p_strncpy"
"strtok|csx_p_strtok"
"strcat|csx_p_strcat"
"strlen|csx_p_strlen"
"strncat|csx_p_strncat"
"memcpy|csx_p_memcpy"
"sscanf|csx_p_sscanf"
"memcmp|csx_p_memcmp"
"strcmp|csx_p_strcmp"
"strnicmp|csx_p_strncasecmp"
"lstrcmpi|csx_p_strcasecmp"
"atoi|csx_p_atoi_u32"
"_atoi64|csx_p_atoi_u64"
"_strtoui64|csx_p_atoi_u64"
"sprintf|csx_p_sprintf"
"vprintf|csx_p_stdio_vprintf"
"printf|csx_p_stdio_printf"
"memset|csx_p_memset"		# Caution: we may need memzero() instead
"fprintf|csx_p_stdio_fprintf" 	# Caution: we may need stderr redefines
"vfprintf|csx_p_stdio_vfprintf" # Caution: we may need stderr redefines
"fgets|csx_p_stdio_fgets" 	# Caution: we may need stderr redefines
"fflush|csx_p_stdio_fflush"	# Caution: we may need stderr redefines
)

function usage() {
    cat <<EOF

usage: $0 <command>

Here, <command> can be: 
	list:    list all the original replacement list
	grep:    try to grep all the keywords
	replace: automatically replace the keywords

EOF
}

val=$1
word_list="strlen strcpy strcat memcpy memset sscanf atoi _atoi64"

# this is a function do the API replacement.
# we should provide some params:
# 	FILES: 	should be some wildcard like "*.c"
#	FROM: 	the former API function name
#	TO:	the latter API function name
# actually our code only support C syntax replacement
function replace_API () {
    if [ $# -ne 2 ]; then
	echo "replace_API can only support 2 args. quitting"
	exit 1
    fi
    from=$1
    to=$2
    sed_str='{s/\<'$from'\>/'$to'/g}'
    find -name "*.c" | xargs sed -i $sed_str
}
# replace_API "*.c" strlen csx_p_strlen

function display_replacement {
    printf "%20s" $(echo_c red $1)
    echo -n " "
    echo_c white -n '-->'
    echo -n " "
    echo_c green $2
}

function do_traverse() {
    for i in ${rules[@]}; do
	rule=(${i/|/ })
	from=${rule[0]}
	to=${rule[1]}
	case $1 in
	    "list")
		display_replacement $from $to
		;;
	    "grep")
		echo_c white -ne "displaying API: "
		echo_c yellow $from
		find -name "*.c" -exec grep --color "\<${from}\>" {} \+
		;;
	    "replace")
		replace_API $from $to
		;;
	esac
    done
}

function handle_cmd() {
    case $1 in
	"list")
	    do_traverse list
	    ;;
	"grep")
	    do_traverse grep
	    ;;
	"replace")
	    do_traverse replace
	    ;;
	*)
	    usage
	    ;;
    esac
}

handle_cmd $1
