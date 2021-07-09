import requests as req


def read_meta(path): #permet de lire correctement le fichier des metadonnées
    data=open(path,'r').readlines()[1:]
    name=[]
    instruments=[]
    type=[]
    for i in data:
        tmp=i.split('\t')
        name.append(tmp[0])
        instruments.append(tmp[1])
        type.append(tmp[2])
    return name,instruments,type

def write(object,path): #permet d'ecrire dans un document
    f=open(path,'w')
    f.write(object)
    f.close()

def filter():
    for i in range(len(name)):
        if 'II' in type[i] or 'Ia' in type[i] or '?' in type[i] or 'GRB' in type[i] or 'UVOT' in instruments[i]:
            continue
        elif 'MJD' not in req.get(f'https://api.astrocats.space/{name[i]}/photometry/u_time').text:
            continue
        else:
            definitivname.append(name[i])

type=['Ib','Ic']
definitivname=[]
for t in type:
    metadata_request=req.get(f'https://api.astrocats.space/catalog/instruments+claimedtype+ebv?ebv&claimedtype={t}&instruments=v&format=tsv').text
    write(metadata_request,'C:\\Users\\cleme\\Desktop\\APC_2021\\tmp\\meta_tmp.txt')
    name,instruments,type=read_meta(dir+'meta_tmp.txt')
    filter()

inputdata=''
for i in definitivname:
    inputdata=inputdata+str(i)+'\n'
write(inputdata,'C:\\Users\\cleme\\Desktop\\APC_2021\\tmp\\'+'SN1bc.txt')