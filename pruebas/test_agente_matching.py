"""
test_agente_matching.py

Prueba aislada del Agente de Matching.

Objetivo:
- Verificar que el agente de Matching pueda ejecutarse sin depender de los
  demas agentes del pipeline.
- Confirmar que recibe estado["perfil"] como entrada.
- Confirmar que escribe estado["matching"] como salida.
- Validar que la salida cumpla el contrato MatchingResultado.
- Confirmar que el agente no modifica campos del estado que no le corresponden.

Ejecutar desde la raiz del repositorio:

    python pruebas/test_agente_matching.py

Entrada usada:
- PERFIL_GUION, definido en fixtures.py

Salida esperada:
- estado["matching"] lleno con un objeto MatchingResultado
"""

from agentes.agente_matching import ejecutar
from contratos import MatchingResultado, ResultadoMatching
from errores import ErrorAgente
from fixtures import PERFIL_GUION
from orquestacion.estado import EstadoInvestigIA


def construir_estado_de_entrada() -> EstadoInvestigIA:
    """
    Construye un estado minimo para probar el Agente de Matching.

    En el pipeline real, Matching corre despues del Agente de Perfil.
    Por eso, para esta prueba aislada, solo se llena estado["perfil"].

    Campos:
    - perfil: entrada del agente de Matching.
    - matching: salida esperada del agente de Matching.
    - esquema, evidencia, protocolo, revision: se dejan en None porque
      pertenecen a otros agentes.
    """
    estado: EstadoInvestigIA = {
        "perfil": None,
        "matching": None,
        "esquema": None,
        "evidencia": None,
        "protocolo": None,
        "revision": None,
    }

    estado["perfil"] = PERFIL_GUION

    return estado


def imprimir_separador(titulo: str) -> None:
    """
    Imprime un separador para que la salida en consola sea mas legible.
    """
    print()
    print("=" * 70)
    print(titulo)
    print("=" * 70)


def validar_matching_no_vacio(matching: MatchingResultado) -> None:
    """
    Valida que el MatchingResultado tenga al menos un resultado.

    El contrato MatchingResultado exige una lista de resultados. Para esta
    PoC debe existir por lo menos un candidato en el ranking.
    """
    assert matching.resultados is not None, "matching.resultados no debe ser None."
    assert len(matching.resultados) >= 1, "Debe existir al menos un resultado de matching."


def validar_resultado_individual(resultado: ResultadoMatching) -> None:
    """
    Valida un resultado individual del ranking.

    Cada ResultadoMatching debe tener:
    - investigador_id no vacio.
    - nombre no vacio.
    - score entre 0 y 1.
    - justificacion no vacia.
    """
    assert resultado.investigador_id.strip(), "investigador_id no debe estar vacio."
    assert resultado.nombre.strip(), "nombre no debe estar vacio."
    assert 0.0 <= resultado.score <= 1.0, "score debe estar entre 0.0 y 1.0."
    assert resultado.justificacion.strip(), "justificacion no debe estar vacia."


def validar_ranking_ordenado(matching: MatchingResultado) -> None:
    """
    Valida que el ranking este ordenado de mayor a menor score.

    Aunque en el happy path actual solo exista un investigador falso, esta
    validacion deja lista la prueba para cuando el catalogo tenga mas
    candidatos.
    """
    scores = [resultado.score for resultado in matching.resultados]
    scores_ordenados = sorted(scores, reverse=True)

    assert scores == scores_ordenados, "Los resultados deben estar ordenados por score descendente."


def validar_campos_no_modificados(
    estado_entrada: EstadoInvestigIA,
    estado_salida: EstadoInvestigIA,
) -> None:
    """
    Confirma que el agente solo escribio estado["matching"].

    Un agente no debe borrar ni modificar campos que pertenecen a otros
    agentes. Esta regla facilita la integracion posterior en el grafo.
    """
    for campo in estado_entrada:
        if campo == "matching":
            continue

        assert estado_salida[campo] == estado_entrada[campo], (
            f"El agente modifico estado['{campo}'], pero solo debe escribir estado['matching']."
        )


def validar_salida(
    estado_entrada: EstadoInvestigIA,
    estado_salida: EstadoInvestigIA,
) -> None:
    """
    Ejecuta todas las validaciones minimas de la prueba.

    Esta funcion concentra las reglas esperadas para que la prueba sea mas
    facil de leer desde main().
    """
    matching = estado_salida["matching"]

    assert matching is not None, "estado['matching'] no debe quedar en None."
    assert isinstance(matching, MatchingResultado), "estado['matching'] debe ser MatchingResultado."

    validar_matching_no_vacio(matching)
    validar_ranking_ordenado(matching)

    for resultado in matching.resultados:
        validar_resultado_individual(resultado)

    validar_campos_no_modificados(estado_entrada, estado_salida)


def main() -> None:
    """
    Ejecuta la prueba aislada del Agente de Matching.

    La prueba esta pensada para ejecutarse en consola sin pytest. Si algo
    falla, imprime un mensaje claro para ubicar el problema.
    """
    imprimir_separador("ENTRADA")
    estado_entrada = construir_estado_de_entrada()

    for campo, valor in estado_entrada.items():
        if valor is not None:
            print(f"{campo}:")
            print(f"  {valor}")

    imprimir_separador("EJECUTANDO AGENTE")

    try:
        estado_salida = ejecutar(estado_entrada)

    except ErrorAgente as error:
        print("FALLO CONTROLADO -- el agente reporto un ErrorAgente:")
        print(f"  agente : {error.agente}")
        print(f"  mensaje: {error.mensaje}")
        return

    except Exception as error:
        print("FALLO NO CONTROLADO -- esto no deberia pasar.")
        print("El agente debe convertir sus fallos internos en ErrorAgente.")
        print(f"  tipo   : {type(error).__name__}")
        print(f"  detalle: {error}")
        return

    imprimir_separador("SALIDA")
    print("estado['matching']:")
    print(f"  {estado_salida['matching']}")

    imprimir_separador("VALIDACION RAPIDA")

    try:
        validar_salida(estado_entrada, estado_salida)

    except AssertionError as error:
        print("PROBLEMA EN LA VALIDACION:")
        print(f"  {error}")
        return

    matching = estado_salida["matching"]
    mejor_resultado = matching.resultados[0]

    print("OK -- estado['matching'] fue generado correctamente.")
    print(f"  tipo de salida    : {type(matching).__name__}")
    print(f"  total resultados  : {len(matching.resultados)}")
    print(f"  mejor candidato   : {mejor_resultado.nombre}")
    print(f"  score             : {mejor_resultado.score}")
    print("OK -- la salida cumple el contrato MatchingResultado.")
    print("OK -- el agente no modifico campos que no le correspondian.")


if __name__ == "__main__":
    main()