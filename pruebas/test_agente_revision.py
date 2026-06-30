"""
test_agente_revision.py

Prueba aislada del Agente de Revision.

Verifica que:
- Reciba estado["protocolo"] como entrada.
- Escriba estado["revision"] como salida.
- Genere un ReporteRevision valido.
- No modifique campos que pertenecen a otros agentes.

Ejecutar desde la raiz del repositorio:

    python -m pruebas.test_agente_revision
"""

from agentes.agente_revision import ejecutar
from contratos import Observacion, ReporteRevision
from errores import ErrorAgente
from fixtures import PROTOCOLO_GUION
from orquestacion.estado import EstadoInvestigIA


def construir_estado_de_entrada() -> EstadoInvestigIA:
    """Construye un estado minimo para probar Revision de forma aislada."""
    estado: EstadoInvestigIA = {
        "perfil": None,
        "matching": None,
        "esquema": None,
        "evidencia": None,
        "protocolo": None,
        "revision": None,
    }

    estado["protocolo"] = PROTOCOLO_GUION

    return estado


def imprimir_separador(titulo: str) -> None:
    """Imprime un separador para lectura en consola."""
    print()
    print("=" * 50)
    print(titulo)
    print("=" * 50)


def validar_revision(revision: ReporteRevision) -> None:
    """Valida los campos obligatorios de ReporteRevision."""
    assert 0.0 <= revision.puntaje_coherencia <= 1.0, (
        "puntaje_coherencia debe estar entre 0.0 y 1.0."
    )
    assert isinstance(revision.aprobado, bool), "aprobado debe ser booleano."
    assert isinstance(revision.observaciones, list), "observaciones debe ser una lista."

    for observacion in revision.observaciones:
        assert isinstance(observacion, Observacion), (
            "Cada elemento de observaciones debe ser Observacion."
        )
        assert observacion.seccion.strip(), "observacion.seccion no debe estar vacia."
        assert observacion.descripcion.strip(), "observacion.descripcion no debe estar vacia."


def validar_campos_no_modificados(
    estado_entrada: EstadoInvestigIA,
    estado_salida: EstadoInvestigIA,
) -> None:
    """Confirma que el agente solo escribio estado["revision"]."""
    for campo in estado_entrada:
        if campo == "revision":
            continue

        assert estado_salida[campo] == estado_entrada[campo], (
            f"El agente modifico estado['{campo}'], pero solo debe escribir estado['revision']."
        )


def validar_salida(
    estado_entrada: EstadoInvestigIA,
    estado_salida: EstadoInvestigIA,
) -> None:
    """Ejecuta las validaciones minimas de la prueba."""
    revision = estado_salida["revision"]

    assert revision is not None, "estado['revision'] no debe quedar en None."
    assert isinstance(revision, ReporteRevision), (
        "estado['revision'] debe ser ReporteRevision."
    )

    validar_revision(revision)
    validar_campos_no_modificados(estado_entrada, estado_salida)


def main() -> None:
    """Ejecuta la prueba aislada del Agente de Revision."""
    imprimir_separador("ENTRADA")
    estado_entrada = construir_estado_de_entrada()

    for campo, valor in estado_entrada.items():
        if valor is not None:
            print(f"{campo}:")

            if campo == "protocolo":
                print(f"  pregunta: {valor.pregunta}")
                print(f"  objetivos: {valor.objetivos[:120]}...")
                print(f"  metodologia: {valor.metodologia[:120]}...")
            else:
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
    print("estado['revision']:")
    print(f"  {estado_salida['revision']}")

    imprimir_separador("VALIDACION RAPIDA")

    try:
        validar_salida(estado_entrada, estado_salida)

    except AssertionError as error:
        print("PROBLEMA EN LA VALIDACION:")
        print(f"  {error}")
        return

    revision = estado_salida["revision"]

    print("OK -- estado['revision'] fue generado correctamente.")
    print(f"  tipo de salida       : {type(revision).__name__}")
    print(f"  puntaje_coherencia   : {revision.puntaje_coherencia}")
    print(f"  aprobado             : {revision.aprobado}")
    print(f"  total observaciones  : {len(revision.observaciones)}")
    print("OK -- la salida cumple el contrato ReporteRevision.")
    print("OK -- el agente no modifico campos que no le correspondian.")

    if revision.observaciones:
        print()
        print("OBSERVACIONES:")
        for observacion in revision.observaciones:
            print(f"  - [{observacion.seccion}] {observacion.descripcion}")


if __name__ == "__main__":
    main()
