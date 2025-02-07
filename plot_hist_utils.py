import os
import sys
import numpy as np
import pandas as pd
import scipy.stats as sct
import matplotlib.pyplot as plt

from scipy.optimize import curve_fit
import invisible_cities.io.dst_io as dio

#path of the current file, added to pythonpath to use the functions
dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dir_path)

from utils_hist import get_hist_from_data, get_group_nodes_names

def compare_hist(expe_hist, meas_hist, min_hist_count):
    # cleaning in the expected histograms to compute chi2
    # I was doing this cleaning on the 'norm_values', but for some special cases it
    # raised an error, so had to change it like it is now
    clean_hist_mask = expe_hist['values'] > min_hist_count
    
    expe_hist = expe_hist[clean_hist_mask].copy()
    meas_hist = meas_hist[clean_hist_mask].copy()

    #NORMALIZATION ADDED BECAUSE THE CHISQUARE FUNCTION CHANGED AND NOW NEEDS THIS
    expe_hist['norm_values'] = expe_hist['values'] / expe_hist['values'].sum()
    meas_hist['norm_values'] = meas_hist['values'] / meas_hist['values'].sum()
        
    stats = sct.chisquare(meas_hist['norm_values'], f_exp = expe_hist['norm_values'])
    return stats

def get_chi2_stats(path, refactor_path, city, min_hist_count = 0, tag = ('', '')):
    city_dct = {'hypathia':'hypathia', 'penthesilea':'sophronia', 'esmeralda':'esmeralda', 'beersheba':'beersheba', 'isaura':'isaura'}
    group_names, node_names = get_group_nodes_names(path)
    ref_group_names, ref_node_names = get_group_nodes_names(refactor_path)
    
    hist_names = node_names[group_names.index(city + tag[0])]
    ref_hist_names = ref_node_names[ref_group_names.index(city_dct[city] + tag[1])]
    
    #assure same nodes are going to be compared
    hist_names = list(np.array(hist_names)[np.isin(hist_names, ref_hist_names)])
    
    results = []
    for n in hist_names:
        if n.split('_')[-1] == 'cut':
            #avoid the non histogram data in the files
            continue
        expe_hist = get_hist_from_data(path, city + tag[0], n)
        meas_hist = get_hist_from_data(refactor_path, city_dct[city] + tag[1], n)
        
        stats = compare_hist(expe_hist, meas_hist, min_hist_count)
        
        results.append([n, stats.statistic, stats.pvalue])
    return pd.DataFrame(results, columns = ['name', 'chi2', 'pvalue'])

def bin_err(ref_hist, meas_hist):
    N_meas = meas_hist['values']
    N_ref  = ref_hist['values']
    
    sig = (N_meas - N_ref) / np.sqrt(N_meas + N_ref)
    #chi2 is not an err but i wanted to see the points
    chi2 = (N_meas - N_ref) ** 2 / N_ref
    return sig, chi2

def ene_resolution(mean, sigma):
    R = 2*np.sqrt(2*np.log(2)) * sigma / mean
    return R

def fit_values(hist):
    def gauss(x, H, A, x0, sigma):
        return H + A * np.exp(-(x - x0) ** 2 / (2 * sigma ** 2))

    bins = hist.bins.values
    x = (bins[:-1] + bins[1:]) / 2
    y = hist['values'].values[:-1]
    p, cov = curve_fit(gauss, x, y)
    fit_y = gauss(x, p[0], p[1], p[2], p[3])

    plt.plot(x, fit_y, '-', label=r'$\sigma$ = {:.5e}'.format(p[3]) + '\n' + r'$\mu = {:.5}$'.format(p[2]))
    print(ene_resolution(p[2], p[3]))

def plot_hist_from_data(hist_path, group, node, opacity = 0, lw = 1, legend = '', scale = 'linear', fit = False):
    if isinstance(hist_path, str):
        hist = dio.load_dst(hist_path, group, node)
    elif isinstance(hist_path, pd.DataFrame):
        hist = hist_path
    else:
        raise Exception("Not a path or a DF")
        
    edges = hist['bins'].values[:-1]
    freq  = hist['values'].values[:-1]
    diff  = np.diff(edges)[0]
    
    
    plt.bar(edges, freq, width=diff, align="edge", alpha = opacity)
    step_edges = np.append(np.append(0, edges), edges[-1] + diff)
    step_freq  = np.append(np.append(0, freq), 0)
    plt.step(step_edges, step_freq, where = 'post', linewidth = lw, label = legend)
    plt.yscale(scale)
    if fit:
        fit_values(hist)
    return hist, diff

def plot_hist_comparison(ref_path, meas_path, ref_group, meas_group, node, figsize = (9, 7), scale = 'linear', legend1 = 'reference', legend2 = 'measured', title = None, fit = False):
    fig    = plt.figure(figsize = figsize)
    gs     = fig.add_gridspec(4, 1)
    plt.subplots_adjust(wspace=0, hspace=0)

    #HISTOGRAM
    ax     = fig.add_subplot(gs[0:3, 0])
    ref_hist, diff  = plot_hist_from_data(ref_path, ref_group, node, lw = 2, legend = legend1, fit = fit)
    meas_hist, diff = plot_hist_from_data(meas_path, meas_group, node, lw = 1, legend = legend2, fit = fit)
    
    bins = ref_hist['bins'] #assuming both histograms have the same bins
    plt.xlim((bins.min() - diff, bins.max() + diff))
    plt.xticks(alpha = 0)
    plt.ylabel('Count')
    plt.legend()
    ax.set_yscale(scale)
    ax.grid()
    
    stats = compare_hist(ref_hist, meas_hist, 0)
    plt.title(r'$\chi^2$ = {chi}, $p_{val}$ = {pval}'.format(chi = stats.statistic, val = '{val}', pval = stats.pvalue))
    
    ax_err = fig.add_subplot(gs[3, 0])
    sig, chi2 = bin_err(ref_hist, meas_hist)
    max_sig = abs(sig).max()
    
    plt.plot(bins + diff/2, sig, 'o')
    #plt.plot(bins + diff/2, chi2, 'o')
    plt.xlim((bins.min() - diff, bins.max() + diff))
    if max_sig != 0:
        plt.ylim((-1.3*max_sig , 1.3*max_sig)) #center in 0 the error points
        
    plt.ylabel(r'$\sigma$')
    
    if not title:
        plt.xlabel(node)
    else:
        plt.xlabel(title)
    ax_err.grid()