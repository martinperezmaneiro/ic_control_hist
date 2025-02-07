import os
import sys
import matplotlib.pyplot as plt

#path of the current file, added to pythonpath to use the functions
dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dir_path)

from plot_hist_utils import plot_hist_comparison
from utils_hist import get_group_nodes_names

'''
Takes the comparison histogram files and plots all the variables
'''

path = '/Users/mperez/NEXT/ic_dev/prueba/{}_comp.h5'
A_tag = 'old'
B_tag = 'ref'
cities = ['hypathia', 'sophronia', 'esmeralda', 'beersheba', 'isaura']
is_A_penthesilea = True
plot_scale = 'linear'

for city in cities:
    print(city)
    city_A, city_B = city, city
    hist_file = path.format(city[:3])
    group_names, node_names = get_group_nodes_names(hist_file)
    for variable in node_names[0]:
        if variable.split('_')[-1] == 'cut':
            continue
        if variable[0:3] == 'low':
            continue
        if (city_A == 'sophronia') and is_A_penthesilea: city_A = 'penthesilea'
        else: city_A = city_A
        print(variable)
        
        plot_hist_comparison(hist_file, hist_file, city_A + A_tag, city_B + B_tag, variable, scale = plot_scale, legend1=city_A, legend2=city_B)
        # plt.savefig('plot_folder/{}/{}_'.format(city, city) + variable + '.png')
        plt.show()