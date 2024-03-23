#!/bin/bash

set -e

tags_dir="tags/"
branch="$1"

if [[ -z "$branch" ]]; then
    echo "usage: $0 <branch>"
    echo
    echo "Switch to the branch <branch> with its tags"
    exit -1
fi

old=$(git branch --show-current)

if [[ -z "$old" ]]; then
    # We're not under a valid branch so far, do the checkout and done
    git checkout $branch
    exit 0
fi

git checkout $branch
old_dir=$tags_dir/$old

if ls ./cscope* &> /dev/null; then
    echo "Found cscope tags for branch '$old', updating in cache"
    mkdir -p $old_dir
    rm -f $old_dir/cscope*
    mv ./cscope* $old_dir
else
    echo "No tags found for the old branch"
fi

new_dir=$tags_dir/$branch
if [[ ! -d $new_dir ]]; then
    # didn't have history tags, ignor
    echo "Didn't see old cscope tags, skip"
    exit 0
fi

if ls $new_dir/cscope* &> /dev/null; then
    echo "Found existing tags for new branch '$branch', restoring"
    mv $new_dir/cscope* ./
fi
