
from pandas import DataFrame
from numpy import sqrt,array,exp,log,amin,amax,pi,arctan,tan


def bollinger_bands(df, window=20, numsd=2):

    dg = df.copy()
#    dg.sort_index(ascending=False,inplace=True)
    dg = DataFrame(dg)
    ave = dg.rolling(window=window,center=False).mean()
    sd = dg.rolling(window=window,center=False).std()
    upband = ave + (sd*numsd)
    dnband = ave - (sd*numsd)

    dg['Rolling Mean'] = ave#round(ave,3)
    dg['Upper Band'] = upband#round(upband,3)
    dg['Lower Band'] = dnband#round(dnband,3)

    return dg[['Rolling Mean','Upper Band','Lower Band']]



def relative_strength_index(series, period=7):
    delta = series.diff().dropna()
    u,d = delta.copy(),delta.copy()

    u[u < 0] = 0
    d[d > 0] = 0
    d = d.abs()
 # rolup = u.rolling(window=period, center=False).mean()
 # roldn = d.rolling(window=period, center=False).mean()

    rolup = u.ewm(com=period-1,adjust=False).mean()
    roldn = d.ewm(com=period-1,adjust=False).mean()


    return 100*(rolup/(rolup+roldn))


def stochastic_oscillator(df,k=14,d=3):
    dg = DataFrame(df)
    dh = dg.rolling(window=k).min()
    di = dg.rolling(window=k).max()
    dg  = 100*(dg - dh)/(di-dh)	
    return dg.rolling(window=d,center=False).mean()
