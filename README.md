# Smart_Wallet_API
Repo que contém os primeiros códigos da API do sistema smart wallet

API que disponibiliza uma otimização da carteira baseado nas classes e seus ativos

## @app.route('/carteira', methods=['POST'])
Formato da resposta: JSON
Requerimento ou não de autenticação: Falso
Limitação de uso: 1 call

Parametros:
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

Descrição dos possíveis retornos:
Se for bem sucedida o retorno será {"success": true} e assim poderá fazer todos os gets necessários
Se não for como esperado {"success": false}, e muito provável seja os parametros serem incorretos ou multiplas chamadas feitas.

## @app.route('/statswallet', methods=['GET'])
Formato da resposta: JSON
Requerimento ou não de autenticação: Falso
Limitação de uso: 1 call por carteira

Parametros:
Sem parametros

Descrição dos possíveis retornos:
{
  "faixa_hj": [
    {
      "Aluguel": -9.8,
      ...
      "Tesouro Direto": -6.11
    }
  ],
  "id": 99,
  "ordem_ips": [
    {
      "defit": "Derivativos de Bal\u00e7\u00e3o",
      "peso": 0.02,
      "retorno": 0.06,
      "risco": 0.29,
      "superavit": "COE"
    },
    ...
    {
      "defit": "NPS",
      "peso": 0.01,
      "retorno": 0.36,
      "risco": 3.47,
      "superavit": "Renda Fixa"
    }
  ],
  "perfil": "Moderado",
  "pesos_hj": [
    {
      "Aluguel": 0.2,
      ...
      "pl": 434604550.0
    }
  ],
  "pp_saude": 82,
  "retorno_hj": 0.06,
  "risco_hj": 0.3,
  "status_saude": "debilitado"
}

Se não for como esperado {"success": false}, e muito provável seja os parametros serem incorretos ou multiplas chamadas feitas.

## @app.route('/getwallet', methods=['GET'])
Formato da resposta: JSON
Requerimento ou não de autenticação: Falso
Limitação de uso: 1 call por carteira

Parametros:
Sem parametros

Descrição dos possíveis retornos:
{
  "band_hoje": [
    {
      "maximo": {
        "Aluguel": 0.8999999999999999,
        ...
        "Tesouro Direto": 0.010000000000000134
      },
      "minimo": {
        "Aluguel": 0.010000000000000037,
        ...
        "Tesouro Direto": 0.010000000000000002
      },
      "position": {
        "Aluguel": 0.0020094704484801182,
        ...
        "Tesouro Direto": 0.03893818619852231
      }
    }
  ],
  "id": 99,
  "rentabil": [
    {
      "classe": [
        "Aluguel",
        ...
        "Tesouro Direto"
      ],
      "retorno": [
        0.034516061616254305,
        ...
        -0.0003071667149725388
      ],
      "volatil": [
        0.34516061616254284,
        ...
        0.004684661368221145
      ]
    }
  ]
}

Se não for como esperado {"success": false}, e muito provável seja os parametros serem incorretos ou multiplas chamadas feitas.

## @app.route('/getativo', methods=['GET'])
Formato da resposta: JSON
Requerimento ou não de autenticação: Falso
Limitação de uso: 1 call por carteira

Parametros:
Sem parametros

Descrição dos possíveis retornos:
{
  "data": [
    {
      "Aluguel": [
        {
          "produto": [
            "ARZZ3",
            "HYPE3",
            "RRRP3"
          ]
        },
        {
          "retorno": [
            0.0,
            0.0,
            0.0
          ]
        },
        {
          "volat": [
            0.0,
            0.0,
            0.0
          ]
        }
      ]
    },
    ...
    {
      "Tesouro Direto": [
        {
          "produto": [
            "NTN-B",
            "NTNB PRINC"
          ]
        },
        {
          "retorno": [
            -0.0003026032390344069,
            -0.00019751569145574633
          ]
        },
        {
          "volat": [
            0.004012588606445353,
            0.005608929826540907
          ]
        }
      ]
    }
  ],
  "id": [
    99
  ],
  "perfil": [
    "Moderado"
  ],
  "peso": [
    {
      "Aluguel": [
        7.065872406632215,
        81.65678205004735,
        11.277345543320425
      ]
    },
    ...
    {
      "Tesouro Direto": [
        63.31760496120498,
        36.68239503879502
      ]
    }
  ],
  "sugestao": [
    {
      "Aluguel": [
        "ativos": NaN,
        "pesos": NaN,
        "ret_otimo": 0.0,
        "vol_otimo": 0.0
      ]
    },
    ...
    {
      "Tesouro Direto": [
        "ativos": [
        "NTNB PRINC"
        ],
        "pesos": [
            0.99
        ],
        "ret_otimo": -0.019856656693153292,
        "vol_otimo": 0.5579837207019904
      ]
    }
  ]
}

## @app.route('/getranger', methods=['POST'])
Formato da resposta: JSON
Requerimento ou não de autenticação: Falso
Limitação de uso: 1 call por carteira
Observação: Preisa que seja feita uma call inicial para '/carteira' antes de fazer o post aqui.

Parametros:
{
    classe: str(): {
        peso: int(),
        min: int(),
        max: int()
    }
}

{
  "ativos": {
    "Aluguel": {
      "maximo": 35,
      "minimo": 23,
      "posicao": 12,
      "retorno": 2.1069978858350953,
      "risco": -3.8871303395399783
    },
    ...
    "Tesouro Direto": {
      "maximo": 22.0,
      "minimo": 0.0,
      "posicao": 6.0,
      "retorno": 0.8384989429175478,
      "risco": -4.01856516976999
    }
  },
  "carteira": {
    "retorno": 0.43,
    "risco": 4.15
  },
  "impacto": [
    {
      "classe": "Aluguel",
      "menos_rent": [
        NaN
      ],
      "peso_impacto": 12.0
    },
    ...
    {
      "classe": "Tesouro Direto",
      "menos_rent": [
        NaN
      ],
      "peso_impacto": 2.0
    }
  ]
}

