import os
import glob
import tables as tb
import numpy  as np
import pandas as pd

import invisible_cities.io.dst_io as dio

#GENERAL FUNCTIONS (get files, do histograms...)
get_file_number = lambda x: int(x.split("_")[-2])

def get_hist_from_data(path, group, node):
    return dio.load_dst(path, group, node)

def get_all_files(temp_dir, city):
    '''
    Takes a path and gets all the files
    '''
    all_files = glob.glob(os.path.expandvars(temp_dir.format(city = city)))
    all_files = sorted(all_files, key = get_file_number)
    return all_files

def get_files_contents(all_files, group, table):
    '''
    Takes a list of files and creates a DataFrame with all of them
    '''
    df = pd.DataFrame()
    for f in all_files:
        read_df = dio.load_dst(f, group, table)
        df = df.append(read_df)
    return df

def create_hist_df_simple(var, nbins, weight = None, xrange = None):
    '''
    Creates a basic histogram taking a variable and returning it in a DataFrame to store.
    '''
    values, bins = np.histogram(var, bins = nbins, weights = weight, range = xrange)
    df = pd.DataFrame([values, bins]).transpose()
    df.columns = ['values', 'bins']
    return df

def create_hist_df(df, var, nbins, weight = None, xrange = None):
    '''
    Creates an histogram from a DataFrame selecting a variable per event; this is
    used for variables that are unique per event. Also returns the histogram in
    a DataFrame to store.
    '''
    if weight:
        hist_df = df[['event', var, weight]].drop_duplicates()[var]
        weight = df[['event', var, weight]].drop_duplicates()[weight]
    else:
        hist_df = df[['event', var]].drop_duplicates()[var]

    values, bins = np.histogram(hist_df, bins = nbins, weights = weight, range = xrange)
    df = pd.DataFrame([values, bins]).transpose()
    df.columns = ['values', 'bins']
    return df

def create_tracks_hist(tracks_df, var, nbins = 30, xrange = [None] * 2):
    main_tracks = tracks_df[tracks_df.trackID == 0]
    #seco_tracks = tracks_df[tracks_df.trackID != 0]

    all_hist  = create_hist_df_simple(tracks_df[var], nbins, xrange = xrange[0])
    main_hist = create_hist_df_simple(main_tracks[var], nbins, xrange = xrange[1])

    return all_hist, main_hist

def get_group_nodes_names(path):
    h5 = tb.open_file(path, 'r')
    group_names = []
    node_names  = []
    for group in h5.list_nodes('/'):
        str_gr = group.__str__().split('/')[-1].split(' ')[0]
        group_names.append(str_gr)
        node_names_group = []
        for node in h5.list_nodes('/' + str_gr):
            node_names_group.append(node.name)

        node_names.append(node_names_group)
    h5.close()
    return group_names, node_names


def common_xlims(old_path, ref_path, order_list):
    group_old, _ = get_group_nodes_names(old_path)
    group_ref, _ = get_group_nodes_names(ref_path)
    xlims = []
    for o in order_list:
        if (o.split('_')[1] == 'eff'):
            continue
    
        old_bins = dio.load_dst(old_path, group_old[0], o).bins
        ref_bins = dio.load_dst(ref_path, group_ref[0], o).bins
        min_old, max_old = min(old_bins), max(old_bins)
        min_ref, max_ref = min(ref_bins), max(ref_bins)
        absmin, absmax   = min(min_old, min_ref), max(max_old, max_ref)
        xlims.append((absmin, absmax))
    return xlims

#as the h5 files sort the nodes alphabetically, in order for them to
#match the order in my code, I'll provide a list with the exact order they appear...
#very messy, should change this
hyp_order_list = ['S1_e', 'S1_total_e', 'S1_t', 'S1_total_t',
'S1_t_weight_e', 'S2_e', 'S2_total_e', 'S2_t', 'S2_total_t', 
'S2_t_weight_e', 'S1_e_PMT', 'S1_total_e_PMT', 'S1_PMT_weight_e', 
'S2_e_PMT', 'S2_total_e_PMT', 'S2_PMT_weight_e', 'S2_e_Si', 
'S2_total_e_Si', 'S2_Si_weight_e']

pen_order_list = ['dst_S1w', 'dst_S1h', 'dst_S1e', 'dst_nS1', 'dst_S2w', 
'dst_S2h', 'dst_S2e', 'dst_S2q', 'dst_nS2', 'peak_X', 
'peak_Xrms', 'peak_Y', 'peak_Yrms', 'peak_Z', 'peak_Zrms', 
'peak_DT', 'peak_R', 'peak_qmax', 'peak_Phi', 'peak_Nsipm', 
'hits_Q', 'hits_Q_peak', 'hits_E', 'hits_E_peak', 'hits_X', 
'hits_X_weight_Q', 'hits_X_weight_E', 'hits_Y', 'hits_Y_weight_Q', 
'hits_Y_weight_E', 'hits_Z', 'hits_Z_weight_Q', 'hits_Z_weight_E', 
'hits_n', 'hits_n_peak']

esm_order_list = ['highTh_eff_cut', 'highTh_totE', 'highTh_Q', 'highTh_Q_peak', 
'highTh_E', 'highTh_E_peak', 'highTh_Ec', 'highTh_Ec_peak', 'highTh_X', 'highTh_X_weight_Q', 'highTh_X_weight_E',
'highTh_Y', 'highTh_Y_weight_Q', 'highTh_Y_weight_E', 'highTh_Z', 'highTh_Z_weight_Q', 
'highTh_Z_weight_E', 'highTh_n', 'highTh_n_peak', 
'tracks_E', 'maintracks_E', 'tracks_L', 'maintracks_L', 'tracks_nhits', 'maintracks_nhits', 
'tracks_nvox', 'maintracks_nvox', 'tracks_X', 'maintracks_X', 'tracks_Y', 'maintracks_Y', 
'tracks_Z', 'maintracks_Z', 'tracks_R', 'maintracks_R', 'tracks_Rmax', 'maintracks_Rmax', 
'tracks_eblob1', 'maintracks_eblob1', 'tracks_eblob2', 'maintracks_eblob2', 'tracks_ovlp', 
'maintracks_ovlp']

bee_order_list = ['deco_totE', 'deco_E', 'deco_X', 'deco_X_weight_E', 'deco_Y', 
'deco_Y_weight_E', 'deco_Z', 'deco_Z_weight_E', 'deco_nhits']


