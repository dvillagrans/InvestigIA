"""
agente_matching.py

Agente de Matching - Dev A.

Responsabilidad:
- Leer el perfil del estudiante desde estado["perfil"].
- Comparar los intereses del estudiante contra el catalogo disponible.
- Generar un MatchingResultado con ranking, score y justificacion.
- Escribir el resultado en estado["matching"].

Version PoC:
- No LLM.
- Similitud lexica simple con coseno
- Mantiene el ranking interpretable
- Usa el contrato Pydantic definido en contratos.py

"""

from __future__ import annotations

import logging
# Para quitar acentos
import math
import re
import unicodedata
from collections import Counter
from typing import Final

from contratos import MatchingResultado, PerfilEstudiante, ResultadoMatching
from errores import ErrorAgente
from fixtures import INVESTIGADOR_FALSO
from orquestacion.estado import EstadoInvestigIA


_NOMBRE_AGENTE: Final[str] = "matching"
_VERSION_AGENTE: Final[str] = "matching-deterministico-v1"
_MAX_ITERACIONES: Final[int] = 1

# En esta PoC el contrato PerfilEstudiante solo contiene intereses
# Por eso todo el peso se asigna a similitud de intereses
_PESOS: Final[dict[str, float]] = {
    "intereses": 1.0,
    "experiencia": 0.0,
    "habilidades": 0.0,
    "disponibilidad": 0.0,
}

logger = logging.getLogger(__name__)


def _validar_pesos(pesos: dict[str, float]) -> None:
    """
    Valida que los pesos del matching sean interpretables.

    Reglas:
    - Ningun peso puede ser negativo.
    - La suma de pesos debe ser 1.
    """
    if any(valor < 0 for valor in pesos.values()):
        raise ErrorAgente(
            _NOMBRE_AGENTE,
            "Los pesos del matching no pueden ser negativos.",
        )

    suma = sum(pesos.values())
    if not math.isclose(suma, 1.0, rel_tol=1e-9):
        raise ErrorAgente(
            _NOMBRE_AGENTE,
            f"La suma de pesos debe ser 1. Suma recibida: {suma}.",
        )


def _normalizar_texto(texto: str) -> list[str]:
    """
    Convierte texto libre en tokens comparables.

    Operaciones:
    - Pasa a minusculas.
    - Elimina acentos.
    - Conserva solo palabras alfanumericas.
    """
    texto = texto.lower()
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(caracter for caracter in texto if unicodedata.category(caracter) != "Mn")

    return re.findall(r"\b[a-z0-9]+\b", texto)


def _vectorizar(texto: str) -> Counter[str]:
    """
    Representa un texto como conteo de palabras.
    """
    return Counter(_normalizar_texto(texto))


def _similitud_coseno(texto_a: str, texto_b: str) -> float:
    """
    Calcula similitud coseno entre dos textos usando conteo de palabras.

    Regresa:
    - 0.0 si alguno de los textos queda vacio.
    - Un valor entre 0.0 y 1.0 cuando hay tokens comparables.
    """
    vector_a = _vectorizar(texto_a)
    vector_b = _vectorizar(texto_b)

    if not vector_a or not vector_b:
        return 0.0

    vocabulario = set(vector_a) | set(vector_b)

    producto_punto = sum(vector_a[palabra] * vector_b[palabra] for palabra in vocabulario)
    norma_a = math.sqrt(sum(valor**2 for valor in vector_a.values()))
    norma_b = math.sqrt(sum(valor**2 for valor in vector_b.values()))

    if norma_a == 0 or norma_b == 0:
        return 0.0

    return producto_punto / (norma_a * norma_b)


def _texto_perfil(perfil: PerfilEstudiante) -> str:
    """
    Construye el texto base del estudiante para comparar intereses.
    De lista a texto plano. En la PoC no se usan experiencia, habilidades ni disponibilidad.
    """
    return " ".join(perfil.intereses)


def _texto_candidato(candidato: ResultadoMatching) -> str:
    """
    Construye el texto base del candidato.

    En la PoC el fixture del investigador ya incluye la informacion relevante
    dentro de su justificacion.
    """
    return f"{candidato.nombre} {candidato.justificacion}"


def _calcular_score(perfil: PerfilEstudiante, candidato: ResultadoMatching) -> float:
    """
    Calcula el score formal del matching.

    Formula base:
        S(ai, s) = w1 Ii + w2 Ei + w3 Hi + w4 Di

    En esta PoC:
    - Ii se calcula con similitud coseno lexica.
    - Ei, Hi y Di quedan en 0 porque PerfilEstudiante todavia no contiene
      experiencia, habilidades ni disponibilidad.
    """
    texto_estudiante = _texto_perfil(perfil)
    texto_investigador = _texto_candidato(candidato)

    similitud_intereses = _similitud_coseno(texto_estudiante, texto_investigador)

    score = (
        _PESOS["intereses"] * similitud_intereses
        + _PESOS["experiencia"] * 0.0
        + _PESOS["habilidades"] * 0.0
        + _PESOS["disponibilidad"] * 0.0
    )

    return round(max(0.0, min(1.0, score)), 3)


def _construir_justificacion(
    perfil: PerfilEstudiante,
    candidato: ResultadoMatching,
    score: float,
) -> str:
    """
    Genera una justificacion breve y verificable para el resultado.
    """
    intereses = ", ".join(perfil.intereses)

    return (
        f"El candidato se relaciona con los intereses declarados "
        f"({intereses}). El score {score} se calculo mediante similitud "
        f"lexica entre el perfil del estudiante y la informacion disponible "
        f"del candidato."
    )


def _obtener_catalogo() -> list[ResultadoMatching]:
    """
    Regresa el catalogo disponible para el happy path.

    Por ahora se usa el investigador falso compartido en fixtures.py para
    mantener consistencia con las pruebas aisladas y la integracion.
    """
    return [INVESTIGADOR_FALSO]


def ejecutar(estado: EstadoInvestigIA) -> EstadoInvestigIA:
    """
    Ejecuta el agente de Matching.

    Parametros:
        estado: EstadoInvestigIA con estado["perfil"] lleno.

    Regresa:
        EstadoInvestigIA con estado["matching"] lleno.

    Lanza:
        ErrorAgente si falta el perfil, si el perfil no cumple contrato o
        si no se puede construir un resultado valido.
    """
    try:
        _validar_pesos(_PESOS)

        perfil = estado.get("perfil")

        # Si no hay perfil, no se puede ejecutar el agente de Matching. Se lanza ErrorAgente para que la orquestacion pueda manejarlo.
        if perfil is None:
            raise ErrorAgente(
                _NOMBRE_AGENTE,
                "No se recibio estado['perfil']. El agente de Matching necesita un PerfilEstudiante.",
            )

        # Valida que la entrada respete el contrato esperado.
        if not isinstance(perfil, PerfilEstudiante):
            raise ErrorAgente(
                _NOMBRE_AGENTE,
                f"estado['perfil'] debe ser PerfilEstudiante, pero se recibio {type(perfil).__name__}.",
            )

        logger.info(
            "Ejecutando agente %s con version %s e iteraciones maximas %s.",
            _NOMBRE_AGENTE,
            _VERSION_AGENTE,
            _MAX_ITERACIONES,
        )

        resultados: list[ResultadoMatching] = []

        # Calculo de score para cada candidato en el catalogo
        for candidato in _obtener_catalogo():
            score = _calcular_score(perfil, candidato)

            resultado = ResultadoMatching(
                investigador_id=candidato.investigador_id,
                nombre=candidato.nombre,
                score=score,
                justificacion=_construir_justificacion(perfil, candidato, score),
            )

            resultados.append(resultado)
        # Ranking de resultados por score descendente (max a min)
        resultados.sort(key=lambda item: item.score, reverse=True)

        if not resultados:
            raise ErrorAgente(
                _NOMBRE_AGENTE,
                "El catalogo de candidatos esta vacio. No fue posible generar ranking.",
            )

        # Salida formal del agente
        matching = MatchingResultado(resultados=resultados)

        nuevo_estado = dict(estado)
        nuevo_estado["matching"] = matching

        return nuevo_estado

    except ErrorAgente:
        raise

    except Exception as error:
        raise ErrorAgente(
            _NOMBRE_AGENTE,
            f"Fallo inesperado en el agente de Matching: {type(error).__name__}: {error}",
        )