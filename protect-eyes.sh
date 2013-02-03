#!/bin/bash

# this is a small script to protect my eyes
# some programs have to be installed correctly, e.g.,

# MOCP: the console music player
# ZENITY: the GUI for GTK
# GNOME-SCREENSAVER-COMMAND: to control screens and read status
#   or MINT-SCREENSAVER-COMMAND: which is the same one on mint system

# anyone can use this. xzpeter@gmail.com

# some configuration variables
working_max_mins=80
# set this to a directory that stores some musics. 
music_dir="/media/DataVol/music/favors/"

# checking the system
if cat /etc/issue | grep Mint > /dev/null; then
    screen_cmd="mate-screensaver-command"
elif cat /etc/issue | grep -E "Ubuntu|Debian" > /dev/null; then
    screen_cmd="gnome-screensaver-command"
else
    echo "current system not supported"
    exit 1
fi

# this is the secret to live longer:
# http://www.ted.com/talks/jane_mcgonigal_the_game_that_can_give_you_10_extra_years_of_life.html
live_longer_str="别忘了长寿的秘诀：\n\
1. 高举双拳5秒钟\n\
2. 从100开始不断减n，n为当前星期数\n\
3. 望望窗外/窗内/看看喜欢的小动物\n\
4. 问候一下自己在乎的人\n"

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
    休息一下了！ ${warning_length_secs} 秒后进入屏幕保护...\n\n${live_longer_str}" --auto-close
    giveup=$?
    working_count=0
    if [ $giveup = "0" ]; then
		if [ ! -d $music_dir -a `which mocp` ]; then
			musics=(`ls $music_dir`)
			n=`ls | wc -l`
			random -e $n
			mocp -l ${musics[$?]}
		fi
		$screen_cmd -l
    fi
}

function am_i_working()
{
    $screen_cmd -q | grep -E "未激活|inactive"> /dev/null
	if [ $? = "0" ]; then
		echo "yes"
	else
		echo "no"
	fi
}

function check_current_status() {
    working=`am_i_working`
    if [ $working = "yes" ]; then
		working_count=`expr $working_count + 1`
		echo "$working_count/$working_max_secs" > /dev/shm/protect-eye.current
    else
		working_count=0
    fi
}

if [ ! -z "$1" ]; then
	working_count=$1
fi

while [ 1 ]; do
    check_current_status
    sleep 1
    if [ $working_count -gt $working_max_secs ]; then
		warn_to_rest
    fi
done
