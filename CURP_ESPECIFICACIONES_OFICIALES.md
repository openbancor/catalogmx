# Especificaciones Oficiales Completas del CURP

## Fuentes

Basado en:
- Instructivo Normativo para la Asignación de la CURP (DOF 18/10/2021)
- Reglas para la Ejecución de los Procedimientos para la Asignación de la CURP (RENAPO)
- Anexo 2: Lista de Palabras Inconvenientes

## Estructura del CURP (18 caracteres)

```
Posiciones 1-4:   Letras del nombre (similar a RFC)
Posiciones 5-10:  Fecha de nacimiento (AAMMDD)
Posición 11:      Sexo (H=Hombre, M=Mujer)
Posiciones 12-13: Código de entidad federativa
Posiciones 14-16: Consonantes internas
Posición 17:      Diferenciador de homonimia
Posición 18:      Dígito verificador
```

## Reglas para las Primeras 4 Letras

1. **Primera letra:** Inicial del apellido paterno
2. **Segunda letra:** Primera vocal interna del apellido paterno (después de la primera letra)
3. **Tercera letra:** Inicial del apellido materno (X si no tiene)
4. **Cuarta letra:** Inicial del primer nombre

### Casos Especiales

- **Nombres compuestos con MARÍA o JOSÉ:** Se omite y se usa el segundo nombre
  - "María Luisa" → usa "L" de Luisa
  - "José Antonio" → usa "A" de Antonio

- **Apellidos con partículas:** Se omiten "DE", "LA", "DEL", "LOS", "LAS", "Y", "MC", "VON", "MAC", "VAN"

- **Caracteres especiales y Ñ:**
  - Ñ se trata como N
  - Se eliminan acentos y diacríticos
  - Se ignoran caracteres especiales (@, #, $, &, etc.)

## Lista Oficial Completa de Palabras Inconvenientes (Anexo 2)

Cuando las primeras 4 letras forman una de estas palabras, **se sustituye la segunda letra (primera vocal) con 'X'**:

### Palabras Inconvenientes

```
BACA  BAKA  BUEI  BUEY
CACA  CACO  CAGA  CAGO  CAKA  KAKO  COGE  COGI  COJA  COJE  COJI  COJO  COLA  CULO
FALO  FETO
GETA  GUEI  GUEY
JETA  JOTO
KACA  KACO  KAGA  KAGO  KAKA  KAKO  KOGE  KOGI  KOJA  KOJE  KOJI  KOJO  KOLA  KULO
LILO  LOCA  LOCO  LOKA  LOKO
MAME  MAMO  MEAR  MEAS  MEON  MIAR  MION  MOCO  MOKO  MULA  MULO
NACA  NACO
PEDA  PEDO  PENE  PIPI  PITO  POPO  PUTA  PUTO
QULO
RATA  ROBA  ROBE  ROBO  RUIN
SENO
TETA
VACA  VAGA  VAGO  VAKA  VUEI  VUEY
WUEI  WUEY
```

### Ejemplo de Sustitución

- BACA → B**X**CA (segunda letra 'A' se sustituye por 'X')
- PEDO → P**X**DO (segunda letra 'E' se sustituye por 'X')
- CACA → C**X**CA (segunda letra 'A' se sustituye por 'X')

## Códigos de Entidades Federativas

```
AS - Aguascalientes          BC - Baja California
BS - Baja California Sur      CC - Campeche
CL - Coahuila                 CM - Colima
CS - Chiapas                  CH - Chihuahua
DF - Ciudad de México         DG - Durango
GT - Guanajuato               GR - Guerrero
HG - Hidalgo                  JC - Jalisco
MC - Estado de México         MN - Michoacán
MS - Morelos                  NT - Nayarit
NL - Nuevo León               OC - Oaxaca
PL - Puebla                   QT - Querétaro
QR - Quintana Roo             SP - San Luis Potosí
SL - Sinaloa                  SR - Sonora
TC - Tabasco                  TS - Tamaulipas
TL - Tlaxcala                 VZ - Veracruz
YN - Yucatán                  ZS - Zacatecas
NE - Nacido en el Extranjero
```

## Consonantes Internas (Posiciones 14-16)

Se extraen las primeras consonantes internas (que no sean la inicial) de:
1. Apellido paterno
2. Apellido materno (X si no tiene)
3. Primer nombre

**Consonantes:** B, C, D, F, G, H, J, K, L, M, N, P, Q, R, S, T, V, W, X, Y, Z

## Diferenciador de Homonimia (Posición 17)

**IMPORTANTE:** Esta posición es **asignada por RENAPO** para evitar duplicados y **NO es calculable algorítmicamente**.

### Reglas de Asignación

- Para personas nacidas **antes del año 2000:** números del 0 al 9
- Para personas nacidas **del año 2000 en adelante:** letras A-Z o números 0-9

### Cómo Funciona

Cuando dos o más personas tienen los mismos primeros 16 caracteres (mismo nombre, apellidos, fecha de nacimiento, género y estado), RENAPO asigna **diferentes diferenciadores** para hacer únicos sus CURPs:

**Ejemplo de Homonimia:**
```
Persona 1: MAPR990512HJCRRS0  → diferenciador '0' → dígito verificador calculado
Persona 2: MAPR990512HJCRRS1  → diferenciador '1' → dígito verificador calculado
Persona 3: MAPR990512HJCRRS2  → diferenciador '2' → dígito verificador calculado
```

Cada diferenciador genera un **dígito verificador diferente** (posición 18), por lo que aunque compartan los primeros 16 caracteres, cada CURP es único y válido.

**Nota:** Los generadores automáticos no pueden calcular este valor con precisión. Solo RENAPO puede asignarlo oficialmente al consultar su base de datos de CURPs existentes.

## Dígito Verificador (Posición 18)

El dígito verificador **SÍ es calculable** mediante el siguiente algoritmo oficial:

### Algoritmo del Dígito Verificador

1. **Diccionario de valores:** `"0123456789ABCDEFGHIJKLMNÑOPQRSTUVWXYZ"`
   - '0' tiene valor 0
   - '9' tiene valor 9
   - 'A' tiene valor 10
   - 'Z' tiene valor 36
   - 'Ñ' tiene valor 24 (entre N y O)

2. **Cálculo:**
   ```
   Para cada carácter de los primeros 17:
       valor = índice_en_diccionario × (18 - posición)
   
   suma_total = suma de todos los valores
   
   dígito = 10 - (suma_total mod 10)
   
   Si dígito == 10, entonces dígito = 0
   ```

3. **Ejemplo:**
   ```
   CURP (primeros 17): PEGJ900512HJCRRS0
   
   P (pos 0): 26 × 18 = 468
   E (pos 1): 14 × 17 = 238
   G (pos 2): 16 × 16 = 256
   J (pos 3): 19 × 15 = 285
   ... (continuar para las 17 posiciones)
   
   Suma total: 2136
   2136 mod 10 = 6
   10 - 6 = 4
   
   Dígito verificador: 4
   ```

## Validación de CURP

Un CURP es válido si cumple:

1. ✅ Longitud exacta de 18 caracteres
2. ✅ Estructura válida según regex oficial
3. ✅ Fecha de nacimiento válida (posiciones 5-10)
4. ✅ Sexo válido: H o M (posición 11)
5. ✅ Código de estado válido (posiciones 12-13)
6. ✅ Consonantes válidas (posiciones 14-16): solo consonantes
7. ✅ **Dígito verificador correcto (posición 18)** - ¡ESTO ES VALIDABLE!

### Validación del Dígito Verificador

**IMPORTANTE:** Aunque el diferenciador (posición 17) es asignado por RENAPO, el **dígito verificador (posición 18) SÍ puede validarse** para cualquier CURP completo.

Esto permite verificar que un CURP es **matemáticamente consistente**:

```python
# Ejemplo de validación
curp = "PEGJ900512HJCRRS04"  # CURP completo

# Extraer primeros 17 caracteres
curp_17 = curp[:17]  # "PEGJ900512HJCRRS0"

# Calcular dígito verificador esperado
digito_esperado = calculate_check_digit(curp_17)  # "4"

# Comparar con el dígito actual (posición 18)
digito_actual = curp[17]  # "4"

es_valido = (digito_esperado == digito_actual)  # True
```

**Casos de uso:**
- ✅ Validar CURPs capturados manualmente (detectar errores de tipeo)
- ✅ Verificar integridad de CURPs almacenados en bases de datos
- ✅ Confirmar que un CURP oficial de RENAPO es matemáticamente correcto

**Nota:** La validación del diferenciador (posición 17) no es posible sin acceso a la base de datos oficial de RENAPO, pero el dígito verificador (18) sí es validable.

## Capacidades y Limitaciones de Generadores Automáticos

### ✅ Lo que SÍ puede hacer este generador:

1. ✅ Generar las primeras **16 posiciones** del CURP con precisión
2. ✅ Aplicar todas las reglas oficiales de RENAPO (palabras inconvenientes, nombres especiales, etc.)
3. ✅ **Calcular el dígito verificador (posición 18)** para cualquier CURP
4. ✅ **Validar cualquier CURP completo** verificando su dígito verificador
5. ✅ Generar CURPs válidos para pruebas y desarrollo

### ❌ Lo que NO puede hacer:

1. ❌ Determinar el diferenciador exacto (posición 17) que asignaría RENAPO
2. ❌ Acceder a la base de datos oficial para verificar duplicados
3. ❌ Garantizar que el CURP generado coincida 100% con el oficial de RENAPO

### Por qué la posición 17 varía:

RENAPO asigna el diferenciador consultando su base de datos para evitar duplicados. Si hay homonimias (dos personas con los mismos primeros 16 caracteres), cada una recibe un diferenciador único (0, 1, 2... o A, B, C...).

**Para obtener un CURP oficial:** Consultar https://www.gob.mx/curp/

**Para validar un CURP existente:** Use el método `validate_check_digit()` de este proyecto.

## Referencias Oficiales

- Diario Oficial de la Federación (DOF) - Modificación al Instructivo Normativo (18/10/2021)
- RENAPO (Registro Nacional de Población e Identidad)
- Secretaría de Gobernación (SEGOB)

---

**Implementado en:** `python-rfcmx` v1.0
**Última actualización:** 2025-01-08
