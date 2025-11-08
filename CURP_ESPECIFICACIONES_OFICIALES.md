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

**IMPORTANTE:** Esta posición es **asignada aleatoriamente por RENAPO** y **NO es calculable algorítmicamente**.

- Para personas nacidas **antes del año 2000:** números del 0 al 9
- Para personas nacidas **del año 2000 en adelante:** letras A-Z o números 0-9

**Nota:** Los generadores automáticos no pueden calcular este valor con precisión. Solo RENAPO puede asignarlo oficialmente.

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
7. ✅ Dígito verificador correcto (posición 18)

**Nota:** La validación del diferenciador (posición 17) no es posible sin acceso a la base de datos oficial de RENAPO.

## Limitaciones de Generadores Automáticos

Los generadores automáticos de CURP (como este proyecto) **NO pueden generar CURPs 100% oficiales** porque:

1. ❌ La posición 17 (diferenciador) es asignada aleatoriamente por RENAPO
2. ❌ No tienen acceso a la base de datos de CURPs existentes para evitar duplicados
3. ⚠️ El dígito verificador puede calcularse, pero depende del diferenciador

**Para obtener un CURP oficial:** Consultar https://www.gob.mx/curp/

## Referencias Oficiales

- Diario Oficial de la Federación (DOF) - Modificación al Instructivo Normativo (18/10/2021)
- RENAPO (Registro Nacional de Población e Identidad)
- Secretaría de Gobernación (SEGOB)

---

**Implementado en:** `python-rfcmx` v1.0
**Última actualización:** 2025-01-08
