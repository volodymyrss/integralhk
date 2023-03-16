import re
import glob
import time
import logging

import numpy as np
from astropy.time import Time

from . import spiacs_config, integral


logger = logging.getLogger(__name__)

# TODO: store time lags regularly

def get_realtime_data(ijd, window):
    logger.info("requested logger for ijd=%s window=%s", ijd, window)
    
    realtime_dump_root = spiacs_config.isdc_env['isdc_rt']    

    logger.info("realtime_dump_root=%s", realtime_dump_root)

    scw = integral.ijd2scw(ijd, rbp=spiacs_config.isdc_env['isdc_nrt'])
    current_rev = int(scw[:4])

    logger.info("current_rev=%s", current_rev)

    now_ijd = Time.now().mjd - 51544 + 69.20/24/3600
    t0_ijd = ijd
    window = float(window)

    logger.info("now_ijd=%s", now_ijd)

    for rt_fn in reversed(sorted(glob.glob(realtime_dump_root+"/lcdump-revol-*.csv"))): 
        logger.info("trying rt_fn=%s", rt_fn)
        filerev = int(re.search(r"lcdump-revol-(\d{4}).*.csv", rt_fn).groups()[0])
        logger.info("filerev=%s", filerev)

        if filerev > current_rev + 1:
            logger.info("this is in the future, skipping rt_fn=%s", rt_fn)
            continue        

        rt_lc = np.genfromtxt(rt_fn)
        logger.info("filerev=%s", filerev)

        lc = rt_lc[:,(3,0,2,0)]
        lc[:,1] = 0.05
        
        first_data = lc[:,0][0]
        last_data = lc[:,0][-1]

        logger.info("loaded %s entries %s - %s", lc.shape, first_data, last_data)

        data_ahead_of_request_center_seconds = (last_data-t0_ijd)*24*3600
        data_ahead_of_request_end_seconds = data_ahead_of_request_center_seconds - window
        data_behind_of_now_seconds = (now_ijd-last_data)*24*3600

        logger.info(f"now {now_ijd} "
                    f"first data in file {first_data} " 
                    f"last data {last_data} " 
                    f"requested {t0_ijd} "
                    f"data ahead of request center {data_ahead_of_request_center_seconds} s "
                    f"end {data_ahead_of_request_end_seconds} s "
                    f"data behind current moment by {data_behind_of_now_seconds} s "
                    f"window {window}")


        if t0_ijd<first_data:
            logger.info("data in the previous file")
            continue
            

        if data_ahead_of_request_end_seconds > window*1.5 + 100:                            
            logger.info("this margin is sufficient")
            return lc, ""
        else:
            logger.info("this margin is NOT sufficient")

            return "", None
    
    logger.info("no data found for the requested time")
    return "", None
        