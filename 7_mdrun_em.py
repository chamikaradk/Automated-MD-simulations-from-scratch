#######################################################
##						     ##
## Run the pre-equilibration - Steepest Descent      ##
## Developed by Chamikara Karunasena                 ##
#######################################################
import gmxapi as gmx
import os
import glob
import subprocess
import sys


#create mdp file 

#define job protocols

step_name='em'
maxwarns='1'
previous_step='box'
if __name__ == '__main__':  #run this way to pass input from bash main
    code_name = sys.argv[1]

#EM STEP
grompp_em = gmx.commandline_operation('gmx_mpi', 'grompp',
                                   input_files={
                                       '-f': 'MDP/'+step_name+'.mdp',
                                       '-c': previous_step+'.gro',
                                       '-p': code_name+'.top',
				       '-maxwarn': maxwarns,
                                   },
                                   output_files={'-o': step_name+'.tpr'}
                                   )

grompp_em.run() #generates em.tpr
# run MD code

mdcode = 'mpirun -np 1 gmx_mpi mdrun -ntomp 8 -v -pin on -deffnm '+step_name
#proc = subprocess.Popen(mdcode.split(), stdout = subprocess.PIPE)
proc = subprocess.run(mdcode.split(), capture_output=True)
