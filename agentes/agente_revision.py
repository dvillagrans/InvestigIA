"""
agente_revision.py

Agente de Revision - Dev A.

Responsabilidad:
- Leer el protocolo desde estado["protocolo"].
- Evaluar si el protocolo cumple con secciones minimas.
- Generar observaciones cuando detecta problemas.
- Calcular un puntaje de coherencia entre 0.0 y 1.0.
- Escribir el resultado en estado["revision"].

Version PoC:
- No usa LLM.
- Usa reglas deterministicas simples.
- Usa el contrato Pydantic definido en contratos.py.
"""

from __future__ import annotations

import logging
from typing import Final

from contratos import Observacion, Protocolo, ReporteRevision
from errores import ErrorAgente
from orquestacion.estado import EstadoInvestigIA


_NOMBRE_AGENTE: Final[str] = "revision"
_VERSION_AGENTE: Final[str] = "revision-deterministica-v1"
_MAX_ITERACIONES: Final[int] = 1
_UMBRAL_APROBACION: Final[float] = 0.7

logger = logging.getLogger(__name__)


def _texto_vacio(texto: str) -> bool:
    """
    Indica si un texto esta vacio o solo contiene espacios.
    """
    return not texto or not texto.strip()


def _agregar_observacion(
    observaciones: list[Observacion],
    seccion: str,
    descripcion: str,
) -> None:
    """
    Agrega una observacion al reporte de revision.
    """
    observaciones.append(
        Observacion(
            seccion=seccion,
            descripcion=descripcion,
        )
    )


def _evaluar_secciones_obligatorias(
    protocolo: Protocolo,
    observaciones: list[Observacion],
) -> float:
    """
    Revisa que las secciones minimas del protocolo no esten vacias.

    Regresa:
        Penalizacion acumulada por secciones vacias.
    """
    penalizacion = 0.0

    secciones = {
        "pregunta": protocolo.pregunta,
        "objetivos": protocolo.objetivos,
        "hipotesis": protocolo.hipotesis,
        "metodologia": protocolo.metodologia,
        "justificacion": protocolo.justificacion,
        "alcance": protocolo.alcance,
        "resultados_esperados": protocolo.resultados_esperados,
    }

    for nombre_seccion, contenido in secciones.items():
        if _texto_vacio(contenido):
            _agregar_observacion(
                observaciones,
                nombre_seccion,
                "La seccion esta vacia o no contiene informacion suficiente.",
            )
            penalizacion += 0.15

    return penalizacion


def _evaluar_pregunta(
    protocolo: Protocolo,
    observaciones: list[Observacion],
) -> float:
    """
    Revisa que la pregunta de investigacion este formulada como pregunta.

    Regresa:
        Penalizacion asociada a la pregunta.
    """
    if "?" in protocolo.pregunta or "¿" in protocolo.pregunta:
        return 0.0

    _agregar_observacion(
        observaciones,
        "pregunta",
        "La pregunta de investigacion no esta formulada claramente como pregunta.",
    )
    return 0.10


def _evaluar_objetivos(
    protocolo: Protocolo,
    observaciones: list[Observacion],
) -> float:
    """
    Revisa que la seccion de objetivos tenga desarrollo minimo.

    Regresa:
        Penalizacion asociada a objetivos.
    """
    total_palabras = len(protocolo.objetivos.split())

    if total_palabras >= 8:
        return 0.0

    _agregar_observacion(
        observaciones,
        "objetivos",
        "Los objetivos parecen demasiado breves; se recomienda detallarlos mas.",
    )
    return 0.10


def _evaluar_metodologia(
    protocolo: Protocolo,
    observaciones: list[Observacion],
) -> float:
    """
    Revisa que la metodologia tenga desarrollo minimo.

    Regresa:
        Penalizacion asociada a metodologia.
    """
    total_palabras = len(protocolo.metodologia.split())

    if total_palabras >= 10:
        return 0.0

    _agregar_observacion(
        observaciones,
        "metodologia",
        "La metodologia parece insuficiente para explicar como se realizara el estudio.",
    )
    return 0.15


def _evaluar_fuentes(
    protocolo: Protocolo,
    observaciones: list[Observacion],
) -> float:
    """
    Revisa si el protocolo contiene marcas de falta de evidencia.

    Regresa:
        Penalizacion asociada a evidencia insuficiente.
    """
    texto_protocolo = " ".join(
        [
            protocolo.pregunta,
            protocolo.objetivos,
            protocolo.hipotesis,
            protocolo.metodologia,
            protocolo.justificacion,
            protocolo.alcance,
            protocolo.resultados_esperados,
        ]
    ).lower()

    if "[sin fuente]" not in texto_protocolo:
        return 0.0

    _agregar_observacion(
        observaciones,
        "evidencia",
        "El protocolo contiene afirmaciones marcadas como [sin fuente].",
    )
    return 0.10


def _calcular_revision(protocolo: Protocolo) -> ReporteRevision:
    """
    Calcula el reporte de revision del protocolo.

    El puntaje inicia en 1.0 y disminuye segun las penalizaciones
    encontradas. El protocolo se aprueba si el puntaje final es mayor o
    igual al umbral configurado.
    """
    observaciones: list[Observacion] = []
    penalizacion = 0.0

    penalizacion += _evaluar_secciones_obligatorias(protocolo, observaciones)
    penalizacion += _evaluar_pregunta(protocolo, observaciones)
    penalizacion += _evaluar_objetivos(protocolo, observaciones)
    penalizacion += _evaluar_metodologia(protocolo, observaciones)
    penalizacion += _evaluar_fuentes(protocolo, observaciones)

    puntaje = round(max(0.0, min(1.0, 1.0 - penalizacion)), 2)
    aprobado = puntaje >= _UMBRAL_APROBACION

    return ReporteRevision(
        puntaje_coherencia=puntaje,
        aprobado=aprobado,
        observaciones=observaciones,
    )


def ejecutar(estado: EstadoInvestigIA) -> EstadoInvestigIA:
    """
    Ejecuta el agente de Revision.

    Parametros:
        estado: EstadoInvestigIA con estado["protocolo"] lleno.

    Regresa:
        EstadoInvestigIA con estado["revision"] lleno.

    Lanza:
        ErrorAgente si falta el protocolo, si el protocolo no cumple
        contrato o si ocurre un fallo inesperado.
    """
    try:
        protocolo = estado.get("protocolo")

        # Sin protocolo no hay entrada valida para Revision.
        if protocolo is None:
            raise ErrorAgente(
                _NOMBRE_AGENTE,
                "No se recibio estado['protocolo']. El agente de Revision necesita un Protocolo.",
            )

        # Valida que la entrada respete el contrato esperado.
        if not isinstance(protocolo, Protocolo):
            raise ErrorAgente(
                _NOMBRE_AGENTE,
                f"estado['protocolo'] debe ser Protocolo, pero se recibio {type(protocolo).__name__}.",
            )

        logger.info(
            "Ejecutando agente %s con version %s e iteraciones maximas %s.",
            _NOMBRE_AGENTE,
            _VERSION_AGENTE,
            _MAX_ITERACIONES,
        )

        revision = _calcular_revision(protocolo)

        nuevo_estado = dict(estado)
        nuevo_estado["revision"] = revision

        return nuevo_estado

    except ErrorAgente:
        raise

    except Exception as error:
        raise ErrorAgente(
            _NOMBRE_AGENTE,
            f"Fallo inesperado en el agente de Revision: {type(error).__name__}: {error}",
        )