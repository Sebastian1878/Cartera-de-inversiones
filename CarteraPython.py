# 1 - Importación de librerías necesarias

import pandas as pd
import numpy as np
from pandas_datareader import data as wb
import matplotlib.pyplot as plt
import scipy.optimize as optimize

assets = ['V','HD','JD']        

data = pd.DataFrame()
for t in assets:
    data[t] = wb.DataReader(t, data_source='yahoo', start='2015-1-1')['Adj Close']

log_returns = np.log(1+data.pct_change())

port_returns = []
port_vols = []

#Ciclo Retornos 
for i in range (1000):
    num_assets = len(assets)
    weights = np.random.random(num_assets)
    weights /= np.sum(weights) 
    port_ret = np.sum(log_returns.mean() * weights) * 252
    port_var = np.sqrt(np.dot(weights.T, np.dot(log_returns.cov()*252, weights)))       
    port_returns.append(port_ret)
    port_vols.append(port_var)

#Funciones portafolio
def portfolio_stats(weights, log_returns):
    port_ret = np.sum(log_returns.mean() * weights) * 252
    port_var = np.sqrt(np.dot(weights.T, np.dot(log_returns.cov() * 252, weights)))
    sharpe = port_ret/port_var    
    return {'Return': port_ret, 'Volatility': port_var, 'Sharpe': sharpe}

def minimize_sharpe(weights, log_returns): 
    return -portfolio_stats(weights, log_returns)['Sharpe'] 

port_returns = np.array(port_returns)
port_vols = np.array(port_vols)
sharpe = port_returns/port_vols

max_sr_vol = port_vols[sharpe.argmax()]
max_sr_ret = port_returns[sharpe.argmax()]

constraints = ({'type' : 'eq', 'fun': lambda x: np.sum(x) -1})
bounds = tuple((0,1) for x in range(num_assets))
initializer = num_assets * [1./num_assets,]

optimal_sharpe = optimize.minimize(minimize_sharpe, initializer, method = 'SLSQP', args = (log_returns,) ,bounds = bounds, constraints = constraints)
optimal_sharpe_weights = optimal_sharpe['x'].round(4)
optimal_stats = portfolio_stats(optimal_sharpe_weights, log_returns)


#Salida De Datos
print("Pesos óptimos de la cartera: ", list(zip(assets, list(optimal_sharpe_weights*100))))
print("Retorno óptimo de la cartera: ", round(optimal_stats['Return']*100,4))
print("Volatilidad óptima de la cartera: ", round(optimal_stats['Volatility']*100,4))
print("Ratio Sharpe óptimo de la cartera: ", round(optimal_stats['Sharpe'],4))

plt.figure(figsize = (12,6))
plt.scatter(port_vols,port_returns,c = (port_returns/port_vols))
plt.scatter(max_sr_vol, max_sr_ret,c='red', s=30)
plt.colorbar(label = 'Ratio Sharpe (rf=0)')
plt.xlabel('Volatilidad de la cartera')
plt.ylabel('Retorno de la cartera')
plt.show()
