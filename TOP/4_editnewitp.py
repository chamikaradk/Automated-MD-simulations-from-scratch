#######################################################
##						     ##
## Generate the ITP file with calculated CM5 charges ##
## Code developed by Chamikara Karunasena            ##
#######################################################

import pandas as pd
import numpy as np
import sys
optline = "!   Optimized Parameters   !"
startline = "Hirshfeld charges, spin densities, dipoles, and CM5 charges using IRadAn="
endline = " Hirshfeld charges with hydrogens summed into heavy atoms:"

#1. read log get charges - get cm5
def getcharges(loginputfile):

    printgo, printgo2 = False, False
    optimizedlines, charges = [], []
    chargefile = open('charges.txt', 'w+')  # open file handler for writing

    with open(loginputfile, "r") as logfile:
        allines = logfile.readlines()

        for line in allines:  # search for start end line
            if optline in line:
                printgo = True
            if startline in line:
                printgo2 = True
            if endline in line:
                printgo, printgo2 = False, False
            if printgo and printgo2:
                optimizedlines.append(line.split())
    chg = optimizedlines[2:-1] # skip header lines
    charges4 = pd.DataFrame()     #convert to dataframe
    for i in chg:
        #charges4[i] = float(i[2])
        charges.append(float(i[7]))
    chargefile.write(F'{charges} \n')

    chargefile.close()            #write to a text file for monitoring
    return charges

#2. replace charges and make new itp
def makenewitp(olditpfile, codename):
    part1, part2, part3, part4 = [], [], [], []
    go = False

    with open(olditpfile, "r") as itpfile:
        contents = itpfile.readlines()
        # print first half - everything before [ atoms ]
        for line in contents:
            if line.startswith("[ atoms ]"):
                break
            else:
                part1.append(line)
        part1.append('[ atoms ]')  # fill up missing part

        # print third half - after [ bonds ]
        for line in contents:
            if line.startswith("[ bonds ]"):
                go = True
            if go:
                part3.append(line)
        go = False

        # take data in second half
        for line in contents:
            if ";   nr  type  resi  res  atom  cgnr     charge" in line:
                go = True
            if "[ bonds ]" in line:
                # go = False
                break
            if go:
                part2.append(line)

        # take part2 lines ready to dataframe
        for i in part2[1:-1]:  # read lines and skip last line
            part4.append(i.split())
    # replace new charges with old charges

    data = pd.DataFrame(part4)
    data[6] = getcharges(loginputfile='../DFT/opt_'+code_name+'.log')

    # correct residue charge - only add or subtract onto ha atoms
    charges = data[6].round(6)
    correction = data[6].sum().round(6) / np.absolute(data[6].sum().round(6) / 0.000001)  # get correctional divisor (10^-6) with sign
    # iterate as long as charge sum is not equal to zero
    while charges.sum().round(6) != 0.000000:
        for line in data.groupby([1]).groups["ha"]:
            if charges.sum().round(6) == 0.000000:
                break
            ha_line = charges[line]
            charges[line] = ha_line - correction
        data[6] = charges.round(6)
    
    print(data[6].sum().round(6))
    # print all lines combined to output file
    with open('{}_GMX.itp'.format(codename), 'w') as file:
	#file.truncate(0) 
        print(''.join(part1), file=file)
        print(data.to_string(index=False, header=False), file=file,
              sep='\t')  # prints dataframe without header and index
        print(''.join(part3), file=file)

#invoke function to make newitp with charges

#data = makenewitp('NDT_molbackup.itp',code_name)
#makenewitp('NDT.acpype/NDT_GMX.itp', 'NDT')
if __name__ == '__main__':  #run this way to pass input from bash main
    code_name = sys.argv[1]
    makenewitp(code_name+'.acpype/'+code_name+'_GMX.itp',code_name)
