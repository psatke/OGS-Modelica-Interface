import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("T_out.txt", delimiter = ";")




plt.figure()
plt.plot(df['time'], df['T_out'], c='r',markersize=4, lw=1, label= 'BHE outflow temperature')

plt.grid(True, linestyle = "-.", linewidth = "1")

plt.xlim([100,100000])
plt.ylim([293,314])
plt.xscale('log')
plt.xticks([100, 1000, 10000, 100000])
plt.ylabel('Temperature [K]',fontsize=12)
plt.xlabel('Time [s]',fontsize=12)
plt.legend(loc='upper left',ncol =1)
plt.title('BHE outflow temperature',fontsize=12)
#plt.title('Timestep = 1, T_bottom_diff ={:.2f} K'.format(abs(x_temp[29,0] - x_temp[31,0])),fontsize=12)
plt.savefig('T_out.png', dpi = 310, transparent = False)