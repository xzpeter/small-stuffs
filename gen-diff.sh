#!/bin/bash
git diff HEAD~ > ~/review
scp ~/review mac:
rm -rf ~/review
