"""
agente_metodologico.py — Dev C

Agente Metodológico.
Recibe PerfilEstudiante + MatchingResultado y produce EsquemaInvestigacion.

El agente toma el perfil del estudiante y el investigador asignado por
el matching, y genera un esquema de investigación con: pregunta,
objetivo general, objetivos específicos e hipótesis.
"""
from __future__ import annotations

import json

from contratos import EsquemaInvestigacion
from errores import ErrorAgente
from llm_client import invocar_agente
from orquestacion.estado import EstadoInvestigIA

_NOMBRE = "metodologico"

_PROMPT_SISTEMA = """\
Eres un asistente metodológico académico. Tu tarea es generar un esquema \
de investigación a partir del perfil de un estudiante y del investigador \
que le fue asignado.

Debes responder EXCLUSIVAMENTE con un JSON válido con esta estructura:
{
  "pregunta": "...",
  "objetivo_general": "...",
  "objetivos_especificos": ["...", "..."],
  "hipotesis": "..."
}

Reglas:
- La pregunta debe ser clara, específica y acotada.
- El objetivo general debe responder directamente a la pregunta.
- Los objetivos específicos deben formularse siguiendo la taxonomía de Bloom.
  Usa verbos de acción correspondientes al nivel cognitivo adecuado:
    * Recordar: listar, identificar, describir, nombrar.
    * Comprender: explicar, resumir, interpretar, clasificar.
    * Aplicar: implementar, usar, demostrar, resolver.
    * Analizar: comparar, contrastar, examinar, distinguir.
    * Evaluar: juzgar, criticar, justificar, defender.
    * Crear: diseñar, construir, proponer, desarrollar.
  Cada objetivo específico debe empezar con un verbo en infinitivo y ser medible.
  Mínimo 2 objetivos específicos.
- La hipótesis debe ser testeable.
- No inventes información que no esté en el perfil o el matching.
- No incluyas texto fuera del JSON.
"""


def ejecutar(estado: EstadoInvestigIA) -> EstadoInvestigIA:
    """
    Lee 'perfil' y 'matching' del estado, genera un EsquemaInvestigacion
    mediante el LLM, y lo escribe en estado['esquema'].

    Levanta ErrorAgente si:
    - perfil o matching son None.
    - El LLM no responde o responde con texto vacío.
    - La respuesta del LLM no es un JSON válido con los campos requeridos.
    """
    perfil = estado.get("perfil")
    matching = estado.get("matching")

    if perfil is None:
        raise ErrorAgente(_NOMBRE, "No hay perfil en el estado. El agente de perfil debe ejecutar primero.")
    if matching is None:
        raise ErrorAgente(_NOMBRE, "No hay matching en el estado. El agente de matching debe ejecutar primero.")

    mejor_candidato = matching.resultados[0]

    prompt_usuario = (
        f"Perfil del estudiante:\n"
        f"- Nombre: {perfil.nombre}\n"
        f"- Nivel: {perfil.nivel.value}\n"
        f"- Intereses: {', '.join(perfil.intereses)}\n\n"
        f"Investigador asignado:\n"
        f"- Nombre: {mejor_candidato.nombre}\n"
        f"- Score: {mejor_candidato.score}\n"
        f"- Justificación: {mejor_candidato.justificacion}\n\n"
        f"Genera el esquema de investigación."
    )

    try:
        texto = invocar_agente(
            agente=_NOMBRE,
            sistema=_PROMPT_SISTEMA,
            usuario=prompt_usuario,
            temperatura=0.3,
        )
    except ErrorAgente:
        raise

    try:
        datos = json.loads(texto)
    except json.JSONDecodeError as error:
        raise ErrorAgente(
            _NOMBRE,
            f"El LLM no respondió con JSON válido. "
            f"Respuesta recibida: {texto[:200]}... Detalle: {error}",
        )

    try:
        esquema = EsquemaInvestigacion(**datos)
    except Exception as error:
        raise ErrorAgente(
            _NOMBRE,
            f"El JSON del LLM no cumple el contrato EsquemaInvestigacion. "
            f"Datos: {datos}. Detalle: {error}",
        )

    resultado = dict(estado)
    resultado["esquema"] = esquema
    return resultado
