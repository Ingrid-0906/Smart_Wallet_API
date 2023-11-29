import pandas as pd
import numpy as np
from utill.otimizador import OtimoModel
from utill.data import ProcessData
from utill.analise import AnaliseCarteira
from utill.common import BasicStat

class CarteiraStats():
    def __init__(self, path_data):
        """
            Nota.
            'tipo_investimento_para_coluna' precisa ser alterado para que possa ser lido com uma classe real nos dados da Wealth.
            Atualmente usando os dados da MB.
        """
        self.DF_CARTEIRA = ProcessData().getCliente(path_data)
        self.PERSONAS = ProcessData().getIPS()
        self.tipo_investimento_para_coluna = {
            'Aluguel': 'Aluguel', 
            'Ações': 'Ações', 
            'COE': 'COE', 
            'Derivativos de Balção': 'Derivativos de Balção',
            'Fundos Imobiliarios' : 'Fundos Imobiliarios', 
            'Fundos de Investimento': 'Fundos de Investimento',
            'NPS': 'NPS',
            'Previdencia Privada': 'Previdencia Privada', 
            'Produtos Estruturados': 'Produtos Estruturados',
            'Renda Fixa': 'Renda Fixa',
            'Tesouro Direto':'Tesouro Direto'
        }

    def statsWallet(self):
        """
            Método que retorna um resumo da atual situaçao da carteira do cliente.
            
            return:
            - id: id do cliente que pode ser xp_code ou qualquer outro indentificador unico 
            - perfil: perfil do cliente,
            - pesos_hj: proporção atual das classes na carteira
            - retorno_hj: média do retorno acumulado do periodo historico analisado
            - risco_hj: valor do risco atual calculado dentro do periodo historico analisado
            - faixa_hj: atual proporçao dos defits e superavits calculados da carteira
            - pp_saude: valor final em porcentagem do nivel de debilidade da carteira frente ao perfil no IPS
            - status_saude: categoria de debilidade entre 'aceitavel', 'razoavel', 'debilitado'
            - ordem_ips: dicionario com os defits normalizados em reais vs capital necessario e a fonte para ser realocado
        """
        stats_hoje = {
            'id': np.nan,
            'perfil': np.nan,
            'retorno_hj': np.nan,
            'risco_hj': np.nan,
            'pesos_hj': [],
            'pp_saude': np.nan,
            'status_saude': np.nan,
            'faixa_hj': [],
            'ordem_ips':[]
        }
        
        # Salvando id e perfil
        stats_hoje['id'] = self.DF_CARTEIRA['id']
        stats_hoje['perfil'] = self.DF_CARTEIRA['perfil']
        
        # Gerando pesos
        DATA_PP = pd.DataFrame(self.DF_CARTEIRA['hoje'])
        for tipo_investimento, coluna in self.tipo_investimento_para_coluna.items():
            DATA_PP[coluna] = DATA_PP.apply(
                lambda row: AnaliseCarteira().porcento_classe(row, tipo_investimento),
                axis=1
            )
        pesos_hj = round(DATA_PP*100, 2)
        stats_hoje['pesos_hj'].append(pesos_hj.to_dict(orient='records')[0])
        
        # Salvando faixas da carteira vs. IPS faixas
        DATA_PP.insert(1, 'perfil', self.DF_CARTEIRA['perfil'].lower())
        DATA_BR = DATA_PP.copy()
        for tipo_investimento, coluna in self.tipo_investimento_para_coluna.items():
            DATA_BR[coluna] = DATA_BR.apply(
                lambda row: AnaliseCarteira().bandeira_classe(row, self.PERSONAS, tipo_investimento),
                axis=1)
        
        # Gerando saúde IPS e status // remover pl e perfil
        saude_hj = DATA_BR.iloc[:, 2:].apply(AnaliseCarteira().saude_investimentos, axis=1)

        faixa_hj = round(DATA_BR.iloc[:, 2:], 2)
        stats_hoje['faixa_hj'].append(faixa_hj.to_dict(orient='records')[0])
        stats_hoje['pp_saude'] = int(saude_hj.apply(lambda x: x[0]).values[0]*100)
        stats_hoje['status_saude'] = saude_hj.apply(lambda x: x[1]).values[0]

        #Salvando retorno e risco
        DATA_HY = self.DF_CARTEIRA['historico'][0]
        _, _, e_r, _, mat_cov = BasicStat().calc_stats(DATA_HY)
        
        weight = DATA_PP.iloc[:, 2:]
        
        i_ret, i_vol = BasicStat().generate_position(pesos=weight.values[0], e_r=e_r, mat_cov=mat_cov)
        
        stats_hoje['retorno_hj'] = round(i_ret[0]*100, 2)
        stats_hoje['risco_hj'] = round(i_vol[0]*100, 2)
        
        # Ordenar segundo o IPS // observando as faixas de pesos
        DATA_REAL = DATA_BR.copy()
        DATA_REAL.drop('perfil', axis=1, inplace=True)
        
        for tipo_investimento, coluna in self.tipo_investimento_para_coluna.items():
            DATA_REAL[coluna] = DATA_REAL.apply(lambda row: AnaliseCarteira().reais_classe(row, tipo_investimento),axis=1)
        
        DATA_REAL.drop('pl', axis=1, inplace=True)
        ordem = pd.DataFrame(data=[{k: v for k, v in sorted(DATA_REAL.loc[0].items(), key=lambda item: item[1])}])
        sugestao, _ = AnaliseCarteira().alinhamento_classe(ordem)

        # Gerando a posicao do retorno apos a reordenaçao
        DATA_NEW = pd.DataFrame(self.DF_CARTEIRA['hoje'])
        for _, y in sugestao.iterrows():
            aloccation = {
            'defit': np.nan,
            'superavit': np.nan,
            'peso': np.nan,
            'retorno': np.nan,
            'risco': np.nan
            }
            coluna_defit = y['ativo']
            coluna_superavit = y['realocar']
            DATA_NEW[coluna_defit] = DATA_NEW[coluna_defit].values[0] + y['valor']
            DATA_NEW[coluna_superavit] = DATA_NEW[coluna_superavit].values[0] - y['valor']
            DATA_new_copy = DATA_NEW.copy()
            for tipo_investimento, coluna in self.tipo_investimento_para_coluna.items():
                DATA_new_copy[coluna] = DATA_new_copy.apply(
                    lambda row: AnaliseCarteira().porcento_classe(row, tipo_investimento),
                    axis=1
                )
            weight_new = DATA_new_copy.iloc[:, 1:]
            i_ret, i_vol = BasicStat().generate_position(pesos=weight_new.values[0], e_r=e_r, mat_cov=mat_cov)
            aloccation['defit'] = coluna_defit
            aloccation['superavit'] = coluna_superavit
            aloccation['peso'] = round(y['valor']/DATA_NEW['pl'].values[0], 2)
            aloccation['retorno'] = round(i_ret[0]*100, 2)
            aloccation['risco'] = round(i_vol[0]*100, 2)
            
            stats_hoje['ordem_ips'].append(aloccation)
        return stats_hoje
        
    def getCarteira(self):
        """
            Método que retorna a carteira otimizada por classe e as bandas de alocaçao considerando
            o fator 'menor risco' e 'maior retorno'.
            
            return:
            - caderneta:
                - id:
                - rentabil:
                    - classe
                    - ret
                    - vol
                - band_hoje:
                    - min: peso ideal de acordo com o menor risco
                    - max: peso ideal de acordo com o maior retorno
                    - posicao: posicao atual do ativo
        """
        caderneta = {
            'id': np.nan,
            'rentabil': [],
            'band_hoje': []
        }
        
        # Salvando id e perfil
        caderneta['id'] = self.DF_CARTEIRA['id']
        
        # Gerando pesos
        DATA_PP = pd.DataFrame(self.DF_CARTEIRA['hoje'])
        for tipo_investimento, coluna in self.tipo_investimento_para_coluna.items():
            DATA_PP[coluna] = DATA_PP.apply(
                lambda row: AnaliseCarteira().porcento_classe(row, tipo_investimento),
                axis=1
            )

        weight = DATA_PP.iloc[:, 1:]
        
        #Salvando retorno e risco
        DATA_HC = pd.DataFrame(self.DF_CARTEIRA['historico'][0])
        tickers = DATA_HC.columns
        
        _, _, e_r, vol, mat_cov = BasicStat().calc_stats(DATA_HC)

        caderneta['rentabil'].append(
            {
                'classe' : list(e_r.index.values),
                'retorno': list(e_r.values),
                'volatil': list(vol.values)
            }
        )
        
        # Gerando as bandas iniciais de limite de acordo com o menor e maior risco individual
        # por classe e carteira
        peso_otimo_1, _, _ = OtimoModel().optimize_portfolio(e_r, mat_cov, len(tickers))
        peso_otimo_2, _, _ = OtimoModel().optimize_portfolio_min(e_r, mat_cov, len(tickers))

        # Criando os dataframes
        cart_band_1 = pd.DataFrame(data=peso_otimo_1, index=tickers, columns=['max_sharpe'])
        cart_band_2 = pd.DataFrame(data=peso_otimo_2, index=tickers, columns=['min_risk'])
        cart_position = pd.DataFrame(data=weight.values[0], index=tickers, columns=['position'])

         # Unindo os datafames e adicionando a posiçao inicial na caderneta
        lower_uper_bands = pd.concat([cart_band_1, cart_band_2], axis=1, join='inner')
        lower_uper_bands['minimo'] = lower_uper_bands.min(axis=1)
        lower_uper_bands['maximo'] = lower_uper_bands.max(axis=1)
        
        lower_uper_bands.drop(['max_sharpe', 'min_risk'], axis=1, inplace=True)
        
        # Adicionando a posiçao inicial na caderneta
        bands = pd.concat([lower_uper_bands, cart_position], axis=1,  join='inner')
        caderneta['band_hoje'].append(bands.to_dict())

        return caderneta
    
    def gerarCenarios(self):
        """
            Método que gera 10mil possivels cenários de alocacoes baseando se na otimizaçao do patrimonio e reorganizacao dos pesos da carteira
            
            params:
            - n: quantidade de classes (padrao wealth ips = 11)
            - media_retorno: valor historico da media do retorno acumulado durante o periodo coletado
            - matrix_cov: dataframe que mostra as correlacoes entre os elementos sem limite de classe
            - ativos: nome das classes
            
            return:
            - cenarios_df:
            - pesos: proporcao calculada que tem como resultado o retorno e o risco unitario
            - retorno: retorno da carteira unitaria estimada
            - risco: risco da carteira unitaria estimada
            
            (Proximo passo): Gerar portifolio especificando qual classe quer usar como parametro.
        """
        
        DATA_HY = pd.DataFrame(self.DF_CARTEIRA['historico'][0])
        ativos = DATA_HY.columns
        _, _, e_r, _, mat_cov = BasicStat().calc_stats(DATA_HY)
        p_ret, p_vol, p_pesos = BasicStat().generate_portfolios(n_ativos=len(ativos), e_r=e_r, mat_cov=mat_cov)
        pesos_df = pd.DataFrame(data=p_pesos, columns=ativos)
        rv_df = pd.DataFrame(data={'retorno': p_ret, 'volatil': p_vol}, columns=['retorno', 'volatil'])
        cenarios_df = pd.concat([rv_df, pesos_df], axis=1, join='inner')*100
        
        """
        # Gerar os pesos para ser repassados nos rangers
        DATA_PP = DATA_HY.copy()
        for tipo_investimento, coluna in self.tipo_investimento_para_coluna.items():
            DATA_PP[coluna] = DATA_PP.apply(
                lambda row: AnaliseCarteira().porcento_classe(row, tipo_investimento),
                axis=1
            )
        """
        return cenarios_df.to_dict()
    
class ProRange():
    def __init__(self, cenarios, arquivo):
        self.cenario = cenarios
        self.data_arquivo = arquivo
        self.arquivo = ProcessData().getCliente(arquivo)
        
    def rangesData(self, rangers):
        """
         Metodo que retorna o menor peso, o novo peso estimado e o maior peso, do cenário escolhido pelo filtro.
         O ativo o qual o filtro foi usado não será alterado, somente os outros terao os ranges atualizados.
         
        """
        
        prov_dict = dict()
        DataFinal = pd.DataFrame(self.cenario)
        DataHist = pd.DataFrame(self.data_arquivo['historico'])

        for key, value in rangers.items():
            DRanger = DataFinal.iloc[(DataFinal[key] - value['peso']).abs().argsort()][:300].sort_values(by=key, ascending=False).sort_values(by='retorno', ascending=False)
            rentabil = {
                'retorno': round(DRanger['retorno'].values[0], 2),
                'risco': round(DRanger['volatil'].values[0], 2)
            }
                        
            newRanges = DRanger.iloc[:, 2:].copy()
            peso_novo = list()
            for col in range(len(newRanges.columns)):
                name = newRanges.iloc[:, [col]].columns.values[0]
                pos = newRanges.iloc[:1, [col]].values[0]
                peso_novo.append(round(pos[0], 0))
                max = newRanges.iloc[:, [col]].max().values[0]
                min = newRanges.iloc[:, [col]].min().values[0]
                p_e = (round(pos[0], 0)/(len(newRanges.columns)*rentabil['retorno']))-rentabil['retorno']
                p_r = (round(pos[0], 0)/(len(newRanges.columns)*rentabil['risco']))-rentabil['risco']
                prov_dict[name] = {
                    'minimo': round(min, 0),
                    'posicao': round(pos[0], 0),
                    'maximo': round(max, 0),
                    'retorno': p_e,
                    'risco': p_r
                }
            prov_dict[key].update({'minimo': rangers[key]['min'], 'posicao': value['peso'], 'maximo': rangers[key]['max']})
        solved_ranger = {
            'carteira': rentabil,
            'ativos': prov_dict,
            'impacto': []
        }
        
        # Gerando retorno por carteira
        DATA_H = pd.DataFrame(self.arquivo['historico'][0])
        _, _, e_r, _, mat_cov = BasicStat().calc_stats(DATA_H)
        i_ret, i_vol = BasicStat().generate_position(pesos=peso_novo, e_r=e_r, mat_cov=mat_cov)
        
        DT_HJ = pd.DataFrame(self.arquivo['hoje'])
        peso_hoje = list((round((DT_HJ.iloc[:,1:]/DT_HJ['pl'].values[0])*100, 0)).values[0])
        DT_HJ.drop('pl', axis=1, inplace=True)
        
        for x in range(len(peso_novo)):
            diff = peso_novo[x] - peso_hoje[x]
            diff_pesos = {
                'classe': DT_HJ.columns[x],
                'peso_impacto': diff,
                'menos_rent': []
            }
            if diff < 0: # Se a diferença é negativa
                dtb = DataHist[DataHist['categoria'] == DT_HJ.columns[x]]
                dtb_pivot = dtb.pivot_table(index='data_posicao', columns='descricao', values='valor_total', aggfunc='max', fill_value=None).reset_index().rename_axis(None, axis=1).ffill()
                n_ativo = len(dtb_pivot.iloc[:,1:].columns)
                if n_ativo > 1: # Preciso que tenha 1 produto na classe
                    _, _, e_r, _, _ = BasicStat().calc_stats(dtb_pivot.iloc[:,1:])
                    e_r = e_r.sort_values(ascending=False)
                    pl = sum(dtb_pivot.iloc[:,1:].tail(1).values[0])
                    peso_ativo = (dtb_pivot.iloc[:,1:].tail(1).values[0] / pl)*100
                    limit = 0
                    index = 0
                    for ativo, retorno in e_r.items():
                        if retorno <= 0:
                            limit += peso_ativo[index]
                            index += 1
                            if limit < abs(diff):
                                diff_pesos['menos_rent'].append({ativo: peso_ativo[index]})
                            else:
                                limit -= peso_ativo[index]
                                pass 
                else:
                    diff_pesos['menos_rent'].append(np.nan)
            else:
                diff_pesos['menos_rent'].append(np.nan)
            
            solved_ranger['impacto'].append(diff_pesos)
        return solved_ranger
