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
    outputFile = f"../temp/newfile{i}.rein"
    #create the new file that keep track of removed experiments in case there are multiple cores
    saveFile = "../temp/savefile.rein"
    fr = open(file, "r")
    fw = open(outputFile, "w")
    fs = open(saveFile, "a")
    line = fr.readline()
    
    if option == 1: 
        
        while line:

            #ignore lines that are commented out 
            if line[:2] != "//":
                
                #only write out the line to newfile if it doesn't contain the experiment we are up to removing
                if not eNames[n] in line: fw.write(line)

                #write all other lines to savefile 
                else: fs.write(line)

            line = fr.readline()

    if option == 2:
        count = 0
        
        #read in the original file and only write out the lines that are not 
        #part of the experiment we are removing
        while line:
            
            #ignore lines that are commented out 
            if line[:2] != "//":

                #if the current line doesn't contain an experiment, write it to both files
                if not "#Experiment" in line: 
                    fw.write(line)
                    fs.write(line)
                
                else:

                    count += 1

                    #if this experiment is not the one we're removing, write it to newfile
                    if n != count: fw.write(line)

                    #if it is the one we're removing, write it to savefile
                    else: fs.write(line)


            line = fr.readline()

    fr.close()
    fw.close()
    fs.close()


    #base case depends on option so figure out if it has been triggered
    basecase = False
    if option == 1 and n > len(eNames): basecase = True
    if option == 2 and n >= count: basecase = True

    #base case, once we've checked all the experiments from the original file
    if basecase: 

        #any experiments left in file at this point are part of the inconsistancy core
        #go through the current file and put any experiments that are left into a list
        f = open(file, "r")
        line = f.readline()
        core = []
        while line: 
            if line[:1] == "#" or line[:2] == "(#": 
                core += [line]
            line = f.readline()

        #before we return the inconsistancy core, we want to make sure savefile 
        #doesn't contain another one new one so run the latest version of it 
        #through rein 

        #tell rein which file to run
        f = open("../temp/curFile.txt", 'w')
        f.write(saveFile)
        f.close()

        #run the rein jupyter notebook on the savefile 
        with open('REINnotebook.ipynb') as ff:
            nb_in = nbformat.read(ff, nbformat.NO_CONVERT)

        ep = ExecutePreprocessor(timeout=1200, kernel_name='ifsharp')

        nb_out = ep.preprocess(nb_in)

        #catch the result
        result = nb_out[0]['cells'][0]['outputs'][1]['data']['text/plain']

        #don't know why this clean up doesn't work 
        #for num in range(i-1):
        #   os.remove(f'newfile{num}.rein')

        #if savefile has no core, return the just this core
        if result == '"Solution(s) found"': return core

        #otherwise we need to find the core in savefile
        other_core = findCore(saveFile, option, eNames)
        return [core, other_core]

    #end of basecase
    
    #tell rein which temp file we are up to 
    f = open("../temp/curFile.txt", 'w')
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

    #clear curFile and saveFile for next use
    f = open("../temp/curFile.txt", 'w')
    f.write("")
    f.close()
    f = open("../temp/savefile.rein", 'w')
    f.write("")
    f.close()

main()

