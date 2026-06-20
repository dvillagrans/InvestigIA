# Estructura del repositorio — InvestigIA (Happy Path / PoC)

Esta es la estructura de carpetas con la que el equipo debe trabajar, está diseñada para lo contratos compartidos, estado del grafo, fixtures, manejo de errores, cliente de LLM único y con la repartición de agentes. Si algo no está aquí, probablemente significa que no se ha decidido en conjunto todavía, y justo es parte de lo que se trata en un inicio, ver como el equipo se pone de acuerdo y soluciona ese tipo de problemas.

```
InvestigIA-PoC/
│
├── README.md
├── ESTRUCTURA.md                  # este documento
├── .env.example
├── .gitignore
├── requirements.txt
│
├── contratos.py                   # archivo compartido — un solo dueño
├── fixtures.py                    # archivo compartido — un solo dueño
├── llm_client.py                  # archivo compartido — un solo dueño
├── errores.py                     # archivo compartido (ErrorAgente)
│
├── agentes/
│   ├── __init__.py
│   ├── agente_perfil.py           # Dev B
│   ├── agente_matching.py         # Dev A
│   ├── agente_metodologico.py     # Dev C
│   ├── agente_investigador.py     # Dev D
│   ├── agente_redaccion.py        # Dev D
│   └── agente_revision.py         # Dev A
│
├── orquestacion/
│   ├── __init__.py
│   ├── estado.py                  # EstadoInvestigIA (TypedDict)
│   └── grafo.py                   # construcción del grafo con LangGraph — Dev A + Dev C
│
├── pruebas/
│   ├── __init__.py
│   ├── test_agente_perfil.py
│   ├── test_agente_matching.py
│   ├── test_agente_metodologico.py
│   ├── test_agente_investigador.py
│   ├── test_agente_redaccion.py
│   ├── test_agente_revision.py
│   └── test_integracion.py        # corre el pipeline completo de extremo a extremo
│
└── docs/
    └── working_agreement_tecnico.pdf
```

---

## Los archivos compartidos van en la raíz, no en una subcarpeta

`contratos.py`, `fixtures.py`, `llm_client.py` y `errores.py` se importan constantemente desde cada agente, las pruebas y el grafo. Si vivieran dentro de una carpeta como `comun/`, `shared/` o `core/`, cada import se vuelve más largo.

```python
# Con los archivos en la raíz:
from contratos import PerfilEstudiante
from fixtures import PERFIL_GUION
from llm_client import invocar_agente
from errores import ErrorAgente
```

### Un archivo por agente, todos dentro de `agentes/`

Cada agente vive solo, con la firma común ya acordada (`def ejecutar(estado: EstadoInvestigIA) -> EstadoInvestigIA`). Por favor no hay que editar el archivo de otro agente.

### `orquestacion/` está separada y es de acceso restringido

`estado.py` (la definición de `EstadoInvestigIA`) y `grafo.py` (las aristas condicionales de LangGraph) son responsabilidad de quienes integran el pipeline. El resto del equipo **lee** `estado.py` para saber qué campo le toca escribir, pero no lo edita sin avisar al grupo — es exactamente la misma razón por la que `contratos.py` tiene un solo dueño.

### `pruebas/` separada del código del agente

Cada Dev prueba su propio agente de forma aislada sin depender de que los demás ya hayan terminado el suyo, usando los `fixtures.py` compartidos como entrada. `test_integracion.py` es la prueba que sí necesita que los seis agentes existan, y es la que se corre el día de integración.

---

## Quién es dueño de cada archivo compartido

| Archivo | Dueño (sube el primer borrador) | Acordado en |
|---|---|---|
| `contratos.py` | Dev C | Working Agreement, sección "Contratos de entrada/salida" |
| `fixtures.py` | Dev D | Working Agreement, sección "Los datos falsos (fixtures)" |
| `llm_client.py` | Dev B | Working Agreement, sección "Un único punto de invocación al LLM" |
| `errores.py` | Dev C (junto con `contratos.py`, mismo día) | Working Agreement, sección "Formato mínimo de error" |
| `orquestacion/estado.py` | Acordado en conjunto el día 1 | Working Agreement, sección "El estado compartido del grafo" |
| `orquestacion/grafo.py` | Dev A + Dev C (integración final) | Reparto de agentes, sección "Integración final del grafo" |

**Regla general:** estos seis archivos/carpetas se escriben o se modifican en conjunto durante la sesión del día 1 (o, en el caso de `grafo.py`, durante los días de integración). La persona asignada como dueño es quien los sube al repositorio y queda como punto de referencia si alguien tiene dudas después — no significa que solo esa persona pueda opinar sobre su contenido.

## De quién es cada agente:

| Agente | Archivo | Dueño |
|---|---|---|
| Perfil | `agentes/agente_perfil.py` | Dev B |
| Matching | `agentes/agente_matching.py` | Dev A |
| Metodológico | `agentes/agente_metodologico.py` | Dev C |
| Investigador | `agentes/agente_investigador.py` | Dev D |
| Redacción | `agentes/agente_redaccion.py` | Dev D |
| Revisión | `agentes/agente_revision.py` | Dev A |

---
