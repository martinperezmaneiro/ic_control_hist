import os
import sys
import tables as tb

import invisible_cities.io.dst_io as dio

#path of the current file, added to pythonpath to use the functions from utils_hist
dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append('/'.join(dir_path.split('/')[0:-1]))

#imports of other files here
from utils_hist import *

#HITS
#ALMOST EQUAL TO PENTHESILEA HITS FUNCTIONS (the only difference is the last
# global function, get_chits_hits)
def get_chits_ener(hits, etype, binlist, xrange = [None] * 2):
    hits_etype = create_hist_df_simple(hits[etype], binlist[0], xrange = xrange[0])

    a = pd.DataFrame(hits.groupby(['event', 'Xpeak']).apply(lambda x: x[etype].sum()), columns=[etype]).reset_index()
    hits_etype_peak = create_hist_df(a, etype, binlist[1], xrange = xrange[1])
    return hits_etype, hits_etype_peak

def get_chits_spatial(hits, coor, binlist, xrange = [None] * 3):
    hits_c = create_hist_df_simple(hits[coor], binlist[0], xrange = xrange[0])
    hits_c_weight_Q = create_hist_df_simple(hits[coor], binlist[1], weight=hits.Q, xrange = xrange[1])
    hits_c_weight_E = create_hist_df_simple(hits[coor], binlist[2], weight=hits.E, xrange = xrange[2])
    return hits_c, hits_c_weight_Q, hits_c_weight_E

def get_chits_n(hits, binlist, xrange = [None] * 2):
    a = pd.DataFrame(hits.groupby('event').apply(lambda x:len(x)), columns=['nhits']).reset_index()
    hits_n = create_hist_df_simple(a.nhits, binlist[0], xrange = xrange[0])

    a = pd.DataFrame(hits.groupby(['event', 'Xpeak']).apply(lambda x:len(x)), columns=['nhits_peak']).reset_index()
    hits_n_peak = create_hist_df_simple(a.nhits_peak, binlist[1], xrange = xrange[1])
    return hits_n, hits_n_peak

def get_chits(files, threshold_name, xrange = [None] * 18):
    '''

    '''

    th_hits = get_files_contents(files, 'CHITS', threshold_name)

    clean_th_hits = th_hits[th_hits.Ypeak> -1000]
    th_eff_cut = pd.DataFrame([len(clean_th_hits) /len(th_hits)], columns=[threshold_name + '_eff_cut'])

    #Total energy
    th_totE = create_hist_df_simple(clean_th_hits.groupby('event').Ec.sum(), 100, xrange=xrange[0])

    #Hits energy
    Q = get_chits_ener(clean_th_hits, 'Q', [25, 25], xrange = xrange[1:3])
    E = get_chits_ener(clean_th_hits, 'E', [25, 25], xrange = xrange[3:5])
    Ec = get_chits_ener(clean_th_hits[~np.isnan(clean_th_hits.Ec)], 'Ec', [25, 25], xrange = xrange[5:7])

    #Hits spatial
    X = get_chits_spatial(clean_th_hits, 'X', [25, 25, 25], xrange = xrange[7:10])
    Y = get_chits_spatial(clean_th_hits, 'Y', [25, 25, 25], xrange = xrange[10:13])
    Z = get_chits_spatial(clean_th_hits, 'Z', [25, 25, 25], xrange = xrange[13:16])

    n = get_chits_n(clean_th_hits, [50, 50], xrange = xrange[16:18])

    return th_eff_cut, th_totE, Q, E, Ec, X, Y, Z, n

def chits_file_writer(files_path, out_path, th, city = 'esmeralda', tag = '', xrange = [None] * 18):
    '''
    Creates the corrected hits group in the file with all the related histograms
    for a threshold
    '''
    files = get_all_files(files_path, city)
    th_eff_cut, th_totE, Q_, E_, Ec_, X_, Y_, Z_, n_ = get_chits(files, th, xrange = xrange)

    th_Q, th_Q_peak = Q_
    th_E, th_E_peak = E_
    th_Ec, th_Ec_peak = Ec_
    th_X, th_X_weight_Q, th_X_weight_E = X_
    th_Y, th_Y_weight_Q, th_Y_weight_E = Y_
    th_Z, th_Z_weight_Q, th_Z_weight_E = Z_
    th_n, th_n_peak = n_

    with tb.open_file(out_path, 'a') as h5out:
        dio.df_writer(h5out, th_eff_cut,  city + tag, th + '_eff_cut', descriptive_string = '')

        dio.df_writer(h5out, th_totE,    city + tag, th + '_totE', descriptive_string = '')
        dio.df_writer(h5out, th_Q,       city + tag, th + '_Q', descriptive_string = '')
        dio.df_writer(h5out, th_Q_peak,  city + tag, th + '_Q_peak', descriptive_string = '')
        dio.df_writer(h5out, th_E,       city + tag, th + '_E', descriptive_string = '')
        dio.df_writer(h5out, th_E_peak,  city + tag, th + '_E_peak', descriptive_string = '')
        dio.df_writer(h5out, th_Ec,       city + tag, th + '_Ec', descriptive_string = '')
        dio.df_writer(h5out, th_Ec_peak,  city + tag, th + '_Ec_peak', descriptive_string = '')

        dio.df_writer(h5out, th_X,           city + tag, th + '_X', descriptive_string = '')
        dio.df_writer(h5out, th_X_weight_Q,  city + tag, th + '_X_weight_Q', descriptive_string = '')
        dio.df_writer(h5out, th_X_weight_E,  city + tag, th + '_X_weight_E', descriptive_string = '')
        dio.df_writer(h5out, th_Y,           city + tag, th + '_Y', descriptive_string = '')
        dio.df_writer(h5out, th_Y_weight_Q,  city + tag, th + '_Y_weight_Q', descriptive_string = '')
        dio.df_writer(h5out, th_Y_weight_E,  city + tag, th + '_Y_weight_E', descriptive_string = '')
        dio.df_writer(h5out, th_Z,           city + tag, th + '_Z', descriptive_string = '')
        dio.df_writer(h5out, th_Z_weight_Q,  city + tag, th + '_Z_weight_Q', descriptive_string = '')
        dio.df_writer(h5out, th_Z_weight_E,  city + tag, th + '_Z_weight_E', descriptive_string = '')

        dio.df_writer(h5out, th_n,       city + tag, th + '_n', descriptive_string = '')
        dio.df_writer(h5out, th_n_peak,  city + tag, th + '_n_peak', descriptive_string = '')
