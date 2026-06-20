"""
errores.py

Forma uniforme de reportar un fallo, igual en los seis agentes y en
llm_client.py. Ningun agente regresa None en silencio ni imprime el error 
con print() y continua. Si algo sale mal, se lanza ErrorAgente con el nombre del agente
y un mensaje claro -- asi, quien integre el grafo sabe exactamente donde
mirar.
"""


class ErrorAgente(Exception):
    def __init__(self, agente: str, mensaje: str):
        self.agente = agente
        self.mensaje = mensaje
        super().__init__(f"[{agente}] {mensaje}")