"""
estado.py

Definición del estado compartido del grafo LangGraph.
Todos los agentes leen y escriben sobre este mismo TypedDict.
"""
from __future__ import annotations

from typing import TypedDict

from contratos import (
    PerfilEstudiante,
    MatchingResultado,
    EsquemaInvestigacion,
    EvidenciaRecuperada,
    Protocolo,
    ReporteRevision,
)


class EstadoInvestigIA(TypedDict, total=False):
    perfil: PerfilEstudiante | None
    matching: MatchingResultado | None
    esquema: EsquemaInvestigacion | None
    evidencia: EvidenciaRecuperada | None
    protocolo: Protocolo | None
    revision: ReporteRevision | None
