## Import libraries
import numpy as np
import matplotlib.pyplot as plt
import scipy
from scipy.stats import rv_discrete,ks_2samp

maxabs=np.loadtxt(dirtmp+bandstr+'_maxabs.txt')
min=int(round(np.min(maxabs),0))
max=int(round(np.max(maxabs),0)+1)
delta=max-min
bins=np.linspace(min,max,delta+1)

probalist,binlist,c=plt.hist(maxabs,bins=bins,density=True,histtype='step')
mag_distrib=rv_discrete(name='cstm1',values=(binlist[:-1],probalist))
test_distrib=mag_distrib.rvs(size=1000)

test_probalist,test_binlist,test_c=plt.hist(test_distrib,bins=bins,density=True,histtype='step')
plt.xlabel('magnitudes absolues')
plt.ylabel('proportion')
plt.title('distribution des magnitudes absolues aux pics de luminosité des SN1 b/c')
plt.show()
KS_test=ks_2samp(probalist,test_probalist)

