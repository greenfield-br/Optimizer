from os import chdir, listdir
import pandas
import numpy
from datetime import datetime, timedelta
from calendar import monthrange
from json import load
from plotly.subplots import make_subplots
from plotly.graph_objects import Heatmap, Bar
import plotly.express as px
import plotly.io
plotly.io.renderers.default = 'chromium'

#functions should be called in the same order they appear in this file.
#edit this file with caution. you were warned.

#generates list with all subfolders in given path
def list_exURL(_home, _path):
	chdir(_home + _path)
	_lst = sorted(listdir())
	_lst_len_half = int(len(_lst) / 2)
	_lst = _lst[:_lst_len_half]
	return _lst


def dict2_exList(period_ini):

	#adapting from original YYMM list to exFilename period_ini
	end_date = datetime.today()
	date = datetime(int(period_ini[:4]), int(period_ini[4:6]), int(period_ini[-2:]))
	trailing_months = (end_date.year - date.year) * 12 + (end_date.month - date.month)

	#_lst building from datetime ex period_ini
	_lst = []
	if trailing_months > 0:
		if trailing_months > 12:
			trailing_months = 12
		while date < end_date:
			_year = str(date.year)[2:4]
			_month = str(date.month)
			if date.month < 10:
				_month = '0' + _month
			_lst.append(_year + _month)
			if date.month < 12:
				date = datetime(date.year, date.month+1, 1)
			else:
				date = datetime(date.year+1, 1, 1)
	#excludes tailing current uncomplete month
	_lst = _lst[:trailing_months]

	#with _lst rebuilt, reuses original _dict building
	lst = []
	count = 0
	_dict = {}
	i_max = len(_lst) - 1
	for i in range(i_max):
		lst.append(_lst[i][2:])
		if (_lst[i][:2] != _lst[i+1][:2]) and (i < i_max-1):
			_dict[_lst[i][:2]] = dict.fromkeys(lst, 0)
			lst = []
		if i == i_max-1:
			if _lst[i][:2] == _lst[i+1][:2]:
				lst.append(_lst[i+1][2:])
			_dict[_lst[i][:2]] = dict.fromkeys(lst, 0)
			if _lst[i][:2] != _lst[i+1][:2]:
				lst = []
				lst.append(_lst[i+1][2:])
				_dict[_lst[i+1][:2]] = dict.fromkeys(lst, 0)

	return _dict

def dict_exFile3(home, path, k, _k, filename):

	_filename_opt = home +path +filename[:-8] +'20' +k +_k +'01_' +'20' +k +_k + str(monthrange(2000+int(k),int(_k))[1]) +filename[-4:]

	dataframe = pandas.read_csv(_filename_opt, sep=',', skiprows=8, nrows=1331)
	dataframe_columns = dataframe.columns
	filtered_columns = []
	for column_name in dataframe_columns:
		column_name = column_name.replace('\t','')
		filtered_columns.append(column_name)
	dataframe.columns = filtered_columns
	pivot = dataframe.groupby(by=['window buy', 'window sell']).median()
	narray_exPivot = pivot['cum profit [%]'].to_numpy().reshape(11,11)
	x_plot = numpy.unique(dataframe['window buy'].tolist())
	y_plot = numpy.unique(dataframe['window sell'].tolist())
	pivot = dataframe.groupby(by=['standard dev.']).median()
	x_plot2 = numpy.unique(dataframe['standard dev.'].tolist())
	y1_plot2 = pivot['cum profit [%]'].tolist()
	y2_plot2 = pivot['buy count'].tolist()
	_dict = {
		'_narray_exPivot': narray_exPivot,
		'_x_plot': x_plot,
		'_y_plot': y_plot,
		'_x_plot2': x_plot2,
		'_y1_plot2': y1_plot2,
		'_y2_plot2': y2_plot2
	}
	return _dict



def _dict_exDict_plot(_dict, _max_columns):
	_tmp = {}
	reversed_keys = list(_dict.keys())[::-1]
	len_last1_keys = len(_dict[reversed_keys[0]].keys())

	if ( len_last1_keys < _max_columns ) and ( len(reversed_keys) > 1 ):

		len_last2_keys = len(_dict[reversed_keys[1]].keys())
		_columns_complement = _max_columns - len_last1_keys

		list_keys_1 = list(_dict[reversed_keys[1]].keys())
		if ( len_last2_keys > _columns_complement ):
 
			list_keys_1 = list(_dict[reversed_keys[1]].keys())[-_columns_complement:]
	
		for _k in list_keys_1:
			_tmp[ reversed_keys[1] + _k ] = _dict[reversed_keys[1]][_k]
	
	for _k in _dict[ reversed_keys[0] ].keys():
		_tmp[ reversed_keys[0] + _k ] = _dict[reversed_keys[0]][_k]

	_columns = len(_tmp.keys())
	_dict = _tmp.copy()
	_tmp.clear()

	return _dict, _columns



def datetime_exKeys_plot(_keys):
	_start = _keys[0][:2] + '/' + _keys[0][-2:] + '/01 00:00:00'
	_start = datetime.strptime(_start, '%y/%m/%d %H:%M:%S')
	_end = _keys[-1][:2] + '/' + _keys[-1][-2:] + '/' + str(monthrange(2000+int(_keys[-1][:2]),int(_keys[-1][-2:]))[1]) +' 23:59:59'
	_end = datetime.strptime(_end, '%y/%m/%d %H:%M:%S')
	return _start, _end



def dataframe_exFile(filename, _start, _end):

	with open(filename) as f:
		lst = load(f)
	ohlcv_dataframe = pandas.DataFrame(lst, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
	ohlcv_dataframe['datetime'] = pandas.to_datetime(ohlcv_dataframe['datetime'], unit='ms')
#	ohlcv_dataframe.set_index('datetime', inplace=True)
	tmp = ohlcv_dataframe['close'].shift(-1) - ohlcv_dataframe['close']
	tmp = numpy.divide(tmp, ohlcv_dataframe['close'])
	ohlcv_dataframe['change'] = tmp.shift(1)

	ohlcv_dataframe = ohlcv_dataframe.loc[(ohlcv_dataframe['datetime'] >= _start) & (ohlcv_dataframe['datetime'] <= _end)]

	return ohlcv_dataframe


def dataframe_list_exDataframe(change_factor, parameters):

	win = parameters[0]
	loss = parameters [1]
	cost = parameters [2]
	
	#sell reason array building
	sell_reason = list()
	trade_performance = 1
	for candle_change in change_factor:
		trade_performance *= candle_change
		if trade_performance > ( 1 + win/100 ):
#			sell_reason.append(win * (1 - cost))
			sell_reason.append(1)
			trade_performance = 1
		if trade_performance < ( 1 + loss/100 ):
#			sell_reason.append(loss * (1 + cost))
			sell_reason.append(-1)
			trade_performance = 1
	trades_performance = pandas.DataFrame([sum(sell_reason)], columns=['sum'])

	return trades_performance, sell_reason


def dataframe_exDataframe_List(trades_performance, sell_reason):
	#sell reason array compacting
#	print(trades_performance)
#	print(sell_reason)
	if sell_reason:
		sell_reason_compact = list()
		sell_reason_compact.append(sell_reason[0])
		j = 0
		for i in range(len(sell_reason)-1):
			if(sell_reason[i] == sell_reason[i+1]):
				sell_reason_compact[j] += sell_reason[i+1]
			else:
				j += 1
				sell_reason_compact.append(sell_reason[i+1])

		sell_reason_compact_cumulative = list()
		sell_reason_compact_cumulative.append(sell_reason_compact[0])
		for i in range(len(sell_reason_compact)-1):
			sell_reason_compact_cumulative.append(sell_reason_compact_cumulative[i] + sell_reason_compact[i+1])

		trades_performance['max']=max(sell_reason_compact)
		trades_performance['min']=min(sell_reason_compact)
		trades_performance['trades']=len(sell_reason)
	else:
		trades_performance['max'] = 0
		trades_performance['min'] = 0
		trades_performance['trades'] = 0	

	return trades_performance


def plot_exDict4(_dict, filename_opt, filename_trades, parameters):

	#internal size
	_max_columns = 8
	#external size
	_width = 1560
	_height = 1060
	if parameters[3] == 'screen':
		_width = 1366
		_height = 768

	#rebuilding _dict dictionary for last _columns entries
	_dict, _columns = _dict_exDict_plot(_dict, _max_columns)

	#getting trades from the same period
	#getting timerange for the trades
	_keys = list(_dict.keys())
	_start, _end = datetime_exKeys_plot(_keys)
	
	#subsetting file dataframe
	#opening the file
	candle_dataframe = dataframe_exFile(filename_trades, _start, _end)
	dataframe_grouped = candle_dataframe.groupby(pandas.Grouper(key='datetime', freq='M'))
	monthly_dataframe = pandas.DataFrame(columns=['year', 'month', 'sum', 'max', 'min', 'trades'])
	list_dataframes = [group for _,group in dataframe_grouped]
	for _dataframe in list_dataframes:
	#	_dataframe.set_index('datetime', inplace=True)
		change_factor = _dataframe['change'][1:] + 1
		trades_performance, sell_reason = dataframe_list_exDataframe(change_factor, parameters)
		trades_performance = dataframe_exDataframe_List(trades_performance, sell_reason)
		trades_performance['year'] = _dataframe['datetime'].iloc[0].year
		trades_performance['month'] = _dataframe['datetime'].iloc[0].month
		monthly_dataframe = pandas.concat([monthly_dataframe, trades_performance])
	monthly_dataframe.set_index(['year', 'month'], inplace=True)

	monthly_dataframe.columns = monthly_dataframe.columns.map(lambda x: x[1])
	monthly_dataframe = monthly_dataframe.reset_index()
	monthly_dataframe.columns = ['year', 'month', 'sum', 'max', 'min', 'trades']

	#plotting
	_title = filename_opt
	_subtitles = ['stop loss / roi performance']
	_subtitles = numpy.append(_subtitles, list(_dict.keys()))

	fig = make_subplots(rows=3, cols=_columns,
						row_heights=[0.6, 0.2, 0.2],
					    specs=[[{"colspan": _columns}] + [None] * (_columns - 1),
					           [{}] * _columns,
					           [{}] * _columns
					           ],
						subplot_titles=_subtitles,
						x_title='window buy / standard deviation',
						y_title='window sell')

	#adjusting top plot x axis
	_x_plot0 = []
	for _month in list(monthly_dataframe['month']):
		_x_plot0.append('yy/' + str(_month))
	_y_plot0 = list(monthly_dataframe['sum'])

	len_x_plot0 = len(_x_plot0)

	fig.add_trace(
		Bar(x=_x_plot0, y=_y_plot0, width=[0.4]*len_x_plot0),
		row=1, col=1)
	fig.update_traces(marker_color='#003153')

	#2nd, 3rd row plots
	col_count = 1
	for k in _dict.keys():

		narray_exPivot = _dict[k]['_narray_exPivot']
		x_plot = _dict[k]['_x_plot']
		y_plot = _dict[k]['_y_plot']
		x_plot2 = _dict[k]['_x_plot2']
		y1_plot2 = _dict[k]['_y1_plot2']
		y2_plot2 = _dict[k]['_y2_plot2']
		_row = 2
		_col = col_count

		fig.add_trace(
			Heatmap(
				z=narray_exPivot.transpose(),
				x=x_plot,
				y=y_plot,
				coloraxis="coloraxis"),
			row=_row, col=_col)
		fig.add_trace(
			Bar(
				x=x_plot2,
				y=y1_plot2,
				marker={
					'color': y2_plot2,
					'cmin': 0,
					'cmax': 10,
					'colorscale': 'greys',
					'showscale': True,
					'colorbar': {'len': 0.6, 'y': .2}
				}),
			row=_row+1, col=_col)

		col_count += 1

	fig.update_layout(
		title_text=_title,
		coloraxis=dict(
			colorbar={'lenmode': 'fraction', 'len': 0.6, 'y':.8},
			colorscale='RdBu', cmin=-5, cmid=0, cmax=5
		),
		showlegend=False,
		autosize=False,
		width=_width,
		height=_height)

	fig.show()
