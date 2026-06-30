"""
agente_revision.py

Agente de Revision - Dev A.

Responsabilidad:
- Leer el protocolo desde estado["protocolo"].
- Evaluar reglas minimas del protocolo.
- Generar observaciones cuando detecta problemas.
- Calcular un puntaje de coherencia entre 0.0 y 1.0.
- Escribir el resultado en estado["revision"].

Version PoC:
- No usa LLM.
- Usa reglas deterministicas simples.
- Usa penalizaciones homogeneas para reglas especificas.
- Usa penalizacion proporcional para secciones con contenido insuficiente.
- Usa el contrato Pydantic definido en contratos.py.
"""

from __future__ import annotations

import logging
import re
import unicodedata
from typing import Final

from contratos import Observacion, Protocolo, ReporteRevision
from errores import ErrorAgente
from orquestacion.estado import EstadoInvestigIA


_NOMBRE_AGENTE: Final[str] = "revision"
_VERSION_AGENTE: Final[str] = "revision-deterministica-v1"
_MAX_ITERACIONES: Final[int] = 1

_UMBRAL_APROBACION: Final[float] = 0.70
_PENALIZACION_REGLA: Final[float] = 0.10
_PENALIZACION_MAX_SECCIONES: Final[float] = 0.40

_MIN_PALABRAS_SECCION: Final[int] = 3
_MIN_PALABRAS_OBJETIVOS: Final[int] = 8
_MIN_PALABRAS_METODOLOGIA: Final[int] = 10

_PALABRAS_INTERROGATIVAS: Final[tuple[str, ...]] = (
    "como",
    "que",
    "cual",
    "cuales",
    "en que medida",
    "por que",
    "para que",
)

logger = logging.getLogger(__name__)


def _normalizar_texto(texto: str) -> str:
    """Normaliza texto para comparaciones simples."""
    texto = texto.lower()
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(
        caracter
        for caracter in texto
        if unicodedata.category(caracter) != "Mn"
    )
    texto = re.sub(r"\s+", " ", texto).strip()

    return texto


def _agregar_observacion(
    observaciones: list[Observacion],
    seccion: str,
    descripcion: str,
) -> None:
    """Agrega una observacion al reporte."""
    observaciones.append(
        Observacion(
            seccion=seccion,
            descripcion=descripcion,
        )
    )


def _texto_completo(protocolo: Protocolo) -> str:
    """Une las secciones del protocolo en un solo texto."""
    return " ".join(
        [
            protocolo.pregunta,
            protocolo.objetivos,
            protocolo.hipotesis,
            protocolo.metodologia,
            protocolo.justificacion,
            protocolo.alcance,
            protocolo.resultados_esperados,
        ]
    )


def _evaluar_secciones_obligatorias(
    protocolo: Protocolo,
    observaciones: list[Observacion],
) -> float:
    """
    Penaliza proporcionalmente secciones con contenido insuficiente.

    La penalizacion maxima de esta categoria es 0.40, aunque varias secciones
    tengan problemas. Esto evita acumulacion excesiva.
    """
    secciones = {
        "pregunta": protocolo.pregunta,
        "objetivos": protocolo.objetivos,
        "hipotesis": protocolo.hipotesis,
        "metodologia": protocolo.metodologia,
        "justificacion": protocolo.justificacion,
        "alcance": protocolo.alcance,
        "resultados_esperados": protocolo.resultados_esperados,
    }

    secciones_insuficientes: list[str] = []

    for nombre_seccion, contenido in secciones.items():
        if len(contenido.split()) < _MIN_PALABRAS_SECCION:
            secciones_insuficientes.append(nombre_seccion)
            _agregar_observacion(
                observaciones,
                nombre_seccion,
                "La seccion existe, pero parece tener contenido insuficiente.",
            )

    proporcion_insuficiente = len(secciones_insuficientes) / len(secciones)

    return round(proporcion_insuficiente * _PENALIZACION_MAX_SECCIONES, 2)


def _evaluar_pregunta(
    protocolo: Protocolo,
    observaciones: list[Observacion],
) -> float:
    """Evalua si la pregunta tiene estructura interrogativa minima."""
    pregunta = _normalizar_texto(protocolo.pregunta)

    inicia_con_interrogativo = any(
        pregunta.startswith(palabra)
        for palabra in _PALABRAS_INTERROGATIVAS
    )

    if inicia_con_interrogativo:
        return 0.0

    _agregar_observacion(
        observaciones,
        "pregunta",
        "La pregunta de investigacion no muestra una estructura interrogativa clara.",
    )
    return _PENALIZACION_REGLA


def _evaluar_objetivos(
    protocolo: Protocolo,
    observaciones: list[Observacion],
) -> float:
    """Evalua desarrollo minimo de la seccion de objetivos."""
    if len(protocolo.objetivos.split()) >= _MIN_PALABRAS_OBJETIVOS:
        return 0.0

    _agregar_observacion(
        observaciones,
        "objetivos",
        "Los objetivos parecen demasiado breves; se recomienda detallarlos mas.",
    )
    return _PENALIZACION_REGLA


def _evaluar_metodologia(
    protocolo: Protocolo,
    observaciones: list[Observacion],
) -> float:
    """Evalua desarrollo minimo de la metodologia."""
    if len(protocolo.metodologia.split()) >= _MIN_PALABRAS_METODOLOGIA:
        return 0.0

    _agregar_observacion(
        observaciones,
        "metodologia",
        "La metodologia parece insuficiente para explicar como se realizara el estudio.",
    )
    return _PENALIZACION_REGLA


def _evaluar_fuentes(
    protocolo: Protocolo,
    observaciones: list[Observacion],
) -> float:
    """
    Registra marcas [sin fuente] sin penalizacion automatica.

    La marca [sin fuente] es una senal de transparencia del agente de
    redaccion cuando no tiene evidencia suficiente.
    """
    texto_protocolo = _normalizar_texto(_texto_completo(protocolo))

    if "[sin fuente]" in texto_protocolo:
        _agregar_observacion(
            observaciones,
            "evidencia",
            "El protocolo contiene afirmaciones marcadas como [sin fuente]; requieren revision humana.",
        )

    return 0.0


def _calcular_revision(protocolo: Protocolo) -> ReporteRevision:
    """Calcula puntaje, observaciones y aprobacion del protocolo."""
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

    Entrada:
        estado["protocolo"]

    Salida:
        estado["revision"]
    """
    try:
        protocolo = estado.get("protocolo")

        # Validacion defensiva: evita que el grafo avance con estado mal armado.
        if protocolo is None:
            raise ErrorAgente(
                _NOMBRE_AGENTE,
                "No se recibio estado['protocolo']. El agente de Revision necesita un Protocolo.",
            )

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
    