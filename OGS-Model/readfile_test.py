from pandas import read_csv

def get_Tin(t):
    df_readfile = read_csv("readfile.txt", delimiter=";")
    time_list = df_readfile["time"].tolist()
    t = min(time_list, key=lambda x:abs(x-t))
    return float(df_readfile.Tin[df_readfile.time==t])

t = 60.01

print(get_Tin(t))

