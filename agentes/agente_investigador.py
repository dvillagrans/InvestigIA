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


from contratos import EvidenciaRecuperada
from errores import ErrorAgente
from fixtures import CORPUS_FALSO
from orquestacion.estado import EstadoInvestigIA

from sentence_transformers import SentenceTransformer
import numpy as np                                                                                                                         

_NOMBRE = "investigador"
_MODELO = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
_CORPUS_EMBEDDINGS = _MODELO.encode([doc.texto for doc in CORPUS_FALSO])


def ejecutar(estado: EstadoInvestigIA) -> EstadoInvestigIA:
    """
    Lee 'esquema' del estado, usa RAG para recuperar los fragmentos mas relevantes
    del CORPUS_FALSO, y escribe el resultado en estado['evidencia']

    Indica un error si el resultado es un None
    """
    esquema = estado.get("esquema")

    if esquema is None:
        raise ErrorAgente(
            _NOMBRE,
            "No hay un esquema en el estado. El agente metodologico se debe ejecutar primero.",
        )
    
    query_embedding = _MODELO.encode([esquema.pregunta])
    similitudes = query_embedding @ _CORPUS_EMBEDDINGS.T

    indices = np.argsort(similitudes[0])[::-1][:4]
    fragmentos = [CORPUS_FALSO[i] for i in indices]

    resultado = dict(estado)
    resultado["evidencia"] = EvidenciaRecuperada(fragmentos = fragmentos)

    return resultado
