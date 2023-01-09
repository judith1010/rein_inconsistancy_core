#!/usr/bin/env python3

#import subprocess
import sys
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
import os 

def findCore(file, n=0, i=0):
    
    # read in the original rein file 
    fr = open(file, "r")
    line = fr.readline()
    count = 0
    experiment = ""
    
    #find the name of the experiment that we are up to removing
    while line: 

        if line[:1] == "$" and n == count:
            end = line.index(':')
            experiment = line[1:end]
            break
        if "}" in line: count += 1
        line = fr.readline()

    print (f'Removing Experiment {experiment} :')
    fr.close()
    
    #create the new temp file that will be the same as the original minus one experiment 
    outputFile = f"/mnt/tacas/Examples/temp/newfile{i}.rein"
    fr = open(file, "r")
    fw = open(outputFile, "w")

    line = fr.readline()
    count = 0
    removeExperiment = False
    
    #read in the original file and only write out the lines that are not 
    #associated with the experiment we are removing
    while line:

        if line[:1] == "$" and n == count: removeExperiment = True
            
        if not removeExperiment and not f'${experiment}' in line: fw.write(line)

        if "}" in line: 
            removeExperiment = False 
            count += 1

        line = fr.readline()

    fr.close()
    fw.close()

    #base case, once we've checked all the experiments from the original file
    if n >= count: 
        
        #any experiments left in the file at this point are part of the nconsistancy core
        #go through the current file and put any experiments that are left into a list
        f = open(file, "r")
        line = f.readline()
        core = []
        while line: 
            if line[:1] == "$": 
                end = line.index(':')
                core += [line[1:4]]
            line = f.readline()
            
        #for num in range(i-1):
        #   os.remove(f'newfile{num}.rein')
        #return the inconsistancy core
        return core

    #p = subprocess.Popen("dotnet fsi rein.fsx" , stdout=subprocess.PIPE, shell=True)
    #result = p.communicate()
    #print(result)
    
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
    if result == '"Solution(s) found"': return findCore(file, n+1, i+1)
    
    #special case: only one experiment yielded no solutions, experiment itself is the core
    if n == 0 and count == 1: 
        
        #read through the temp file and return the only experiment that's left  
        f = open(file, "r")
        line = f.readline()
        while line: 
            if line[:1] == "$": 
                end = line.index(':')
                return line[1:end]
            line = f.readline()
    #if removing this experiment did not yield results, its not part of the core
    #continue the recursion with the new tmep file, removing experiments from the same position
    return findCore(outputFile, n, i+1)


def main():
    file = sys.argv[1]
    print(f"Inconsistancy Core: {findCore(file)}")
    f = open("curFile.txt", 'w')
    f.write("")
    f.close()

main()
