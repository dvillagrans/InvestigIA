name: "Archivo compartido"
description: "Tarea sobre contratos, fixtures, llm_client o errores"
title: "[Shared] "
labels: ["tarea", "shared"]
body:
  - type: input
    id: dev
    attributes:
      label: Responsable
      placeholder: "Dev C, Dev D, etc."
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
      label: Archivos afectados
      placeholder: |
        - contratos.py
    validations:
      required: true

  - type: textarea
    id: criterios
    attributes:
      label: Criterios de aceptación
      placeholder: |
        - [ ] Los modelos Pydantic validan correctamente
        - [ ] Los fixtures usan los modelos de contratos.py
    validations:
      required: true
