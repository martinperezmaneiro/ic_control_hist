import os
import sys
import glob
import numpy  as np
import tables as tb
import pandas as pd

import invisible_cities.io.dst_io as dio

#path of the current file, added to pythonpath to use the functions
dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dir_path)

#imports of other files here
from utils_hist import *

from city_hist.pmaps_hist import pmaps_file_writer
from city_hist.kdst_hist  import kdst_file_writer
from city_hist.chits_hist   import chits_file_writer
from city_hist.tracks_hist import tracks_file_writer
from city_hist.deco_hist   import deco_file_writer

'''
Takes 2 groups of files to compare (A and B), creates the histograms, reads them selecting commmon limits for the variables, 
and redoes them finally to completely compare the values.
The structure of folders should be main_path/group_path/city/files.h5, where group_path should be the name of A and B productions.
'''

##########################################################################################################

#NEEDED VARIABLES
data_path = '/Users/mperez/NEXT/ic_dev/prueba/' #path to A and B productions

A_path = data_path + 'old_prod/'
B_path = data_path + 'refactor_prod/'
A_tag, B_tag = 'old', 'ref'

#cities forlders should be in lower case: hypathia, penthesilea/sophronia, esmeralda, beersheba, isaura
tag = '228Th' #kind of data in the files
file_structure = '{city}/{city}_*_{tag}.h5'
#for penthesilea we will replace when needed the word with sophronia
cities = ['hypathia', 'sophronia', 'esmeralda', 'beersheba', 'isaura']
# put true if the production A is penthesilea instead of sophronia
is_A_penthesilea = True

##########################################################################################################

#FILE NAME FOR THE FIRST HISTOGRAMS
hist_file = 'hist_{}.h5' #str filled with first 3 letters of the correspondent city
A_hist_temp = A_path + hist_file
B_hist_temp = B_path + hist_file

out_file = '{}_comp.h5'


#STARTUP
#PICKING ALL THE FILES (OLD AND REFACTOR) TO RE-DO THE HISTOGRAMS
A_files = A_path + file_structure
A_files = A_files.format(city = '{city}', tag = tag)
B_files = B_path + file_structure
B_files = B_files.format(city = '{city}', tag = tag)

out_path_temp = data_path + out_file

hist_dict = {'hypathia':    pmaps_file_writer,
             'penthesilea': kdst_file_writer,
             'sophronia':   kdst_file_writer,
             'esmeralda':   (chits_file_writer, tracks_file_writer),
             'beersheba':   deco_file_writer,
             'isaura':      tracks_file_writer}

order_dict = {'hypathia':  hyp_order_list,
              'sophronia': pen_order_list, #same for penthesilea
              'esmeralda':esm_order_list, 
              'beersheba':bee_order_list,
              'isaura':esm_order_list[19:]}

#START OF THE SCRIPT
if __name__ == "__main__":
    
    #HYPATHIA
    if np.isin(cities, 'hypathia').any():
        # Change name to files 
        A_hist, B_hist = A_hist_temp.format('hyp'), B_hist_temp.format('hyp')
        out_path = out_path_temp.format('hyp')
        # First we create the histograms for each type of data we want to compare (A vs B)
        hist_dict['hypathia'](A_files, A_hist, city = 'hypathia')
        hist_dict['hypathia'](B_files, B_hist, city = 'hypathia')
        # Once created, we read both histograms and select the common xlims
        xlims = common_xlims(A_hist, B_hist, order_dict['hypathia'])
        # Recalculate with the new lims
        hist_dict['hypathia'](A_files, out_path, city = 'hypathia', tag = A_tag, xrange = xlims)
        hist_dict['hypathia'](B_files, out_path, city = 'hypathia', tag = B_tag, xrange = xlims)

    #SOPHRONIA (If we wanted to compare penthesilea vs sophronia, we can change names )
    if np.isin(cities, 'sophronia').any():
        # if A files are penthesilea, it changes the name of the city
        if is_A_penthesilea: change_name = 'penthesilea'
        else: change_name = 'sophronia'
        # Change name to files
        A_hist, B_hist = A_hist_temp.format(change_name[:3]), B_hist_temp.format('sop')
        out_path = out_path_temp.format('sop')
        # We create histograms for each group of data
        hist_dict[change_name](A_files, A_hist, city = change_name)
        hist_dict['sophronia'](B_files, B_hist, city = 'sophronia')
        # Read histograms to select common xlims
        xlims = common_xlims(A_hist, B_hist, order_dict['sophronia'])
        # Recalculate with the new lims
        hist_dict[change_name](A_files, out_path, city = change_name, tag = A_tag, xrange = xlims)
        hist_dict['sophronia'](B_files, out_path, city = 'sophronia', tag = B_tag, xrange = xlims)

    #ESMERALDA
    if np.isin(cities, 'esmeralda').any():
        A_hist, B_hist = A_hist_temp.format('esm'), B_hist_temp.format('esm')
        out_path = out_path_temp.format('esm')
        # For esmeralda we have the hits and the tracking comparison
        hist_dict['esmeralda'][0](A_files, A_hist, 'highTh', city = 'esmeralda')
        hist_dict['esmeralda'][1](A_files, A_hist,           city = 'esmeralda')
        hist_dict['esmeralda'][0](B_files, B_hist, 'highTh', city = 'esmeralda')
        hist_dict['esmeralda'][1](B_files, B_hist,           city = 'esmeralda')

        xlims = common_xlims(A_hist, B_hist, order_dict['esmeralda'])
        
        #Careful here using the xlim because there are some lims for the chits part and some for the tracks one!
        hist_dict['esmeralda'][0](A_files, out_path, 'highTh', city = 'esmeralda', tag = A_tag, xrange = xlims[0:18])
        hist_dict['esmeralda'][1](A_files, out_path,           city = 'esmeralda', tag = A_tag, xrange = xlims[18:])
        # this was for the old version of esmeralda, now there is no low threshold
        # hist_dict['esmeralda'][0](A_files, out_path, 'lowTh', city = 'esmeralda', tag = A_tag) 

        hist_dict['esmeralda'][0](B_files, out_path, 'highTh', city = 'esmeralda', tag = B_tag, xrange = xlims[0:18])
        hist_dict['esmeralda'][1](B_files, out_path,           city = 'esmeralda', tag = B_tag, xrange = xlims[18:])

    #BEERSHEBA
    if np.isin(cities, 'beersheba').any():
        A_hist, B_hist = A_hist_temp.format('bee'), B_hist_temp.format('bee')
        out_path = out_path_temp.format('bee')

        hist_dict['beersheba'](A_files, A_hist, city = 'beersheba')
        hist_dict['beersheba'](B_files, B_hist, city = 'beersheba')

        xlims = common_xlims(A_hist, B_hist, order_dict['beersheba'])

        hist_dict['beersheba'](A_files, out_path, city = 'beersheba', tag = A_tag, xrange = xlims)
        hist_dict['beersheba'](B_files, out_path, city = 'beersheba', tag = B_tag, xrange = xlims)

    #ISAURA
    if np.isin(cities, 'isaura').any():
        A_hist, B_hist = A_hist_temp.format('isa'), B_hist_temp.format('isa')
        out_path = out_path_temp.format('isa')

        hist_dict['isaura'](A_files, A_hist, city = 'isaura')
        hist_dict['isaura'](B_files, B_hist, city = 'isaura')

        xlims = common_xlims(A_hist, B_hist, order_dict['isaura'])

        hist_dict['isaura'](A_files, out_path, city = 'isaura', tag = A_tag, xrange = xlims)
        hist_dict['isaura'](B_files, out_path, city = 'isaura', tag = B_tag, xrange = xlims)
        
