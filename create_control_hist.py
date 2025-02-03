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


#NEEDED VARIABLES
data_path = '/Users/mperez/NEXT/ic_dev/files/refactor_prod/' #path to cities folders containing data
#cities forlders should be in lower case: hypathia, penthesilea/sophronia, esmeralda, beersheba, isaura
tag = '228Th' #kind of data in the files
is_refactor = True #asks if the production is the new or the old
cities = ['esmeralda']
out_file = 'hist_esm_n100.h5'


#START
#cities = [dir.split('/')[-1] for dir in glob.glob(data_path + '*')]
files_path = data_path + '{city}/{city}_*_{tag}.h5'
files_path = files_path.format(city = '{city}', tag = tag)
out_path = data_path + out_file

hist_dict = {'hypathia':    pmaps_file_writer,
             'penthesilea': kdst_file_writer,
             'sophronia':   kdst_file_writer,
             'esmeralda':   (chits_file_writer, tracks_file_writer),
             'beersheba':   deco_file_writer,
             'isaura':      tracks_file_writer}


#START OF THE SCRIPT
if __name__ == "__main__":
    #HYPATHIA
    if np.isin(cities, 'hypathia').any():
        hist_dict['hypathia'](files_path, out_path, city = 'hypathia')

    #PENTHESILEA
    if np.isin(cities, 'penthesilea').any():
        hist_dict['penthesilea'](files_path, out_path, city = 'penthesilea')

    #SOPHRONIA
    if np.isin(cities, 'sophronia').any():
        hist_dict['sophronia'](files_path, out_path, city = 'sophronia')

    #ESMERALDA
    if np.isin(cities, 'esmeralda').any():
        hist_dict['esmeralda'][0](files_path, out_path, 'highTh', city = 'esmeralda')
        hist_dict['esmeralda'][1](files_path, out_path, city = 'esmeralda')
        if not is_refactor:
            hist_dict['esmeralda'][0](files_path, out_path, 'lowTh', city = 'esmeralda')

    #BEERSHEBA
    if np.isin(cities, 'beersheba').any():
        hist_dict['beersheba'](files_path, out_path, city = 'beersheba')

    #ISAURA
    if np.isin(cities, 'isaura').any():
        hist_dict['isaura'](files_path, out_path, city = 'isaura')
