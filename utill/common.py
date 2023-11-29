import pandas as pd
import numpy as np

class BasicStat():
    
    def calc_stats(self, precos):
        """
            Calcula oo retorno, volatilidade, risco e covariancia entre os ativo(s)
             
            params:
            - precos: dataframe com todo o historico de precos da carteira
             
            vars:
            - retornos: retorno atual
            - rotulo: nome dos ativos
            - e_r: media dos retornos
            - vol: volatilidade dos retornos
            - mat_cov: matriz de covariancia dos ativos
             
            return:
            - retornos, rotulo, e_r, vol, mat_cov
        """
        
        retornos = precos.pct_change().fillna(0)
        rotulo= retornos.columns.to_list()
        e_r=retornos.mean().replace([np.inf, -np.inf], 0.000)
        vol=retornos.std().fillna(0)
        mat_cov=retornos.cov().fillna(0)
        return retornos, rotulo, e_r, vol, mat_cov
    
    def generate_portfolios(self, n_ativos, e_r, mat_cov):
        """
            Simulador qur gera 100K portifoilios de acordo com suas classes 
            individuais e coletivas com sua carteira.
            A complexidade de tempo envove 1mil por 1 segundo.
            
            params:
             - n_ativos: quantidade de classes (padrao 11)
             - e_r: media do retorno da carteira em relacao ao periodo historico fornecido
             - mat_cov: matriz de covariancia das classes
            
            return:
             - p_ret: retorno da carteira estimado de acordo com o historico fornecido
             - p_vol: risco da carteia estimado de acordo com o historico fornecido
             - p_pesos: pesos das classes estimado de acordo com o historico fornecido
        """
        
        p_ret = []
        p_vol = []
        p_pesos = []

        for x in range(60000):
            pesos = np.random.random(n_ativos)
            pesos = pesos / np.sum(pesos)
            p_pesos.append(pesos)

            returns = np.dot(pesos, e_r)
            p_ret.append(returns)

            var = mat_cov.mul(pesos, axis=0).mul(pesos, axis=1).sum().sum()
            dp = np.sqrt(var)
            p_vol.append(dp)

        p_ret = np.array(p_ret)
        p_vol = np.array(p_vol)
        p_pesos = np.array(p_pesos)

        return p_ret, p_vol, p_pesos

    def generate_position(self, pesos, e_r, mat_cov):
        """
            Gera a posicao inicial e uma estimada posicao para todas as classes estimando
            seu respectivo retorno e risco da carteira
            
            params:
             - n_ativos: quantidade de classes (padrao 11)
             - e_r: media do retorno da carteira em relacao ao periodo historico fornecido
             - mat_cov: matriz de covariancia das classes
        """
        
        p_ret = []
        p_vol = []
        
        retorns = np.dot(pesos, e_r)
        p_ret.append(retorns)

        var = mat_cov.mul(pesos, axis=0).mul(pesos, axis=1).sum().sum()
        dp = np.sqrt(var)
        p_vol.append(dp)
        
        p_ret = np.array(p_ret)
        p_vol = np.array(p_vol)
        return p_ret, p_vol