
#######################################################
##						                             ##
## Generate the crystal supercell 		             ##
## Developed by Chamikara Karunasena                 ##
#######################################################

#run gmxapi to handle gromacs command line

#This code generate a supercell box with nearly equal x, y, z, dimensions based on unit cell

import numpy as np
import gmxapi as gmx
import sys
import os

if __name__ == '__main__':  #run this way to pass input from bash main
    code_name = sys.argv[1]
    box_size = sys.argv[2]


def getboxparams(file, repeat):  #get a nearly cubic box parameter
    with open(file) as ucellfile:
        lastline = ucellfile.readlines()[-1]
        boxparams, celparams, celpar, newbox, factor =np.array([]), np.array([]), np.array([]),np.array([]),np.array([]),
        for i in range(3):
            celparams = float(lastline.split()[i])
            boxparams = np.append(boxparams, celparams)
        #boxparams = celparams / np.max(celparams)
        factor =boxparams.max() / boxparams
        newbox = np.around(factor * repeat)
    return newbox

#define a global vaiable to store data from the function
newbox = getboxparams(code_name+'_UC.gro', float(box_size))

genconf = gmx.commandline_operation('gmx_mpi', arguments=['genconf', '-nbox', str(int(newbox[0])), str(int(newbox[1])), str(int(newbox[2]))], input_files={'-f': code_name+'_UC.gro'}, output_files={'-o': 'box.gro'})

genconf.run()



