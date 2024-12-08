#############################################
##Generate DFT calculated CM5 charges      ##
##					                       ##
#############################################

import multiprocessing
import subprocess
from pymatgen.io.gaussian import *
from pymatgen.core.structure import Molecule
import sys
cpus = [multiprocessing.cpu_count() if multiprocessing.cpu_count() < 16 else 16]
nprocs = str(cpus[0])


def generate_gaussian_input(paramset=None,mol=None):
    route_parameters = paramset["route_parameters"]
    #input_parameters = paramset["input_parameters"]
    charge = paramset["charge"]
    multiplicity = paramset["multiplicity"]
    functional = paramset["functional"]
    basis_set = paramset["basis_set"]
    ginput = GaussianInput(mol=mol,charge=charge, spin_multiplicity=multiplicity,
                           title=None, functional=functional, basis_set=basis_set,
                           route_parameters=route_parameters,  dieze_tag="#P")
    return ginput
def run_task(mol_xyz, gaussian_cmd, prefix, iop_str=None):
    # get parameter
    paramset = {
        "route_parameters":{
            "opt": "", "pop": "cm5",
            "scf(maxcyc=512)" : ""
        },
        "functional": "wb97xd",
        "basis_set": "6-31g(d)",
        "charge": 0,
        "multiplicity": 1
    }
    if iop_str:
        paramset["route_parameters"].update({"iop(3/107={},3/108={})".format(iop_str, iop_str): ""})
    mol = Molecule.from_file(mol_xyz)
    file_com = prefix + ".com"
    file_chk = prefix + ".chk"
    file_log = prefix + ".log"

    gauss_inp = generate_gaussian_input(paramset=paramset, mol=mol)
    gauss_inp.link0_parameters = {"%chk": file_chk, "%mem": "48GB", "%nprocshared": nprocs}
    gauss_inp.write_file(file_com, cart_coords=True)



# run gaussian optimize until normal termination is achieved. max runs is 5
    converged = False
    runs = 0
    while not converged and runs < 5:
        runs += 1
        # write input files for gaussian optimization calculation
        gauss_inp = generate_gaussian_input(paramset=paramset, mol=mol)
        gauss_inp.link0_parameters = {"%chk": file_chk, "%mem": "48GB", "%nprocshared": nprocs}
        gauss_inp.write_file(file_com, cart_coords=True)
        # run gaussian optimization
        return_code = subprocess.call(gaussian_cmd + " " +file_com, shell=True)
        gout = GaussianOutput(file_log)
        # check for normal termination
        if not gout.properly_terminated:
            mol = gout.final_structure
        else:
            '''# generate input for frequency calculation
            ginp = gout.to_input()
            # update route parameters
            if ginp.route_parameters.get("iop(3107", ):
                iop_str = ginp.route_parameters["iop(3107"].split(",")[0]
                ginp.route_parameters = {"iop(3/107={},3/108={})".format(iop_str, iop_str): "", "freq": "",
                                         "Geom": "AllCheck", "Guess": "TCheck", "SCRF": "Check"}
            else:
                ginp.route_parameters = {"freq": "", "Geom": "AllCheck", "Guess": "TCheck", "SCRF": "Check"}
            ginp.link0_parameters = {"%chk": "freq.chk", "%mem": "48GB", "%nprocshared": nprocs, "%oldchk": file_chk}
            ginp.dieze_tag = '#P'
            ginp.write_file("freq.com", cart_coords=True)
            # run gaussian frequency
            return_code = subprocess.call(gaussian_cmd + "  freq.com", shell=True)
            gout = GaussianOutput("freq.log")
            if not gout.properly_terminated:
                raise RuntimeError("Frequency calculation failed Normal termination")
            if gout.frequencies[0][0]["frequency"] < 0:
                pass 
            else:'''
            converged = True
            gout = GaussianOutput(file_log)
            mol = gout.final_structure
    if not converged:
        raise RuntimeError("Structure not converged")


if __name__ == '__main__':  #run this way to pass input from bash main
    code_name = sys.argv[1]
    run_task(code_name+'.xyz','g16', prefix='opt_'+code_name, iop_str=None)



#run_task('NDT.xyz','g16', prefix="opt_NDT", iop_str=None)
