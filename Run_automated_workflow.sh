#!/bin/bash
##SBATCH -t 7-00:00:00                                   #Time for the job to run 
#SBATCH -t 1:00:00                             #Time for the job to run 
#SBATCH --job-name=NDT-auto                     #Name of the job

#SBATCH -N 1                                    #Number of nodes required
#SBATCH -n 16                                   #Number of cores needed for the job
#SBATCH -e wall.err                             #Number of cores needed for the job
##SBATCH --partition=SKY32M192_L                 #Name of the queue
#SBATCH --partition=CAL48M192_D                 #Name of the queue
#SBATCH --mail-type ALL                         #Send email on start/end
#SBATCH --mem 180000MB                         #Send email on start/end
##SBATCH --mail-user cdka229@uky.edu            #Where to send email
#SBATCH --account=col_cmri235_uksr              #Name of account to run under

module swap intel gnu7/7.3.0
module swap impi/2018.3.222 openmpi3
module load ccs/cuda/10.0.130
module load ccs/gaussian/g16-A.03/g16-sandybridge
source ~/.bashrc
source /pscratch/cmri235_uksr/cdka229/gmxapi_4/gromacs/bin/GMXRC

set -e

conda activate ocelot

cif_file=812876_NDT.cif
code_name=NDT
box_size=5

python 1_cif2gro.py $cif_file $code_name
cd DFT 
python 2_run_DFT.py $code_name 
cd ../

conda activate gmxapi20.1

cd TOP
source 3_get_top.sh
python 4_editnewitp.py $code_name
cd ../
cp TOP/*_GMX.itp ./

python 5_getbox.py $code_name $box_size
python 6_make_topol.py $code_name
touch INITIALIZATION-DONE
#===========================================================
#creates equllibrated MD 
#assign temperature  
#=======================================================MDRUN
refT=298
timestep=0.002
python 7_mdrun_em.py $code_name 
python 8_mdrun_nvt.py $code_name $refT $timestep 1000
python 9_mdrun_npt.py $code_name $refT $timestep 1000
python 10_mdrun_PR.py $code_name $refT $timestep 1000
touch MD_EQUILIBRATION-DONE
#============================================================
#creates anneal simulation with 2 ns pre eq followed by 6 ns 
#post eq of the annealed structure
#define the anneal temp and rate to run
#=======================================================MDRUN
timestep=0.001 #fs
annealT=850  #K 
annealrate=20 #K/ns
python 11_heat.py $code_name $refT $timestep $annealT $annealrate
python 12_cool.py $code_name $refT $timestep $annealT $annealrate
touch ANNEAL-DONE
