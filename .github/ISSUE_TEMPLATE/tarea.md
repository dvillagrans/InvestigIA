name: "Tarea de desarrollo"
description: "Tarea asignada a un desarrollador del equipo"
title: "[Dev X] "
labels: ["tarea"]
body:
  - type: input
    id: dev
    attributes:
      label: Desarrollador
      placeholder: "Dev A, Dev B, Dev C, Dev D"
    validations:
      required: true

  - type: textarea
    id: descripcion
    attributes:
      label: Descripción
      placeholder: "Qué se debe hacer"
    validations:
      required: true

  - type: textarea
    id: archivos
    attributes:
      label: Archivos a crear o modificar
      placeholder: |
        - agentes/agente_perfil.py
        - pruebas/test_agente_perfil.py
    validations:
      required: true

  - type: textarea
    id: criterios
    attributes:
      label: Criterios de aceptación
      placeholder: |
        - [ ] El agente pasa su prueba aislada
        - [ ] No modifica campos del estado que no le corresponden
        - [ ] Lanza ErrorAgente en caso de fallo
    validations:
      required: true

  - type: textarea
    id: dependencias
    attributes:
      label: Dependencias
      placeholder: "Qué necesita estar listo antes de empezar"
    validations:
      required: false
