#!/usr/bin/env python3
from functions2 import prepare_files, list2_exInt, download_data, maxmin_trades, make_header, best_value, backtesting_and_save

#main settings
strategy = 'TS'
exchange = 'binance'
pairs = ['BTC/USDT'] #, 'ETH/USDT', 'LTC/USDT']
timeframes = ['1d'] #, '15m', '30m', '1h']
inf_pair = 'BTC/USDT' #, 'ETH/USDT', 'LTC/USDT']
inf_timeframe = '1w' #, '15m', '30m', '1h']
fee = 0.1/100 #trading fee

#timeperiod
trailing_months = 6
periods = list2_exInt(trailing_months)

# set search bounds parameters
timeperiod_ini  = 10
timeperiod_end  = 30
stoploss_ini = -0.05
roi_ini      = 0.20
step_size = 1


# ------------------------------------------------------------------------------
# get home/user directory
path = prepare_files(strategy)

# for all declared pairs
for pair in pairs:

	# for all declared timeframes
	for timeframe in timeframes:

		# download data
		period_ini = periods[0][0]
		period_end = periods[0][1]
		download_data(period_ini, period_end, exchange, pair, timeframe, inf_pair, inf_timeframe)

		for _period in periods:
			period_ini = _period[0]
			period_end = _period[1]

			# reset CLI, files and best values
			output = path +'/results/' +strategy +'_' +pair.replace('/','_') +'_' +timeframe

			# reset bests values
			best_timeperiod_buy_value = timeperiod_ini
			best_timeperiod_sell_value = timeperiod_ini
			best_stoploss = stoploss_ini
			best_trailing_stop_bool = False
			best_roi = roi_ini
			best_trailing_stop_pos_offset = 1
			best_trailing_stop_pos = 0.1
			best_result = -10000

			# table of max_avg_duration in hours allowed
			max_avg_duration, min_buycount = maxmin_trades(timeframe, period_ini, period_end)

			trailing_stop_bool = best_trailing_stop_bool
			trailing_stop_pos_offset = best_trailing_stop_pos_offset
			trailing_stop_pos = best_trailing_stop_pos

			# header for .csv output
			make_header(output, strategy, timeframe, period_ini, period_end, min_buycount, max_avg_duration, fee)

			# search for all buy and sell combinations

			for timeperiod_buy_value in range( round(timeperiod_ini), round(timeperiod_end)+1, step_size):
				for timeperiod_sell_value in range( round(timeperiod_ini), round(timeperiod_end)+1, step_size):
					results = backtesting_and_save(pair, timeframe, inf_pair, inf_timeframe, period_ini, period_end, timeperiod_buy_value, timeperiod_sell_value, stoploss_ini, trailing_stop_bool, roi_ini, trailing_stop_pos_offset, trailing_stop_pos, strategy, fee, path, output)
					best_timeperiod_buy_value, best_timeperiod_sell_value, best_stoploss, best_trailing_stop_bool, best_roi, best_trailing_stop_pos_offset, best_result = best_value(best_timeperiod_buy_value, best_timeperiod_sell_value, best_stoploss, best_trailing_stop_bool, best_roi, best_trailing_stop_pos_offset, timeperiod_buy_value, timeperiod_sell_value, stoploss_ini, trailing_stop_bool, roi_ini, trailing_stop_pos_offset, results, best_result, max_avg_duration, min_buycount)

			# for best strategy up to here search for STATIC stop loss combinations
			for stoploss in range(int(stoploss_ini*100), 0, step_size):
				stoploss = stoploss/100
				results = backtesting_and_save(pair, timeframe, inf_pair, inf_timeframe, period_ini, period_end, best_timeperiod_buy_value, best_timeperiod_sell_value, stoploss, trailing_stop_bool, roi_ini, trailing_stop_pos_offset, trailing_stop_pos, strategy, fee, path, output)
				best_timeperiod_buy_value, best_timeperiod_sell_value, best_stoploss, best_trailing_stop_bool, best_roi, best_trailing_stop_pos_offset, best_result = best_value(best_timeperiod_buy_value, best_timeperiod_sell_value, best_stoploss, best_trailing_stop_bool, best_roi, best_trailing_stop_pos_offset, best_timeperiod_buy_value, best_timeperiod_sell_value, stoploss, trailing_stop_bool, roi_ini, trailing_stop_pos_offset, results, best_result, max_avg_duration, min_buycount)

			# for best strategy up to here search for TRAILING stop loss combinations
			for stoploss in range(int(stoploss_ini*100), 0, step_size):
				stoploss = stoploss/100
				trailing_stop_bool = True
				results = backtesting_and_save(pair, timeframe, inf_pair, inf_timeframe, period_ini, period_end, best_timeperiod_buy_value, best_timeperiod_sell_value, stoploss, trailing_stop_bool, roi_ini, trailing_stop_pos_offset, trailing_stop_pos, strategy, fee, path, output)
				best_timeperiod_buy_value, best_timeperiod_sell_value, best_stoploss, best_trailing_stop_bool, best_roi, best_trailing_stop_pos_offset, best_result = best_value(best_timeperiod_buy_value, best_timeperiod_sell_value, best_stoploss, best_trailing_stop_bool, best_roi, best_trailing_stop_pos_offset, best_timeperiod_buy_value, best_timeperiod_sell_value, stoploss, trailing_stop_bool, roi_ini, trailing_stop_pos_offset, results, best_result, max_avg_duration, min_buycount)

			# for best strategy up to here search for ROI combinations
			for roi in range(int(roi_ini*100), 0, -step_size):
				roi = roi/100
				results = backtesting_and_save(pair, timeframe, inf_pair, inf_timeframe, period_ini, period_end, best_timeperiod_buy_value, best_timeperiod_sell_value, best_stoploss, best_trailing_stop_bool, roi, trailing_stop_pos_offset, trailing_stop_pos, strategy, fee, path, output)
				best_timeperiod_buy_value, best_timeperiod_sell_value, best_stoploss, best_trailing_stop_bool, best_roi, best_trailing_stop_pos_offset, best_result = best_value(best_timeperiod_buy_value, best_timeperiod_sell_value, best_stoploss, best_trailing_stop_bool, best_roi, best_trailing_stop_pos_offset, best_timeperiod_buy_value, best_timeperiod_sell_value, best_stoploss, best_trailing_stop_bool, roi, trailing_stop_pos_offset, results, best_result, max_avg_duration, min_buycount)

			# for best strategy up to here search for POSITIVE TRAILING stop loss combinations
			best_trailing_stop_pos_offset = trailing_stop_pos_offset_ini = best_roi
			trailing_stop_pos = 0.2*trailing_stop_pos_offset_ini
			for trailing_stop_pos_offset in range( int(trailing_stop_pos_offset_ini*100 ), int(trailing_stop_pos*100)+1, -step_size):
				trailing_stop_pos_offset = trailing_stop_pos_offset/100
				results = backtesting_and_save(pair, timeframe, inf_pair, inf_timeframe, period_ini, period_end, best_timeperiod_buy_value, best_timeperiod_sell_value, best_stoploss, best_trailing_stop_bool, best_roi, trailing_stop_pos_offset, trailing_stop_pos, strategy, fee, path, output)
				best_timeperiod_buy_value, best_timeperiod_sell_value, best_stoploss, best_trailing_stop_bool, best_roi, best_trailing_stop_pos_offset, best_result = best_value(best_timeperiod_buy_value, best_timeperiod_sell_value, best_stoploss, best_trailing_stop_bool, best_roi, best_trailing_stop_pos_offset, best_timeperiod_buy_value, best_timeperiod_sell_value, best_stoploss, best_trailing_stop_bool, roi, trailing_stop_pos_offset, results, best_result, max_avg_duration, min_buycount)

			# run best strategy
			results = backtesting_and_save(pair, timeframe, inf_pair, inf_timeframe, period_ini, period_end, best_timeperiod_buy_value, best_timeperiod_sell_value, best_stoploss, best_trailing_stop_bool, best_roi, best_trailing_stop_pos_offset, trailing_stop_pos, strategy, fee, path, output)

print('******************************************************************************')
print('*** thank you for your preference. visit our website https://greenfield-br.com')
