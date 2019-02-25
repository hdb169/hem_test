#!/usr/bin/python

import re, sys
import pickle
import argparse
import os.path

parser = argparse.ArgumentParser(description='Check spectrometer field settings. You need hms and shms field data files and set current epics variables.')
parser.add_argument('-m','--mode',help='Identify spectrometer: hms, shms', required=True)
parser.add_argument('filename', type=str, help='path to standard.kinematics file')
args = parser.parse_args()
mode = args.mode

kin_file = args.filename
field_file = '%s_field.dat' % mode
epics_file = 'coin.pkl'

print_all = False

def main():

    if not os.path.isfile(field_file):
        print "****ERROR: Field data file does not exist!****"
        sys.exit()

    if not os.path.isfile(epics_file):
        print "****ERROR: EPICS data file does not exist!****"
        sys.exit()

    ## Read EPICS data file. Use qa.py if there is no epics file
    dde = {}
    dde = read_epics_file(epics_file)

    ddf = {}
    ddf = read_field_file(field_file)

    #print ddf['2.433']['HB']
    #print dde['6453'][variable]

    ## Read standard.kinematics
    kin_data = parse_kin_file(kin_file)

    fout =  open('output_field.%s' % mode, 'w')

    ##FIXME: REMOVE/MODIFY MIN RUN NUMBER!!!!!!!
    for ll in kin_data:
        if float(ll[0]) < 6009:
            continue
        elif float(ll[0]) > 6552:
            continue
        else:
            check_sanity(ll, dde, ddf, fout)

def check_sanity(ll, depics, dfield, fout):

    if mode == 'shms':
        epics_keys = {'HB':'ecSHB_I_coarse',
                      'Q1':'ecSQ1_I_coarse',
                      'Q2':'ecSQ2_I_coarse',
                      'Q3':'ecSQ3_I_coarse',
                      'Dipole':'ecSDI_I_coarse'}
    else:
#        epics_keys = {'NMR':'ecDI_B_True_NMR'}

       epics_keys = {'Q1':'ecQ1_I_coarse',
                     'Q2':'ecQ2_I_coarse',
                     'Q3':'ecQ3_I_coarse',
                     'Dipole':'ecDI_I_coarse',
                     'NMR':'ecDI_B_True_NMR'}

#        epics_keys = {'Q1':'ecQ1_I_coarse',
#                      'Q2':'ecQ2_I_coarse',
#                      'Q3':'ecQ3_I_coarse',
#                      'Dipole':'ecDI_I_coarse',
#                      'NMR':'ecDI_B_True_NMR'}


    ## ignore the default entry
    if int(ll[0]) == 0:
        return ""
    if int(ll[1]) == 9999:
        ll[1] = str(int(ll[0]))

    for runnum in range(int(ll[0]), int(ll[1])+1):
        run = str(runnum)
        bad_run_mark = False

        c_glob = "****FIXME:\t" + run
        c_keys = ""
        c_diff = ""

        pcent = "%.3f" % float(ll[3])
        ##CHECK IF KEY (PCENT) EXIST IN FIELD DATA
        if not pcent in dfield:
            print "RUN: %s CHECK FIELD DATA! MISSING MOMENTUM: %s" % (run, pcent)
            continue

        if run in depics:

            ## adding beam p check
            p_epics = depics[run]['HALLC:p'][0]
           # if abs(float(p_epics) - 10598) > 1.:
            if abs(float(p_epics) - 10598) > 0.:
                print run,   p_epics,      abs(float(p_epics) - 10598)

            for keys in dfield[pcent]:
                if "*" in depics[run][epics_keys[keys]][0]:
                    c_keys = c_keys + "\t" + keys
                    bad_run_mark = True
                else:                    
                    var1 = dfield[pcent][keys] 
                    var2 = depics[run][epics_keys[keys]][0]
                    diff = abs( float(var1) - float(var2) )
                    if keys == 'NMR':
                        ## DIFF FOR NMR VALUES (in fraction), HMS ONLY
                        if diff > float(var1)*0.0001:
                            c_diff = c_diff + " NMR(%s, %s)" % (var1, var2) 
                            bad_run_mark = True
                    else:
                        ## DIFF FOR CURRENT VALUES (UNIT IN AMP)
                        if diff > 8.:
                            c_diff = c_diff + " " + keys + "(%.4f, %.4f)" % (float(var1), float(var2))
                            bad_run_mark = True
        else:
            c_glob = c_glob + "  key does not exist"
            bad_run_mark =  True

        if bad_run_mark == True:
            if len(c_keys) > 0:
                c_keys = " Not connected: " + c_keys
            if len(c_diff) > 0:
                c_diff = "pcent(%s)" % pcent + " DIFF: " + c_diff

            marker = check_physics_run(run)
## FIXME: FORCE MARKER TO 0 FOR NOW
#            marker = 0
            if marker > 0:
                print ("check this physics run", run)
            if print_all: 
                print >> fout, c_glob, c_keys, c_diff
            else:
                if marker > 0:
                    print >> fout, c_glob, c_keys, c_diff

def check_physics_run(run):
    ## FIXME: SET RUN LIST NAME AS YOU WANT
    with open('goodruns.txt', 'rb') as f:
        for line in f:
            if run in line:
                return 1
    return 0

def read_field_file(field_file):
    print "Hello, read field file"

    ddict = {}
    
    with open(field_file,'rb') as f:
        lines = filter(None, (line.strip() for line in f))
        for line in lines:
            if '#' in line:
                continue
            if mode == 'shms':
                p = line.split(None)[0]
                HB = line.split(None)[1]
                Q1 = line.split(None)[2]
                Q2 = line.split(None)[3]
                Q3 = line.split(None)[4]
                Dipole = line.split(None)[5]

                ddict[p] = {}
                ddict[p]['HB'] = HB
                ddict[p]['Q1'] = Q1
                ddict[p]['Q2'] = Q2
                ddict[p]['Q3'] = Q3
                ddict[p]['Dipole'] = Dipole
            else:                
#COMMENTED OUT FOR NOW TO ONLY CHECK DIPOLE FOR HMS
                p = line.split(None)[0]
                Q1 = line.split(None)[1]
                Q2 = line.split(None)[2]
                Q3 = line.split(None)[3]
                Dipole = line.split(None)[4]
                NMR = line.split(None)[5]
#COMMENTED OUT FOR NOW TO ONLY CHECK DIPOLE FOR HMS

                ddict[p] = {}
                ddict[p]['Q1'] = Q1
                ddict[p]['Q2'] = Q2
                ddict[p]['Q3'] = Q3
                ddict[p]['Dipole'] = Dipole
                ddict[p]['NMR'] = NMR
    return ddict

def read_epics_file(epics_file):

    ddict = {}

    print "Hello, load EPICS data...it may take some time"
    infile = open(epics_file,'rb')
    ddict = pickle.load(infile)

    infile.close()

    print "EPIC data loaded!"
    return ddict

def parse_kin_file(infile):
    
    if mode == "shms":
        p_string = "ppcentral"
    elif mode == "hms":
        p_string = "hpcentral"
    else:
        print "wrong mode input!!!!!!"
        sys.exit()

    kin_list = []
    with open(kin_file, 'rb') as f:
        kin_data = []
        lines = filter(None, (line.rstrip() for line in f))
        for line in lines:
            if '#' in line:
                continue

            if line[0].isdigit():
                if len(kin_data) > 0:
                    print ("Forgot to clear the list?", kin_data, line)
                else:
                    brun = ""
                    erun = ""
                    if "-" in line:
                        brun = line.split('-')[0]
                        erun = line.split('-')[1]
                    else:
                        brun = line
                        erun = line
                    kin_data.append(brun.strip())
                    kin_data.append(erun.strip())
            else:
                if len(kin_data) < 1:
                    continue
                else:
                    if "gtargmass" in line:
                        tar_mass = line.split('=')[1]
                        kin_data.append(tar_mass.strip())
                    elif p_string in line:
                        pcentral = line.split('=')[1]
                        kin_data.append(pcentral.strip())
                    else:
                        continue

            if len(kin_data) == 4:
                kin_list.append(kin_data)
                kin_data = []

    return kin_list

if __name__ == '__main__':
    main()
