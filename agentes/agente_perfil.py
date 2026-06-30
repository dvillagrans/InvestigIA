"""
agente_perfil.py — Dev B

Agente de Perfil Académico.
Recibe texto libre del estudiante y produce un PerfilEstudiante.
"""
import json
import re
from collections.abc import Sequence
from typing import Any

from contratos import PerfilEstudiante
from errores import ErrorAgente
from llm_client import invocar_agente
from orquestacion.estado import EstadoInvestigIA

_NOMBRE = "perfil"
_CAMPO_ENTRADA = "entrada_usuario"

_PROMPT_SISTEMA = """\
Eres un asistente de perfilado academico. Extrae un perfil estructurado a
partir de las respuestas de un estudiante.

Responde EXCLUSIVAMENTE con un JSON valido con esta estructura:
{
  "nombre": "...",
  "nivel": "licenciatura | maestria | doctorado",
  "intereses": ["...", "..."]
}

Reglas:
- Usa solamente informacion expresada por el estudiante.
- "nombre" debe ser una cadena no vacia.
- "nivel" debe ser exactamente "licenciatura", "maestria" o "doctorado",
  en minusculas y sin acentos.
- "intereses" debe ser una lista no vacia de temas concretos, sin duplicados.
- Conserva los nombres propios tal como fueron proporcionados.
- No agregues explicaciones ni texto fuera del JSON.
"""


def _normalizar_entrada(entrada: Any) -> str:
    """Convierte texto o respuestas de entrevista en un solo bloque."""
    if isinstance(entrada, str):
        texto = entrada.strip()
        if texto:
            return texto

    if isinstance(entrada, Sequence) and not isinstance(entrada, (str, bytes)):
        respuestas = [
            respuesta.strip()
            for respuesta in entrada
            if isinstance(respuesta, str) and respuesta.strip()
        ]
        if respuestas:
            return "\n".join(
                f"Respuesta {indice}: {respuesta}"
                for indice, respuesta in enumerate(respuestas, start=1)
            )

    raise ErrorAgente(
        _NOMBRE,
        f"El campo '{_CAMPO_ENTRADA}' debe contener texto libre o una lista "
        "no vacia de respuestas del estudiante.",
    )


def ejecutar(estado: EstadoInvestigIA) -> EstadoInvestigIA:
    """Genera ``estado['perfil']`` sin modificar los demas campos."""
    # La entrada conversacional es transitoria y aun no forma parte del
    # contrato TypedDict. En ejecucion, el estado sigue siendo un dict.
    entrada = estado.get(_CAMPO_ENTRADA) # Clave transitoria para campo de entrada
    texto_estudiante = _normalizar_entrada(entrada)

    texto = invocar_agente(
        agente=_NOMBRE,
        sistema=_PROMPT_SISTEMA,
        usuario=(
            "Respuestas del estudiante:\n"
            f"{texto_estudiante}\n\n"
            "Construye su perfil academico."
        ),
        temperatura=0.1,
    )

    try:
        bloque_json = re.search(r"```(?:json)?\s*(.*?)```", texto, re.DOTALL)
        if bloque_json:
            texto = bloque_json.group(1).strip()
        datos = json.loads(texto)
    except json.JSONDecodeError as error:
        raise ErrorAgente(
            _NOMBRE,
            "El LLM no respondio con JSON valido. "
            f"Respuesta recibida: {texto[:200]}... Detalle: {error}",
        ) from error

    try:
        perfil = PerfilEstudiante(**datos)
    except Exception as error:
        raise ErrorAgente(
            _NOMBRE,
            "El JSON generado no cumple el contrato PerfilEstudiante. "
            f"Datos: {datos}. Detalle: {error}",
        ) from error

    resultado = dict(estado)
    resultado["perfil"] = perfil
    return resultado 
