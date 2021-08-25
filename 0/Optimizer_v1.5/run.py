#!/usr/bin/env python3
from json import loads
from functions import prepare_files, list2_exInt, download_data, maxmin_trades, make_header, best_value, backtesting_and_save

with open('/home/operations/Documents/GF/freqtrade/0/Optimizer_v1.5/settings.json', 'r') as settings_file:
	settings = loads(settings_file.read())

exchange = settings['exchange']['name']
pairs = settings['exchange']['pairs']
timeframes = settings['exchange']['timeframes']
inf_pair = settings['exchange']['inf_pair']
inf_timeframe = settings['exchange']['inf_timeframe']
fee = settings['exchange']['fee_pct'] / 100


#main settings
strategy = settings['strategy']['name']
print(strategy)

# set search bounds parameters
bb_ini  = 20
bb_end  = 40
std_ini = 2
std_end = 4
stoploss_ini = -0.02
roi_ini      = 0.10
step_size = 2

#timeperiod
trailing_months = 0
periods = list2_exInt(trailing_months)



if trailing_months == 0:
	quit()

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
			best_bb_value_buy = bb_ini
			best_bb_value_sell = bb_ini
			best_std_value = std_ini
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
			for std_value in range( 10*round(std_ini), 10*round(std_end)+1, step_size):
				std_value = std_value/10

				for bb_value_buy in range( round(bb_ini), round(bb_end)+1, step_size):
					for bb_value_sell in range( round(bb_ini), round(bb_end)+1, step_size):
						results = backtesting_and_save(pair, timeframe, inf_pair, inf_timeframe, period_ini, period_end, bb_value_buy, bb_value_sell, std_value, stoploss_ini, trailing_stop_bool, roi_ini, trailing_stop_pos_offset, trailing_stop_pos, strategy, fee, path, output)
						best_bb_value_buy, best_bb_value_sell, best_std_value, best_stoploss, best_trailing_stop_bool, best_roi, best_trailing_stop_pos_offset, best_result = best_value(best_bb_value_buy, best_bb_value_sell, best_std_value, best_stoploss, best_trailing_stop_bool, best_roi, best_trailing_stop_pos_offset, bb_value_buy, bb_value_sell, std_value, stoploss_ini, trailing_stop_bool, roi_ini, trailing_stop_pos_offset, results, best_result, max_avg_duration, min_buycount)

			# for best strategy up to here search for STATIC stop loss combinations
			for stoploss in range(int(stoploss_ini*100), 0, step_size):
					stoploss = stoploss/100
					results = backtesting_and_save(pair, timeframe, inf_pair, inf_timeframe, period_ini, period_end, best_bb_value_buy, best_bb_value_sell, best_std_value, stoploss, trailing_stop_bool, roi_ini, trailing_stop_pos_offset, trailing_stop_pos, strategy, fee, path, output)
					best_bb_value_buy, best_bb_value_sell, best_std_value, best_stoploss, best_trailing_stop_bool, best_roi, best_trailing_stop_pos_offset, best_result = best_value(best_bb_value_buy, best_bb_value_sell, best_std_value, best_stoploss, best_trailing_stop_bool, best_roi, best_trailing_stop_pos_offset, best_bb_value_buy, best_bb_value_sell, best_std_value, stoploss, trailing_stop_bool, roi_ini, trailing_stop_pos_offset, results, best_result, max_avg_duration, min_buycount)


			# for best strategy up to here search for TRAILING stop loss combinations
			for stoploss in range(int(stoploss_ini*100), 0, step_size):
					stoploss = stoploss/100
					trailing_stop_bool = True
					results = backtesting_and_save(pair, timeframe, inf_pair, inf_timeframe, period_ini, period_end, best_bb_value_buy, best_bb_value_sell, best_std_value, stoploss, trailing_stop_bool, roi_ini, trailing_stop_pos_offset, trailing_stop_pos, strategy, fee, path, output)
					best_bb_value_buy, best_bb_value_sell, best_std_value, best_stoploss, best_trailing_stop_bool, best_roi, best_trailing_stop_pos_offset, best_result = best_value(best_bb_value_buy, best_bb_value_sell, best_std_value, best_stoploss, best_trailing_stop_bool, best_roi, best_trailing_stop_pos_offset, best_bb_value_buy, best_bb_value_sell, best_std_value, stoploss, trailing_stop_bool, roi_ini, trailing_stop_pos_offset, results, best_result, max_avg_duration, min_buycount)


			# for best strategy up to here search for ROI combinations
			for roi in range(int(roi_ini*100), 0, -step_size):
					roi = roi/100
					results = backtesting_and_save(pair, timeframe, inf_pair, inf_timeframe, period_ini, period_end, best_bb_value_buy, best_bb_value_sell, best_std_value, best_stoploss, best_trailing_stop_bool, roi, trailing_stop_pos_offset, trailing_stop_pos, strategy, fee, path, output)
					best_bb_value_buy, best_bb_value_sell, best_std_value, best_stoploss, best_trailing_stop_bool, best_roi, best_trailing_stop_pos_offset, best_result = best_value(best_bb_value_buy, best_bb_value_sell, best_std_value, best_stoploss, best_trailing_stop_bool, best_roi, best_trailing_stop_pos_offset, best_bb_value_buy, best_bb_value_sell, best_std_value, best_stoploss, best_trailing_stop_bool, roi, trailing_stop_pos_offset, results, best_result, max_avg_duration, min_buycount)


			# for best strategy up to here search for POSITIVE TRAILING stop loss combinations
			best_trailing_stop_pos_offset = trailing_stop_pos_offset_ini = best_roi
			trailing_stop_pos = 0.2*trailing_stop_pos_offset_ini
			for trailing_stop_pos_offset in range( int(trailing_stop_pos_offset_ini*100 ), int(trailing_stop_pos*100)+1, -step_size):
					trailing_stop_pos_offset = trailing_stop_pos_offset/100
					results = backtesting_and_save(pair, timeframe, inf_pair, inf_timeframe, period_ini, period_end, best_bb_value_buy, best_bb_value_sell, best_std_value, best_stoploss, best_trailing_stop_bool, best_roi, trailing_stop_pos_offset, trailing_stop_pos, strategy, fee, path, output)
					best_bb_value_buy, best_bb_value_sell, best_std_value, best_stoploss, best_trailing_stop_bool, best_roi, best_trailing_stop_pos_offset, best_result = best_value(best_bb_value_buy, best_bb_value_sell, best_std_value, best_stoploss, best_trailing_stop_bool, best_roi, best_trailing_stop_pos_offset, best_bb_value_buy, best_bb_value_sell, best_std_value, best_stoploss, best_trailing_stop_bool, roi, trailing_stop_pos_offset, results, best_result, max_avg_duration, min_buycount)

			# run best strategy
			results = backtesting_and_save(pair, timeframe, inf_pair, inf_timeframe, period_ini, period_end, best_bb_value_buy, best_bb_value_sell, best_std_value, best_stoploss, best_trailing_stop_bool, best_roi, best_trailing_stop_pos_offset, trailing_stop_pos, strategy, fee, path, output)

print('******************************************************************************')
print('*** thank you for your preference. visit our website https://greenfield-br.com')
