import os
import sys
import tables as tb

import invisible_cities.io.dst_io as dio

#path of the current file, added to pythonpath to use the functions from utils_hist
dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append('/'.join(dir_path.split('/')[0:-1]))

#imports of other files here
from utils_hist import *

def get_deco_spatial_hit(deco_hits, coor, binlist, xrange = [None] * 2):
    hits_c = create_hist_df_simple(deco_hits[coor], binlist[0], xrange = xrange[0])
    hits_c_weight_E = create_hist_df_simple(deco_hits[coor], binlist[1], weight=deco_hits.E, xrange = xrange[1])
    return hits_c, hits_c_weight_E

def get_deco_hits(files, xrange = [None] * 9):
    '''

    '''
    deco_beersh = get_files_contents(files, 'DECO', 'Events')

    #Total energy
    deco_totE = create_hist_df_simple(deco_beersh.groupby('event').E.sum(), 100, xrange = xrange[0])

    #Hits energy
    deco_E = create_hist_df_simple(deco_beersh.E, 25, xrange = xrange[1])

    #Hits spatial
    X = get_deco_spatial_hit(deco_beersh, 'X', [25, 25], xrange = xrange[2:4])
    Y = get_deco_spatial_hit(deco_beersh, 'Y', [25, 25], xrange = xrange[4:6])
    Z = get_deco_spatial_hit(deco_beersh, 'Z', [25, 25], xrange = xrange[6:8])

    deco_nhits = create_hist_df_simple(deco_beersh.groupby('event').apply(lambda x:len(x)), 50, xrange = xrange[8])

    return deco_totE, deco_E, X, Y, Z, deco_nhits

def deco_file_writer(files_path, out_path, city = 'beersheba', tag = '', xrange = [None] * 9):
    '''
    Creates the deconvolved hits group in the file with all the related histograms
    '''
    files = get_all_files(files_path, city)

    deco_totE, deco_E, X, Y, Z, deco_nhits = get_deco_hits(files, xrange = xrange)

    deco_X, deco_X_weight_E = X
    deco_Y, deco_Y_weight_E = Y
    deco_Z, deco_Z_weight_E = Z

    with tb.open_file(out_path, 'a') as h5out:
        dio.df_writer(h5out, deco_totE,    city + tag, 'deco_totE', descriptive_string = '')
        dio.df_writer(h5out, deco_E,       city + tag, 'deco_E', descriptive_string = '')

        dio.df_writer(h5out, deco_X,           city + tag, 'deco_X', descriptive_string = '')
        dio.df_writer(h5out, deco_X_weight_E,  city + tag, 'deco_X_weight_E', descriptive_string = '')
        dio.df_writer(h5out, deco_Y,           city + tag, 'deco_Y', descriptive_string = '')
        dio.df_writer(h5out, deco_Y_weight_E,  city + tag, 'deco_Y_weight_E', descriptive_string = '')
        dio.df_writer(h5out, deco_Z,           city + tag, 'deco_Z', descriptive_string = '')
        dio.df_writer(h5out, deco_Z_weight_E,  city + tag, 'deco_Z_weight_E', descriptive_string = '')

        dio.df_writer(h5out, deco_nhits,       city + tag, 'deco_nhits', descriptive_string = '')
