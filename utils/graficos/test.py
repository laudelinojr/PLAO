import pandas as pd

#collet data
df = pd.read_csv("coleta/openstack1_10.159.205.6_history.txt")
df2 = = pd.read_csv("coleta/openstack2_10.159.205.12_history.txt")

print(df)
#check type in file
#df.info()

#print(df.index)
#print(df.columns)
#print(df.values)