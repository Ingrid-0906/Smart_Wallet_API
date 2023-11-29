import pandas as pd
import numpy as np

class AnaliseCarteira:
    """
        Macrovisão: Analisando carteiras e estimando a diferença entre o perfil baseado em IPS profiles
            - Levantar a diferença entre a carteira e o perfil de acordo com os threshold do perfil escolhido.
            - Sinalizar em porcento entre -100% e +100% o valor esperado para cada perfil.
            - Sinalizar em moeda corrente o valor em diferença.
            
        Metodo:
            - porcento_classe: Transforma os valores em proporcoes equivalentes ao patrimonio liquido total
            - bandeira_classe: Enquadra a carteira no perfil designado e sinaliza onde está fora do padrao
            - reais_classe: Informa o quanto em reais(R$) está fora ou dentro do range do perfil designado
            - alinhamento_classe: Informa onde deve ser feita a alocação e a quantidade de montante em reais (R$)
    """
    
    def porcento_classe(self, row, tipo_investimento):
        """
            Transforma as classes em porcentagem de acordo com a proporcao devida
            em relacao ao patrimonio liquido total
            
            params:
            - row: linha do dataframe que contem os valores das classes (carteira)
            - tipo_investimento: nome da coluna que contem a classe
            
            return:
            - proporção da classe na carteira (%)
        """
        return row[tipo_investimento] / row['pl']

    def bandeira_classe(self, row, persona, tipo_investimento):
        """
            Sinaliza onde está para mais ou menos de acordo com os ranges acordados no ips.
            Lógica Aplicada:
                - O cliente tem que ter 0 para estar dentro do padrão do perfil.
                - Se estiver negativo, quer dizer que está abaixo do esperado (oportunidade de venda ou reinvestimento)
                - Se estiver positivo, quer dizer que ultrapassou o limite do perfil (realocar)
                
            params:
            - row: linha do dataframe que contem os valores das classes (carteira)
            - persona: perfil da carteira do usuario
            - tipo_investimento: nome da coluna que contem a classe no dataframe
            
            return:
            - delta: a diferença aplicada entre a atual proporção da classe vs. o padrao aplicado
            na IPS para o perfil
        """
        n = row[tipo_investimento] - persona[persona['ips'] == tipo_investimento][row['perfil']]
        delta = n * 100
        return delta  

    def saude_investimentos(self, row):
        """
            Analisa o estado de saúde da carteira observando o percentual do range de alocação.
            A atribuicao é dada ditribuindo um peso igualmente proporcional para cada classe.
            Se a o valor de uma classe estiver dentro da margem de segurança (2% / -2%) então
            não é necessária a intervencao do consultor. Caso contrário, será indicado o estado de
            saúde como debilitado.
            Foi dado um espaço de 2% de margem para evitar alarme desnecessário.
            
            param:
            - row: linha do dataframe que contem os valores das classes (carteira)
           
            return:
            - status da carteira vs. classe
        """
        
        classe_health = np.where((row > -2.0) & (row < 2.0), 0, 1/11)
        status = np.sum(classe_health)

        if status < 0.33:
            return [round(status, 2), str('aceitavel')]
        elif status < 0.66:
            return [round(status, 2), str('razoavel')]
        else:
            return [round(status, 2), str('debilitado')]    
        
    def reais_classe(self, row, tipo_investimento):
        """
            Transforma os valores sinalizados em montante de real (R$)
            
            params:
            - row: linha do dataframe que contem os valores das classes (carteira)
            - tipo_investimento: nome da coluna que contem a classe
            
            return:
            - result: transforma a proporção atual do defit em porcento e transforma em reais
        """
        n = round(row[tipo_investimento] / 100, 8)
        result = row['pl'] * n
        return result

    def alinhamento_classe(self, ordenado):
        """
            Cria uma matriz com os valores alinhados com o perfil proposto pela ips e indica onde
            deve ser feita a alocacao para chegar ao balanco dos ranges
            
            params:
            - ordenado: dataframe com as proporções dos defits e superavits
            
            return:
            - sugestao: dataframe com os ativos em defits e a fonte do capital para repor
            - ordenado: dataframe com a carteira alinhada ao perfil vs patrimonio atual
        """
        valores = {'ativo':[], 'realocar':[], 'valor':[]}

        for col in range(len(ordenado.columns)):
            valor = ordenado.iloc[0, col]
        
            while valor < 0:
                for i in range(col + 1, len(ordenado.columns)):
                    proximo_ativo = ordenado.columns[i]
                    proximo = ordenado.iloc[0, i]

                    if proximo > 0:
                        sobra = valor + proximo
                        valores['ativo'].append(ordenado.columns[col])
                        valores['realocar'].append(proximo_ativo)
                        valores['valor'].append(proximo if sobra < 0 else abs(valor))
                        valor = 0 if sobra > 0 else sobra
                        ordenado.iloc[0, i] = sobra if sobra > 0 else 0
                    else:
                        pass
                else:
                    break

        sugestao = pd.DataFrame(data=valores)
        sugestao['valor'] = sugestao['valor'].apply(lambda x: int(x * (10**3))/(10**3))
        ordenado = ordenado.apply(lambda x: int(abs(x.loc[0]) * (10**3))/(10**3), axis=0)
        return sugestao, ordenado


        