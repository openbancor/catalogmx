# Algoritmo para Generar el RFC con Homoclave para Personas Físicas y Morales

**Documento:** IFAI 0610100135506
**Fecha:** 18/10/2006
**Fuente:** Servicio de Administración Tributaria (SAT)

> **Nota:** Solo la Secretaría de Hacienda y Crédito Público, a través del Servicio de Administración Tributaria, es la única instancia que oficialmente asigna las claves de RFC a los contribuyentes que así lo soliciten, a partir de la aplicación de este procedimiento a la base de datos del Padrón de Contribuyentes, con la finalidad de identificar homonimias y evitar la duplicidad de registros.

---

## Antecedentes

Este documento describe los procedimientos para la generación de la clave de Registro Federal de Contribuyentes a 10 posiciones, tomándose como base legal el "Instructivo para Formación del Registro Federal de Contribuyentes" emitido por la Dirección General de Recaudación en abril de 1988.

También describe la forma en que se genera la **clave diferenciadora (homónima)** así como el **dígito verificador**, obteniéndose con estos dos elementos la clave de RFC a **13 posiciones**.

---

## 1. Fuentes de Información

### A) Personas Morales
- Copia del acta constitutiva o documento que motivó su origen.

### B) Personas Físicas
- Acta de Nacimiento, Cartilla, Pasaporte o Certificado de Estudios de Enseñanza Pública.
- Para asalariados: datos proporcionados por el empleador (retenedor).

---

## 2. Estructura de la Clave

| Tipo | Primeras 10 posiciones | Ejemplo |
|------|------------------------|---------|
| Persona Moral | 1 espacio + 3 letras + 6 dígitos | `_SIA821129` |
| Persona Física | 4 letras + 6 dígitos | `BAFJ701213` |

Una vez asignada la clave a 10 posiciones, se generan:
- **2 posiciones** para la clave diferenciadora de homonimia
- **1 posición** para el dígito verificador

**La clave completa de RFC consta de 13 posiciones (12 para personas morales visualmente).**

---

## 3. Reglas para Personas Morales

### REGLA 1ª - Tres o más palabras
Se toman las primeras letras de las tres primeras palabras de la denominación o razón social.

| Razón Social | Resultado |
|--------------|-----------|
| Sonora Industrial Azucarera, S. de R. L. | SIA-821129 |
| Herrajes, Cortinas y Maquinaria, S.A. | HCM-841122 |
| Artículos de piel y Baúles, S. de R. L. | APB-791215 |

### REGLA 2ª - Fecha de constitución
Se anota en formato AAMMDD:

| Componente | Ejemplo | Resultado |
|------------|---------|-----------|
| Año | 1982 | 82 |
| Mes | Noviembre | 11 |
| Día | 29 | 29 |

Ejemplos completos:
| Razón Social | RFC |
|--------------|-----|
| Tecnología y Equipo contra Incendios, S.A. | TEC-830305 |
| Internacional Turística Flacón, S.A. | ITF-850128 |
| Artículos de Caza y Pesca, S. de R. L. | ACP-860215 |

### REGLA 3ª - Letras compuestas (CH, LL)
Cuando la letra inicial sea compuesta, únicamente se anota la inicial: CH → C, LL → L.

| Razón Social | RFC |
|--------------|-----|
| Champion Mexicana de Bujías, S.A. | CMB-830702 |
| Casa Chávez de maquinaria, S. de R. L. | CCM-800620 |
| Artículos de Piel y Chamarras, S. de R.L. | APC-810202 |
| Llantas, Cámaras y Refacciones, S. de R.L. | LCR-851015 |
| Candados, Llaves y Cerraduras, S.A. | CLC-830820 |
| Luis Molina Llorantes y Cía., S. de R.L. | LML-860911 |

### REGLA 4ª - Iniciales como palabras
Las iniciales se consideran palabras individuales.

| Razón Social | RFC |
|--------------|-----|
| F.A.Z., S.A. | FAZ-870420 |
| U.S. Ruber Mexicana, S.A. | USR-860201 |
| H. Prieto y Martínez, S. de R.L. | HPM-841221 |

### REGLA 5ª - Abreviaturas de tipo de sociedad (excluidas)
No se toman en consideración: S. en N.C., S. en C., S. de R.L., S. en C. por A., S.A., S.A. de C.V., S.N.C., S.C., A.C., A. en P., S.C.L., S.C.S.

| Razón Social | RFC |
|--------------|-----|
| Guantes Industriales Guadalupe, S. en C. | GIG-841215 |
| Construcciones Metálicas Mexicanas, S.A. | CMM-830120 |
| Fundición de Precisión Eutectic, S. de R.L. | FPE-861125 |

### REGLA 6ª - Dos palabras
Se toma la inicial de la primera palabra y las dos primeras letras de la segunda.

| Razón Social | RFC |
|--------------|-----|
| Fonograbaciones Cinelandia, S. de R.L. | FCI-841019 |
| Aceros Ecatepec, S.A. | AEC-890130 |
| Distribuidora Ges, S.A. | DGE-850628 |

### REGLA 7ª - Una sola palabra
Se toman las tres primeras letras consecutivas.

| Razón Social | RFC |
|--------------|-----|
| Arsuyama, S.A. | ARS-821129 |
| Calidra, S.A. | CAL-850920 |
| Electrólisis, S.A. | ELE-840821 |

### REGLA 8ª - Una palabra con menos de 3 letras
Se suple con "X".

| Razón Social | RFC |
|--------------|-----|
| Al, S.A. | ALX-830101 |
| Z, S.A. | ZXX-860110 |

### REGLA 9ª - Artículos, preposiciones y conjunciones (excluidos)
No se toman: El, La, De, Los, Las, Y, Del, etc.

| Razón Social | RFC |
|--------------|-----|
| El abastecedor Ferretero, S.A. | AFE-840510 |
| Cigarros la Tabacalera Mexicana, S.A. de C.V. | CTM-860901 |
| Los Viajes Internacionales de Marco Polo, S.A. | VIM-824225 |
| Artículos y Accesorios para Automóviles, S.A. | AAA-800521 |
| Productos de la Industria del Papel, S.A. | PIP-811231 |

### REGLA 10ª - Números (arábigos y romanos)
Se convierten a texto.

| Razón Social | Conversión | RFC |
|--------------|------------|-----|
| El 12, S.A. | DOCE | DOC-801029 |
| El 2 de Enero, S de R.L. | DOS | DEN-840101 |
| El 505, S.A. | QUINIENTOS CINCO | QCI-851215 |
| Editorial Siglo XXI, S.A. | VEINTIUNO | ESV-831114 |

### REGLA 11ª - Compañía/Sociedad (excluidas)
Las palabras "Compañía", "Cía.", "Sociedad", "Soc." no se incluyen.

| Razón Social | RFC |
|--------------|-----|
| Compañía Periodística Nacional, S.A. | PNA-861121 |
| Cía. De Artículos Eléctricos, S. de R.L. | AEL-850110 |
| Cía. Nal. De Subsistencias Mexicanas, S.A. | NSM-841011 |
| Pimienta Hnos. y Cía., S.A. | PHN-830228 |
| Sociedad Cooperativa de Producción Agrícola de Michoacán | CPA-861016 |
| Sociedad de Consumo Agrícola del Sur, S.C.L. | CAS-821110 |
| Sociedad de Producción Rural de Sonora | PRS-800101 |

### REGLA 12ª - Caracteres especiales
Se excluyen para el cálculo del homónimo y dígito verificador: @, ', %, #, !, ., $, ", -, /, +, (, )

| Denominación | RFC |
|--------------|-----|
| LA S@NDIA S.A DE C.V. | SND-861121 |
| LA @ S.A. DE C.V | ARR-860120 |
| LA @ DEL % SA DE CV | APO-830120 |
| @ COMER.COM | ACO-800210 |
| LAS ( BLANCAS ) | APB-700202 |
| EL # DEL TEJADO | NET-010202 |
| LA / DEL SUR | DSU-010102 |
| EL C@FE.NET | CFE-030210 |

---

## 4. Reglas para Personas Físicas

### REGLA 1ª - Formación básica
1. Primera letra del apellido paterno + primera vocal del mismo
2. Primera letra del apellido materno
3. Primera letra del nombre

| Nombre | Desglose | RFC |
|--------|----------|-----|
| Juan Barrios Fernández | BA + F + J | BAFJ-701213 |
| Eva Iriarte Méndez | II + M + E | IIME-691117 |

### REGLA 2ª - Fecha de nacimiento
Formato AAMMDD (igual que personas morales).

| Nombre | RFC |
|--------|-----|
| Juan Barrios Fernández | BAFJ-070401 |
| Francisco Ortíz Pérez | OIPF-290205 |
| Manuel Martínez Hernández | MAHM-570102 |
| Gabriel Courturier Moreno | COMG-600703 |

### REGLA 3ª - Letras compuestas (CH, LL)
CH → C, LL → L.

| Nombre | RFC |
|--------|-----|
| Manuel Chávez González | CAGM-240618 |
| Felipe Camargo Llamas | CALF-450228 |
| Charles Kennedy Truman | KETC-511012 |

### REGLA 4ª - Apellido paterno de 1-2 letras
Se forma: inicial paterno + inicial materno + primera y segunda letra del nombre.

| Nombre | RFC |
|--------|-----|
| Alvaro de la O Lozano | OLAL-401201 |
| Ernesto Ek Rivera | ERER-071120 |

### REGLA 5ª - Apellidos compuestos
Se toma la primera palabra del apellido compuesto.

| Nombre | RFC |
|--------|-----|
| Dolores San Martín Dávalos | SADD-180812 |
| Mario Sánchez de la Barquera Gómez | SAGM-190224 |
| Antonio Jiménez Ponce de León | JIPA-170808 |

### REGLA 6ª - Nombres compuestos (MARIA/JOSE)
Si el primer nombre es MARIA o JOSE, se usa la inicial del segundo nombre.

| Nombre | RFC |
|--------|-----|
| Luz María Fernández Juárez | FEJL-200205 |
| José Antonio Camargo Hernández | CAHA-211218 |
| María Luisa Ramírez Sánchez | RASL-251112 |

### REGLA 7ª - Un solo apellido
Se usan las dos primeras letras del apellido + las dos primeras del nombre.

| Nombre | RFC |
|--------|-----|
| Juan Martínez | MAJU-420116 |
| Gerarda Zafra | ZAGE-251115 |

### REGLA 8ª - Artículos, preposiciones y conjunciones
No se toman en cuenta.

| Nombre | RFC |
|--------|-----|
| Carmen de la Peña Ramírez | PERC-631201 |
| Mario Sánchez de los Cobos | SACM-701110 |
| Roberto González y Durán | GODR-600101 |
| Juan del Valle Martínez | VAMJ-691001 |

### REGLA 9ª - Palabras inconvenientes
La última letra se sustituye por "X".

| Original | Corregido |
|----------|-----------|
| BUEI | BUEX |
| BUEY | BUEX |
| CACA | CACX |
| CACO | CACX |
| CAGA | CAGX |
| CAGO | CAGX |
| COGE | COGX |
| COJA | COJX |
| COJE | COJX |
| COJI | COJX |
| COJO | COJX |
| CULO | CULX |
| FETO | FETX |
| GUEY | GUEX |
| JOTO | JOTX |
| KACA | KACX |
| KACO | KACX |
| KAGA | KAGX |
| KAGO | KAGX |
| KOGE | KOGX |
| KOJO | KOJX |
| KAKA | KAKX |
| KULO | KULX |
| MAME | MAMX |
| MAMO | MAMX |
| MEAR | MEAX |
| MEAS | MEAX |
| MEON | MEOX |
| MION | MIOX |
| MOCO | MOCX |
| MULA | MULX |
| PEDA | PEDX |
| PEDO | PEDX |
| PENE | PENX |
| PUTA | PUTX |
| PUTO | PUTX |
| QULO | QULX |
| RATA | RATX |
| RUIN | RUIX |

### REGLA 10ª - Caracteres especiales en nombres
Se excluyen: ' (apóstrofe), . (punto)

| Nombre | RFC |
|--------|-----|
| Roberto O'farril Carballo | OACR-661121 |
| Rubén D'angelo Fargo | DAFR-710108 |
| Luz Ma. Fernández Juárez | FEJL-830120 |

---

## 5. Procedimiento para Obtener la Clave Diferenciadora de Homonimia

### Paso 1: Asignar valores (Anexo I)
```
Espacio = 00   B = 12   O = 26
0 = 00         C = 13   P = 27
1 = 01         D = 14   Q = 28
2 = 02         E = 15   R = 29
3 = 03         F = 16   S = 32
4 = 04         G = 17   T = 33
5 = 05         H = 18   U = 34
6 = 06         I = 19   V = 35
7 = 07         J = 21   W = 36
8 = 08         K = 22   X = 37
9 = 09         L = 23   Y = 38
& = 10         M = 24   Z = 39
A = 11         N = 25   Ñ = 40
```

### Paso 2: Ejemplo con "Gómez Díaz Emma"

```
G O M E Z   D I A Z   E M M A
017 26 24 15 39 00 14 19 11 39 00 15 24 24 11
```

Se agrega un cero al inicio para uniformar.

### Paso 3: Multiplicaciones de parejas

Cada par de dígitos se multiplica por el segundo dígito del par:
```
01 * 1 = 1      90 * 0 = 0      90 * 0 = 0
17 * 7 = 119    00 * 0 = 0      00 * 0 = 0
72 * 2 = 144    01 * 1 = 1      01 * 1 = 1
26 * 6 = 156    14 * 4 = 56     15 * 5 = 75
62 * 2 = 124    41 * 1 = 41     52 * 2 = 104
24 * 4 = 96     19 * 9 = 171    24 * 4 = 96
41 * 1 = 41     91 * 1 = 91     42 * 2 = 84
15 * 5 = 75     11 * 1 = 11     24 * 4 = 96
53 * 3 = 159    13 * 3 = 39     41 * 1 = 41
39 * 9 = 351    39 * 9 = 351    11 * 1 = 11
```

### Paso 4: Suma y división
```
Suma total = 2535
Últimas 3 cifras = 535
535 ÷ 34 = 15 cociente, 25 residuo
```

### Paso 5: Asignar homonimia (Anexo II)
```
0 = 1    9 = A    18 = J   27 = T
1 = 2    10 = B   19 = K   28 = U
2 = 3    11 = C   20 = L   29 = V
3 = 4    12 = D   21 = M   30 = W
4 = 5    13 = E   22 = N   31 = X
5 = 6    14 = F   23 = P   32 = Y
6 = 7    15 = G   24 = Q   33 = Z
7 = 8    16 = H   25 = R
8 = 9    17 = I   26 = S
```

**Resultado:**
- Cociente 15 = G
- Residuo 25 = R
- **Homonimia: GR**

RFC con homonimia: `GODE561231GR`

---

## 6. Procedimiento para Calcular el Dígito Verificador

### Tabla de valores (Anexo III)
```
0 = 00   A = 10   K = 20   U = 31
1 = 01   B = 11   L = 21   V = 32
2 = 02   C = 12   M = 22   W = 33
3 = 03   D = 13   N = 23   X = 34
4 = 04   E = 14   & = 24   Y = 35
5 = 05   F = 15   O = 25   Z = 36
6 = 06   G = 16   P = 26   BLANCO = 37
7 = 07   H = 17   Q = 27   Ñ = 38
8 = 08   I = 18   R = 28
9 = 09   J = 19   S = 29
                  T = 30
```

### Ejemplo: GODE561231GR

| Carácter | Valor | Posición | Multiplicación |
|----------|-------|----------|----------------|
| G | 16 | 13 | 16 × 13 = 208 |
| O | 25 | 12 | 25 × 12 = 300 |
| D | 13 | 11 | 13 × 11 = 143 |
| E | 14 | 10 | 14 × 10 = 140 |
| 5 | 05 | 9 | 5 × 9 = 45 |
| 6 | 06 | 8 | 6 × 8 = 48 |
| 1 | 01 | 7 | 1 × 7 = 7 |
| 2 | 02 | 6 | 2 × 6 = 12 |
| 3 | 03 | 5 | 3 × 5 = 15 |
| 1 | 01 | 4 | 1 × 4 = 4 |
| G | 16 | 3 | 16 × 3 = 48 |
| R | 28 | 2 | 28 × 2 = 56 |

**Suma = 1026**

```
1026 ÷ 11 = 93 cociente, 3 residuo
11 - 3 = 8
```

**Reglas del dígito verificador:**
- Si residuo = 0 → dígito = 0
- Si residuo > 0 → dígito = 11 - residuo
- Si resultado = 10 → dígito = A

**RFC completo: GODE561231GR8**

---

## Anexos

### Palabras Excluidas - Personas Morales
EL, LA, DE, LOS, LAS, Y, DEL, MI, COMPAÑÍA, CIA, SOCIEDAD, SOC, COOPERATIVA, COOP, S.A., S. DE R.L., S. EN C., S.C., A.C., A. EN P., S.C.L., S.N.C., C.V., THE, OF, AND, COMPANY, CO, MC, VON, MAC, VAN, PARA, POR, AL, E, EN, CON, SUS, A

### Palabras Excluidas - Personas Físicas
DE, LA, LAS, MC, VON, DEL, LOS, Y, MAC, VAN, MI

### Caracteres Especiales - Personas Morales
@, ', %, #, !, ., $, ", -, /, +, (, )

### Caracteres Especiales - Personas Físicas
' (apóstrofe), . (punto)

---

## Resumen de Ejemplos de Prueba

### Personas Morales (solo iniciales y fecha, sin homoclave)

| Razón Social | RFC Base |
|--------------|----------|
| Sonora Industrial Azucarera | SIA-821129 |
| F.A.Z. | FAZ-870420 |
| Aceros Ecatepec | AEC-890130 |
| Arsuyama | ARS-821129 |
| Al | ALX-830101 |
| El 12 | DOC-801029 |
| Editorial Siglo XXI | ESV-831114 |

### Personas Físicas (solo iniciales y fecha, sin homoclave)

| Nombre Completo | RFC Base |
|-----------------|----------|
| Juan Barrios Fernández | BAFJ-701213 |
| Eva Iriarte Méndez | IIME-691117 |
| Manuel Chávez González | CAGM-240618 |
| Alvaro de la O Lozano | OLAL-401201 |
| Luz María Fernández Juárez | FEJL-200205 |
| Juan Martínez (solo apellido) | MAJU-420116 |

### Ejemplo Completo con Homoclave y Dígito Verificador

| Nombre | RFC Completo |
|--------|--------------|
| Emma Gómez Díaz (31/12/1956) | GODE561231GR8 |
