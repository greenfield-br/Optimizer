# pragma pylint: disable=missing-docstring, invalid-name, pointless-string-statement

# --- Do not remove these libs ---
import numpy as np  # noqa
import pandas as pd  # noqa
from pandas import DataFrame
from freqtrade.strategy.interface import IStrategy

# --------------------------------
# Add your lib to import here
import talib.abstract as ta
import freqtrade.vendor.qtpylib.indicators as qtpylib


class TR(IStrategy):
    """
    This is a strategy template to get you started.
    More information in https://github.com/freqtrade/freqtrade/blob/develop/docs/bot-optimization.md
    You can:
        :return: a Dataframe with all mandatory indicators for the strategies
    - Rename the class name (Do not forget to update class_name)
    - Add any methods you want to build your strategy
    - Add any lib you need to build your strategy

    You must keep:
    - the lib in the section "Do not remove these libs"
    - the prototype for the methods: minimal_roi, stoploss, populate_indicators, populate_buy_trend,
    populate_sell_trend, hyperopt_space, buy_strategy_generator
    """

    # Strategy interface version - allow new iterations of the strategy interface.
    # Check the documentation or the Sample strategy to get the latest version.
    INTERFACE_VERSION = 2

    # Minimal ROI designed for the strategy.
    minimal_roi = {"0": roi_value}

    # Number of candles the strategy requires before producing valid signals
    startup_candle_count: int = startup_candle_count_value

    # Optimal stoploss designed for the strategy.p
    stoploss = stoploss_value

    # Trailing stoploss
    trailing_stop = trailing_stop_bool
    trailing_stop_positive = trailing_stop_pos_value
    trailing_stop_positive_offset = trailing_stop_pos_offset_value
    trailing_only_offset_is_reached = False

    # Optimal ticker interval for the strategy.
    ticker_interval = 'timeframe_value'

    # Run "populate_indicators()" only for new candle.
    process_only_new_candles = True

    # These values can be overridden in the "ask_strategy" section in the config.
    use_sell_signal = True
    sell_profit_only = False
    ignore_roi_if_buy_signal = True

    # Optional order type mapping.
    order_types = {
        'buy': 'limit',
        'sell': 'limit',
        'stoploss': 'limit',
        'stoploss_on_exchange': True
    }


    # Optional order time in force.
    order_time_in_force = {
        'buy': 'gtc',
        'sell': 'gtc'
    }

    def informative_pairs(self):
        """
        Define additional, informative pair/interval combinations to be cached from the exchange.
        These pair/interval combinations are non-tradeable, unless they are part
        of the whitelist as well.
        For more information, please consult the documentation
        :return: List of tuples in the format (pair, interval)
            Sample: return [("ETH/USDT", "5m"),
                            ("BTC/USDT", "15m"),

                            ]
        """
#       return [("BTC/USDT", "5m"),
#        		("ETH/USDT", "5m")]
        return inf_pair_timeframe

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        bollinger_buy  = qtpylib.bollinger_bands(dataframe['close'], window=bb_value_buy, stds=std_value)
        bollinger_sell = qtpylib.bollinger_bands(dataframe['close'], window=bb_value_sell, stds=std_value)
        dataframe['bb_lowerband'] = bollinger_buy['lower']
        dataframe['bb_upperband'] = bollinger_sell['upper']

        if self.dp:
            inf_pair, inf_timeframe = self.informative_pairs()[0]
            informative = self.dp.get_pair_dataframe(pair=inf_pair, timeframe=inf_timeframe)
            # obtain a dataframe with macd, signal, histogram on (BTC/USDT, 1w)

            macd = ta.MACD(informative)
            # replaces macd.histogram by boolean on its acclivity.
            macd['macdhist'] = (macd['macdhist'] > macd['macdhist'].shift(1))
            
            # inserts new column on informative dataframe
            informative['macd'] = macd['macdhist']

            # merges it with the function return value to cope with code structure.
            dataframe = dataframe.merge(informative[["date", "macd"]], on="date", how="left")

            # forward fills empty cells entries on merged columns with its previous value
            # because there is a mismatch between (BTC/USDT, 1w) and (stake_currency, timeframe).
            dataframe['macd'] = dataframe['macd'].ffill()

            return dataframe

    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (qtpylib.crossed_above(dataframe['close'], dataframe['bb_lowerband'])) &
                (dataframe['macd'] == True) &
                (dataframe['volume'] > 0)  # Make sure Volume is not 0
            ),
            'buy'] = 1
        return dataframe

    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (qtpylib.crossed_above(dataframe['close'], dataframe['bb_upperband'])) &
                (dataframe['volume'] > 0)  # Make sure Volume is not 0
            ),
            'sell'] = 1
        return dataframe
