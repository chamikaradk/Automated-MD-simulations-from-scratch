#######################################################
##						     ##
## Run the pre-equilibration - NPT ensemble          ##
## Developed by Chamikara Karunasena                 ##
#######################################################
import gmxapi as gmx
import os
import glob
import subprocess
import sys

if __name__ == '__main__':  #run this way to pass input from bash main
    code_name = sys.argv[1]
    refT = sys.argv[2]
    timestep = sys.argv[3]
    nsteps = sys.argv[4]

step='npt'
previous_step='nvt'
maxwarns='0'


# create mdp file
newlines = []
def edit_mdp(step, refT, timestep, nsteps):
    with open ('MDP/'+step+'_equil.mdp', "r") as mdpcontents:
        alllines = mdpcontents.readlines()
        for line in alllines:
            if line.startswith('nsteps'): #lines to look for
                newlines.append("nsteps = "+str(nsteps)+'\n')
                continue
            if line.startswith('dt '):
                newlines.append("dt = "+str(timestep)+'\n')
                continue
            if line.startswith('ref-t'):
                newlines.append("ref-t = "+ str(refT)+'\n')
                continue #move on to next line
            if line.startswith('gen-temp'):
                newlines.append("gen-temp = "+str(refT)+'\n')
                continue
            else:
                newlines.append(line)
    with open('MDP/{}_new.mdp'.format(step), 'w') as outfile:
        #outfile.truncate(0)
        print(''.join(newlines), sep='\n\t', file=outfile)

edit_mdp(step, refT, timestep, nsteps)


#NVT STEP
grompp_em = gmx.commandline_operation('gmx_mpi', 'grompp',
                                   input_files={
                                       '-f': 'MDP/'+step+'_new.mdp',
                                       '-c': previous_step+'.gro',
                                       '-p': code_name+'.top',
				      '-maxwarn': maxwarns,
 
                                   },
                                   output_files={'-o': step+'.tpr'}
                                   )

grompp_em.run() #generates nvt.tpr

# run MD code
mdcode = 'mpirun -np 4 gmx_mpi mdrun -ntomp 8 -v -pin on -deffnm '+step
#proc = subprocess.Popen(mdcode.split(), stdout = subprocess.PIPE)
proc = subprocess.run(mdcode.split(), capture_output=True)

