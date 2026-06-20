"""
test_agente_plantilla.py

Plantilla para probar UN agente de forma aislada, en consola, sin depender
de que los demas agentes ya esten terminados.


--------------------------
1. Copia este archivo a pruebas/test_agente_<nombre>.py
   (ej. pruebas/test_agente_metodologico.py)
2. Reemplaza las 4 secciones marcadas con "# >>> AJUSTAR" segun la tabla
   de abajo.
3. Corre el archivo solo, desde la raiz del repositorio:

       python pruebas/test_agente_metodologico.py

   Debe imprimir la entrada que recibio, la salida que produjo, y un
   resumen de validacion -- sin necesitar que ningun otro agente exista
   todavia.

Que entrada y que contrato de salida usa cada agente
--------------------------------------------------------
    Agente          Entrada (de fixtures.py)              Contrato de salida
    --------------  -------------------------------------  --------------------
    Perfil          texto libre                             PerfilEstudiante
    Matching        PERFIL_GUION                            MatchingResultado
    Metodologico    PERFIL_GUION, INVESTIGADOR_FALSO         EsquemaInvestigacion
    Investigador    ESQUEMA_GUION                            EvidenciaRecuperada
    Redaccion       ESQUEMA_GUION, EVIDENCIA_GUION           Protocolo
    Revision        PROTOCOLO_GUION                          ReporteRevision

Nota sobre el Agente de Perfil
---------------------------------
Es el unico que no recibe un fixture de contratos.py como entrada (su
entrada es la conversacion con el "estudiante"). Para probarlo solo, se
simulan las respuestas del guion como una lista de strings -- ver el
archivo ya adaptado pruebas/test_agente_perfil.py para el ejemplo
completo.
"""

# >>> AJUSTAR (1 de 4): importa SOLO el agente que vas a probar
from agentes.agente_metodologico import ejecutar

# >>> AJUSTAR (2 de 4): importa el/los fixture(s) que tu agente necesita
#     como entrada (ver tabla de arriba)
from fixtures import PERFIL_GUION, INVESTIGADOR_FALSO

# Estos dos imports no cambian: son comunes a las pruebas de cualquier agente
from orquestacion.estado import EstadoInvestigIA
from errores import ErrorAgente


def construir_estado_de_entrada() -> EstadoInvestigIA:
    """
    Arma un EstadoInvestigIA con SOLO los campos que tu agente necesita
    para correr, dejando el resto en None -- igual que estarian en el
    pipeline real si tu agente corriera en su turno.
    """
    estado: EstadoInvestigIA = {
        "perfil": None,
        "matching": None,
        "esquema": None,
        "evidencia": None,
        "protocolo": None,
        "revision": None,
    }

    # >>> AJUSTAR (3 de 4): llena aqui SOLO los campos de entrada de tu
    #     agente, usando los fixtures importados arriba. Ejemplo para el
    #     Agente Metodologico (recibe perfil + matching):
    estado["perfil"] = PERFIL_GUION
    estado["matching"] = INVESTIGADOR_FALSO

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
        print(f"FALLO CONTROLADO -- el agente reporto un error:")
        print(f"  agente : {error.agente}")
        print(f"  mensaje: {error.mensaje}")
        return
    except Exception as error:
        print(f"FALLO NO CONTROLADO -- esto NO deberia pasar.")
        print(f"  El agente debe atrapar sus propios errores y lanzar")
        print(f"  ErrorAgente, no dejar pasar una excepcion generica.")
        print(f"  Tipo: {type(error).__name__}")
        print(f"  Detalle: {error}")
        return

    imprimir_separador("SALIDA")
    # >>> AJUSTAR (4 de 4): imprime SOLO el campo que tu agente escribe.
    #     Ejemplo para el Agente Metodologico (escribe "esquema"):
    print("estado['esquema']:")
    print(f"  {estado_salida['esquema']}")

    imprimir_separador("VALIDACION RAPIDA")
    # Confirmaciones minimas de que el contrato se respeto. No reemplazan
    # una prueba formal, son una lectura rapida en consola.
    campo_propio = estado_salida["esquema"]  # >>> AJUSTAR el nombre del campo
    if campo_propio is None:
        print("PROBLEMA: el campo de salida quedo en None.")
    else:
        print(f"OK -- el campo de salida quedo lleno, tipo: {type(campo_propio).__name__}")

    # Confirmar que los demas campos del estado NO se tocaron (un agente
    # solo debe escribir su propio campo, nunca borrar ni modificar otros)
    otros_campos_intactos = all(
        estado_salida[campo] == estado_entrada[campo]
        for campo in estado_entrada
        if campo != "esquema"  # >>> AJUSTAR el nombre del campo
    )
    if otros_campos_intactos:
        print("OK -- el agente no modifico campos que no le correspondian.")
    else:
        print("PROBLEMA: el agente toco un campo del estado que no era suyo.")


if __name__ == "__main__":
    main()