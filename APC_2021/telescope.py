

dirtmp='C:\\Users\\cleme\\Desktop\\APC_2021\\tmp\\' #chemin du directory des fichiers temporaires
dirdata='C:\\Users\\cleme\\Desktop\\APC_2021\\data\\'
dirconfig='C:\\Users\\cleme\\Desktop\\APC_2021\\config\\'
dir='C:\\Users\\cleme\\Desktop\\APC_2021\\'

telescope_file=open(dirconfig+'telescopes.txt')
telescope_list=telescope_file.read().split('\n')
telescope_file.close()

class telescope:

    def __init__(self,name):
        self.Name=name
        config_file=open(dirconfig+name+'.config','r')
        telescope_data=config_file.read().split('\n')
        config_file.close()
        self.Filter=[i for i in telescope_data if 'filt' in i][0].split(' ')[1]
        self.Magnitude=float([i for i in telescope_data if 'magnitude' in i][0].split(' ')[1])
        self.Exposuretime=float([i for i in telescope_data if 'exposuretime' in i][0].split(' ')[1])
        self.Latitude=float([i for i in telescope_data if 'latitude' in i][0].split(' ')[1])
        self.Longitude=float([i for i in telescope_data if 'longitude' in i][0].split(' ')[1])
        self.Elevation=float([i for i in telescope_data if 'elevation' in i][0].split(' ')[1])

def can_detect(mag,filter):
    telescope_OK=[]
    for tel in telescope_list:
        if (globals()[f'{tel}'].Magnitude>mag) and (filter.upper() in globals()[f'{tel}'].Filter.upper()):
            telescope_OK.append(tel)
        else:
            print(tel)
    return telescope_OK

for tel in telescope_list:
    globals()[f'{tel}']=telescope(tel)
    print(tel)
    print(globals()[f'{tel}'].Filter)
