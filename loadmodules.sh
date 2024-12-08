#!/bin/bash

module swap intel/19.1.3.304 gnu7
module swap impi/2018.3.222 openmpi3
module load ccs/cuda/10.0.130
module load ccs/gaussian/g16-A.03/g16-sandybridge



source /pscratch/cmri235_uksr/cdka229/gmxapi_3/gromacs/bin/GMXRC
