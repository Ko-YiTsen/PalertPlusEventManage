current_directory = '/home/skai/obspy'
csv_dir = '/home/skai/obspy/csv'
sac_dir = '/home/skai/obspy/sac'
ins_d={ '4441':'ED002',
        '4397':'ED001',
        '4584':'ED003',
        '4365':'ED004',
        '4406':'ED005',
        '4650':'ED006',
        '4404':'ED007',
        '4551':'ED008',
        '4668':'ED009',
        '5021':'ED010',
        '5067':'ED011',
        '5050':'ED012',
        '5017':'ED013',
        '5032':'ED014',
        '5053':'ED015',
        '5040':'ED016',
        '5018':'ED017',
        '5080':'ED018',
        '5048':'ED019',
        '4573':'ED020'
}
import os
os.chdir(csv_dir)
os.getcwd()

import glob
subdir='20211114210515'
ascii_file_name = glob.glob(subdir+"/*.csv")
print(ascii_file_name)

import numpy as np
from obspy.core import UTCDateTime
from obspy.io.sac import SACTrace

# Read ascii files
for k,file_dat in enumerate(ascii_file_name):
    f = open(ascii_file_name[k])
    lines = f.read()
    f.close()
    
    file_head = ascii_file_name[k].split('.')[0]
    instru_code = str.rstrip(str.lstrip(lines.split('\n')[0].split(':')[1]))
    print('station_code: '+instru_code)
    print('diction number: '+ins_d[instru_code])
    station_code = ins_d[instru_code]
    file_head.split('_')[0]
#    file_head.split('_')[2]
    print(str.rstrip(str.lstrip(lines.split('\n')[0].split(':')[1])))
    
    station_start_time = lines.split('\n')[2]
    print(station_start_time[11:])
    sampling_rate = lines.split('\n')[4].split(':')[1]
    
    # Singal Process
    signal = lines.split('\n')[18:-1]
    dataset = []
    for i,x in enumerate(signal):
        time_step_array = []
        for j,y in enumerate(signal[i].split(',')):
            time_step_array.append(float(signal[i].split(',')[j]))
        dataset.append(time_step_array)
    dataset = np.array(dataset)
    signal_T = dataset[:,0]
    signal_Z = dataset[:,1]
    signal_N = dataset[:,2]
    signal_E = dataset[:,3]
    signal_Pd = dataset[:,4]
    signal_Displacement = dataset[:,5]
        
#        trace[0].stats.network = 'ED'
        
    Z_header = {'kstnm': station_code, 'kcmpnm': 'HLZ', 
                'delta': 1.0/int(sampling_rate),'nzyear': 2021, 'nzjday': 318, 'nzhour': 13, 'nzmin': 5, 'nzsec': 15, 'nzmsec': 0, 'knetwk':'ED','khole':'00'}

    sacfile_format = SACTrace(data=signal_Z, **Z_header)
    sacfile_format.write(sac_dir+"/"+file_head.split('_')[0]+'_'+station_code+'_'+'Z.SAC')
    print('save to: '+sac_dir+"/"+file_head.split('_')[0]+'_'+station_code+'_'+'Z.SAC')
    #=============================
    N_header = {'kstnm': station_code, 'kcmpnm': 'HLN', 
                'delta': 1.0/int(sampling_rate),'nzyear': 2021, 'nzjday': 318, 'nzhour': 13, 'nzmin': 5, 'nzsec': 15, 'nzmsec': 0, 'knetwk':'ED','khole':'00'}

    sacfile_format = SACTrace(data=signal_N, **N_header)
    sacfile_format.write(sac_dir+"/"+file_head.split('_')[0]+'_'+station_code+'_'+'N.SAC')
    print('save to: '+ sac_dir+"/"+file_head.split('_')[0]+'_'+station_code+'_'+'N.SAC')
    #=============================
    E_header = {'kstnm': station_code, 'kcmpnm': 'HLE', 
                'delta': 1.0/int(sampling_rate),'nzyear': 2021, 'nzjday': 318, 'nzhour': 13, 'nzmin': 5, 'nzsec': 15, 'nzmsec': 0, 'knetwk':'ED','khole':'00'}

    sacfile_format = SACTrace(data=signal_E, **E_header)
    sacfile_format.write(sac_dir+"/"+file_head.split('_')[0]+'_'+station_code+'_'+'E.SAC')
    print('save to: '+ sac_dir+"/"+file_head.split('_')[0]+'_'+station_code+'_'+'E.SAC')
    #=============================
    Pd_header = {'kstnm': station_code, 'kcmpnm': 'Pd', 
                'delta': 1.0/int(sampling_rate)}
    
    sacfile_format = SACTrace(data=signal_Pd, **Pd_header)
    sacfile_format.write(sac_dir+"/"+file_head.split('_')[0]+'_'+station_code+'_'+'_Pd.SAC')
    print('save to: '+ sac_dir+"/"+file_head.split('_')[0]+'_'+station_code+'_'+'_Pd.SAC')
    #=============================
    dis_header = {'kstnm': station_code, 'kcmpnm': 'dis', 
                'delta': 1.0/int(sampling_rate)}
    
    sacfile_format = SACTrace(data=signal_Displacement, **dis_header)
    sacfile_format.write(sac_dir+"/"+file_head.split('_')[0]+'_'+station_code+'_'+'_dis.SAC')
    print('save to: '+sac_dir+"/"+file_head.split('_')[0]+'_'+station_code+'_'+'_dis.SAC')
    print(sac_dir)
    print(file_head.split('_')[0])
#    print(file_head.split('_')[2])

# PLOT diagram
from obspy import read
import glob

a_f_Z = glob.glob(sac_dir+"/20211018134918"+"/20211018134918??_ED0??*Z.SAC")
a_f_Z.extend(glob.glob(sac_dir+"/20211018134918"+"/*ED00?_Z.SAC"))

a_f_N = glob.glob(sac_dir+"/20211018134918"+"/20211018134918??_ED0??*N.SAC")
a_f_N.extend(glob.glob(sac_dir+"/20211018134918"+"/*ED00?_N.SAC"))

a_f_E = glob.glob(sac_dir+"/20211018134918"+"/20211018134918??_ED0??*E.SAC")
a_f_E.extend(glob.glob(sac_dir+"/20211018134918"+"/*ED00?_E.SAC"))

print(sorted(a_f_Z, key = lambda s: s.split('_')[1]))

a_f_Z = sorted(a_f_Z, key = lambda s: s.split('_')[1]) # sort the stations by station code
a_f_N = sorted(a_f_N, key = lambda s: s.split('_')[1])
a_f_E = sorted(a_f_E, key = lambda s: s.split('_')[1])

st = []
for coor in [a_f_Z,a_f_N,a_f_E]:
    for i,x in enumerate(coor):
        print(x)
        if i == 0:
            st = read(coor[i])
        else:
            st += read(coor[i])
            #st[i].stats.starttime=UTCDateTime(station_start_time[11:])
    print(st)
    st.plot(automerge=False);
    
# PLOT diagram
from obspy import read
import glob

a_f = glob.glob(sac_dir+"/*.SAC")
print(a_f)
st = []
for i,x in enumerate(a_f):
    if i == 0:
        st = read(a_f[i])
    else:
        st += read(a_f[i])
print(st[0].stats.sac.kstnm)
st.plot();    
    