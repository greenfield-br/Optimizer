#!/bin/sh
freqtrade download-data -c ./config.inf.json --pairs BTC/USDT -t 1w --days 100 && freqtrade download-data -t 15m 30m 1h 2h 4h 1d --days 100
