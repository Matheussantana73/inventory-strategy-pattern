"""Rotas da API de cálculo"""

from fastapi import APIRouter, HTTPException, status
from typing import List

from .schemas import (
    CalculoInput,
    ResultadoCalculo,
    EstrategiaInfo,
    EstrategiasListResponse,
    SimulacaoInput,
    SimulacaoResponse,
    SimulacaoResultado,
)
from .calculadora import CalculadoraPedido
from .strategies import (
    obter_estrategia_desconto,
    obter_estrategia_frete,
    listar_estrategias_desconto,
    listar_estrategias_frete,
)

router = APIRouter(prefix="/api/v1", tags=["Cálculos"])


@router.post("/calcular", response_model=ResultadoCalculo)
def calcular_pedido(input_data: CalculoInput):
    """
    Calcula valores do pedido com estratégias específicas

    Recebe os valores do pedido e aplica as estratégias de desconto e frete.
    """
    try:
        # Obter estratégias
        estrategia_desconto = obter_estrategia_desconto(input_data.tipo_desconto)
        estrategia_frete = obter_estrategia_frete(input_data.tipo_frete)

        # Criar calculadora e calcular
        calculadora = CalculadoraPedido(estrategia_desconto, estrategia_frete)
        resultado = calculadora.calcular_total(
            valor_produtos=input_data.valor_produtos,
            quantidade=input_data.quantidade,
            peso_kg=input_data.peso_kg,
            distancia_km=input_data.distancia_km,
        )

        return resultado

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/estrategias", response_model=EstrategiasListResponse)
def listar_estrategias():
    """Lista todas as estratégias de desconto e frete disponíveis"""
    return EstrategiasListResponse(
        desconto=[EstrategiaInfo(**e) for e in listar_estrategias_desconto()],
        frete=[EstrategiaInfo(**e) for e in listar_estrategias_frete()],
    )


@router.get("/estrategias/desconto", response_model=list[EstrategiaInfo])
def listar_estrategias_desconto_api():
    """Lista estratégias de desconto disponíveis"""
    return [EstrategiaInfo(**e) for e in listar_estrategias_desconto()]


@router.get("/estrategias/frete", response_model=list[EstrategiaInfo])
def listar_estrategias_frete_api():
    """Lista estratégias de frete disponíveis"""
    return [EstrategiaInfo(**e) for e in listar_estrategias_frete()]


@router.post("/simular", response_model=SimulacaoResponse)
def simular_estrategias(input_data: SimulacaoInput):
    """
    Simula cálculos com múltiplas combinações de estratégias

    Útil para comparar diferentes opções e encontrar a melhor combinação.
    """
    resultados = []

    for tipo_desconto in input_data.estrategias_desconto:
        for tipo_frete in input_data.estrategias_frete:
            # Obter estratégias
            estrategia_desconto = obter_estrategia_desconto(tipo_desconto)
            estrategia_frete = obter_estrategia_frete(tipo_frete)

            # Calcular
            calculadora = CalculadoraPedido(estrategia_desconto, estrategia_frete)
            resultado = calculadora.calcular_total(
                valor_produtos=input_data.valor_produtos,
                quantidade=input_data.quantidade,
                peso_kg=input_data.peso_kg,
                distancia_km=input_data.distancia_km,
            )

            resultados.append(
                SimulacaoResultado(
                    tipo_desconto=tipo_desconto,
                    tipo_frete=tipo_frete,
                    valor_produtos=float(resultado.valor_produtos),
                    desconto=float(resultado.desconto),
                    frete=float(resultado.frete),
                    valor_final=float(resultado.valor_final),
                    percentual_desconto=resultado.percentual_desconto,
                )
            )

    # Encontrar melhor opção (menor valor final)
    melhor = min(resultados, key=lambda r: r.valor_final)

    return SimulacaoResponse(resultados=resultados, melhor_opcao=melhor)


@router.post("/calcular/detalhado", response_model=dict)
def calcular_detalhado(input_data: CalculoInput):
    """
    Calcula valores com detalhamento adicional

    Inclui explicação de como o cálculo foi feito.
    """
    # Obter estratégias
    estrategia_desconto = obter_estrategia_desconto(input_data.tipo_desconto)
    estrategia_frete = obter_estrategia_frete(input_data.tipo_frete)

    # Calcular
    calculadora = CalculadoraPedido(estrategia_desconto, estrategia_frete)
    resultado = calculadora.calcular_total(
        valor_produtos=input_data.valor_produtos,
        quantidade=input_data.quantidade,
        peso_kg=input_data.peso_kg,
        distancia_km=input_data.distancia_km,
    )

    return {
        "resultado": {
            "valor_produtos": float(resultado.valor_produtos),
            "desconto": float(resultado.desconto),
            "frete": float(resultado.frete),
            "valor_final": float(resultado.valor_final),
            "percentual_desconto": resultado.percentual_desconto,
        },
        "detalhes": {
            "estrategia_desconto": {
                "tipo": input_data.tipo_desconto,
                "descricao": estrategia_desconto.descricao,
            },
            "estrategia_frete": {
                "tipo": input_data.tipo_frete,
                "descricao": estrategia_frete.descricao,
            },
            "parametros": {
                "valor_produtos": input_data.valor_produtos,
                "quantidade": input_data.quantidade,
                "peso_kg": input_data.peso_kg,
                "distancia_km": input_data.distancia_km,
            },
        },
    }
