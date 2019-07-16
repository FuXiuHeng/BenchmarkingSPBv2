#!/usr/bin/python
import threading

from settings.settings import settings
from overlay_nodes import miner_ctp, miner_erc, poller

miner_ctp_thread = threading.Thread(target=miner_ctp.run, args=(settings,))
miner_erc_thread = threading.Thread(target=miner_erc.run, args=(settings,))
poller_thread = threading.Thread(target=poller.run, args=(settings,))

miner_ctp_thread.start()
miner_erc_thread.start()
poller_thread.start()

miner_ctp_thread.join()
miner_erc_thread.join()
poller_thread.join()

print('End')