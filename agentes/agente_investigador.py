"""
agente_investigador.py — Dev D

Agente Investigador (RAG).
Recibe EsquemaInvestigacion y produce EvidenciaRecuperada.

El agente toma el esquema de investigacion generado por el agente
metodologico e implementa RAG para ver cuales documentos del corpus local
son relevantes para la pregunta e hipotesis planteadas. Solo escribe
en estado['evidencia'].
"""
from __future__ import annotations

import numpy as np

from contratos import EvidenciaRecuperada
from errores import ErrorAgente
from fixtures import CORPUS_FALSO
from orquestacion.estado import EstadoInvestigIA

_NOMBRE = "investigador"
_TOP_K = 5
_UMBRAL_SCORE = 0.15

_modelo = None
_corpus_embeddings = None


def _get_model():
    global _modelo, _corpus_embeddings
    if _modelo is None:
        from sentence_transformers import SentenceTransformer
        _modelo = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
        _corpus_embeddings = _modelo.encode([doc.texto for doc in CORPUS_FALSO])
    return _modelo, _corpus_embeddings


def ejecutar(estado: EstadoInvestigIA) -> EstadoInvestigIA:
    esquema = estado.get("esquema")

    if esquema is None:
        raise ErrorAgente(
            _NOMBRE,
            "No hay un esquema en el estado. El agente metodologico se debe ejecutar primero.",
        )

    modelo, corpus_embeddings = _get_model()

    query_embedding = modelo.encode([esquema.pregunta])
    similitudes = query_embedding @ corpus_embeddings.T

    indices = np.argsort(similitudes[0])[::-1]

    fragmentos = []
    for i in indices:
        if similitudes[0][i] < _UMBRAL_SCORE:
            break
        fragmentos.append(CORPUS_FALSO[i])
        if len(fragmentos) >= _TOP_K:
            break

    resultado = dict(estado)
    resultado["evidencia"] = EvidenciaRecuperada(fragmentos=fragmentos)

    return resultado
