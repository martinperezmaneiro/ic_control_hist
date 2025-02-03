import os
import sys
import tables as tb

import invisible_cities.io.dst_io as dio

#path of the current file, added to pythonpath to use the functions from utils_hist
dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append('/'.join(dir_path.split('/')[0:-1]))

#imports of other files here
from utils_hist import *


#DST
def get_kdst_signal(dst, signal, binlist, xrange = [None] * 4):
    '''
    Performs the S1 and S2 signal histograms
    '''
    dst_Sw = create_hist_df(dst, signal + 'w', binlist[0], xrange = xrange[0])
    dst_Sh = create_hist_df(dst, signal + 'h', binlist[1], xrange = xrange[1])
    dst_Se = create_hist_df(dst, signal + 'e', binlist[2], xrange = xrange[2])

    nbins = len(dst['n' + signal].unique())
    dst_nS = create_hist_df(dst, 'n' + signal, nbins, xrange = (1, nbins + 1))

    if signal == 'S2':
        dst_S2q = create_hist_df(dst[dst.S2q > -1], 'S2q', binlist[3], xrange = xrange[3])
        return dst_Sw, dst_Sh, dst_Se, dst_nS, dst_S2q
    return dst_Sw, dst_Sh, dst_Se, dst_nS

def get_kdst_peaks(dst, binlist, xrange = [None] * 11):
    '''
    Performs the peaks information histograms
    '''
    peak_spatial = []
    for i, c in enumerate(['X', 'Y', 'Z']):
        peak_c = create_hist_df(dst, c, binlist[0][i], xrange = xrange[2 * i])
        peak_crms = create_hist_df(dst, c + 'rms', binlist[1][i], xrange = xrange[2 * i + 1])
        peak_spatial.append([peak_c, peak_crms])

    peak_DT = create_hist_df(dst, 'DT', binlist[2], xrange = xrange[6])
    peak_R = create_hist_df(dst, 'R', binlist[3], xrange = xrange[7])
    peak_qmax = create_hist_df(dst, 'qmax', binlist[4], xrange = xrange[8])
    peak_Phi = create_hist_df(dst, 'Phi', binlist[5], xrange = xrange[9])
    peak_Nsipm = create_hist_df(dst, 'Nsipm', binlist[6], xrange = xrange[10])

    return peak_spatial, peak_DT, peak_R, peak_qmax, peak_Phi, peak_Nsipm


def get_kdst_dst(files, xrange = [None] * 20):
    '''
    Takes dst, applies a cut and computes S1, S2 and the peaks histograms
    '''

    #DST
    dst = get_files_contents(files, 'DST', 'Events')
    clean_dst = dst[dst.S2q > -1]

    dst_eff_cut = pd.DataFrame([len(clean_dst) / len(dst)], columns=['dst_eff_cut'])

    #S1
    S1 = get_kdst_signal(dst, 'S1', [25, 25, 25], xrange = xrange[0:4])

    #S2
    S2 = get_kdst_signal(dst, 'S2', [25, 25, 25, 25], xrange = xrange[4:9])

    #PEAKS
    peaks = get_kdst_peaks(clean_dst, [[25, 25, 25], [25, 25, 25], 25, 25, 25, 25, 25], xrange = xrange[9:20])

    return dst_eff_cut, S1, S2, peaks

#HITS
def get_kdst_ener_hit(reco_hits, etype, binlist, xrange = [None] * 2):
    hits_etype = create_hist_df_simple(reco_hits[etype], binlist[0], xrange = xrange[0])

    a = pd.DataFrame(reco_hits.groupby(['event', 'Xpeak']).apply(lambda x: x[etype].sum()), columns=[etype]).reset_index()
    hits_etype_peak = create_hist_df(a, etype, binlist[1], xrange = xrange[1])
    return hits_etype, hits_etype_peak

def get_kdst_spatial_hit(reco_hits, coor, binlist, xrange = [None] * 3):
    hits_c = create_hist_df_simple(reco_hits[coor], binlist[0], xrange = xrange[0])
    hits_c_weight_Q = create_hist_df_simple(reco_hits[coor], binlist[1], weight=reco_hits.Q, xrange = xrange[1])
    hits_c_weight_E = create_hist_df_simple(reco_hits[coor], binlist[2], weight=reco_hits.E, xrange = xrange[2])
    return hits_c, hits_c_weight_Q, hits_c_weight_E

def get_kdst_n_hits(reco_hits, binlist, xrange = [None] * 2):
    a = pd.DataFrame(reco_hits.groupby('event').apply(lambda x:len(x)), columns=['nhits']).reset_index()
    hits_n = create_hist_df_simple(a.nhits, binlist[0], xrange = xrange[0])

    a = pd.DataFrame(reco_hits.groupby(['event', 'Xpeak']).apply(lambda x:len(x)), columns=['nhits_peak']).reset_index()
    hits_n_peak = create_hist_df_simple(a.nhits_peak, binlist[1], xrange = xrange[1])
    return hits_n, hits_n_peak

def get_kdst_hits(files, xrange = [None] * 15):
    '''

    '''
    #HITS
    reco_hits = get_files_contents(files, 'RECO', 'Events')
    clean_reco_hits = reco_hits[(reco_hits.Q > -1) & (reco_hits.Xpeak > -1000)]

    hits_eff_cut = pd.DataFrame([len(clean_reco_hits) / len(reco_hits)], columns=['hits_eff_cut'])

    #Hits energy
    Q = get_kdst_ener_hit(clean_reco_hits, 'Q', [25, 25], xrange = xrange[0:2])
    E = get_kdst_ener_hit(clean_reco_hits, 'E', [25, 25], xrange = xrange[2:4])

    #Hits spatial
    X = get_kdst_spatial_hit(clean_reco_hits, 'X', [25, 25, 25], xrange = xrange[4:7])
    Y = get_kdst_spatial_hit(clean_reco_hits, 'Y', [25, 25, 25], xrange = xrange[7:10])
    Z = get_kdst_spatial_hit(clean_reco_hits, 'Z', [25, 25, 25], xrange = xrange[10:13])

    n = get_kdst_n_hits(clean_reco_hits, [50, 50], xrange = xrange[13:15])

    return hits_eff_cut, Q, E, X, Y, Z, n

def kdst_file_writer(files_path, out_path, city = 'penthesilea', tag = '', xrange = [None] * 35):
    '''
    Creates the kdst group in the file with all the related histograms

    This includes all the histograms for penthesilea and sophronia
    '''
    kdst_files = get_all_files(files_path, city)

    #DST
    dst_eff_cut, S1, S2, peaks = get_kdst_dst(kdst_files, xrange = xrange[0:20])

    dst_S1w, dst_S1h, dst_S1e, dst_nS1 = S1
    dst_S2w, dst_S2h, dst_S2e, dst_nS2, dst_S2q = S2
    peak_spatial, peak_DT, peak_R, peak_qmax, peak_Phi, peak_Nsipm = peaks
    peak_X, peak_Xrms = peak_spatial[0][0], peak_spatial[0][1]
    peak_Y, peak_Yrms = peak_spatial[1][0], peak_spatial[1][1]
    peak_Z, peak_Zrms = peak_spatial[2][0], peak_spatial[2][1]

    #HITS
    hits_eff_cut, Q, E, X, Y, Z, n = get_kdst_hits(kdst_files, xrange = xrange[20:35])

    hits_Q, hits_Q_peak = Q
    hits_E, hits_E_peak = E
    hits_X, hits_X_weight_Q, hits_X_weight_E = X
    hits_Y, hits_Y_weight_Q, hits_Y_weight_E = Y
    hits_Z, hits_Z_weight_Q, hits_Z_weight_E = Z
    hits_n, hits_n_peak = n


    with tb.open_file(out_path, 'a') as h5out:
        dio.df_writer(h5out, dst_eff_cut,  city + tag, 'dst_eff_cut', descriptive_string = '')
        dio.df_writer(h5out, hits_eff_cut, city + tag, 'hits_eff_cut', descriptive_string = '')

        dio.df_writer(h5out, dst_S1w, city + tag, 'dst_S1w', descriptive_string = '')
        dio.df_writer(h5out, dst_S1h, city + tag, 'dst_S1h', descriptive_string = '')
        dio.df_writer(h5out, dst_S1e, city + tag, 'dst_S1e', descriptive_string = '')
        dio.df_writer(h5out, dst_nS1, city + tag, 'dst_nS1', descriptive_string = '')

        dio.df_writer(h5out, dst_S2w, city + tag, 'dst_S2w', descriptive_string = '')
        dio.df_writer(h5out, dst_S2h, city + tag, 'dst_S2h', descriptive_string = '')
        dio.df_writer(h5out, dst_S2e, city + tag, 'dst_S2e', descriptive_string = '')
        dio.df_writer(h5out, dst_S2q, city + tag, 'dst_S2q', descriptive_string = '')
        dio.df_writer(h5out, dst_nS2, city + tag, 'dst_nS2', descriptive_string = '')

        dio.df_writer(h5out, peak_X,     city + tag, 'peak_X', descriptive_string = '')
        dio.df_writer(h5out, peak_Xrms,  city + tag, 'peak_Xrms', descriptive_string = '')
        dio.df_writer(h5out, peak_Y,     city + tag, 'peak_Y', descriptive_string = '')
        dio.df_writer(h5out, peak_Yrms,  city + tag, 'peak_Yrms', descriptive_string = '')
        dio.df_writer(h5out, peak_Z,     city + tag, 'peak_Z', descriptive_string = '')
        dio.df_writer(h5out, peak_Zrms,  city + tag, 'peak_Zrms', descriptive_string = '')
        dio.df_writer(h5out, peak_DT,    city + tag, 'peak_DT', descriptive_string = '')
        dio.df_writer(h5out, peak_R,     city + tag, 'peak_R', descriptive_string = '')
        dio.df_writer(h5out, peak_qmax,  city + tag, 'peak_qmax', descriptive_string = '')
        dio.df_writer(h5out, peak_Phi,   city + tag, 'peak_Phi', descriptive_string = '')
        dio.df_writer(h5out, peak_Nsipm, city + tag, 'peak_Nsipm', descriptive_string = '')

        dio.df_writer(h5out, hits_Q, city + tag, 'hits_Q', descriptive_string = '')
        dio.df_writer(h5out, hits_E, city + tag, 'hits_E', descriptive_string = '')

        dio.df_writer(h5out, hits_Q_peak, city + tag, 'hits_Q_peak', descriptive_string = '')
        dio.df_writer(h5out, hits_E_peak, city + tag, 'hits_E_peak', descriptive_string = '')

        dio.df_writer(h5out, hits_X,          city + tag, 'hits_X', descriptive_string = '')
        dio.df_writer(h5out, hits_X_weight_Q, city + tag, 'hits_X_weight_Q', descriptive_string = '')
        dio.df_writer(h5out, hits_X_weight_E, city + tag, 'hits_X_weight_E', descriptive_string = '')
        dio.df_writer(h5out, hits_Y,          city + tag, 'hits_Y', descriptive_string = '')
        dio.df_writer(h5out, hits_Y_weight_Q, city + tag, 'hits_Y_weight_Q', descriptive_string = '')
        dio.df_writer(h5out, hits_Y_weight_E, city + tag, 'hits_Y_weight_E', descriptive_string = '')
        dio.df_writer(h5out, hits_Z,          city + tag, 'hits_Z', descriptive_string = '')
        dio.df_writer(h5out, hits_Z_weight_Q, city + tag, 'hits_Z_weight_Q', descriptive_string = '')
        dio.df_writer(h5out, hits_Z_weight_E, city + tag, 'hits_Z_weight_E', descriptive_string = '')

        dio.df_writer(h5out, hits_n, city + tag, 'hits_n', descriptive_string = '')
        dio.df_writer(h5out, hits_n_peak, city + tag, 'hits_n_peak', descriptive_string = '')
