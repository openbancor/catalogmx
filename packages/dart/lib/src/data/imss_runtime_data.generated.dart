// GENERATED FILE. DO NOT EDIT.
// Run: python scripts/sync_imss_runtime_data.py

const String imssTablesJson = r'''
{
  "_meta": {
    "schema_version": 2,
    "description": "Tablas IMSS México - cuotas obrero-patronales y modalidades voluntarias",
    "calculation": "Parámetros históricos para cuotas IMSS, Modalidad 40 y Modalidad 10",
    "updated": "2026-08-29",
    "verification": {
      "cuotas_obrero_patronales": "verified",
      "modalidad_40": "verified",
      "modalidad_10": "legacy_unverified"
    },
    "sources": {
      "lss": {
        "authority": "Cámara de Diputados",
        "title": "Ley del Seguro Social",
        "url": "https://www.diputados.gob.mx/LeyesBiblio/pdf/LSS.pdf"
      },
      "reforma_pensiones_2020": {
        "authority": "Diario Oficial de la Federación",
        "title": "Decreto de reforma a la Ley del Seguro Social y Ley de los Sistemas de Ahorro para el Retiro",
        "published_at": "2020-12-16",
        "url": "https://www.dof.gob.mx/nota_detalle.php?codigo=5607729&fecha=16/12/2020"
      },
      "uma_2023": {
        "authority": "INEGI",
        "title": "Unidad de Medida y Actualización 2023",
        "url": "https://www.inegi.org.mx/contenidos/saladeprensa/boletines/2023/UMA/UMA2023.pdf"
      },
      "uma_2024": {
        "authority": "INEGI",
        "title": "Unidad de Medida y Actualización 2024",
        "published_at": "2024-01-09",
        "url": "https://www.inegi.org.mx/contenidos/saladeprensa/boletines/2024/UMA/UMA2024.pdf"
      },
      "uma_2025": {
        "authority": "INEGI",
        "title": "Unidad de Medida y Actualización 2025",
        "published_at": "2025-01-09",
        "url": "https://www.inegi.org.mx/contenidos/saladeprensa/boletines/2025/uma/uma2025.pdf"
      },
      "uma_2026": {
        "authority": "INEGI",
        "title": "Unidad de Medida y Actualización 2026",
        "published_at": "2026-01-08",
        "url": "https://www.inegi.org.mx/contenidos/saladeprensa/boletines/2026/uma/uma2026.pdf"
      },
      "salario_minimo_2024": {
        "authority": "CONASAMI / Diario Oficial de la Federación",
        "title": "Salarios mínimos generales 2024",
        "url": "https://www.dof.gob.mx/nota_detalle.php?codigo=5711066"
      },
      "salario_minimo_2025": {
        "authority": "CONASAMI",
        "title": "Salarios mínimos generales 2025",
        "url": "https://www.gob.mx/conasami"
      },
      "salario_minimo_2026": {
        "authority": "CONASAMI / Diario Oficial de la Federación",
        "title": "Salarios mínimos generales 2026",
        "published_at": "2025-12-09",
        "url": "https://www.dof.gob.mx/nota_detalle.php?codigo=5775534&fecha=09/12/2025"
      }
    }
  },
  "uma": {
    "2023": {
      "diaria": 103.74,
      "mensual": 3153.7,
      "anual": 37844.4,
      "vigencia_desde": "2023-02-01",
      "vigencia_hasta": "2024-01-31",
      "source_id": "uma_2023"
    },
    "2024": {
      "diaria": 108.57,
      "mensual": 3300.53,
      "anual": 39606.36,
      "vigencia_desde": "2024-02-01",
      "vigencia_hasta": "2025-01-31",
      "source_id": "uma_2024"
    },
    "2025": {
      "diaria": 113.14,
      "mensual": 3439.46,
      "anual": 41273.52,
      "vigencia_desde": "2025-02-01",
      "vigencia_hasta": "2026-01-31",
      "source_id": "uma_2025"
    },
    "2026": {
      "diaria": 117.31,
      "mensual": 3566.22,
      "anual": 42794.64,
      "vigencia_desde": "2026-02-01",
      "vigencia_hasta": "2027-01-31",
      "source_id": "uma_2026"
    }
  },
  "salario_minimo": {
    "2024": {
      "general": 248.93,
      "frontera": 374.89,
      "vigencia_desde": "2024-01-01",
      "vigencia_hasta": "2024-12-31",
      "source_id": "salario_minimo_2024"
    },
    "2025": {
      "general": 278.8,
      "frontera": 419.88,
      "vigencia_desde": "2025-01-01",
      "vigencia_hasta": "2025-12-31",
      "source_id": "salario_minimo_2025"
    },
    "2026": {
      "general": 315.04,
      "frontera": 440.87,
      "vigencia_desde": "2026-01-01",
      "vigencia_hasta": "2026-12-31",
      "source_id": "salario_minimo_2026"
    }
  },
  "cuotas_imss": {
    "enfermedad_maternidad": {
      "prestaciones_en_especie": {
        "descripcion": "Prestaciones en especie (cuota fija)",
        "patron": 0.204,
        "trabajador": 0.0,
        "base": "uma_diaria"
      },
      "prestaciones_en_especie_excedente": {
        "descripcion": "Prestaciones en especie (excedente de 3 UMA)",
        "patron": 0.011,
        "trabajador": 0.004,
        "umbral_uma": 3,
        "base": "excedente_sbc_diario"
      },
      "prestaciones_en_dinero": {
        "descripcion": "Prestaciones en dinero",
        "patron": 0.007,
        "trabajador": 0.0025,
        "base": "salario"
      },
      "gastos_medicos_pensionados": {
        "descripcion": "Gastos médicos para pensionados",
        "patron": 0.0105,
        "trabajador": 0.00375,
        "base": "salario"
      }
    },
    "invalidez_vida": {
      "descripcion": "Invalidez y vida",
      "patron": 0.0175,
      "trabajador": 0.00625,
      "base": "salario"
    },
    "retiro_cesantia_vejez": {
      "retiro": {
        "descripcion": "Retiro",
        "patron": 0.02,
        "trabajador": 0.0,
        "base": "salario"
      },
      "cesantia_vejez": {
        "descripcion": "Cesantía en edad avanzada y vejez",
        "trabajador": 0.01125,
        "base": "salario",
        "patron_por_ejercicio": {
          "2024": [
            {
              "rango": "1_sm",
              "tasa": 0.0315
            },
            {
              "rango": "1_01_sm_a_1_50_uma",
              "tasa": 0.03413
            },
            {
              "rango": "1_51_a_2_00_uma",
              "tasa": 0.04
            },
            {
              "rango": "2_01_a_2_50_uma",
              "tasa": 0.04353
            },
            {
              "rango": "2_51_a_3_00_uma",
              "tasa": 0.04588
            },
            {
              "rango": "3_01_a_3_50_uma",
              "tasa": 0.04756
            },
            {
              "rango": "3_51_a_4_00_uma",
              "tasa": 0.04882
            },
            {
              "rango": "4_01_uma_en_adelante",
              "tasa": 0.05331
            }
          ],
          "2025": [
            {
              "rango": "1_sm",
              "tasa": 0.0315
            },
            {
              "rango": "1_01_sm_a_1_50_uma",
              "tasa": 0.03544
            },
            {
              "rango": "1_51_a_2_00_uma",
              "tasa": 0.04426
            },
            {
              "rango": "2_01_a_2_50_uma",
              "tasa": 0.04954
            },
            {
              "rango": "2_51_a_3_00_uma",
              "tasa": 0.05307
            },
            {
              "rango": "3_01_a_3_50_uma",
              "tasa": 0.05559
            },
            {
              "rango": "3_51_a_4_00_uma",
              "tasa": 0.05747
            },
            {
              "rango": "4_01_uma_en_adelante",
              "tasa": 0.06422
            }
          ],
          "2026": [
            {
              "rango": "1_sm",
              "tasa": 0.0315
            },
            {
              "rango": "1_01_sm_a_1_50_uma",
              "tasa": 0.03676
            },
            {
              "rango": "1_51_a_2_00_uma",
              "tasa": 0.04851
            },
            {
              "rango": "2_01_a_2_50_uma",
              "tasa": 0.05556
            },
            {
              "rango": "2_51_a_3_00_uma",
              "tasa": 0.06026
            },
            {
              "rango": "3_01_a_3_50_uma",
              "tasa": 0.06361
            },
            {
              "rango": "3_51_a_4_00_uma",
              "tasa": 0.06613
            },
            {
              "rango": "4_01_uma_en_adelante",
              "tasa": 0.07513
            }
          ]
        }
      }
    },
    "guarderias_prestaciones_sociales": {
      "descripcion": "Guarderías y prestaciones sociales",
      "patron": 0.01,
      "trabajador": 0.0,
      "base": "salario"
    },
    "riesgo_trabajo": {
      "descripcion": "Riesgos de trabajo (prima media de clase para inscripción inicial; la prima real depende de siniestralidad)",
      "clase_1": 0.0054355,
      "clase_2": 0.0113065,
      "clase_3": 0.025984,
      "clase_4": 0.0465325,
      "clase_5": 0.0758875,
      "minima": 0.005,
      "maxima": 0.15,
      "base": "salario"
    }
  },
  "modalidad_40": {
    "descripcion": "Continuación voluntaria en el régimen obligatorio",
    "verification": "verified_for_2024_2026",
    "requisitos": {
      "baja_imss": "Tener baja del régimen obligatorio",
      "semanas_minimas": 52,
      "semanas_minimas_periodo_anios": 5,
      "plazo_ejercicio_derecho_anios": 5
    },
    "limites_salario": {
      "maximo_uma": 25,
      "minimo_regla": "no_inferior_al_ultimo_sbc_registrado"
    },
    "calculo": {
      "componentes_constantes": {
        "retiro_patron": 0.02,
        "cesantia_vejez_trabajador": 0.01125,
        "invalidez_vida_patron": 0.0175,
        "invalidez_vida_trabajador": 0.00625,
        "gastos_medicos_pensionados_patron": 0.0105,
        "gastos_medicos_pensionados_trabajador": 0.00375
      },
      "ceav_patronal": {
        "source_path": "cuotas_imss.retiro_cesantia_vejez.cesantia_vejez.patron_por_ejercicio",
        "selection": "sbc_band_and_exercise"
      }
    },
    "referencia_por_ejercicio": {
      "2024": {
        "vigencia_desde": "2024-01-01",
        "vigencia_hasta": "2024-12-31",
        "tasa_total_banda_4_01_uma_en_adelante": 0.12256
      },
      "2025": {
        "vigencia_desde": "2025-01-01",
        "vigencia_hasta": "2025-12-31",
        "tasa_total_banda_4_01_uma_en_adelante": 0.13347
      },
      "2026": {
        "vigencia_desde": "2026-01-01",
        "vigencia_hasta": "2026-12-31",
        "tasa_total_banda_4_01_uma_en_adelante": 0.14438
      }
    }
  },
  "modalidad_10": {
    "descripcion": "Incorporación voluntaria al régimen obligatorio (trabajadores independientes)",
    "verification": "legacy_unverified",
    "requisitos": {
      "edad_minima": 16,
      "edad_maxima": 60,
      "no_cotizar_obligatorio": true,
      "mexicano_o_extranjero_residente": true
    },
    "cuota_mensual": {
      "formula": "salario_base_cotizacion × tasa_total + cuota_fija_uma",
      "porcentaje_variable": 0.1047,
      "cuota_fija_uma_factor": 3.3,
      "componentes": {
        "prestaciones_en_especie_fija": "3.3 UMAs",
        "cesantia_vejez": 0.04275,
        "invalidez_vida": 0.02375,
        "gastos_medicos_pensionados": 0.01425,
        "prestaciones_dinero": 0.0095,
        "guarderias": 0.01
      }
    },
    "limites_salario": {
      "minimo_uma": 1,
      "maximo_uma": 25
    },
    "beneficios": [
      "Seguro de enfermedades y maternidad",
      "Seguro de riesgos de trabajo",
      "Seguro de invalidez y vida",
      "Seguro de retiro, cesantía y vejez",
      "Guarderías y prestaciones sociales"
    ]
  },
  "topes_cotizacion": {
    "salario_base_minimo": {
      "descripcion": "1 salario mínimo aplicable",
      "tipo": "salario_minimo"
    },
    "salario_base_maximo": {
      "descripcion": "25 UMAs",
      "uma_factor": 25
    }
  },
  "riesgos_trabajo_clases": [
    {
      "clase": 1,
      "prima": 0.0054355,
      "descripcion": "Clase I - prima media",
      "ejemplos": [
        "Oficinas",
        "Comercio",
        "Servicios administrativos"
      ]
    },
    {
      "clase": 2,
      "prima": 0.0113065,
      "descripcion": "Clase II - prima media",
      "ejemplos": [
        "Manufactura ligera",
        "Servicios profesionales"
      ]
    },
    {
      "clase": 3,
      "prima": 0.025984,
      "descripcion": "Clase III - prima media",
      "ejemplos": [
        "Manufactura pesada",
        "Transporte"
      ]
    },
    {
      "clase": 4,
      "prima": 0.0465325,
      "descripcion": "Clase IV - prima media",
      "ejemplos": [
        "Construcción",
        "Industria química"
      ]
    },
    {
      "clase": 5,
      "prima": 0.0758875,
      "descripcion": "Clase V - prima media",
      "ejemplos": [
        "Minería",
        "Petróleo",
        "Explosivos"
      ]
    }
  ]
}
''';

const String imssCatalogsJson = r'''
{
  "_meta": {
    "description": "Catálogos del IMSS (Sistema Único de Autodeterminación - SUA)",
    "source": "IMSS - Vigente 2024-2026",
    "updated": "2026-01-05"
  },
  "tipos_movimiento_afiliatorio": [
    {
      "clave": "08",
      "descripcion": "Alta de trabajador",
      "tipo": "alta"
    },
    {
      "clave": "02",
      "descripcion": "Baja de trabajador",
      "tipo": "baja"
    },
    {
      "clave": "07",
      "descripcion": "Modificación de salario",
      "tipo": "modificacion"
    },
    {
      "clave": "12",
      "descripcion": "Reingreso",
      "tipo": "reingreso"
    }
  ],
  "tipos_trabajador": [
    {
      "clave": "1",
      "descripcion": "Permanente",
      "caracteristicas": "Relación laboral por tiempo indeterminado"
    },
    {
      "clave": "2",
      "descripcion": "Eventual Ciudad",
      "caracteristicas": "Trabajador urbano eventual"
    },
    {
      "clave": "3",
      "descripcion": "Eventual del Campo",
      "caracteristicas": "Trabajador agrícola eventual"
    },
    {
      "clave": "4",
      "descripcion": "Trabajador del hogar",
      "caracteristicas": "Trabajador doméstico"
    }
  ],
  "tipos_incapacidad": [
    {
      "clave": "1",
      "descripcion": "Riesgo de trabajo",
      "dias_pago": "100% del salario registrado"
    },
    {
      "clave": "2",
      "descripcion": "Enfermedad general",
      "dias_pago": "60% del salario desde el 4to día"
    },
    {
      "clave": "3",
      "descripcion": "Maternidad",
      "dias_pago": "100% del salario, 42 días antes y 42 después del parto"
    }
  ],
  "seguros_imss": [
    {
      "id": "riesgo_trabajo",
      "nombre": "Riesgos de Trabajo",
      "descripcion": "Cubre accidentes y enfermedades de trabajo",
      "beneficios": [
        "Asistencia médica",
        "Hospitalización",
        "Medicamentos",
        "Indemnizaciones por incapacidad",
        "Pensión por invalidez o muerte"
      ],
      "cuota_patron": "Variable (0.5% a 15% según riesgo)",
      "cuota_trabajador": "0%"
    },
    {
      "id": "enfermedad_maternidad",
      "nombre": "Enfermedad y Maternidad",
      "descripcion": "Atención médica y prestaciones en dinero",
      "beneficios": [
        "Asistencia médica",
        "Subsidios por incapacidad",
        "Prestaciones de maternidad",
        "Ayudas de lactancia"
      ],
      "cuota_patron": "20.4% (cuota fija) + 1.1% (excedente 3 UMAs) + 0.7% (dinero) + 1.05% (pensionados)",
      "cuota_trabajador": "0.4% (excedente) + 0.25% (dinero) + 0.375% (pensionados)"
    },
    {
      "id": "invalidez_vida",
      "nombre": "Invalidez y Vida",
      "descripcion": "Pensiones por invalidez o muerte del asegurado",
      "beneficios": [
        "Pensión por invalidez",
        "Pensión de viudez",
        "Pensión de orfandad",
        "Ayuda asistencial"
      ],
      "cuota_patron": "1.75%",
      "cuota_trabajador": "0.625%"
    },
    {
      "id": "retiro",
      "nombre": "Retiro",
      "descripcion": "Aportaciones para el retiro (cuenta individual)",
      "beneficios": [
        "Ahorro para el retiro",
        "Cuenta individual AFORE"
      ],
      "cuota_patron": "2%",
      "cuota_trabajador": "0%"
    },
    {
      "id": "cesantia_vejez",
      "nombre": "Cesantía en Edad Avanzada y Vejez",
      "descripcion": "Pensión al cumplir 60 o 65 años",
      "beneficios": [
        "Pensión por cesantía (60 años)",
        "Pensión por vejez (65 años)",
        "Asistencia médica"
      ],
      "cuota_patron": "3.15%",
      "cuota_trabajador": "1.125%"
    },
    {
      "id": "guarderias",
      "nombre": "Guarderías y Prestaciones Sociales",
      "descripcion": "Servicio de guardería y prestaciones sociales",
      "beneficios": [
        "Guarderías para hijos de trabajadoras",
        "Prestaciones sociales",
        "Centros vacacionales"
      ],
      "cuota_patron": "1%",
      "cuota_trabajador": "0%"
    }
  ],
  "subdelegaciones_ejemplo": [
    {
      "estado": "Ciudad de México",
      "subdelegacion": "01",
      "nombre": "Norte",
      "alcaldias": ["Azcapotzalco", "Gustavo A. Madero"]
    },
    {
      "estado": "Ciudad de México",
      "subdelegacion": "02",
      "nombre": "Sur",
      "alcaldias": ["Coyoacán", "Tlalpan", "Xochimilco"]
    },
    {
      "estado": "Jalisco",
      "subdelegacion": "01",
      "nombre": "Guadalajara",
      "municipios": ["Guadalajara", "Zapopan", "Tlaquepaque"]
    },
    {
      "estado": "Nuevo León",
      "subdelegacion": "01",
      "nombre": "Monterrey",
      "municipios": ["Monterrey", "San Pedro Garza García", "Santa Catarina"]
    }
  ],
  "tabulador_pensiones_minimas": {
    "2024": {
      "pension_minima_garantizada": 2622.00,
      "ayuda_asistencial": 1311.00,
      "asignaciones_familiares": {
        "esposa": 262.20,
        "hijo_menor_16": 174.80,
        "ascendiente": 174.80
      }
    },
    "2025": {
      "pension_minima_garantizada": 2738.00,
      "ayuda_asistencial": 1369.00,
      "asignaciones_familiares": {
        "esposa": 273.80,
        "hijo_menor_16": 182.53,
        "ascendiente": 182.53
      }
    },
    "2026": {
      "pension_minima_garantizada": 2738.00,
      "ayuda_asistencial": 1369.00,
      "asignaciones_familiares": {
        "esposa": 273.80,
        "hijo_menor_16": 182.53,
        "ascendiente": 182.53
      }
    }
  },
  "semanas_cotizadas_requeridas": {
    "pension_cesantia_vejez": {
      "minimo": 1250,
      "descripcion": "Semanas mínimas para pensión (Ley 97)"
    },
    "pension_vejez_ley_73": {
      "minimo": 500,
      "descripcion": "Semanas mínimas para pensión (Ley 73)"
    },
    "modalidad_40": {
      "minimo": 52,
      "descripcion": "Semanas previas requeridas para Modalidad 40"
    }
  }
}
''';
