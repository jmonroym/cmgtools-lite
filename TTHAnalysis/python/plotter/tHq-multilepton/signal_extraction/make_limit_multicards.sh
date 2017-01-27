#!/bin/bash

#This script takes as argument a files with the list of cards to be used
#to execute run: source make_limit_multicards.sh list.txt 

# Set environment for combine                                                                                                                                                                               
COMBINEDIR="/afs/cern.ch/user/s/stiegerb/combine/"                                                                                                                                                        
cd $COMBINEDIR; eval `scramv1 runtime -sh`; cd -;
#it=0;
while IFS='' read -r line || [[ -n "$line" ]]; do
    #it=$((it+1))
    #echo "$line">>limits_$it.dat;
    combine -M Asymptotic --run blind --rAbsAcc 0.0005 --rRelAcc 0.0005 $line >> limit_$line.dat;
done < "$1"

# Set back environment                                                                                                                                                                                     
eval `scramv1 runtime -sh`;
