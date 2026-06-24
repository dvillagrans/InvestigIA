"""      
agente_redaccion.py — Dev D                                                                                                                                                                

Agente de Redacción.                                                                                                                                                                       
Recibe EsquemaInvestigacion + EvidenciaRecuperada y produce Protocolo.

El agente toma el esquema generado por el agente metodológico y la
evidencia recuperada por el agente investigador, y redacta un protocolo                                                                                                                    
de investigación con siete secciones. Solo escribe en estado['protocolo'].                                                                                                               
"""   
from __future__ import annotations

import json

from contratos import Protocolo
from errores import ErrorAgente
from llm_client import invocar_agente
from orquestacion.estado import EstadoInvestigIA

_NOMBRE = "redaccion"

_PROMPT_SISTEMA = """\                                                                                                                                                                   
Eres un asistente de redaccion academica. Tu tarea es generar un protocolo \                                                                                                               
de investigacion a partir de un esquema y evidencia bibliografica recuperada.                                                                                                              

Debes responder EXCLUSIVAMENTE con un JSON valido con esta estructura:                                                                                                                     
{                                                                                                                                                                                          
    "pregunta": "...",
    "objetivos": "...",                                                                                                                                                                    
    "hipotesis": "...",                                                                                                                                                                  
    "metodologia": "...",
    "justificacion": "...",                                                                                                                                                                
    "alcance": "...",
    "resultados_esperados": "..."                                                                                                                                                          
}                                                                                                                                                                                        

Reglas:
- "pregunta": copia la pregunta de investigacion tal como aparece en el esquema.
- "hipotesis": copia la hipotesis tal como aparece en el esquema.                                                                                                                          
- "objetivos": redacta en prosa el objetivo general seguido de los especificos.                                                                                                            
- "metodologia": describe el enfoque metodologico citando los documentos relevantes por su ID.                                                                                             
- "justificacion": justifica la pertinencia del proyecto con base en la evidencia recuperada.                                                                                              
- "alcance": delimita que incluye y que no incluye el proyecto.                                                                                                                            
- "resultados_esperados": describe los productos y contribuciones esperados.                                                                                                               
- Si para alguna seccion no hay evidencia suficiente, escribe [sin fuente].                                                                                                                
- No incluyas texto fuera del JSON.                                                                                                                                                        
"""  


def ejecutar(estado: EstadoInvestigIA) -> EstadoInvestigIA:
    """
    Lee 'esquema' del estado que contiene EsquemaInvestigacion + EvidenciaRecuperada
    y consulta al LLM para producir Protocolo de Investigación

    Levanta ErrorAgente si:
        1. Esquema es None: el agente metodológico no corrió antes                                                                                                                                
        2. Evidencia es None: el agente investigador no corrió antes
        3. El LLM devuelve algo inválido, ya sea:                                                                                                                                                  
            - Texto vacío o fallo de conexión (lo lanza invocar_agente internamente)                                                                                                                 
            - JSON malformado (falla el json.loads)                                                                                                                                                  
            - JSON válido pero que no cumple el contrato Protocolo, por ejemplo un campo vacío o faltante (falla el Protocolo(**datos))  
    """

    esquema = estado.get("esquema")
    evidencia = estado.get("evidencia")

    if esquema is None:
        raise ErrorAgente(
            _NOMBRE,
            "No hay un esquema en el estado, el agente metodológico se debe ejecutar primero"
        )

    if evidencia is None:
        raise ErrorAgente(
            _NOMBRE,
            "No hay una evidencia en el estado, el agente investigador se debe ejecutar antes"
        )

    evidencia_texto = "\n\n".join(                                                                                                                                                             
    f"ID: {f.id}\n"                                                                                                                                                                        
    f"Titulo: {f.titulo}\n"                                                                                                                                                                
    f"Autores: {', '.join(f.autores)}\n"                                                                                                                                                   
    f"Anio: {f.anio}\n"                                                                                                                                                                    
    f"Texto: {f.texto}"                                                                                                                                                                    
    for f in evidencia.fragmentos
    ) or "[sin fuente]"                                                                                                                                                                        


    prompt_usuario = (
    f"Esquema de investigacion:\n"                                                                                                                                                         
    f"- Pregunta: {esquema.pregunta}\n"                                                                                                                                                  
    f"- Objetivo general: {esquema.objetivo_general}\n"
    f"- Objetivos especificos:\n"                                                                                                                                                          
    + "\n".join(f"  * {obj}" for obj in esquema.objetivos_especificos)
    + f"\n- Hipotesis: {esquema.hipotesis}\n\n"                                                                                                                                            
    f"Evidencia bibliografica recuperada:\n{evidencia_texto}\n\n"                                                                                                                          
    f"Genera el protocolo de investigacion."                                                                                                                                               
    )      

    try:
        texto = invocar_agente(
            agente = _NOMBRE,
            sistema = _PROMPT_SISTEMA,
            usuario = prompt_usuario,
            temperatura = 0.3
        )
    except ErrorAgente:
        raise

    try:
        datos = json.loads(texto)
    except json.JSONDecodeError as error:
        raise ErrorAgente(
            _NOMBRE,
            f"El LLM no está repondiendo con un JSON que sea válido"
            f"Respuesta recibida: {texto[:200]}... Detalle: {error}"
        )
    
    try:
        protocolo = Protocolo(**datos)
    except Exception as error:
        raise ErrorAgente(
            _NOMBRE,
            f"El Json que se generó no cumple con el protocolo"
            f"Datos: {datos} error: {error}"
        )
    
    resultado = dict(estado)
    resultado["protocolo"] = protocolo
    return resultado