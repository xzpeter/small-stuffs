_qtool_complete()
{
    local sub_cmd_list
    sub_cmd_list=$(qtool | sed '1,4d; s/:.*//')
    COMPREPLY=()
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    cur="${COMP_WORDS[COMP_CWORD]}"
    if [[ "$prev" == "qtool" ]]; then
        COMPREPLY=( $(compgen -W "${sub_cmd_list}" -- ${cur} ))
    fi
}
complete -F _qtool_complete qtool
