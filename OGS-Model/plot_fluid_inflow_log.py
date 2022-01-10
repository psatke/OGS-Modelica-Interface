import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("T_in.txt", delimiter = ";")




plt.figure()
plt.plot(df['time']/60, df['T_in'], c='r',markersize=4, lw=1, label= 'BHE inflow temperature')

plt.grid(True, linestyle = "-.", linewidth = "1")

plt.xlim([1,10000])
plt.ylim([293,314])
plt.xscale('log')
plt.xticks([1, 10, 100, 1000, 10000])
plt.ylabel('Temperature [K]',fontsize=12)
plt.xlabel('Time [min]',fontsize=12)
plt.legend(loc='best',ncol =1)
plt.title('BHE inflow temperature',fontsize=12)
#plt.title('Timestep = 1, T_bottom_diff ={:.2f} K'.format(abs(x_temp[29,0] - x_temp[31,0])),fontsize=12)
plt.savefig('T_in.png', dpi = 310, transparent = False)