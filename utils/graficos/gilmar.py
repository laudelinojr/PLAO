import matplotlib
matplotlib.__version__

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt

colunas = ['data','cloud','IP','%CPU','MEMORY','NVM','%VCPU','MEMORYC','DISKC']
df = pd.read_csv('coleta/openstack1_10.159.205.6_history.txt')
df.columns = colunas
# print(df.head())
# print(df['%VCPU'])
# df = df.set_index('data')
# print(df.head())

df1 = pd.read_csv('coleta/openstack2_10.159.205.12_history.txt')
df1.columns = colunas
# df1 = df1.set_index('data')
result = pd.merge(df, df1, on="data", how="outer", indicator="indicator_column")
print(result)


t = np.arange(-1, 2, .01)
s = np.sin(2 * np.pi * t)

fig, ax = plt.subplots()

ax.plot(df.index, df['%CPU'], color='r')
ax.plot(df1.index, df1['%CPU'], color='k')