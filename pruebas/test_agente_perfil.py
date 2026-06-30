"""
test_agente_perfil.py

Prueba aislada del Agente de Perfil.

Ejecutar desde la raiz con: python -m pruebas.test_agente_perfil
Requiere LM Studio activo y el modelo configurado cargado.
"""
import unittest
from typing import cast
from unittest.mock import patch

from agentes.agente_perfil import ejecutar
from contratos import PerfilEstudiante
from errores import ErrorAgente
from fixtures import PERFIL_GUION
from orquestacion.estado import EstadoInvestigIA


# No se usa un fixture: estas respuestas representan una entrevista breve.
RESPUESTAS_ESTUDIANTE = [
    "Me llamo Estudiante de prueba.",
    "Actualmente estudio una maestria.",
    "Me interesa investigar robotica movil y vision por computadora.",
]


def construir_estado_de_entrada() -> EstadoInvestigIA:
    estado: dict[str, object] = {
        "entrada_usuario": RESPUESTAS_ESTUDIANTE,
        "perfil": None,
        "matching": None,
        "esquema": None,
        "evidencia": None,
        "protocolo": None,
        "revision": None,
    }
    return cast(EstadoInvestigIA, estado)


def imprimir_separador(titulo: str) -> None:
    print()
    print("=" * 70)
    print(titulo)
    print("=" * 70)


def main() -> None:
    imprimir_separador("ENTRADA")
    estado_entrada = construir_estado_de_entrada()
    for respuesta in RESPUESTAS_ESTUDIANTE:
        print(f"  - {respuesta}")

    imprimir_separador("EJECUTANDO AGENTE")
    try:
        estado_salida = ejecutar(estado_entrada)
    except ErrorAgente as error:
        print("FALLO CONTROLADO -- el agente reporto un error:")
        print(f"  agente : {error.agente}")
        print(f"  mensaje: {error.mensaje}")
        raise SystemExit(1) from error
    except Exception as error:
        print("FALLO NO CONTROLADO -- esto NO deberia pasar.")
        print(f"  Tipo: {type(error).__name__}")
        print(f"  Detalle: {error}")
        raise SystemExit(1) from error

    imprimir_separador("SALIDA")
    print("estado['perfil']:")
    print(f"  {estado_salida['perfil']}")

    imprimir_separador("VALIDACION RAPIDA")
    perfil = estado_salida.get("perfil")
    if not isinstance(perfil, PerfilEstudiante):
        print("PROBLEMA: la salida no es un PerfilEstudiante.")
        raise SystemExit(1)


    print(f"OK -- nombre    : {perfil.nombre}")
    print(f"OK -- nivel     : {perfil.nivel.value}")
    print(f"OK -- intereses : {', '.join(perfil.intereses)}")

    otros_campos_intactos = all(
        estado_salida.get(campo) == valor
        for campo, valor in estado_entrada.items()
        if campo != "perfil"
    )
    if not otros_campos_intactos:
        print("PROBLEMA: el agente modifico campos que no le correspondian.")
        raise SystemExit(1)
    print("OK -- el agente no modifico campos que no le correspondian.")

    imprimir_separador("VALIDACION DE ERROR")
    estado_sin_entrada = dict(estado_entrada)
    estado_sin_entrada.pop("entrada_usuario", None)
    try:
        ejecutar(cast(EstadoInvestigIA, estado_sin_entrada))
    except ErrorAgente as error:
        print(f"OK -- entrada faltante produjo ErrorAgente: {error}")
    else:
        print("PROBLEMA: una entrada faltante no produjo ErrorAgente.")
        raise SystemExit(1)


class TestAgentePerfil(unittest.TestCase):
    @patch(
        "agentes.agente_perfil.invocar_agente",
        return_value=PERFIL_GUION.model_dump_json(),
    )
    def test_genera_perfil_sin_modificar_otros_campos(self, _mock_llm) -> None:
        entrada = construir_estado_de_entrada()
        salida = ejecutar(entrada)

        self.assertIsInstance(salida["perfil"], PerfilEstudiante)
        self.assertEqual(salida["perfil"], PERFIL_GUION)
        self.assertIsNone(entrada["perfil"])
        for campo, valor in entrada.items():
            if campo != "perfil":
                self.assertEqual(salida.get(campo), valor)

    def test_entrada_faltante_lanza_error_agente(self) -> None:
        with self.assertRaises(ErrorAgente):
            ejecutar(cast(EstadoInvestigIA, {"perfil": None}))

    @patch("agentes.agente_perfil.invocar_agente", return_value="no es json")
    def test_respuesta_invalida_lanza_error_agente(self, _mock_llm) -> None:
        with self.assertRaises(ErrorAgente):
            ejecutar(construir_estado_de_entrada())


if __name__ == "__main__":
    main()
