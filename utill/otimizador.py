import numpy as np
import math
from scipy.optimize import minimize

class OtimoModel():
    def optimize_portfolio(self, e_r, mat_cov, n_ativos):
        """
            Cria a carteira otimizada escolhendo as posições que mantem ou supera em retorno e miniminiza o risco da carteira toda.
            
            pars:
                - e_r: media dos retornos
                - mat_cov: matriz de covariancia da carteira
                - n_ativos: # de ativos da carteira
            
            vars:
                - tpl2: máximo disponivel para ser alocado
                - restri: é do tipo igualdade que informa que a volatilidade deve ter como valor maximo 1
                - bnds: limites para cada ativo
                - pesos_i: pesos iguais para todos começarem
        """
            
        rf = ((0.8 + 1)**(1/252))-1 #Calcular taxa livre de risco

        def port_vol(pesos): #Função de cálculo de risco
            return math.sqrt(np.dot(pesos,np.dot(mat_cov, pesos)))
        
        def port_ret(pesos): #Função de cálculo de retorno
            return np.sum(e_r*pesos)
        
        # Estimar carteira de Sharpe Ratio máximo
        def min_func_sharpe(pesos):
            """
                Medida de performance que procura por segurança or uma carteira livre de risco.
                (retorno_esperado[portifolio] - free-risk[selic] / std[portifolio])
            """
            return -(port_ret(pesos)-rf) / port_vol(pesos)
        
        tpl2 = 1 - 0.01
        restri = [{'type': 'eq', 'fun': lambda x: np.sum(x) - 1}]
        bnds = tuple((0.01, tpl2) for _ in range(n_ativos))
        pesos_i = np.array(n_ativos * [1 / n_ativos])

        # Otimização do Sharpe
        otim_sharpe = minimize(min_func_sharpe, pesos_i, method='SLSQP', bounds=bnds, constraints=restri)
        peso_otimo = otim_sharpe['x']
        ret_otimo = port_ret(otim_sharpe['x'])
        vol_otimo = port_vol(otim_sharpe['x'])
        return peso_otimo, ret_otimo, vol_otimo

    def optimize_portfolio_min(self, e_r, mat_cov, n_ativos):
        """
            Cria a carteira otimizada escolhendo as posições que mantem ou supera em retorno e miniminiza o risco da carteira toda.
            O ponto de otimização sempre é igual, devido a base ser mutável em fator diário.
                
            pars:
            - e_r: media dos retornos
            - mat_cov: matriz de covariancia da carteira
            - n_ativos: # de ativos da carteira
            
            vars:
            - tpl2: máximo disponivel para ser alocado
            - restri: é do tipo igualdade que informa que a volatilidade deve ter como valor maximo 1
            - bnds: limites para cada ativo
            - pesos_i: pesos iguais para todos começarem
        """
            
        def port_vol(pesos): #Função de cálculo de risco
            return math.sqrt(np.dot(pesos,np.dot(mat_cov, pesos)))
        
        def port_ret(pesos): #Função de cálculo de retorno
            return np.sum(e_r*pesos)
        
        tpl2 = 1 - 0.01
        restri = [{'type': 'eq', 'fun': lambda x: np.sum(x) - 1}]
        bnds = tuple((0.01, tpl2) for _ in range(n_ativos))
        pesos_i = np.array(n_ativos * [1 / n_ativos])

        otim_menor_vol = minimize(port_vol, pesos_i, method='SLSQP', bounds=bnds, constraints=restri)
        peso_otimo = otim_menor_vol['x']
        ret_otimo = port_ret(otim_menor_vol['x'])
        vol_otimo = port_vol(otim_menor_vol['x'])
        return peso_otimo, ret_otimo, vol_otimo
