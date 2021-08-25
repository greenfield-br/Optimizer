#!/usr/bin/python

#import functions from file
from multifunc_TR import list_exURL, dict2_exList, dict_exFile3, plot_exDict4

#Optimizer 1.4 files location
instance = 2 #0, 1, 2
home = '/home/operations'
path_opt = '/Documents/GF/freqtrade/' +str(instance) +'/results'
path_trades = '/Documents/GF/freqtrade/' +str(instance) +'/freqtrade/user_data/data'
exchange = 'binance'

#list with year/month named folders with target filename
_lst = list_exURL(home, path_opt)

#specifications ex filename
_spec_exlst0 = _lst[0][:-4].split('_')
strategy = _spec_exlst0[0]
pair = _spec_exlst0[1] + '/' + _spec_exlst0[2]
timeframe = _spec_exlst0[3]
period_ini = _spec_exlst0[4]

#empty dictionary (year) of dictionaries (month) from year/month list
_dict = dict2_exList(period_ini)

#[roi, stop loss, slippage, chart sizing]
parameters = [10, -2, 5/100, 'screen']

suffix = str(abs(parameters[1]))
if abs(parameters[1]) < 10:
	suffix = '0' + suffix
suffix = '_sl' + suffix

filename_opt = '/' + strategy + '_' + pair.replace('/', '_') + '_' + timeframe + suffix+'.csv'
filename_trades = home + path_trades + '/' + exchange + '/' + pair.replace('/', '_') + '-' + timeframe + '.json'

# com _dict{} vazio adapto dict_exFile3 para abrir os arquivos do result e povoar o dicionario


#populate dictionary of dictinaries with Optimizer1.4 data plotting ready

for k in _dict.keys():
	for _k in _dict[k].keys():
		_dict[k][_k] = dict_exFile3(home, path_opt, k, _k, filename_opt)

#plotting
plot_exDict4(_dict, filename_opt, filename_trades, parameters)
