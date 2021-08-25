from pathlib import Path
from subprocess import call
import os, csv, re
from calendar import monthrange
from datetime import date, datetime, timedelta


def prepare_files(strategy):
	#update download-data files
#	call(['./update_data.sh'])

	#get local path and instance folder
	path = str(Path().absolute().parent)

	# check if and create folder
	if not os.path.exists(path +'/results'):
		os.makedirs(path +'/results')

	# check if and create new strategy class from template
	if not os.path.isfile(path +'/freqtrade/user_data/strategies/' +strategy +'.py'):
		string = 'freqtrade new-strategy --template minimal --strategy ' +strategy
		os.system(string)
	return path

def MMYY_period(_month, _year):
	_day = monthrange(_year,_month)[1]
	_year = str(_year)
	if _month < 10:
		_month = '0' + str(_month)
	else:
		_month = str(_month)

	if _day < 10:
		_day = '0' + str(_day)
	else:
		_day = str(_day)

	period_ini = _year + _month + '01'
	period_end = _year + _month + _day

	return period_ini, period_end


def list2_exInt(trailing_months):
	if trailing_months > 12:
		trailing_months = 12

	today_month = datetime.today().month
	today_year = datetime.today().year

	month_ini = today_month - trailing_months
	year_ini = today_year
	if trailing_months >= today_month:
		month_ini += 12
		year_ini -= 1

	_year = year_ini
	_month = month_ini
	periods = []
	for count in range(trailing_months):
		period_ini, period_end = MMYY_period(_month, _year)
		periods.append([period_ini, period_end])
		if _month == 12:
			_year += 1
			_month = 0
		_month += 1

	return periods


def download_data(period_ini, period_end, exchange, pair, timeframe, inf_pair, inf_timeframe):
	#if not os.path.isfile(path +'/freqtrade/user_data/data/' +exchange +pair.replace("/","_") +'-'  +timeframe +'.json'):
	timerange = date.today() - date(int(period_ini[:4]), int(period_ini[4:6]), int(period_ini[6:8]))
	timerange = timerange.days
	string = 'freqtrade download-data --exchange ' +exchange +' --pairs ' +pair +' --days ' +str(timerange+15) +' --timeframes ' +timeframe
	os.system(string)
	string = 'freqtrade download-data --exchange ' +exchange +' --pairs ' +inf_pair +' --days ' +str(timerange+245) +' --timeframes ' +inf_timeframe
	os.system(string)


def maxmin_trades(timeframe, period_ini, period_end):
	if timeframe == '5m':
		max_avg_duration = 5
	elif timeframe == '15m':
		max_avg_duration = 15
	elif timeframe == '30m':
		max_avg_duration = 30
	elif timeframe == '1h':
		max_avg_duration = 48
	elif timeframe == '2h':
		max_avg_duration = 72
	elif timeframe == '4h':
		max_avg_duration = 96
	else:
		max_avg_duration = 168

	# table of min_buycount allowed
	datetime_period_ini = datetime.strptime(period_ini, '%Y%m%d')
	datetime_period_end = datetime.strptime(period_end, '%Y%m%d')
	min_buycount = round( 24 * (datetime_period_end - datetime_period_ini).days / (10 * max_avg_duration) )

	return max_avg_duration, min_buycount


def make_header(output, strategy, timeframe, period_ini, period_end, min_buycount, max_avg_duration, fee):
	_suffix = '_' + period_ini + '_' + period_end
	with open(output +_suffix +'.csv','w') as f1:
		writer = csv.writer(f1, delimiter='\t')
		writer.writerows([['Strategy,', strategy], ['Timeframe,', timeframe], ['Period,', period_ini+'-'+period_end], ['Startup candle,', 30], ['Fees [%],', fee * 100], ['Minimum buy count requisit,', min_buycount], ['Maximum avg. duration requisit [h],', max_avg_duration], [], ['timeperiod buy,', 'timeperiod sell,', 'stop loss,', 'trailing,', 'roi,', 'trailing pos. stop loss offset,', 'pos. stop loss,',  'buy count,', 'avg. profit [%],', 'cum profit [%],', 'total profit [USDT],', 'total profit [%],', 'avg. duration,', 'avg. duration [h],', 'profit,', 'loss,', 'force sell,', 'sell signal,', 'stop loss,', 'roi,', 'trailing stop loss,']])


def backtesting_and_save(_pair, _timeframe, inf_pair, inf_timeframe, _period_ini, _period_end, _timeperiod_buy, _timeperiod_sell, _stoploss, _trailing_stop_bool, _roi, _trailing_stop_pos_offset, _trailing_stop_pos, strategy, fee, path, output):
	# create paths
	path_base_strategy = path +'/freqtrade/user_data/strategies/' +strategy +'_default.py'
	path_strategy      = path +'/freqtrade/user_data/strategies/' +strategy +'.py'

	# replace base strategy with current strategy parameters
	with open(path_base_strategy,'r') as f1:

		# startup candle count for 15 days
		_startup_candle_count_value = 15
		if _timeframe == '5m':
			_startup_candle_count_value = 4320 #12 * 24 * 15
		elif _timeframe == '15m':
			_startup_candle_count_value = 1440 #4 * 24 * 15
		elif _timeframe == '30m':
			_startup_candle_count_value = 720 #2 * 24 * 15
		elif _timeframe == '1h':
			_startup_candle_count_value = 360 #24 * 15
		elif _timeframe == '2h':
			_startup_candle_count_value = 180 #12 * 15
		elif _timeframe == '4h':
			_startup_candle_count_value = 90 #6 * 15

		data = f1.read()
		data = data.replace('startup_candle_count_value', str(_startup_candle_count_value))
		data = data.replace('stoploss_value', str(_stoploss))
		data = data.replace('roi_value', str(_roi))
		data = data.replace('trailing_stop_bool', str(_trailing_stop_bool))
		data = data.replace('trailing_stop_pos_value', str(_trailing_stop_pos))
		data = data.replace('trailing_stop_pos_offset_value', str(_trailing_stop_pos_offset))
		data = data.replace('timeframe_value', _timeframe)
		data = data.replace('timeperiod_buy_value', str(_timeperiod_buy))
		data = data.replace('timeperiod_sell_value', str(_timeperiod_sell))

		list_inf = []
		list_inf.append((inf_pair, inf_timeframe))
		data = data.replace('inf_pair_timeframe', str(list_inf))

	with open(path_strategy,'w') as f1:
		f1.writelines(data)
	# replace base config with current pair
	with open(path +'/freqtrade/config_default2.json','r') as f1:
		data = f1.read()
		data = data.replace('pair_name', _pair)
	with open(path +'/freqtrade/config.json','w') as f1:
		f1.writelines(data)

	# backtesting with current strategy and redirect current output to auxiliary file
	_output = '_' +strategy +'_' +_pair.replace('/','_') +'_' +_timeframe
	_suffix = '_' + _period_ini + '_' + _period_end
	string = 'freqtrade backtesting --strategy ' +strategy +' --fee ' +str(fee) +' --timerange ' +_period_ini +'-' +_period_end +' > ' +path +'/results/output' +_output +_suffix +'.txt'
	os.system(string)

	# append to text file
	with open(path +'/results/output' +_output +_suffix +'.txt','r') as f1:
		data = f1.read()
#	with open(output +_suffix +'.txt','a') as f2:
		parameters = [_timeperiod_buy, _timeperiod_sell, _stoploss, _trailing_stop_bool, _roi, _trailing_stop_pos_offset, _trailing_stop_pos]
#		f2.writelines(['[ window buy | window sell | standard dev. | stop loss | trailing | roi value | trailing pos. stop loss offset | pos. stop loss ]\n'])
#		f2.writelines('[ ' +' | '.join(str(e) for e in parameters) +' ]\n')
#		f2.writelines(data)

	# format data
	force_sell = sell_signal = stop_loss = roi = trailing_stop_loss = 0
	if 'force_sell' in data:
		force_sell  = re.findall( '\d+', data.partition('force_sell')[2] )[0]
	if 'sell_signal' in data:
		sell_signal = re.findall( '\d+', data.partition('sell_signal')[2] )[0]
	if 'stop_loss' in data:
		stop_loss   = re.findall( '\d+', data.partition('stop_loss')[2] )[0]
	if 'roi' in data:
		roi         = re.findall( '\d+', data.partition('roi')[2] )[0]
	if 'trailing_stop_loss' in data:
		trailing_stop_loss   = re.findall( '\d+', data.partition(' trailing_stop_loss ')[2] )[0]
	data  = re.findall(r'[-]?\d+\.*\d* | \d+:\d+:\d+ | \d+:\d+ | nan | \d+ day, \d+:\d+:\d+ | \d+ days, \d+:\d+:\d+', data)	# findall possible number patterns

	# average duration in HOURS
	time = re.findall('\d+:\d+:\d+', data[5])[0] if re.findall('\d+:\d+:\d+', data[5]) else '00:00:00'
	days = re.findall('\d+ day, | \d+ days,', data[5])[0] if re.findall('\d+ day, | \d+ days,', data[5]) else '0 day'
	days = days.split()[0]
	ho, mi, se = time.split(':')
	avg_duration = [int( days )*24 +int(ho)]

	# append result to csv file
	with open(output +_suffix +'.csv','a') as f1:
		writer = csv.writer(f1)
		results = parameters +data[0:6] +avg_duration +data[6:8] +[force_sell, sell_signal, stop_loss, roi, trailing_stop_loss]
		writer.writerow(results)

	return results


def best_value(best_timeperiod_buy_value, best_timeperiod_sell_value, best_stoploss, best_trailing_stop_bool, best_roi, best_trailing_stop_pos_offset, timeperiod_buy_value, timeperiod_sell_value, stoploss, trailing_stop_bool, roi, trailing_stop_pos_offset, results, best_result, max_avg_duration, min_buycount):
	profit_per = float(results[11])
	buycount = int(results[7])
	avg_duration = int(results[13])

	if (profit_per > best_result and avg_duration < max_avg_duration and buycount >= min_buycount):
		best_timeperiod_buy_value  = timeperiod_buy_value
		best_timeperiod_sell_value  = timeperiod_sell_value
		best_stoploss  = stoploss
		best_trailing_stop_bool = trailing_stop_bool
		best_roi    = roi
		best_trailing_stop_pos_offset  = trailing_stop_pos_offset
		best_result = profit_per
	return best_timeperiod_buy_value, best_timeperiod_sell_value, best_stoploss, best_trailing_stop_bool, best_roi, best_trailing_stop_pos_offset, best_result
