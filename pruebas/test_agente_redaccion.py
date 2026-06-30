"""
test_agente_redaccion.py

Prueba aislada del Agente de Redacción.
"""

from agentes.agente_redaccion import ejecutar
from contratos import Protocolo
from orquestacion.estado import EstadoInvestigIA
from fixtures import ESQUEMA_GUION, EVIDENCIA_GUION
from errores import ErrorAgente

def construir_estado_de_entrada() -> EstadoInvestigIA:
    estado: EstadoInvestigIA = {
        "perfil": None,
        "matching": None,
        "esquema" : None,
        "evidencia" : None,
        "protocolo" : None,
        "revision" : None
    }
    estado["esquema"] = ESQUEMA_GUION
    estado["evidencia"] = EVIDENCIA_GUION
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
            print(f"{campo}")
            print(f"    {valor}")
    
    imprimir_separador("EJECUTANDO AGENTE")
    try:
        estado_salida = ejecutar(estado_entrada)
    except ErrorAgente as error:
        print("Fallo controlado: EL agente reporto un error:")
        print(f"    Agente : {error.agente}")
        print(f"    Mensaje: {error.mensaje}")
        return 
    except Exception as error:
        print("FALLO NO CONTROLADO -- esto NO deberia pasar.")
        print(f"  Tipo: {type(error).__name__}")
        print(f"  Detalle: {error}")
        return

    imprimir_separador("SALIDA")
    print("estado['protocolo']")
    print(f" {estado_salida['protocolo']}")

    imprimir_separador("VALIDAR PROTOCOLO")
    protocolo = estado_salida["protocolo"]
    if protocolo is None:
        print("El protocolo quedó como None!")
    else:
        print("OK El campo de salida si es un Protocolo")
        secciones = ["pregunta", "objetivos", "hipotesis", "metodologia", "justificacion", "alcance", "resultados_esperados"]
        for seccion in secciones:
            print(f"    {seccion}: {getattr(protocolo,seccion)[:60]}...")
    
    otros_intactos = all(estado_salida[campo] == estado_entrada[campo]
                        for campo in estado_entrada
                        if campo != "protocolo")
    if otros_intactos:
        print("OK el agente no toco nada de otros campos del estado")
    else:
        print("PROBLEMA: El agente toco campos del estado que no le corresponían")

if __name__ == "__main__":
    main()
