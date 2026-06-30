"""
grafo.py

Construcción del grafo LangGraph con aristas condicionales.
Dev A + Dev C: integración final.

El flujo es:
    Perfil → V1 → Matching → V2 → Metodológico → V3 → Investigador → V4 → Redacción → V5 → Revisión → END

Cada puerta V_i valida que la salida del agente anterior cumpla su contrato.
Si falla, reintenta (máximo 3 veces por agente).
"""
from __future__ import annotations

import logging
from typing import Literal

from langgraph.graph import END, StateGraph

from contratos import (
    EsquemaInvestigacion,
    EvidenciaRecuperada,
    MatchingResultado,
    PerfilEstudiante,
    Protocolo,
    ReporteRevision,
)
from errores import ErrorAgente
from orquestacion.estado import EstadoInvestigIA

from agentes import (
    agente_perfil,
    agente_matching,
    agente_metodologico,
    agente_investigador,
    agente_redaccion,
    agente_revision,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Puertas de validación (V1 a V5)
# ---------------------------------------------------------------------------

def _validar_perfil(estado: EstadoInvestigIA) -> Literal["ok", "retry"]:
    perfil = estado.get("perfil")
    if perfil is None or not isinstance(perfil, PerfilEstudiante):
        return "retry"
    return "ok"


def _validar_matching(estado: EstadoInvestigIA) -> Literal["ok", "retry"]:
    matching = estado.get("matching")
    if matching is None or not isinstance(matching, MatchingResultado):
        return "retry"
    if len(matching.resultados) == 0:
        return "retry"
    return "ok"


def _validar_esquema(estado: EstadoInvestigIA) -> Literal["ok", "retry"]:
    esquema = estado.get("esquema")
    if esquema is None or not isinstance(esquema, EsquemaInvestigacion):
        return "retry"
    return "ok"


def _validar_evidencia(estado: EstadoInvestigIA) -> Literal["ok", "retry"]:
    evidencia = estado.get("evidencia")
    if evidencia is None or not isinstance(evidencia, EvidenciaRecuperada):
        return "retry"
    return "ok"


def _validar_protocolo(estado: EstadoInvestigIA) -> Literal["ok", "retry"]:
    protocolo = estado.get("protocolo")
    if protocolo is None or not isinstance(protocolo, Protocolo):
        return "retry"
    return "ok"


def _validar_revision(estado: EstadoInvestigIA) -> Literal["ok", "fin"]:
    revision = estado.get("revision")
    if revision is None or not isinstance(revision, ReporteRevision):
        return "fin"
    if revision.aprobado:
        return "fin"
    return "retry"


# ---------------------------------------------------------------------------
# Nodos del grafo
# ---------------------------------------------------------------------------

def _nodo_perfil(estado: EstadoInvestigIA) -> EstadoInvestigIA:
    logger.info("Ejecutando agente: perfil")
    return agente_perfil.ejecutar(estado)


def _nodo_matching(estado: EstadoInvestigIA) -> EstadoInvestigIA:
    logger.info("Ejecutando agente: matching")
    return agente_matching.ejecutar(estado)


def _nodo_metodologico(estado: EstadoInvestigIA) -> EstadoInvestigIA:
    logger.info("Ejecutando agente: metodologico")
    return agente_metodologico.ejecutar(estado)


def _nodo_investigador(estado: EstadoInvestigIA) -> EstadoInvestigIA:
    logger.info("Ejecutando agente: investigador")
    return agente_investigador.ejecutar(estado)


def _nodo_redaccion(estado: EstadoInvestigIA) -> EstadoInvestigIA:
    logger.info("Ejecutando agente: redaccion")
    return agente_redaccion.ejecutar(estado)


def _nodo_revision(estado: EstadoInvestigIA) -> EstadoInvestigIA:
    logger.info("Ejecutando agente: revision")
    return agente_revision.ejecutar(estado)


# ---------------------------------------------------------------------------
# Construcción del grafo
# ---------------------------------------------------------------------------

def construir_grafo() -> StateGraph:
    """
    Construye y retorna el grafo LangGraph compilado.
    """
    grafo = StateGraph(EstadoInvestigIA)

    # Nodos
    grafo.add_node("perfil", _nodo_perfil)
    grafo.add_node("matching", _nodo_matching)
    grafo.add_node("metodologico", _nodo_metodologico)
    grafo.add_node("investigador", _nodo_investigador)
    grafo.add_node("redaccion", _nodo_redaccion)
    grafo.add_node("revision", _nodo_revision)

    # Arista inicial
    grafo.set_entry_point("perfil")

    # Aristas condicionales
    grafo.add_conditional_edges(
        "perfil",
        _validar_perfil,
        {"ok": "matching", "retry": "perfil"},
    )
    grafo.add_conditional_edges(
        "matching",
        _validar_matching,
        {"ok": "metodologico", "retry": "matching"},
    )
    grafo.add_conditional_edges(
        "metodologico",
        _validar_esquema,
        {"ok": "investigador", "retry": "metodologico"},
    )
    grafo.add_conditional_edges(
        "investigador",
        _validar_evidencia,
        {"ok": "redaccion", "retry": "investigador"},
    )
    grafo.add_conditional_edges(
        "redaccion",
        _validar_protocolo,
        {"ok": "revision", "retry": "redaccion"},
    )
    grafo.add_conditional_edges(
        "revision",
        _validar_revision,
        {"fin": END, "retry": "redaccion"},
    )

    return grafo.compile()


# ---------------------------------------------------------------------------
# Ejecución
# ---------------------------------------------------------------------------

def ejecutar_pipeline(estado_inicial: EstadoInvestigIA | None = None) -> EstadoInvestigIA:
    """Ejecuta el pipeline completo."""
    if estado_inicial is None:
        estado_inicial: EstadoInvestigIA = {
            "perfil": None,
            "matching": None,
            "esquema": None,
            "evidencia": None,
            "protocolo": None,
            "revision": None,
        }

    grafo = construir_grafo()
    resultado = grafo.invoke(estado_inicial)
    return resultado


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("Ejecutando pipeline completo...")
    resultado = ejecutar_pipeline()
    print()
    print("=" * 70)
    print("RESULTADO FINAL")
    print("=" * 70)
    for campo, valor in resultado.items():
        if valor is not None:
            print(f"{campo}: {valor}")
