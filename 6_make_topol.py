
#######################################################
##						     ##
## Generate the Topology      	 		     ##
## Developed by Chamikara Karunasena                 ##
#######################################################
import re
import sys
Natoms = []
Toplines = []
if __name__ == '__main__':  #run this way to pass input from bash main
    code_name = sys.argv[1]

#read box.gro and get the number of atoms
def getnumatoms(gmxinput):
    with open(gmxinput, "r") as gmxfile:
        contents = gmxfile.readlines()[-2] #read last two line and get num atom values
        temp = re.compile("([0-9]+)([a-zA-Z]+)") # break text into num + string pattern
        natoms = temp.match(contents.split()[0]).groups()
    return natoms[0]

#copy and modify topology file
def maketop(oldtopfile,codename,Nmols):
    with open (oldtopfile, "r") as oldtop:
        contents = oldtop.readlines()
        for line in contents:
            if "; Compound" in line:
                break
            else:
                Toplines.append(line)
        Toplines.append(codename + "        " + str(Nmols) )

    with open('{}.top'.format(codename), 'w') as file:
       #file.truncate(0)
       print(''.join(Toplines), file=file)

maketop('TOP/'+code_name+'.acpype/'+code_name+'_GMX.top', code_name, getnumatoms("box.gro"))
