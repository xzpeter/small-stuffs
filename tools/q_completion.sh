_q_complete()
{
    local sub_cmd_list
    sub_cmd_list=$(q | grep "^- " | sed 's/.*: //; s/[,()/]/ /g')
    COMPREPLY=()
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    cur="${COMP_WORDS[COMP_CWORD]}"
    if [[ "$prev" == "q" ]]; then
        if [[ "$cur" == *+* ]]; then
            # completion with existing keys
            existing=${cur%+*}
            new_list=$(compgen -W "${sub_cmd_list}" -- ${cur##*+})
            new_list=$(echo "$new_list" | sed "s/^/${existing}+/")
            COMPREPLY=( $new_list )
        else
            # completion for the first key
            COMPREPLY=( $(compgen -W "${sub_cmd_list}" -- ${cur}) )
        fi
    fi
}
complete -F _q_complete q
