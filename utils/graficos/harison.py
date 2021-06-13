colunas = ['data','cloud','IP','%CPU','MEMORY','NVM','%VCPU','MEMORYC','DISKC']

!git clone 'https://github.com/laudelinojr/PLAO.git' 

df = pd.read_csv('/content/PLAO/coleta/openstack1_10.159.205.6_history.txt')

# df = pd.read('https://github.com/laudelinojr/PLAO/blob/main/coleta/openstack1_10.159.205.6_history.txt')
df.columns = colunas
# print(df.head())
# print(df['%VCPU'])
# df = df.set_index('data')
# print(df.head())

df1 = pd.read_csv('/content/PLAO/coleta/openstack2_10.159.205.12_history.txt')
df1.columns = colunas
# df1 = df1.set_index('data')



# cpu1 = df['%CPU']
# cpu2 = df1['%CPU']


# date =  df['data']
# date_hours = []
# for item in date:
#   hours = item.split('-') 
#   date_hours.append(hours[1])

hrs_sorted = sorted(hrs)

hrs_coleta = []
hrs_coleta.append(hrs_sorted[0])

for i in range(len(hrs_sorted)):
  if i % 10 == 0:
    hrs_coleta.append(hrs_sorted[i]) 


x1 = np.linspace(0, 2000.0, num = 214)
x2 = np.linspace(0, 2000.0, num= 214)



y1 = cpu1
y2 = cpu2


fig, (ax1,ax2) = plt.subplots(2, 1)
fig.suptitle('A tale of 2 subplots')

ax1.plot(x1, y1, 'o-')
ax1.set_ylabel('Damped oscillation')

ax2.plot(x2, y2, '.-')
ax2.set_xlabel('time (s)')
ax2.set_ylabel('Undamped')

plt.subplots_adjust(hspace= 0)


plt.show()


# cpu = df['%CPU']

# t = np.arange(0,136,1)
# s = np.sin(2 * np.pi * t)

# plt.plot(t,cpu)



# fig, (ax1, ax2) = plt.subplots(2, 1)

# ax1.set_axis_off()
# ax2.set_axis_off()
# ax3.set_axis_off()

# ax1.plot(df.index, df['%CPU'], color='r')
# ax2.plot(df1.index, df1['%CPU'], color='b')
# ax.plot(t, s)
# # Thick red horizontal line at y=0 that spans the xrange.
# ax.axhline(linewidth=8, color='#d62728')
# # Horizontal line at y=1 that spans the xrange.
# ax.axhline(y=1)
# # Vertical line at x=1 that spans the yrange.
# ax.axvline(x=1)
# # Thick blue vertical line at x=0 that spans the upper quadrant of the yrange.
# ax.axvline(x=0, ymin=0.75, linewidth=8, color='#1f77b4')
# # Default hline at y=.5 that spans the middle half of the axes.
# ax1.axhline(y=80, xmin=0.25, xmax=0.75)
# # Infinite black line going through (0, 0) to (1, 1).
# ax.axline((0, 0), (1, 1), color='k')
# # 50%-gray rectangle spanning the axes' width from y=0.25 to y=0.75.
# ax2.axhspan(40, 60, facecolor='0.5')
# # Green rectangle spanning the axes' height from x=1.25 to x=1.55.
# ax1.axvspan(60, 80, facecolor='#2ca02c')
# ax1.annotate("Texto", xy=(80, 100))

# plt.show()
# fig.canvas.get_supported_filetypes()