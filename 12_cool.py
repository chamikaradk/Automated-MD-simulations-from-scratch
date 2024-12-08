#######################################################
##						     ##
## Run the production run - solidify the melt        ##
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
    annealT = sys.argv[4]
    annealrate = sys.argv[5]

step = 'npt_revanneal'
previous_step='npt_anneal'
maxwarns='0'

#create mdp file
newlines = []
eqtime = 2000

times = [0, eqtime, (((int(annealT)-int(refT))/int(annealrate))*1000)+eqtime, (((int(annealT)-int(refT))/int(annealrate))*1000)+eqtime*4]

def edit_mdp(step, refT, timestep, annealT):
     with open ('MDP/'+step+'_equil.mdp', "r") as mdpcontents:
         alllines = mdpcontents.readlines()
         for line in alllines:


             if line.startswith('nsteps'): #lines to look for
                 newlines.append("nsteps = "+str(round(times[3]*1000))+'\n')
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
             if line.startswith('annealing-time'):
                 newlines.append("annealing-time = "+ str(' ').join([str(int(v)) for v in times]) + '\n')
                 continue
             if line.startswith('annealing-temp'):
                 newlines.append("annealing-temp = "+str(annealT)+" "+str(annealT)+" "+str(refT)+" "+str(refT)+'\n')
                 continue
             else:
                 newlines.append(line)
         with open('MDP/{}_new.mdp'.format(step), 'w') as outfile:
             print(''.join(newlines), sep='\n\t', file=outfile)

edit_mdp(step, refT, timestep, annealT)
#NVT STEP

grompp_em = gmx.commandline_operation('gmx_mpi', 'grompp',
                                   input_files={
                                       '-f': 'MDP/'+step+'_new.mdp',
                                       '-c': previous_step,
                                       '-p': code_name+'.top',
				       '-maxwarn': maxwarns,
                                   },
                                   output_files={'-o': step+'.tpr'}
                                   )

grompp_em.run() #generates nvt.tpr
# run MD code

mdcode = 'mpirun -np 4 gmx_mpi mdrun -ntomp 4 -v -pin on -deffnm '+step
#proc = subprocess.Popen(mdcode.split(), stdout = subprocess.PIPE)
proc = subprocess.run(mdcode.split(), capture_output=True)


