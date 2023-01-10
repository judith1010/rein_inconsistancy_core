#!/usr/bin/env python3

import subprocess
import sys
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
import os 

#Option 1 goes through the file broadly (experiment at a time)
#Option 2 goes through the file specifically (line at a time)
def findCore(file, option, eNames, n=0, i=0):
        
    #create the new temp file that will be the same as the original minus one experiment 
    outputFile = f"/mnt/tacas/Examples/temp/newfile{i}.rein"
    fr = open(file, "r")
    fw = open(outputFile, "w")
    line = fr.readline()
    
    if option == 1: 
        
        while line:

            #ignore lines that are commented out 
            if line[:2] != "//":
                
                #only write out the line if it doesn't contain the experiment we are up to removing
                if (n < len(eNames) and not eNames[n] in line) or n >= len(eNames): fw.write(line)

            line = fr.readline()

    if option == 2:
        count = 0
        
        #read in the original file and only write out the lines that are not 
        #part of the experiment we are removing
        while line:
            
            #ignore lines that are commented out 
            if line[:2] != "//":

                if not "#Experiment" in line or n != count: fw.write(line)
                #else: print(f"Removing {line}")

                if "#Experiment" in line: count += 1

            line = fr.readline()

    fr.close()
    fw.close()


    #base case depends on option so figure out if it has been triggered
    basecase = False
    if option == 1 and n > len(eNames): basecase = True
    if option == 2 and n >= count: basecase = True

    #base case, once we've checked all the experiments from the original file
    if basecase: 
        
        #any experiments left in the file at this point are part of the inconsistancy core
        #go through the current file and put any experiments that are left into a list
        f = open(file, "r")
        line = f.readline()
        core = []
        while line: 
            if line[:1] == "#" or line[:2] == "(#": 
                core += [line]
            line = f.readline()
            
        #for num in range(i-1):
        #   os.remove(f'newfile{num}.rein')

        #return the inconsistancy core
        return core

    
    #tell rein which temp file we are up to 
    f = open("curFile.txt", 'w')
    f.write(outputFile)
    f.close()
    
    #run the rein jupyter notebook on the temp file 
    with open('REINnotebook.ipynb') as ff:
    	nb_in = nbformat.read(ff, nbformat.NO_CONVERT)

    ep = ExecutePreprocessor(timeout=1200, kernel_name='ifsharp')

    nb_out = ep.preprocess(nb_in)

    #catch the result
    result = nb_out[0]['cells'][0]['outputs'][1]['data']['text/plain']
    print (result)

    #if removing this experiment yielded solutions, its part of the core
    #use the orginal file but look at the next experiemnt next time (put it back in) 
    if result == '"Solution(s) found"': return findCore(file, option, eNames, n+1, i+1)
    
    #special case: only one experiment yielded no solutions, experiment itself is the core
    specialcase = False
    if option == 1 and n == len(eNames-1): specialcase = True
    if option == 2 and n == 0 and count == 1: specialcase = True

    if specialcase:
        
        #read through the temp file and return the only experiment that's left  
        f = open(file, "r")
        line = f.readline()
        while line: 
            if line[:1] == "#" or line[:2] == "(#": 
                return line
            line = f.readline()

    #if removing this experiment did not yield results, its not part of the core
    #continue the recursion with the new tmep file, removing experiments from the same position
    return findCore(outputFile, option, eNames, n, i+1)

#go through a .rein file and return a list of the distinct experiment names
def findExperimentNames(file) -> set():
    experiments = set()
    f = open(file)
    line = f.readline()
    while line: 
        if "#Experiment" in line: 
            start = line.find("#Experiemnt")
            end = line.find("[")
            e = line[start:end]
            experiments.add(e)
        line = f.readline()

    return experiments


def main():
    file = sys.argv[1]
    if len(sys.argv) > 2: option = sys.argv[2]
    else: option = 1
    if option > 2: option = 2   #option can only be 1 or 2 
    names = []                  #if option is not 1, don't need all the experiement names
    if option == 1: names = list(findExperimentNames(file))
    print(f"Inconsistancy Core: {findCore(file, option, names)}")

    #clear curFile so its ready for next use
    f = open("curFile.txt", 'w')
    f.write("")
    f.close()

main()

#if core returns onlt one experiemnt, then the probelm is with the interactions not the experiments 



