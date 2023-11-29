import numpy as np
from utill.data import ProcessData
from utill.wallet import CarteiraStats, ProRange
from flask import Flask, jsonify, request

app = Flask(__name__)
@app.route('/carteira', methods=['POST']) # Tested!
def SendData():
    """
        Schema Data Válido para ser enviado:
        {
            id: int(),
            perfil: str(),
            historico: {
                * categoria: dict( index(), str() ) -> possivel classes de investimento
                * descricao: dict( index(), str() ) -> nome do produto
                * valor_total: dict( index(), float() ) -> valor/posicao atulizado diariamente
                * pl_total_mes_atual: dict( index(), float() ) -> posicao geral da carteira no mes
                * data_posicao: dict( index(), datetime() )
            }
        }
    """
    try:
        global arquivo_json
        global cenario
        global pesos
        
        arquivo_json = request.get_json()
        cenario = CarteiraStats(path_data=arquivo_json).gerarCenarios()
        return jsonify(success=True)
    except:
        return jsonify(success=False)
            
@app.route('/statswallet', methods=['GET']) # Tested!
def StatsCarteira():
    """
        Schema data válido para ser recebido:
        {
            id: int(),
            perfil: str(),
            pesos_hj: dict( classe: str(), valor: float() )
            retorno_hj: float(),
            risco_hj: float(),
            faixa_hj: dict( classe: str(), valor: float() )
            pp_saude: float()
            status_saude: str()
            ordem_ips: dict( defit: str(), superavit: str(), peso: float(), retorno: float(), risco: float() )
        }
    """
    try:
        return jsonify(CarteiraStats(path_data=arquivo_json).statsWallet())
    except:
        return jsonify(success=False)
  
@app.route('/getwallet', methods=['GET']) # Tested!
def GetCarteira():
    """
        Schema data válido para ser recebido:
        {
            id: int(),
            rentabil: {
                'classe' : list( str() ),
                'retorno': list( float() ),
                'volatil': list( float() ),
                'mat_cov': dict( index: int(), classe: str(), covariantes: float() )
            }
            band_hoje: {
                index: int(),
                classe: str(),
                maximum: float(),
                minimum: float(),
                posicao: float()
            }
        }
    """
    try:
        return jsonify(CarteiraStats(path_data=arquivo_json).getCarteira())
    except:
        return jsonify(success=False)

@app.route('/getativo', methods=['GET']) # Tested!
def GetAtivos():
    """
        Schema válido para receber:
        {
            id: int(),
            perfil: str(),
            data (historico): {
                * categoria: dict( index(), str() ) -> possivel classes de investimento
                * descricao: dict( index(), str() ) -> nome do produto
                * valor_total: dict( index(), float() ) -> valor/posicao atulizado diariamente
                * pl_total_mes_atual: dict( index(), float() ) -> posicao geral da carteira no mes
                * data_posicao: dict( index(), datetime() )
            },
            peso: dict( classe: str(), valor: float() ),
            sugestao: dict( classe: str(): peso_ideal: float() )
        }
    """
    try:
        return jsonify(ProcessData().getAtivos(source=arquivo_json))
    except:
        return jsonify(success=False)
    
      
@app.route('/getranger', methods=['POST'])
def getRangers():
    """
        Schema data válido para enviar:
        {
            classe [x]: str(): {
                peso: float(),
                min: float(),
                max: float()
            }
        }
    """
    try:
        rangers = request.get_json()
        return jsonify(ProRange(cenarios=cenario, arquivo=arquivo_json).rangesData(rangers))
    except:
        return jsonify(success=False)
    


if __name__ == '__main__':
    arquivo_json = np.nan
    cenario = np.nan
    
    app.run(port=8080, host='localhost', debug=True)
    