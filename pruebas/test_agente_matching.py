"""
test_agente_matching.py

Prueba aislada del Agente de Matching.

Verifica que:
- Reciba estado["perfil"] como entrada.
- Escriba estado["matching"] como salida.
- Genere un MatchingResultado valido.
- No modifique campos que pertenecen a otros agentes.

Ejecutar desde la raiz del repositorio:

    python -m pruebas.test_agente_matching
"""

from agentes.agente_matching import ejecutar
from contratos import MatchingResultado, ResultadoMatching
from errores import ErrorAgente
from fixtures import PERFIL_GUION
from orquestacion.estado import EstadoInvestigIA


def construir_estado_de_entrada() -> EstadoInvestigIA:
    """Construye un estado minimo para probar Matching de forma aislada."""
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
    """Imprime un separador para lectura en consola."""
    print()
    print("=" * 50)
    print(titulo)
    print("=" * 50)


def validar_matching_no_vacio(matching: MatchingResultado) -> None:
    """Valida que exista al menos un resultado en el ranking."""
    assert matching.resultados is not None, "matching.resultados no debe ser None."
    assert len(matching.resultados) >= 1, "Debe existir al menos un resultado de matching."


def validar_resultado_individual(resultado: ResultadoMatching) -> None:
    """Valida los campos obligatorios de un ResultadoMatching."""
    assert resultado.investigador_id.strip(), "investigador_id no debe estar vacio."
    assert resultado.nombre.strip(), "nombre no debe estar vacio."
    assert 0.0 <= resultado.score <= 1.0, "score debe estar entre 0.0 y 1.0."
    assert resultado.justificacion.strip(), "justificacion no debe estar vacia."


def validar_ranking_ordenado(matching: MatchingResultado) -> None:
    """Valida que el ranking este ordenado por score descendente."""
    scores = [resultado.score for resultado in matching.resultados]
    scores_ordenados = sorted(scores, reverse=True)

    assert scores == scores_ordenados, "Los resultados deben estar ordenados por score descendente."


def validar_campos_no_modificados(
    estado_entrada: EstadoInvestigIA,
    estado_salida: EstadoInvestigIA,
) -> None:
    """Confirma que el agente solo escribio estado["matching"]."""
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
    """Ejecuta las validaciones minimas de la prueba."""
    matching = estado_salida["matching"]

    assert matching is not None, "estado['matching'] no debe quedar en None."
    assert isinstance(matching, MatchingResultado), "estado['matching'] debe ser MatchingResultado."

    validar_matching_no_vacio(matching)
    validar_ranking_ordenado(matching)

    for resultado in matching.resultados:
        validar_resultado_individual(resultado)

    validar_campos_no_modificados(estado_entrada, estado_salida)


def main() -> None:
    """Ejecuta la prueba aislada del Agente de Matching."""
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
