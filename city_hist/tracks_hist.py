import os
import sys
import tables as tb

import invisible_cities.io.dst_io as dio

#path of the current file, added to pythonpath to use the functions from utils_hist
dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append('/'.join(dir_path.split('/')[0:-1]))

#imports of other files here
from utils_hist import *

#TRACKS

def get_feat_tracks(tracks, xrange = [None] * 8):
    E = create_tracks_hist(tracks, 'energy', xrange = xrange[0:2])
    L = create_tracks_hist(tracks, 'length', xrange = xrange[2:4])
    nhits = create_tracks_hist(tracks, 'numb_of_hits', xrange = xrange[4:6])
    nvox = create_tracks_hist(tracks, 'numb_of_voxels', xrange = xrange[6:8])
    return E, L, nhits, nvox

def get_spat_tracks(tracks, xrange = [None] * 10):
    X = create_tracks_hist(tracks, 'x_ave', xrange = xrange[0:2])
    Y = create_tracks_hist(tracks, 'y_ave', xrange = xrange[2:4])
    Z = create_tracks_hist(tracks, 'z_ave', xrange = xrange[4:6])
    R = create_tracks_hist(tracks, 'r_ave', xrange = xrange[6:8])
    Rmax = create_tracks_hist(tracks, 'r_max', xrange = xrange[8:10])
    return X, Y, Z, R, Rmax

def get_blob_tracks(tracks, xrange = [None] * 6):
    eblob1 = create_tracks_hist(tracks, 'eblob1', xrange = xrange[0:2])
    eblob2 = create_tracks_hist(tracks, 'eblob2', xrange = xrange[2:4])
    ovlp = create_tracks_hist(tracks, 'ovlp_blob_energy', xrange = xrange[4:6])
    return eblob1, eblob2, ovlp

def get_tracks(files, xrange = [None] * 24):
    tracks = get_files_contents(files, 'Tracking', 'Tracks')

    ntracks = create_hist_df(tracks, 'numb_of_tracks', nbins=tracks.numb_of_tracks.max(), xrange = (tracks.numb_of_tracks.min(), tracks.numb_of_tracks.max() + 1))
    E, L, nhits, nvox = get_feat_tracks(tracks, xrange = xrange[0:8])
    X, Y, Z, R, Rmax = get_spat_tracks(tracks, xrange = xrange[8:18])
    eblob1, eblob2, ovlp = get_blob_tracks(tracks, xrange = xrange[18:24])
    return ntracks, E, L, nhits, nvox, X, Y, Z, R, Rmax, eblob1, eblob2, ovlp


def tracks_file_writer(files_path, out_path, city = 'esmeralda', tag = '', xrange = [None] * 24):
    '''
    Creates the tracks group in the file with all the related histograms
    '''
    files = get_all_files(files_path, city)
    ntracks, E, L, nhits, nvox, X, Y, Z, R, Rmax, eblob1, eblob2, ovlp = get_tracks(files, xrange = xrange)

    with tb.open_file(out_path, 'a') as h5out:
        dio.df_writer(h5out, ntracks,  city + tag, 'ntracks', descriptive_string = '')

        dio.df_writer(h5out, E[0],      city + tag, 'tracks_E', descriptive_string = '')
        dio.df_writer(h5out, E[1],      city + tag, 'maintracks_E', descriptive_string = '')
        dio.df_writer(h5out, L[0],      city + tag, 'tracks_L', descriptive_string = '')
        dio.df_writer(h5out, L[1],      city + tag, 'maintracks_L', descriptive_string = '')
        dio.df_writer(h5out, nhits[0],  city + tag, 'tracks_nhits', descriptive_string = '')
        dio.df_writer(h5out, nhits[1],  city + tag, 'maintracks_nhits', descriptive_string = '')
        dio.df_writer(h5out, nvox[0],   city + tag, 'tracks_nvox', descriptive_string = '')
        dio.df_writer(h5out, nvox[1],   city + tag, 'maintracks_nvox', descriptive_string = '')

        dio.df_writer(h5out, X[0],     city + tag, 'tracks_X', descriptive_string = '')
        dio.df_writer(h5out, X[1],     city + tag, 'maintracks_X', descriptive_string = '')
        dio.df_writer(h5out, Y[0],     city + tag, 'tracks_Y', descriptive_string = '')
        dio.df_writer(h5out, Y[1],     city + tag, 'maintracks_Y', descriptive_string = '')
        dio.df_writer(h5out, Z[0],     city + tag, 'tracks_Z', descriptive_string = '')
        dio.df_writer(h5out, Z[1],     city + tag, 'maintracks_Z', descriptive_string = '')
        dio.df_writer(h5out, R[0],     city + tag, 'tracks_R', descriptive_string = '')
        dio.df_writer(h5out, R[1],     city + tag, 'maintracks_R', descriptive_string = '')
        dio.df_writer(h5out, Rmax[0],  city + tag, 'tracks_Rmax', descriptive_string = '')
        dio.df_writer(h5out, Rmax[1],  city + tag, 'maintracks_Rmax', descriptive_string = '')

        dio.df_writer(h5out, eblob1[0],  city + tag, 'tracks_eblob1', descriptive_string = '')
        dio.df_writer(h5out, eblob1[1],  city + tag, 'maintracks_eblob1', descriptive_string = '')
        dio.df_writer(h5out, eblob2[0],  city + tag, 'tracks_eblob2', descriptive_string = '')
        dio.df_writer(h5out, eblob2[1],  city + tag, 'maintracks_eblob2', descriptive_string = '')
        dio.df_writer(h5out, ovlp[0],    city + tag, 'tracks_ovlp', descriptive_string = '')
        dio.df_writer(h5out, ovlp[1],    city + tag, 'maintracks_ovlp', descriptive_string = '')
