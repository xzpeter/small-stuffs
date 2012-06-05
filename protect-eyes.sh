#!/bin/bash

# this is a small script to protect my eyes
# some programs have to be installed correctly, e.g.,

# MOCP: the console music player
# ZENITY: the GUI for GTK
# GNOME-SCREENSAVER-COMMAND: to control screens and read status

# anyone can use this. xzpeter@gmail.com

# some configuration variables
working_max_mins=80
# set this to a directory that stores some musics. 
music_dir="/media/DataVol/music/favors/"

# this is the count of working seconds
working_count=0

warning_length_secs=60
working_max_secs=`expr $working_max_mins \* 60 - $warning_length_secs`

function warn_to_rest() {
    count=0
    max_bar=$warning_length_secs
    while [ 1 ]; do
	sleep 1
	count=`expr $count + 1`
	bar_value=`expr 100 \* $count / $max_bar`
	echo $bar_value
    done | zenity --progress --text "已经工作了 ${working_max_mins} 分钟了！该
    休息一下了！ ${warning_length_secs} 秒后进入屏幕保护..." --auto-close --no-cancel
    giveup=$?
    working_count=0
    if [ $giveup = "0" ]; then
	musics=(`ls $music_dir`)
	n=`ls | wc -l`
	random -e $n
	mocp -l ${musics[$?]}
	gnome-screensaver-command -l
    fi
}

function check_current_status() {
    gnome-screensaver-command -q | grep 未激活 > /dev/null
    working=$?
    if [ $working = "0" ]; then
	working_count=`expr $working_count + 1`
	echo "$working_count/$working_max_secs"
    else
	working_count=0
    fi
}

while [ 1 ]; do
    check_current_status
    sleep 1
    if [ $working_count -gt $working_max_secs ]; then
	warn_to_rest
    fi
done
