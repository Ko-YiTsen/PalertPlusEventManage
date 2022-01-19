import os
import shutil

path = os.getcwd()
dirs = os.listdir('eqdata')
for dir in dirs:
    filepath = path + '/eqdata/' +dir
    files = os.listdir(filepath)
    for file in files:
      if '.csv' in file:
        os.remove(os.path.join(filepath, file))
     #pastfile = 'eqdata/'+dir + '/mseed/'
     #nowdir = 'eqdata/'+ dir + '/allFile/'
     #files = os.listdir(pastfile)
     #for file in files:
          #if '.mseed' in file:
               #shutil.move(f'{pastfile}/{file}',nowdir)
     # os.makedirs(path+'/eqdata/'+dir+'/mseed', exist_ok=True)
     # os.makedirs(path+'/eqdata/'+dir+'/csv', exist_ok=True)
     # os.makedirs(path+'/eqdata/'+dir+'/sac', exist_ok=True)