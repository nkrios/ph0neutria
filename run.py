#!/usr/bin/python
from util.ConfigUtils import getBaseConfig
from util.DnsBlUtils import getBLList
from util.FileUtils import getWildFile, isAcceptedUrl
from util.LogUtils import getModuleLogger
from util.Malc0de import getMalc0deList
from util.MalShare import getMalShareList
from util.OtxUtils import getOTXList
from util.PayloadUtils import getPLList
from util.VxVault import getVXList


import multiprocessing
import os
import threading


#       .__    _______                        __         .__       
#______ |  |__ \   _  \   ____   ____  __ ___/  |________|__|____  
#\____ \|  |  \/  /_\  \ /    \_/ __ \|  |  \   __\_  __ \  \__  \ 
#|  |_> >   Y  \  \_/   \   |  \  ___/|  |  /|  |  |  | \/  |/ __ \_
#|   __/|___|  /\_____  /___|  /\___  >____/ |__|  |__|  |__(____  /
#|__|        \/       \/     \/     \/                           \/
#
#                  ph0neutria malware crawler
#                            v0.9.0
#             https://github.com/phage-nz/ph0neutria


rootDir = os.path.dirname(os.path.realpath(__file__))
with open(os.path.join(rootDir, 'res', 'banner.txt'), 'r') as banner:
        print banner.read()


logging = getModuleLogger(__name__)
baseConfig = getBaseConfig(rootDir)


def main(): 
    if not os.path.exists(baseConfig.outputFolder):
        os.makedirs(baseConfig.outputFolder)

    if baseConfig.multiProcess.lower() == "yes":
        logging.info("Spawning multiple ph0neutria processes. Press CTRL+C to terminate.")
        webs = []
        malc0deWeb = multiprocessing.Process(target=startMalc0de)
        vxVaultWeb = multiprocessing.Process(target=startVXVault)
        osintWeb = multiprocessing.Process(target=startOSINT)
        webs.append(malc0deWeb)
        webs.append(vxVaultWeb)
        webs.append(osintWeb)
        malc0deWeb.start()
        vxVaultWeb.start()

        if baseConfig.disableMalShare.lower() == "no":
            malshareWeb = multiprocessing.Process(target=startMalShare)
            webs.append(malshareWeb)
            malshareWeb.start()

        osintWeb.start()

        try:
            for web in webs:
                web.join()
        except KeyboardInterrupt:
            logging.info("Mother spider received Ctrl+C. Killing babies.")
            for web in webs:
                web.terminate()
                web.join()
                
    else:
        logging.info("Spawning single ph0neutria process. Press CTRL+C to terminate.")
        startMalc0de()
        startVXVault()

        if baseConfig.disableMalShare.lower() == "no":
            startMalShare()

        startOSINT()


def startMalc0de():
    for mUrl in getMalc0deList():
        if isAcceptedUrl(mUrl):
            getWildFile(mUrl)


def startMalShare():
    for mUrl in getMalShareList():
        if isAcceptedUrl(mUrl):
            getWildFile(mUrl)


def startVXVault():
    for vUrl in getVXList():
        if isAcceptedUrl(vUrl):
            getWildFile(vUrl)


def startOSINT():
    url_list = []

    pl_list = getPLList()

    if len(pl_list) > 0 and baseConfig.multiProcess.lower() == "yes":
        pl_thread = threading.Thread(target=fetchOSINT, args=[pl_list])
        pl_thread.start()

    if len(pl_list) > 0 and baseConfig.multiProcess.lower() == "no":
        fetchOSINT(pl_list)

    otx_list = getOTXList()

    if len(otx_list) > 0 and baseConfig.multiProcess.lower() == "yes":
        otx_thread = threading.Thread(target=fetchOSINT, args=[otx_list])
        otx_thread.start()

    if len(otx_list) > 0 and baseConfig.multiProcess.lower() == "no":
        fetchOSINT(otx_list)

    bl_list = getBLList()

    if len(bl_list) > 0 and baseConfig.multiProcess.lower() == "yes":
        bl_thread = threading.Thread(target=fetchOSINT, args=[bl_list])
        bl_thread.start()

    if len(bl_list) > 0 and baseConfig.multiProcess.lower() == "no":
        fetchOSINT(bl_list)


def fetchOSINT(url_list):
    for oUrl in url_list:
        if isAcceptedUrl(oUrl):
            getWildFile(oUrl)


if __name__ == "__main__":
    main()
