import os
import sys
import tables as tb

import invisible_cities.io.dst_io as dio

#path of the current file, added to pythonpath to use the functions from utils_hist
dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append('/'.join(dir_path.split('/')[0:-1]))

#imports of other files here
from utils_hist import *

def get_signal_pmaps(files, signal):
    '''
    Get pmaps files + compute some required variables
    '''
    S_pmaps = get_files_contents(files, 'PMAPS', signal)
    S_pmaps = S_pmaps.merge(S_pmaps.groupby('event').apply(lambda x: 
                                                           x.time.values[-1] - x.time.values[0]).reset_index(name = 'tot_time'),
                                                           on = 'event')
    S_pmaps['time_new'] = S_pmaps.groupby('event').apply(lambda x:
                                                          x.time - x.time.values[0]
                                                          ).reset_index().time

    return S_pmaps


def pmaps_signal_histograms(files, signal, binlist, xrange = [None] * 5):
    '''
    pmaps histograms for S1 and S2
    '''
    signal_pmaps = get_signal_pmaps(files, signal)

    S_e = create_hist_df_simple(signal_pmaps.ene, binlist[0], xrange = xrange[0])
    S_total_e = create_hist_df_simple(signal_pmaps.groupby('event').ene.sum(), binlist[1], xrange = xrange[1])
    S_t = create_hist_df_simple(signal_pmaps.time_new, binlist[2], xrange = xrange[2])
    S_total_t = create_hist_df_simple(signal_pmaps[['event', 'tot_time']].drop_duplicates().tot_time, binlist[3], xrange = xrange[3])
    S_t_weight_e = create_hist_df_simple(signal_pmaps.time_new, binlist[4], weight=signal_pmaps.ene, xrange = xrange[4])
    return S_e, S_total_e, S_t, S_total_t, S_t_weight_e


def pmaps_sensor_histograms(files, signal, sensor, binlist, xrange = [None] * 3):
    '''
    Hypahtia histograms for S1 and S2 PMTs, and S2 SiPMs
    '''
    sensor_pmaps = get_files_contents(files, 'PMAPS', signal + sensor)
    if sensor == 'Pmt':
        nsensor = 'npmt'
    if sensor == 'Si':
        nsensor = 'nsipm'
    S_e_sensor = create_hist_df_simple(sensor_pmaps.ene, binlist[0], xrange = xrange[0])
    a = sensor_pmaps.groupby(['event', nsensor]).ene.sum().reset_index()
    S_total_e_sensor = create_hist_df_simple(a.ene, binlist[1], xrange = xrange[1])
    S_sensor_weight_e = create_hist_df_simple(sensor_pmaps[nsensor], binlist[2], xrange = (0, binlist[2]), weight=sensor_pmaps.ene)
    return S_e_sensor, S_total_e_sensor, S_sensor_weight_e


def pmaps_file_writer(files_path, out_path, city = 'hypathia', tag = '', xrange = [None] * 19):
    '''
    Creates the pmaps group in the file with all the related histograms

    This includes all the histograms for hypathia
    '''
    files = get_all_files(files_path, city)
    #S1
    S1_e, S1_total_e, S1_t, S1_total_t, S1_t_weight_e = pmaps_signal_histograms(files,
                                                                                    'S1',
                                                                                    [100, 30, 42, 30, 42], xrange = xrange[0:5])

    #S2
    S2_e, S2_total_e, S2_t, S2_total_t, S2_t_weight_e = pmaps_signal_histograms(files,
                                                                                    'S2',
                                                                                    [100, 30, 100, 50, 100], xrange = xrange[5:10])

    #S1 - PMT
    S1_e_PMT, S1_total_e_PMT, S1_PMT_weight_e = pmaps_sensor_histograms(files,
                                                                            'S1',
                                                                            'Pmt',
                                                                            [16, 38, 60], xrange = xrange[10:13])

    #S2 - PMT
    S2_e_PMT, S2_total_e_PMT, S2_PMT_weight_e = pmaps_sensor_histograms(files,
                                                                            'S2',
                                                                            'Pmt',
                                                                            [30, 50, 60], xrange = xrange[13:16])
    # S2 - SiPM
    S2_e_Si, S2_total_e_Si, S2_Si_weight_e = pmaps_sensor_histograms(files,
                                                                            'S2',
                                                                            'Si',
                                                                            [100, 100, 3584], xrange = xrange[16:19])
    with tb.open_file(out_path, 'a') as h5out:
        dio.df_writer(h5out, S1_e,            city + tag, 'S1_e',            descriptive_string = '')
        dio.df_writer(h5out, S1_total_e,      city + tag, 'S1_total_e',      descriptive_string = '')
        dio.df_writer(h5out, S1_t,            city + tag, 'S1_t',            descriptive_string = '')
        dio.df_writer(h5out, S1_total_t,      city + tag, 'S1_total_t',      descriptive_string = '')
        dio.df_writer(h5out, S1_t_weight_e,   city + tag, 'S1_t_weight_e',   descriptive_string = '')

        dio.df_writer(h5out, S2_e,            city + tag, 'S2_e',            descriptive_string = '')
        dio.df_writer(h5out, S2_total_e,      city + tag, 'S2_total_e',      descriptive_string = '')
        dio.df_writer(h5out, S2_t,            city + tag, 'S2_t',            descriptive_string = '')
        dio.df_writer(h5out, S2_total_t,      city + tag, 'S2_total_t',      descriptive_string = '')
        dio.df_writer(h5out, S2_t_weight_e,   city + tag, 'S2_t_weight_e',   descriptive_string = '')

        dio.df_writer(h5out, S1_e_PMT,        city + tag, 'S1_e_PMT',        descriptive_string = '')
        dio.df_writer(h5out, S1_total_e_PMT,  city + tag, 'S1_total_e_PMT',  descriptive_string = '')
        dio.df_writer(h5out, S1_PMT_weight_e, city + tag, 'S1_PMT_weight_e', descriptive_string = '')

        dio.df_writer(h5out, S2_e_PMT,        city + tag, 'S2_e_PMT',        descriptive_string = '')
        dio.df_writer(h5out, S2_total_e_PMT,  city + tag, 'S2_total_e_PMT',  descriptive_string = '')
        dio.df_writer(h5out, S2_PMT_weight_e, city + tag, 'S2_PMT_weight_e', descriptive_string = '')

        dio.df_writer(h5out, S2_e_Si,         city + tag, 'S2_e_Si',         descriptive_string = '')
        dio.df_writer(h5out, S2_total_e_Si,   city + tag, 'S2_total_e_Si',   descriptive_string = '')
        dio.df_writer(h5out, S2_Si_weight_e,  city + tag, 'S2_Si_weight_e',  descriptive_string = '')

