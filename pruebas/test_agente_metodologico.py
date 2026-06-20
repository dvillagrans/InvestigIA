"""
test_agente_metodologico.py

Prueba aislada del Agente Metodológico.
Correr desde la raíz del repositorio:

    python pruebas/test_agente_metodologico.py
"""
from agentes.agente_metodologico import ejecutar
from contratos import MatchingResultado
from fixtures import PERFIL_GUION, INVESTIGADOR_FALSO
from orquestacion.estado import EstadoInvestigIA
from errores import ErrorAgente


def construir_estado_de_entrada() -> EstadoInvestigIA:
    estado: EstadoInvestigIA = {
        "perfil": None,
        "matching": None,
        "esquema": None,
        "evidencia": None,
        "protocolo": None,
        "revision": None,
    }
    estado["perfil"] = PERFIL_GUION
    estado["matching"] = MatchingResultado(resultados=[INVESTIGADOR_FALSO])
    return estado


def imprimir_separador(titulo: str) -> None:
    print()
    print("=" * 70)
    print(titulo)
    print("=" * 70)


def main() -> None:
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
        print("FALLO CONTROLADO -- el agente reporto un error:")
        print(f"  agente : {error.agente}")
        print(f"  mensaje: {error.mensaje}")
        return
    except Exception as error:
        print("FALLO NO CONTROLADO -- esto NO deberia pasar.")
        print("  El agente debe atrapar sus propios errores y lanzar")
        print("  ErrorAgente, no dejar pasar una excepcion generica.")
        print(f"  Tipo: {type(error).__name__}")
        print(f"  Detalle: {error}")
        return

    imprimir_separador("SALIDA")
    print("estado['esquema']:")
    print(f"  {estado_salida['esquema']}")

    imprimir_separador("VALIDACION RAPIDA")
    campo_propio = estado_salida["esquema"]
    if campo_propio is None:
        print("PROBLEMA: el campo de salida quedo en None.")
    else:
        print(f"OK -- el campo de salida quedo lleno, tipo: {type(campo_propio).__name__}")
        print(f"  pregunta            : {campo_propio.pregunta[:80]}...")
        print(f"  objetivo_general    : {campo_propio.objetivo_general[:80]}...")
        print(f"  objetivos_especificos: {len(campo_propio.objetivos_especificos)} elementos")
        print(f"  hipotesis           : {campo_propio.hipotesis[:80]}...")

    otros_campos_intactos = all(
        estado_salida[campo] == estado_entrada[campo]
        for campo in estado_entrada
        if campo != "esquema"
    )
    if otros_campos_intactos:
        print("OK -- el agente no modifico campos que no le correspondian.")
    else:
        print("PROBLEMA: el agente toco un campo del estado que no era suyo.")


if __name__ == "__main__":
    main()
