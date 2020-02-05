# -*- coding: utf-8 -*-
"""
Created on Sat Nov 16 09:35:12 2019

@author: micah
"""

def minute_passed(oldepoch):
    import time
    return time.time() - oldepoch >= 60

def dlquotes(my_watchlist):
    # Collect preferences and credentials
    import rhutils.preferences as preferences
    email = preferences.rh_email
    password = preferences.rh_password
    filePath = preferences.my_filePath
    avKey = preferences.av_key
    from datetime import datetime
    import sys
    import requests
    import robin_stocks as r
    import time
    from alpha_vantage.timeseries import TimeSeries
    ts = TimeSeries(key=avKey, output_format='pandas', indexing_type='date')
    start_time = datetime.now()
    processed_count = 0
    failed_symbols = []
    
    try:
        login = r.login(email,password)
        watchlist = r.get_watchlist_by_name(name=my_watchlist, info=None)
        watchlistDict = {}
        for item in watchlist:
            url = item['instrument']
            r = requests.get(url)
            data_json = r.json()
            #print(str(data_json))  # print this to see more available symbol info.
            watchlistDict[data_json['symbol']] = data_json['simple_name']
    except Exception as e:
        sys.exit(e)
    
    oldepoch = time.time()
    print("Total number of symbols to update: ",len(watchlistDict))
    print("")
    total_symbols = len(watchlistDict)
    symbols_remaining = total_symbols
    processed_count_continuous = 0
    for _symbol, name in watchlistDict.items():
        try:      
            rate_limit_begin_time = time.time()
            processed_count = processed_count+1     
            processed_count_continuous = processed_count_continuous+1
            print(_symbol,": ",name)
            data, meta = ts.get_daily(_symbol,outputsize='full')
            fileName = _symbol + ".csv" 
            fh = open(filePath + fileName, "w") 
            fh.write( data.to_csv() )  
            fh.close() 
            symbols_remaining = symbols_remaining-1
            # Adjustments for AlphaVantage's Rate Limit, 5 symbols per minute
            if minute_passed(oldepoch) or processed_count==5:
                rate_limit_end_time = time.time()
                time_passed = rate_limit_end_time - rate_limit_begin_time
                pause_time = 60 - time_passed
                processed_count=0
                print("*** Pausing for ",pause_time," seconds.")
                print("*** ",symbols_remaining," symbols remain.")
                time_passed = datetime.now() - start_time
                print("*** This download has been running for ",time_passed)
                download_rate = time_passed / processed_count_continuous     
                estimated_time_remaining = symbols_remaining * download_rate
                print("*** Estimated time remaining: ",estimated_time_remaining)
                est_end_time = datetime.now() + estimated_time_remaining
                print("*** Estimated end time: ",est_end_time)
                print("")
                time.sleep(pause_time)
                oldepoch = time.time()                
        except Exception as e:        
            print("Error on "+_symbol+": ",e)
            failed_symbols.append(_symbol)
    
    if len(failed_symbols) > 0:        
        print("Initial download complete. Pausing 1 minute before downloading ", len(failed_symbols) ," failed symbols.")           
        print("Failed symbols: "+str(failed_symbols))
        print("Please wait 1 minute ...")
        time.sleep(60)
        print("Now downloading failed symbols ...")
        name="Failed Symbol"
        symbols_remaining = len(failed_symbols) 
        for _symbol in failed_symbols:
            try:      
                rate_limit_begin_time = time.time()
                processed_count = processed_count+1     
                processed_count_continuous = processed_count_continuous+1
                print(_symbol,": ",name)
                data, meta = ts.get_daily(_symbol,outputsize='full')
                fileName = _symbol + ".csv" 
                fh = open(filePath + fileName, "w") 
                fh.write( data.to_csv() )  
                fh.close() 
                symbols_remaining = symbols_remaining-1
                # Adjustments for AlphaVantage's Rate Limit, 5 symbols per minute
                if minute_passed(oldepoch) or processed_count==5:
                    rate_limit_end_time = time.time()
                    time_passed = rate_limit_end_time - rate_limit_begin_time
                    pause_time = 60 - time_passed
                    processed_count=0
                    print("*** Pausing for ",pause_time," seconds.")
                    print("*** ",symbols_remaining," symbols remain.")
                    time_passed = datetime.now() - start_time
                    print("*** This download has been running for ",time_passed)
                    download_rate = time_passed / processed_count_continuous     
                    estimated_time_remaining = symbols_remaining * download_rate
                    print("*** Estimated time remaining: ",estimated_time_remaining)
                    est_end_time = datetime.now() + estimated_time_remaining
                    print("*** Estimated end time: ",est_end_time)
                    time.sleep(pause_time)
                    oldepoch = time.time()                
            except Exception as e: 
                print("***************************")
                print("Error on "+_symbol+": ",e)
                print(_symbol," quotes will not be downloaded on this run. Please try again.")
                print("***************************")
        
    else:             
        end_time = datetime.now()
        print("**************************")
        print("")
        print("There were no failed symbols.")
        print("Time Elapsed: "+ str(end_time - start_time) )
        print("Completed at ",end_time)