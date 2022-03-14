# Atharv Kolhar (atharv)

import logging
import warnings

warnings.filterwarnings("ignore")

jamalogger = logging.getLogger("JAMALIB")
jamalogger.setLevel(logging.DEBUG)

handle = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                              "%Y-%m-%d %H:%M:%S")
handle.setFormatter(formatter)
handle.setLevel(logging.INFO)
jamalogger.addHandler(handle)

log_handle = logging.FileHandler("../JamaAutomation_log.txt")
log_handle.setFormatter(formatter)
log_handle.setLevel(logging.DEBUG)
jamalogger.addHandler(log_handle)
