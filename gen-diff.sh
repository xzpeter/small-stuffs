#!/bin/bash
git diff HEAD~ > ~/review
scp ~/review mac:
