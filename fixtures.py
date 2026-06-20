"""
fixtures.py

Datos falsos compartidos por todos para el happy path de InvestigIA: 
un unico investigador, un unico corpus local, y un unico
perfil-guion de estudiante mas el "rastro" completo que ese guion deja
en cada paso del pipeline (esquema, evidencia y protocolo de referencia).

Usar nada mas este archivo
----------------------------
Si cada desarrollador inventa su propio "investigador falso", su propio
"esquema de prueba" o su propio "protocolo de prueba", el agente de uno no
se va a ajustar con el de otro, porque no estan hablando del mismo dato.
Este archivo se genera una sola vez y se usa sin modificacion por los seis
agentes.

Los fixtures se construyen con los modelos de contratos.py
--------------------------------------------------------------------
Los fixtures no son diccionarios sueltos: se instancian usando los modelos
de Pydantic de contratos.py. Esto significa que si alguien edita este
archivo y deja un fixture mal formado, el archivo va a fallar al
importarse con un ValidationError claro en la maquina de quien lo rompio,
no hasta que el agente de otra persona falle al integrar.

Lo que tiene
------------
    PERFIL_GUION        -> PerfilEstudiante ya validado
    INVESTIGADOR_FALSO  -> ResultadoMatching ya validado
    CORPUS_FALSO        -> lista de FragmentoRecuperado ya validados
    ESQUEMA_GUION        -> EsquemaInvestigacion ya validado
    EVIDENCIA_GUION       -> EvidenciaRecuperada ya validada
    PROTOCOLO_GUION       -> Protocolo ya validado

Cada agente importa el fixture que necesita como ENTRADA para probarse de
forma aislada (ver pruebas/PLANTILLA_test_agente.py):

    Agente de Perfil          -> no necesita fixture de entrada (texto libre)
    Agente de Matching        -> from fixtures import PERFIL_GUION
    Agente Metodologico       -> from fixtures import PERFIL_GUION, INVESTIGADOR_FALSO
    Agente Investigador       -> from fixtures import ESQUEMA_GUION
    Agente de Redaccion       -> from fixtures import ESQUEMA_GUION, EVIDENCIA_GUION
    Agente de Revision        -> from fixtures import PROTOCOLO_GUION

Nota sobre el "rastro" (ESQUEMA_GUION, EVIDENCIA_GUION, PROTOCOLO_GUION)
--------------------------------------------------------------------------
Estos tres fixtures NO son lo que cada agente debe producir palabra por
palabra -- son una version de referencia, ya validada, de lo que el
pipeline produciria en cada paso si todo corriera siguiendo el guion. Sirven
para que el agente investigador, el de redaccion y el de revision puedan
probarse SOLOS, sin tener que esperar a que los agentes anteriores ya
esten terminados.
"""

from contratos import (
    NivelAcademico,
    PerfilEstudiante,
    ResultadoMatching,
    FragmentoRecuperado,
    EsquemaInvestigacion,
    EvidenciaRecuperada,
    Protocolo,
)


# ---------------------------------------------------------------------------
# Perfil-guion del estudiante
# ---------------------------------------------------------------------------
# El Agente de Perfil debe estar disenado para que, siguiendo el guion de
# entrevista acordado, SIEMPRE produzca un perfil compatible con este
# fixture. No es el perfil exacto que el agente debe devolver palabra por
# palabra, sino el resultado al que la entrevista debe converger.

PERFIL_GUION = PerfilEstudiante(
    nombre="Estudiante de prueba",
    nivel=NivelAcademico.maestria,
    intereses=["robotica movil", "vision por computadora"],
)


# ---------------------------------------------------------------------------
# Investigador falso
# ---------------------------------------------------------------------------
# El Agente de Matching siempre debe encontrar a este investigador como
# unico resultado del ranking. Las lineas de investigacion coinciden a
# proposito con los intereses de PERFIL_GUION, para que el matching
# converja siempre aqui sin necesidad de un calculo real de score.

INVESTIGADOR_FALSO = ResultadoMatching(
    investigador_id="INV-001",
    nombre="Dra. Ana Torres Medina",
    score=0.95,
    justificacion=(
        "Sus lineas de investigacion (robotica movil, vision por "
        "computadora) coinciden directamente con los intereses del "
        "estudiante."
    ),
)


# ---------------------------------------------------------------------------
# Corpus local fijo
# ---------------------------------------------------------------------------
# El Agente Investigador siempre debe recuperar fragmentos de esta lista,
# nunca de internet. Son 6 documentos: 4 relevantes al tema del guion
# (navegacion autonoma / vision por computadora) y 2 fuera de tema, para
# que quien construya el pipeline de recuperacion tenga algo que filtrar
# en vez de que el corpus completo sea siempre "correcto" por accidente.

CORPUS_FALSO: list[FragmentoRecuperado] = [
    FragmentoRecuperado(
        id="DOC-01",
        titulo="Navegacion autonoma en robots moviles mediante vision artificial",
        autores=["Garcia, R.", "Lopez, M."],
        anio=2023,
        texto=(
            "Este trabajo presenta un enfoque de navegacion autonoma para "
            "robots moviles basado en vision por computadora, evaluado en "
            "entornos de interior con obstaculos dinamicos."
        ),
    ),
    FragmentoRecuperado(
        id="DOC-02",
        titulo="Deteccion de obstaculos en tiempo real para robotica movil",
        autores=["Hernandez, P."],
        anio=2022,
        texto=(
            "Se propone un metodo de deteccion de obstaculos en tiempo real "
            "usando camaras RGB-D, aplicable a plataformas roboticas de bajo "
            "costo computacional."
        ),
    ),
    FragmentoRecuperado(
        id="DOC-03",
        titulo="Vision por computadora aplicada al control de robots moviles",
        autores=["Ramirez, S.", "Torres, A."],
        anio=2021,
        texto=(
            "Se revisan tecnicas de vision por computadora para el control "
            "reactivo de robots moviles, incluyendo segmentacion semantica "
            "y seguimiento visual."
        ),
    ),
    FragmentoRecuperado(
        id="DOC-04",
        titulo="Localizacion y mapeo simultaneo (SLAM) con sensores visuales",
        autores=["Castillo, J.", "Morales, D."],
        anio=2023,
        texto=(
            "Se presenta una implementacion de SLAM visual para robots "
            "moviles en interiores, comparando su precision frente a "
            "metodos basados en LIDAR."
        ),
    ),
    # --- Documentos fuera de tema, a proposito, para que el pipeline de
    #     recuperacion tenga algo real que descartar/priorizar. ---
    FragmentoRecuperado(
        id="DOC-05",
        titulo="Modelos de lenguaje aplicados a la generacion de texto academico",
        autores=["Vega, L."],
        anio=2024,
        texto=(
            "Se analiza el uso de modelos de lenguaje de gran escala para "
            "asistir en la redaccion de articulos cientificos en ciencias "
            "sociales."
        ),
    ),
    FragmentoRecuperado(
        id="DOC-06",
        titulo="Optimizacion energetica en redes de sensores inalambricos",
        autores=["Mendoza, F.", "Cruz, I."],
        anio=2020,
        texto=(
            "Este articulo aborda estrategias de optimizacion energetica "
            "para prolongar la vida util de redes de sensores inalambricos "
            "desplegadas en exteriores."
        ),
    ),
]


# ---------------------------------------------------------------------------
# Esquema de investigacion de referencia
# ---------------------------------------------------------------------------
# Es la salida que el Agente Metodologico deberia producir al recibir
# PERFIL_GUION + INVESTIGADOR_FALSO. Sirve como ENTRADA de prueba para el
# Agente Investigador y el Agente de Redaccion, sin que tengan que esperar
# a que el Agente Metodologico (Dev C) ya este terminado.

ESQUEMA_GUION = EsquemaInvestigacion(
    pregunta=(
        "Como puede mejorarse la navegacion autonoma de un robot movil en "
        "entornos de interior mediante tecnicas de vision por computadora?"
    ),
    objetivo_general=(
        "Disenar e implementar un sistema de navegacion autonoma para "
        "robots moviles basado en vision por computadora."
    ),
    objetivos_especificos=[
        "Revisar el estado del arte en navegacion autonoma y deteccion de obstaculos.",
        "Implementar un modulo de deteccion de obstaculos en tiempo real.",
        "Evaluar el desempeno del sistema en un entorno de interior controlado.",
    ],
    hipotesis=(
        "Un sistema de navegacion basado en vision por computadora reduce "
        "las colisiones con obstaculos dinamicos en comparacion con "
        "metodos basados unicamente en sensores de distancia."
    ),
)


# ---------------------------------------------------------------------------
# Evidencia recuperada de referencia
# ---------------------------------------------------------------------------
# Es la salida que el Agente Investigador deberia producir al recibir
# ESQUEMA_GUION y filtrar CORPUS_FALSO (descartando los documentos fuera
# de tema DOC-05 y DOC-06). Sirve como ENTRADA de prueba para el Agente
# de Redaccion, sin que tenga que esperar a que el Agente Investigador
# (Dev D) ya este terminado.

EVIDENCIA_GUION = EvidenciaRecuperada(
    fragmentos=[doc for doc in CORPUS_FALSO if doc.id in ("DOC-01", "DOC-02", "DOC-03", "DOC-04")]
)


# ---------------------------------------------------------------------------
# Protocolo de referencia
# ---------------------------------------------------------------------------
# Es la salida que el Agente de Redaccion deberia producir al recibir
# ESQUEMA_GUION + EVIDENCIA_GUION. Sirve como ENTRADA de prueba para el
# Agente de Revision, sin que tenga que esperar a que el Agente de
# Redaccion (Dev D) ya este terminado.

PROTOCOLO_GUION = Protocolo(
    pregunta=ESQUEMA_GUION.pregunta,
    objetivos=(
        ESQUEMA_GUION.objetivo_general
        + " Especificamente: "
        + "; ".join(ESQUEMA_GUION.objetivos_especificos)
        + "."
    ),
    hipotesis=ESQUEMA_GUION.hipotesis,
    metodologia=(
        "Se propone un enfoque cuantitativo experimental, con pruebas "
        "controladas en un entorno de interior, siguiendo los hallazgos "
        "de DOC-01 y DOC-04 sobre navegacion autonoma y SLAM visual."
    ),
    justificacion=(
        "El laboratorio de Robotica y Mecatronica cuenta con lineas "
        "activas en navegacion autonoma; este proyecto se alinea "
        "directamente con esas lineas y con el investigador recomendado."
    ),
    alcance=(
        "El proyecto se limita a la navegacion en entornos de interior "
        "con obstaculos estaticos y dinamicos controlados; no incluye "
        "navegacion en exteriores ni en entornos no estructurados."
    ),
    resultados_esperados=(
        "Un prototipo funcional de navegacion autonoma y un articulo "
        "tecnico documentando los resultados experimentales."
    ),
)