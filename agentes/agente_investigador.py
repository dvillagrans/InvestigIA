"""
agente_investigador.py — Dev D

Agente Investigador (RAG).
Recibe EsquemaInvestigacion y produce EvidenciaRecuperada.

El agente toma el esquema de investigacion generado por el agente
metodologico y consulta al LLM cuales documentos del corpus local
son relevantes para la pregunta e hipotesis planteadas. Solo escribe
en estado['evidencia'].
"""
from __future__ import annotations

import json

from contratos import EvidenciaRecuperada
from errores import ErrorAgente
from fixtures import CORPUS_FALSO
from llm_client import invocar_agente
from orquestacion.estado import EstadoInvestigIA

_NOMBRE = "investigador"

_PROMPT_SISTEMA = """\
Eres un asistente de recuperacion de evidencia academica. Tu tarea es 
evaluar una lista de documentos y determinar cuales son relevantes para 
una pregunta de investigacion e hipotesis dadas.

Debes responder EXCLUSIVAMENTE con un JSON valido con esta estructura:
{
    "ids_relevantes": ["DOC-XX", "DOC-YY"]
}

Reglas:
- Incluye el id de un documento solo si su contenido esta directamente relacionado con la pregunta o hipotesis de investigacion.
- Si ningun documento es relevante, devuelve una lista vacia: {"ids_relevantes": []}.
- No incluyas texto fuera del JSON.
- No inventes IDs que no aparezcan en la lista proporcionada.
"""


def ejecutar(estado: EstadoInvestigIA) -> EstadoInvestigIA:
    """
    Lee 'esquema' del estado, consulta al LLM cuales documentos del
    CORPUS_FALSO del PoC son relevantes, y escribe el resultado en estado['evidencia'].

    Levanta ErrorAgente si:
    - El esquema es None.
    - El LLM no responde o responde con texto vacio.
    - La respuesta del LLM no es un JSON valido.
    - Algun ID devuelto por el LLM no existe en el corpus.
    """
    esquema = estado.get("esquema")

    if esquema is None:
        raise ErrorAgente(
            _NOMBRE,
            "No hay un esquema en el estado. El agente metodologico se debe ejecutar primero.",
        )

    corpus_texto = "\n\n".join(
        f"ID: {doc.id}\n"
        f"Titulo: {doc.titulo}\n"
        f"Autores: {', '.join(doc.autores)}\n"
        f"Anio: {doc.anio}\n"
        f"Texto: {doc.texto}"
        for doc in CORPUS_FALSO
    )

    prompt_usuario = (
        f"Pregunta de investigacion:\n{esquema.pregunta}\n\n"
        f"Hipotesis:\n{esquema.hipotesis}\n\n"
        f"Documentos disponibles:\n{corpus_texto}\n\n"
        f"Indica que IDs son relevantes para la pregunta e hipotesis."
    )

    try:
        texto = invocar_agente(
            agente=_NOMBRE,
            sistema=_PROMPT_SISTEMA,
            usuario=prompt_usuario,
            temperatura=0.0,
        )
    except ErrorAgente:
        raise

    try:
        datos = json.loads(texto)
    except json.JSONDecodeError as error:
        raise ErrorAgente(
            _NOMBRE,
            f"El LLM no respondio con JSON valido. "
            f"Respuesta recibida: {texto[:200]}... Detalle: {error}",
        )

    ids_relevantes = datos.get("ids_relevantes", [])

    indice_corpus = {doc.id: doc for doc in CORPUS_FALSO}
    ids_invalidos = [id_ for id_ in ids_relevantes if id_ not in indice_corpus]
    if ids_invalidos:
        raise ErrorAgente(
            _NOMBRE,
            f"El LLM se inventó estos IDs que no existen en el corpus: {ids_invalidos}",
        )

    fragmentos = [indice_corpus[id_] for id_ in ids_relevantes]

    resultado = dict(estado)
    resultado["evidencia"] = EvidenciaRecuperada(fragmentos=fragmentos)
    return resultado
