import os
from obspy import read
import numpy as np


def plot_waveform(filePath):

    waveform = read(filePath)
    # print(waveform[0].data.max())2924.0291
    waveform[0].data = waveform[0].data/2924.0291

    # os.getcwd()+'/'+filePath
    waveform.plot(color='b', outfile=filePath.replace('.mseed', '.png'))

def maxGal(filePath):
    waveform = read(filePath)
    return round(np.abs(waveform[0].data).max()/2924.0291,2)


# dirList = os.listdir('eqdata')
# for dir in dirList:
#     flist = os.listdir('eqdata/'+dir)
#     for file in flist:
#         if 'mseed' in file:
#             print('eqdata/'+dir+'/'+file)

#             plot_waveform('eqdata/'+dir+'/'+file)

#plot_waveform('eqdata/20210805055628/20210804215654_4441_Z.mseed')
