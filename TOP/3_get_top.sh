#!/bin/bash
###########################################
##  Generation of topology though ACPYPE ##
##					 ##
###########################################

obabel -igro *.gro -O *.pdb
acpype -i *.pdb -o gmx
