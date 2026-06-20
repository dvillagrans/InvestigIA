"""
contratos.py

Contratos de datos (Pydantic) para los seis agentes del pipeline de InvestigIA.

Este archivo es el UNICO lugar donde se definen estos modelos. Ningun agente
los redefine ni los copia; todos importan desde aqui:

    from contratos import PerfilEstudiante, MatchingResultado, ...

La logica interna de cada agente puede estar simplificada a modo para el happy path, pero el
contrato de entrada/salida que aqui se define no se simplifica. Esto es para que más adelante, 
alguien reemplace la logica interna de un agente sin que nadie mas tenga que tocar su codigo.

Orden del pipeline (referencia):
    Perfil -> Matching -> Metodologico -> Investigador -> Redaccion -> Revision
"""

from __future__ import annotations

from enum import Enum
from typing import List

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Tipos compartidos
# ---------------------------------------------------------------------------

class NivelAcademico(str, Enum):
    """
    Enum cerrado a tres valores. Se usa Enum en vez de un string libre para
    que ningun agente pueda escribir "Maestria" con mayuscula o con tilde
    en un lugar y "maestria" en otro, rompiendo comparaciones entre agentes.
    """
    licenciatura = "licenciatura"
    maestria = "maestria"
    doctorado = "doctorado"


# ---------------------------------------------------------------------------
# 1. Agente de Perfil -> Agente de Matching
# ---------------------------------------------------------------------------

class PerfilEstudiante(BaseModel):
    """Salida del Agente de Perfil. Entrada del Agente de Matching."""

    nombre: str = Field(..., min_length=1)
    nivel: NivelAcademico
    intereses: List[str] = Field(..., min_length=1)


# ---------------------------------------------------------------------------
# 2. Agente de Matching -> Agente Metodologico
# ---------------------------------------------------------------------------

class ResultadoMatching(BaseModel):
    """Un candidato individual dentro del ranking de matching."""

    investigador_id: str = Field(..., min_length=1)
    nombre: str = Field(..., min_length=1)
    score: float = Field(..., ge=0.0, le=1.0)
    justificacion: str = Field(..., min_length=1)


class MatchingResultado(BaseModel):
    """
    Salida del Agente de Matching. Entrada del Agente Metodologico.

    Es una LISTA aunque en el happy path siempre tenga un solo elemento
    (el investigador falso). Se modela como lista porque asi es como se
    comportaria el sistema completo (un ranking de varios candidatos); el
    contrato no debe mentir sobre la forma real del sistema solo porque hoy
    el agente este simplificado.
    """

    resultados: List[ResultadoMatching] = Field(..., min_length=1)


# ---------------------------------------------------------------------------
# 3. Agente Metodologico -> Agente Investigador
# ---------------------------------------------------------------------------

class EsquemaInvestigacion(BaseModel):
    """Salida del Agente Metodologico. Entrada del Agente Investigador."""

    pregunta: str = Field(..., min_length=1)
    objetivo_general: str = Field(..., min_length=1)
    objetivos_especificos: List[str] = Field(..., min_length=1)
    hipotesis: str = Field(..., min_length=1)


# ---------------------------------------------------------------------------
# 4. Agente Investigador -> Agente de Redaccion
# ---------------------------------------------------------------------------

class FragmentoRecuperado(BaseModel):
    """Un fragmento individual recuperado del corpus local fijo."""

    id: str = Field(..., min_length=1)
    titulo: str = Field(..., min_length=1)
    autores: List[str] = Field(..., min_length=1)
    anio: int = Field(..., ge=1900, le=2100)
    texto: str = Field(..., min_length=1)


class EvidenciaRecuperada(BaseModel):
    """
    Salida del Agente Investigador. Entrada del Agente de Redaccion.

    En el happy path, fragmentos nunca deberia salir vacio (el corpus falso
    siempre tiene resultados para el perfil-guion), pero el campo se permite
    vacio a nivel de tipo para no romper el contrato si alguien prueba con
    un caso distinto al guion.
    """

    fragmentos: List[FragmentoRecuperado] = Field(default_factory=list)

    @property
    def evidencia_insuficiente(self) -> bool:
        return len(self.fragmentos) == 0


# ---------------------------------------------------------------------------
# 5. Agente de Redaccion -> Agente de Revision
# ---------------------------------------------------------------------------

class Protocolo(BaseModel):
    """
    Salida del Agente de Redaccion. Entrada del Agente de Revision.

    Las siete secciones minimas acordadas en el Working Agreement. Todas
    son obligatorias: si al agente de Redaccion le falta evidencia para
    alguna seccion, debe escribir el texto marcando "[sin fuente]" en vez
    de dejar la seccion vacia (la validacion de Pydantic no acepta strings
    vacios).
    """

    pregunta: str = Field(..., min_length=1)
    objetivos: str = Field(..., min_length=1)
    hipotesis: str = Field(..., min_length=1)
    metodologia: str = Field(..., min_length=1)
    justificacion: str = Field(..., min_length=1)
    alcance: str = Field(..., min_length=1)
    resultados_esperados: str = Field(..., min_length=1)


# ---------------------------------------------------------------------------
# 6. Agente de Revision -> Entrega
# ---------------------------------------------------------------------------

class Observacion(BaseModel):
    """Una observacion individual del Agente de Revision sobre el protocolo."""

    seccion: str = Field(..., min_length=1)
    descripcion: str = Field(..., min_length=1)


class ReporteRevision(BaseModel):
    """Salida del Agente de Revision. Resultado final del pipeline."""

    puntaje_coherencia: float = Field(..., ge=0.0, le=1.0)
    aprobado: bool
    observaciones: List[Observacion] = Field(default_factory=list)