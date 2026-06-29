"""
test_contratos.py

Validación de que los contratos Pydantic funcionan correctamente:
- Los fixtures pasan la validación de sus modelos
- Datos inválidos son rechazados
- ErrorAgente funciona correctamente
"""
from contratos import (
    NivelAcademico,
    PerfilEstudiante,
    ResultadoMatching,
    MatchingResultado,
    EsquemaInvestigacion,
    FragmentoRecuperado,
    EvidenciaRecuperada,
    Protocolo,
    Observacion,
    ReporteRevision,
)
from errores import ErrorAgente
from pydantic import ValidationError


def test_perfil_valido() -> None:
    perfil = PerfilEstudiante(
        nombre="Estudiante",
        nivel=NivelAcademico.maestria,
        intereses=["robotica"],
    )
    assert perfil.nombre == "Estudiante"


def test_perfil_invalido_sin_intereses() -> None:
    try:
        PerfilEstudiante(nombre="E", nivel=NivelAcademico.maestria, intereses=[])
        assert False, "Debería haber lanzado ValidationError"
    except ValidationError:
        pass


def test_matching_resultado_valido() -> None:
    matching = MatchingResultado(
        resultados=[
            ResultadoMatching(
                investigador_id="INV-001",
                nombre="Dra. Torres",
                score=0.95,
                justificacion="Coincide",
            )
        ]
    )
    assert len(matching.resultados) == 1


def test_matching_resultado_vacio_rechazado() -> None:
    try:
        MatchingResultado(resultados=[])
        assert False, "Debería haber lanzado ValidationError"
    except ValidationError:
        pass


def test_esquema_valido() -> None:
    esquema = EsquemaInvestigacion(
        pregunta="¿Cómo?",
        objetivo_general="Desarrollar...",
        objetivos_especificos=["Revisar", "Implementar"],
        hipotesis="Se espera que...",
    )
    assert esquema.pregunta == "¿Cómo?"


def test_fragmento_sin_autores_rechazado() -> None:
    try:
        FragmentoRecuperado(
            id="DOC-01",
            titulo="Título",
            autores=[],  # vacío
            anio=2023,
            texto="Texto del documento...",
        )
        assert False, "Debería haber lanzado ValidationError"
    except ValidationError:
        pass


def test_evidencia_insuficiente() -> None:
    evidencia = EvidenciaRecuperada(fragmentos=[])
    assert evidencia.evidencia_insuficiente is True


def test_evidencia_suficiente() -> None:
    fragmento = FragmentoRecuperado(
        id="DOC-01",
        titulo="Título",
        autores=["Autor"],
        anio=2023,
        texto="Contenido del documento de prueba...",
    )
    evidencia = EvidenciaRecuperada(fragmentos=[fragmento])
    assert evidencia.evidencia_insuficiente is False


def test_protocolo_incompleto_rechazado() -> None:
    try:
        Protocolo(
            pregunta="¿Cómo?",
            objetivos="",
            hipotesis="H",
            metodologia="M",
            justificacion="J",
            alcance="A",
            resultados_esperados="R",
        )
        assert False, "Debería haber lanzado ValidationError (objetivos vacío)"
    except ValidationError:
        pass


def test_reporte_revision() -> None:
    reporte = ReporteRevision(
        puntaje_coherencia=0.85,
        aprobado=True,
        observaciones=[
            Observacion(seccion="hipotesis", descripcion="Bien formulada")
        ],
    )
    assert reporte.aprobado is True
    assert len(reporte.observaciones) == 1


def test_error_agente() -> None:
    try:
        raise ErrorAgente("metodologico", "fallo de prueba")
    except ErrorAgente as e:
        assert e.agente == "metodologico"
        assert e.mensaje == "fallo de prueba"
        assert str(e) == "[metodologico] fallo de prueba"


def test_fixtures_usan_contratos() -> None:
    """Verifica que los fixtures importados pasen validación."""
    from fixtures import (
        PERFIL_GUION,
        INVESTIGADOR_FALSO,
        CORPUS_FALSO,
        ESQUEMA_GUION,
        EVIDENCIA_GUION,
        PROTOCOLO_GUION,
    )

    assert isinstance(PERFIL_GUION, PerfilEstudiante)
    assert isinstance(INVESTIGADOR_FALSO, ResultadoMatching)
    assert isinstance(CORPUS_FALSO, list)
    assert all(isinstance(f, FragmentoRecuperado) for f in CORPUS_FALSO)
    assert isinstance(ESQUEMA_GUION, EsquemaInvestigacion)
    assert isinstance(EVIDENCIA_GUION, EvidenciaRecuperada)
    assert isinstance(PROTOCOLO_GUION, Protocolo)


def main() -> None:
    tests = [
        test_perfil_valido,
        test_perfil_invalido_sin_intereses,
        test_matching_resultado_valido,
        test_matching_resultado_vacio_rechazado,
        test_esquema_valido,
        test_fragmento_sin_autores_rechazado,
        test_evidencia_insuficiente,
        test_evidencia_suficiente,
        test_protocolo_incompleto_rechazado,
        test_reporte_revision,
        test_error_agente,
        test_fixtures_usan_contratos,
    ]

    fallos = 0
    for test in tests:
        try:
            test()
            print(f"✓ {test.__name__}")
        except AssertionError as e:
            print(f"✗ {test.__name__}: {e}")
            fallos += 1
        except Exception as e:
            print(f"✗ {test.__name__}: {type(e).__name__}: {e}")
            fallos += 1

    print()
    if fallos == 0:
        print(f"Todos los tests pasaron ({len(tests)}/{len(tests)})")
    else:
        print(f"{fallos} test(s) fallaron ({len(tests) - fallos}/{len(tests)} pasaron)")


if __name__ == "__main__":
    main()
