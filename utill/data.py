import pandas as pd
import numpy as np
from utill.otimizador import OtimoModel
from utill.common import BasicStat

class ProcessData():
    def getIPS(self):
        """
            Método que chama as regras do IPS e seus respectivos perfil de alocaçao
            
            params:
            - path_ips: local do sistema onde se localiza o ips.json
            
            return:
             - data: arquivo lido
        """
        data = pd.read_json('./BD/IPS.json')
        return data

    def getCliente(self, source):
        """
            Método que extrai do input em formato json os dados da carteira e torna mais acessiveis
            durante o funcionamento da api
            
            paramms:
            - path_data: input da carteira em json
            
            return:
            - posiçao hoje: 
                - id: indentificação unica usada para associar a carteira ao cliente já existente no sistema interno da empresa
                - perfil: perfil do cliente
                - hoje: o peso atual por classe
                - historico: mantem a carteira com os todos os dados historicos como um dict
        """
        
        posicao_hoje = {
                'id': np.nan,
                'perfil': np.nan,
                'hoje': [],
                'historico': []
        }
        
        posicao_hoje['id'] = source['id']
        posicao_hoje['perfil'] = source['perfil']
            
        # Transformando os dados históricos em possição atual para tabela
        HY = pd.DataFrame(source['historico'])
        
        # Sum porque estamos somando todos os ativos // levando em consideração que um mesmo ativo não é atualizado duas vezes ou mais no dia
        df_pivot = HY.pivot_table(index='data_posicao', columns='categoria', values='valor_total', aggfunc='sum', fill_value=None).reset_index().rename_axis(None, axis=1).ffill()
    
        # Remover dados que nao fazem parte das classes no IPS
        HY_Clean = df_pivot.drop(columns=['data_posicao','Custodia Remunerada','Proventos','Saldo Projetado'])
        posicao_hoje['historico'].append(HY_Clean)
        
        # Get a ultima posicao atual
        HY_current = HY_Clean.tail(1)
        pl_actual = HY.groupby(['data_posicao'])['pl_total_mes_atual'].max().to_frame().iloc[-1]
        
        # Criando a carteira do administrador
        HY_current.insert(0, 'pl', pl_actual.values[0])
        posicao_hoje['hoje'].append(HY_current.to_dict('records')[0])
        return posicao_hoje

    def getAtivos(self, source):
        """
            Método que extrai além do id e perfil, dados estatisticos relacionados a carteira.
            
            paramms:
            - path_data: input da carteira em json
            
            return:
            - position_ativos:
                - id: indentificação unica usada para associar a carteira ao cliente já existente no sistema interno da empresa
                - perfil: perfil do cliente
                - data: contem a media do retorno e a volatilidade por ativo
                - peso: peso atual do ativo, sendo o peso a posicao atual do ativo em relacao ao patrimonio liquido
                - sugestao: otimizacao da classe dado os ativos e o historico da carteira
        """

        position_ativos = {
            'id': [],
            'perfil': [],
            'data': [],
            'peso': [],
            'sugestao': []
        }
        
        position_ativos['id'].append(source['id'])
        position_ativos['perfil'].append(source['perfil'])
        
        HY = pd.DataFrame(source['historico'])
        # Máxima efetuada por dia de lançamento, se houve duas operações no mesmo produto
        df_pivot = HY.pivot_table(index='data_posicao', columns='categoria', values='valor_total', aggfunc='max', fill_value=None).reset_index().rename_axis(None, axis=1).ffill()
        
        # Remover dados que nao fazem parte das classes no IPS
        HY_Clean = df_pivot.drop(columns=['data_posicao','Custodia Remunerada','Proventos','Saldo Projetado'])
        
        # Separando os produtos e gerando histórico
        dts = pd.DataFrame(source['historico'])
        cats = list(HY_Clean.columns)
        
        for cat in cats:
            dtb = dts[dts['categoria'] == cat]
            dtb_pivot = dtb.pivot_table(index='data_posicao', columns='descricao', values='valor_total', aggfunc='max', fill_value=None).reset_index().rename_axis(None, axis=1).ffill()
            n_ativo = len(dtb_pivot.iloc[:,1:].columns)

            if n_ativo > 1:
                _, _, e_r, vol, mat_cov = BasicStat().calc_stats(dtb_pivot.iloc[:,1:])
                peso_otimo, ret_otimo, vol_otimo = OtimoModel().optimize_portfolio(e_r=e_r, mat_cov=mat_cov, n_ativos=n_ativo)
                
                otimo = pd.DataFrame([e_r.index, peso_otimo]).T
                otimo[1] = np.around(otimo[1].astype(np.double), 2)
                if len(otimo[otimo[1] > (otimo[1].mean()+0.01)]) > 0:
                    fetch = otimo[otimo[1] > (otimo[1].mean()+0.01)]
                    position_ativos['sugestao'].append({cat: [{'ativos': fetch[0].to_list(), 
                                                        'pesos': fetch[1].to_list(), 
                                                        'ret_otimo': ret_otimo*100, 
                                                        'vol_otimo': vol_otimo*100}]})
                else:
                    position_ativos['sugestao'].append({'ativos': np.nan, 
                                                        'pesos': np.nan, 
                                                        'ret_otimo': ret_otimo*100, 
                                                        'vol_otimo': vol_otimo*100})
                
                #Salvando retorno e risco
                index = list(e_r.index)
                rets  = list(e_r)
                vols = list(vol)
                position_ativos['data'].append({cat: [{"produto": index},{"retorno":rets},{"volat": vols}]})
                pl = sum(dtb_pivot.iloc[:,1:].tail(1).values[0])
                pa = (dtb_pivot.iloc[:,1:].tail(1).values / pl)*100
                pa_lista = [x for x in pa[0]]
                position_ativos['peso'].append({cat: pa_lista})
            else:
                position_ativos['data'].append({cat: np.nan})
                position_ativos['sugestao'].append({'peso_otimo': np.nan, 'ret_otimo': np.nan, 'vol_otimo': np.nan})
                position_ativos['peso'].append(np.nan)

        return position_ativos
        