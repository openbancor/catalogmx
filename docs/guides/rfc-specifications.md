# Especificaciones Oficiales del RFC (Registro Federal de Contribuyentes)

## Fuentes

Basado en:
- Algoritmo oficial del SAT (IFAI 0610100135506)
- Referencia: https://www.mariovaldez.net/files/IFAI%200610100135506%20065%20Algoritmo%20para%20generar%20el%20RFC%20con%20homoclave%20para%20personas%20fisicas%20y%20morales.pdf

## Estructura del RFC

### Persona Física (13 caracteres)
```
Posiciones 1-4:   Letras del nombre (VEML)
Posiciones 5-10:  Fecha de nacimiento (AAMMDD)
Posiciones 11-12: Homoclave (calculada)
Posición 13:      Dígito verificador
```

### Persona Moral (12 caracteres)
```
Posiciones 1-3:   Letras de razón social (ABC)
Posiciones 4-9:   Fecha de constitución (AAMMDD)
Posiciones 10-11: Homoclave (calculada)
Posición 12:      Dígito verificador
```

---

## Reglas para Personas Morales

### Regla 1: Tres o más palabras
Se toman las primeras letras de las tres primeras palabras.
- "Sonora Industrial Azucarera" → **SIA**

### Regla 2: Fecha de constitución
Formato AAMMDD (año, mes, día con dos dígitos cada uno).

### Regla 3: Letras compuestas
- CH → C
- LL → L

### Regla 4: Iniciales como palabras
Las iniciales se consideran palabras individuales.
- "F.A.Z." → **FAZ** (F, A, Z son tres palabras)

### Regla 5: Abreviaturas de sociedad
No se toman en consideración: S.A., S.A. de C.V., S. de R.L., S.C., S. en C., etc.

### Regla 6: Dos palabras
Primera letra de la primera palabra + primeras dos letras de la segunda.
- "Aceros Ecatepec" → **AEC** (A + EC)

### Regla 7: Una sola palabra
Tres primeras letras de la palabra.
- "Calidra" → **CAL**

### Regla 8: Menos de tres letras
Se suple con X.
- "Al" → **ALX**
- "Z" → **ZXX**

### Regla 9: Artículos, preposiciones y conjunciones
No se toman: EL, LA, LOS, LAS, DE, DEL, Y, E, A, CON, PARA, POR, EN, etc.
- "El abastecedor Ferretero" → **AFE**

### Regla 10: Números
Los números arábigos y romanos se convierten a texto.
- "505" → "QUINIENTOS CINCO"
- "XXI" → "VEINTIUNO"

### Regla 11: Compañía y Sociedad
Las palabras COMPAÑÍA, CÍA., SOCIEDAD, SOC. no se incluyen.

### Regla 12: Caracteres especiales
Los caracteres especiales se convierten a palabras cuando están aislados:
- @ → ARROBA
- % → PORCIENTO
- # → NUMERO
- ( → ABRE
- / → DIAGONAL

---

## Reglas para Personas Físicas

### Regla 1: Formación básica
1. Primera letra del apellido paterno
2. Primera vocal interna del apellido paterno
3. Primera letra del apellido materno
4. Primera letra del nombre

- "Gómez Díaz, Emma" → **GODE**

### Regla 2: Fecha de nacimiento
Formato AAMMDD.

### Regla 3: Letras compuestas
- CH → C
- LL → L

### Regla 4: Apellido paterno corto (1-2 letras)
Se usan las dos primeras del paterno + primera del materno + primera del nombre.
- "De la O Sánchez, Carlos" → **OXSC**

### Regla 5: Apellidos compuestos
Se toma la primera palabra del apellido.
- "Ponce de León García, Juan" → **POGJ**

### Regla 6: Nombres María o José
Si el primer nombre es MARÍA o JOSÉ (y hay segundo nombre), se usa el segundo nombre.
- "María Luisa Pérez Ruiz" → **PERL** (usa L de Luisa)

### Regla 7: Un solo apellido
Dos primeras del apellido + dos primeras del nombre.
- "Juan (sin materno)" → **JUXX** o las dos del apellido + dos del nombre

### Regla 8: Artículos y preposiciones
No se toman: DE, LA, DEL, LOS, LAS, Y, etc.

### Regla 10: Caracteres especiales
Se excluyen caracteres especiales del nombre.

---

## Palabras Inconvenientes

Cuando las primeras 4 letras forman una palabra inconveniente, se sustituye la segunda letra por 'X':

```
BUEI → BXEI    BUEY → BXEY    CACA → CXCA    CACO → CXCO
CAGA → CXGA    CAGO → CXGO    CAKA → CXKA    CAKO → CXKO
COGE → CXGE    COGI → CXGI    COJA → CXJA    COJE → CXJE
COJI → CXJI    COJO → CXJO    COLA → CXLA    CULO → CXLO
FALO → FXLO    FETO → FXTO    GETA → GXTA    GUEI → GXEI
GUEY → GXEY    JETA → JXTA    JOTO → JXTO    KACA → KXCA
KACO → KXCO    KAGA → KXGA    KAGO → KXGO    KAKA → KXKA
KAKO → KXKO    KOGE → KXGE    KOGI → KXGI    KOJA → KXJA
KOJE → KXJE    KOJI → KXJI    KOJO → KXJO    KOLA → KXLA
KULO → KXLO    LILO → LXLO    LOCA → LXCA    LOCO → LXCO
LOKA → LXKA    LOKO → LXKO    MAME → MXME    MAMO → MXMO
MEAR → MXAR    MEAS → MXAS    MEON → MXON    MIAR → MXAR
MION → MXON    MOCO → MXCO    MOKO → MXKO    MULA → MXLA
MULO → MXLO    NACA → NXCA    NACO → NXCO    PEDA → PXDA
PEDO → PXDO    PENE → PXNE    PIPI → PXPI    PITO → PXTO
POPO → PXPO    PUTA → PXTA    PUTO → PXTO    QULO → QXLO
RATA → RXTA    ROBA → RXBA    ROBE → RXBE    ROBO → RXBO
RUIN → RXIN    SENO → SXNO    TETA → TXTA    VACA → VXCA
VAGA → VXGA    VAGO → VXGO    VAKA → VXKA    VUEI → VXEI
VUEY → VXEY    WUEI → WXEI    WUEY → WXEY
```

---

## Cálculo de Homoclave

La homoclave (2 caracteres) se calcula usando un algoritmo basado en:
1. Transformación del nombre completo a valores numéricos
2. Suma de productos de pares de dígitos
3. División y residuos para obtener los caracteres

Ver documento SAT para detalles completos del algoritmo.

---

## Dígito Verificador

El dígito verificador se calcula con el siguiente algoritmo:

1. **Diccionario de valores:**
   ```
   0=0, 1=1, ..., 9=9
   A=10, B=11, C=12, D=13, E=14, F=15, G=16, H=17, I=18
   J=19, K=20, L=21, M=22, N=23, &=24, O=25, P=26, Q=27
   R=28, S=29, T=30, U=31, V=32, W=33, X=34, Y=35, Z=36
   Ñ=37, espacio=38
   ```

2. **Cálculo:**
   ```
   Para cada carácter (i = 0 a 11/12):
       valor = diccionario[caracter] × (13 - i)  // o (14 - i) para persona física

   suma = suma de todos los valores
   residuo = suma mod 11

   Si residuo == 0: dígito = "0"
   Si residuo == 10: dígito = "A"
   Si no: dígito = str(11 - residuo)
   ```

---

## Correcciones a Test Vectors

### Nota sobre "EL # DEL TEJADO"

El documento de especificación SAT contenía un error en uno de los ejemplos:

| Razón Social | Esperado (erróneo) | Correcto |
|--------------|-------------------|----------|
| EL # DEL TEJADO | NET | **NTE** |

**Explicación:**
- "#" se convierte a "NUMERO"
- Resultado: "EL NUMERO DEL TEJADO"
- Se filtran "EL" y "DEL": "NUMERO TEJADO"
- Regla 6 (dos palabras): Primera letra + dos primeras de segunda
- **N** (de NUMERO) + **TE** (de TEJADO) = **NTE**

El resultado "NET" implicaría aplicar la regla al revés (NE + T), lo cual es incorrecto según las reglas oficiales del SAT.

---

## RFCs Genéricos

Existen RFCs genéricos para operaciones especiales:

- **XAXX010101000** - Público en general (ventas al público)
- **XEXX010101000** - Extranjeros sin RFC

Estos RFCs son válidos y reconocidos por el SAT.

---

## Implementación

Este proyecto implementa el algoritmo completo del SAT para:
- Generación de RFC (personas físicas y morales)
- Cálculo de homoclave
- Cálculo de dígito verificador
- Validación de RFC existentes

**Plataformas soportadas:**
- Python 3.10+
- TypeScript/Node.js
- Dart/Flutter

**Tests:** 120 casos de prueba basados en especificación SAT (100% passing en las 3 plataformas).

---

## Referencias Oficiales

- SAT (Servicio de Administración Tributaria)
- Documento IFAI 0610100135506
- Portal de validación: https://www.sat.gob.mx

---

**Implementado en:** catalogmx v0.3+
**Última actualización:** 2026-01-22
