"""
llm_client.py

Unico punto de invocacion al LLM para los seis agentes de InvestigIA.

Por que existe este archivo
----------------------------
Si cada desarrollador escribe su propia llamada a LM Studio -- con su propio
cliente, sus propias variables de entorno, su propio manejo de errores --
se generan cuatro configuraciones que van a ser distintas y complican la
integracion. Esta es la unica funcion que habla con el LLM;
todos los agentes la importan e implementan en sus propios prompts:

    from llm_client import invocar_agente

    texto = invocar_agente(
        agente="perfil",
        sistema="Eres un asistente que entrevista a un estudiante...",
        usuario="El estudiante dice: ...",
    )

Que resuelve este archivo
-----------------------------------------------------------------
1. Si LM Studio no esta corriendo, la funcion falla con un
   mensaje y no con un traceback crudo de la libreria openai.
2. Reintenta automaticamente 2 veces antes de fallar: los modelos locales
   cuantizados a veces tardan en "despertar" o la primera llamada falla por
   timeout de carga. Sin esto, cualquier Dev pensaria que algo esta roto
   cuando en realidad solo necesitaba reintentar.
3. Detecta respuestas vacias. Un LLM local a veces regresa string vacio sin
   lanzar ninguna excepcion (es una respuesta "exitosa" pero inutil). Si no
   se detecta aqui, un agente downstream recibiria un campo vacio y fallaria
   de forma confusa en Pydantic, lejos de donde realmente esta el problema.
4. Los fallos se reportan como ErrorAgente, igual que el resto del pipeline
   (ver errores.py), no como una excepcion generica de la libreria openai.

Variables de entorno
-----------------------------------------------------------------------------
    LLM_BASE_URL   -> http://localhost:1234/v1   (URL de LM Studio)
    LLM_API_KEY    -> lm-studio                  (no se valida en local)
    LLM_MODEL      -> gemma-4                    (nombre del modelo cargado)
"""

from __future__ import annotations

import os
import time

from openai import OpenAI, APIConnectionError, APITimeoutError

from errores import ErrorAgente


_NOMBRE_AGENTE_CLIENTE = "llm_client"

_BASE_URL = os.getenv("LLM_BASE_URL", "http://localhost:1234/v1")
_API_KEY = os.getenv("LLM_API_KEY", "lm-studio")
_MODELO_DEFECTO = os.getenv("LLM_MODEL", "gemma-4")

_MAX_INTENTOS = 3          # 2 reintentos
_ESPERA_ENTRE_INTENTOS = 2  # segundos
_TIMEOUT_SEGUNDOS = 60      # un modelo local cuantizado puede tardar

_cliente = OpenAI(
    base_url=_BASE_URL,
    api_key=_API_KEY,
    timeout=_TIMEOUT_SEGUNDOS,
)

def invocar_agente(
    agente: str,
    sistema: str,
    usuario: str,
    temperatura: float = 0.2,
    modelo: str | None = None) -> str:
    """
    Envia un prompt de sistema + usuario al LLM local y regresa el texto
    de la respuesta.

    Parametros
    ----------
    agente: nombre corto del agente que invoca (ej. "perfil", "matching").
        Se usa unicamente para que, si algo falla, el mensaje de error diga
        con claridad quien lo disparo.
    sistema: el prompt de sistema de ese agente (su "skill").
    usuario: el mensaje de usuario para esta invocacion puntual.
    temperatura: 0.1-0.2 para tareas deterministas (perfil, revision);
        0.4-0.6 para tareas con mas variabilidad deseada (redaccion).
    modelo: nombre del modelo a usar. Si no se especifica, se usa el de la
        variable de entorno LLM_MODEL (por defecto "gemma-4").

    Excepciones
    -----------
    Lanza ErrorAgente si, despues de reintentar, no fue posible conectar
    con LM Studio o si el modelo respondio con texto vacio.
    """
    modelo_a_usar = modelo or _MODELO_DEFECTO
    ultimo_error: Exception | None = None

    for intento in range(1, _MAX_INTENTOS + 1):
        try:
            respuesta = _cliente.chat.completions.create(
                model=modelo_a_usar,
                temperature=temperatura,
                messages=[
                    {"role": "system", "content": sistema},
                    {"role": "user", "content": usuario},
                ],
            )
            texto = respuesta.choices[0].message.content

            if texto is None or texto.strip() == "":
                raise ErrorAgente(
                    agente,
                    f"El modelo '{modelo_a_usar}' respondio con texto vacio "
                    f"(intento {intento}/{_MAX_INTENTOS}).",
                )

            return texto

        except ErrorAgente:
            # Respuesta vacia: no tiene caso reintentar de inmediato sin
            # que el llamador lo sepa, pero tampoco perdemos el intento de
            # reintento general -- lo dejamos seguir el ciclo normal.
            ultimo_error = ErrorAgente(
                agente,
                f"El modelo '{modelo_a_usar}' respondio con texto vacio "
                f"(intento {intento}/{_MAX_INTENTOS}).",
            )

        except (APIConnectionError, APITimeoutError) as error:
            ultimo_error = ErrorAgente(
                agente,
                f"No se pudo conectar con LM Studio en '{_BASE_URL}' "
                f"(intento {intento}/{_MAX_INTENTOS}). "
                f"Verifica que el servidor este corriendo y que el modelo "
                f"'{modelo_a_usar}' este cargado. Detalle: {error}",
            )

        except Exception as error:  # cualquier otro fallo inesperado de la libreria
            ultimo_error = ErrorAgente(
                agente,
                f"Fallo inesperado al invocar el modelo '{modelo_a_usar}' "
                f"(intento {intento}/{_MAX_INTENTOS}). Detalle: "
                f"{type(error).__name__}: {error}",
            )

        if intento < _MAX_INTENTOS:
            time.sleep(_ESPERA_ENTRE_INTENTOS)

    # Aqui se agotaron los intentos.
    raise ultimo_error


def verificar_conexion(modelo: str | None = None) -> bool:
    """
    Prueba rapida de un solo intento (sin reintentos) para confirmar que
    LM Studio esta corriendo y el modelo responde. Pensada para que cada
    desarrollador la corra el dia 1 antes de empezar a programar su agente:

        python -c "from llm_client import verificar_conexion; verificar_conexion()"

    Regresa True/False e imprime un mensaje legible en cualquier caso.
    No lanza ErrorAgente: esta funcion es para diagnostico manual, no para
    usarse dentro del flujo de un agente.
    """
    modelo_a_usar = modelo or _MODELO_DEFECTO
    print(f"Probando conexion con LM Studio en '{_BASE_URL}' (modelo: '{modelo_a_usar}')...")

    try:
        respuesta = _cliente.chat.completions.create(
            model=modelo_a_usar,
            temperature=0.0,
            messages=[
                {"role": "system", "content": "Responde solo con la palabra HOLA."},
                {"role": "user", "content": "Saluda."},
            ],
        )
        texto = (respuesta.choices[0].message.content or "").strip()

        if texto:
            print(f"Conexion exitosa. El modelo respondio: '{texto}'")
            return True

        print("El servidor respondio pero el texto vino vacio. Revisa el modelo cargado en LM Studio.")
        return False

    except (APIConnectionError, APITimeoutError) as error:
        print(
            f"No se pudo conectar con LM Studio en '{_BASE_URL}'.\n"
            f"Verifica que el servidor este corriendo y el modelo cargado.\n"
            f"Detalle: {error}"
        )
        return False

    except Exception as error:
        print(f"Fallo inesperado: {type(error).__name__}: {error}")
        return False


if __name__ == "__main__":
    verificar_conexion()