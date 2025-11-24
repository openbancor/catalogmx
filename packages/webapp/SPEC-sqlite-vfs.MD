¡Perfecto!
Aquí tienes un instructivo extremadamente detallado, con razonamiento completo, paso a paso, y scripts prácticos, para que puedas convertir todos tus catálogos de catalogmx en un único archivo SQLite unificado, actualizado mensualmente, y servido vía serverless HTTP/Range desde GitHub Pages (o cualquier CDN).

Este instructivo te permitirá:
	•	entender por qué lo hacemos,
	•	replicarlo en tu entorno de desarrollo,
	•	integrarlo con GitHub Actions,
	•	obtener un archivo mexico.sqlite3 listo para usar con SQLite WASM.

⸻

📘 INSTRUCTIVO COMPLETO

Unificar todos los catálogos de CatalogMX en un solo SQLite para Serverless Search

⸻

🧠 1. Razonamiento técnico

✔ Problema actual
	•	Tienes múltiples archivos SQLite independientes.
	•	Cada archivo contiene un catálogo diferente.
	•	Para consultas desde navegador, Node.js o mobile, tendrías que abrir varios archivos.
	•	Cada archivo implica:
	•	un header SQLite,
	•	un B-Tree raíz,
	•	varios bloques,
	•	múltiples HTTP Range requests.

✔ Qué queremos lograr
	•	Un solo archivo SQLite:
	•	más fácil de consumir,
	•	más rápido por HTTP,
	•	mejor cacheado,
	•	más portable,
	•	con todas las tablas dentro del mismo contenedor.

✔ Por qué SQLite es perfecto para esto

SQLite fue diseñado para:
	•	ser portátil (un archivo),
	•	ser consultado en modo sólo lectura,
	•	soportar miles de tablas,
	•	permitir schemas independientes entre tablas,
	•	permitir lectura por páginas fijas (~4 KB).

Y con HTTP VFS, el cliente solo descarga:
	•	las páginas del índice que necesita,
	•	las páginas de los datos que coinciden con la query.

Esto permite serverless search real.

⸻

🧩 2. Diseño final del archivo unificado

El archivo se llamará:

mexico.sqlite3

Dentro contendrá tablas como:

cp
asentamientos
colonias
municipios
bancos
claves_sat
productos_sat
impuestos_sat
…

Cada tabla es independiente.
No hay joins obligatorios entre ellas.
Cada una mantiene su propio esquema.

⸻

🔧 3. Requisitos en tu entorno de desarrollo

Necesitarás:

A. Python 3.8+

Con sqlite3 incluido por defecto.

B. Tu repositorio clonado

git clone https://github.com/OpenBancor/catalogmx
cd catalogmx

C. Las fuentes:
	•	Los CSVs
	•	Los SQLite originales (si decides no usar los CSV)

D. Revisión del schema de cada catálogo

Esto ya viene de tus archivos existentes.

⸻

🛠️ 4. Script: Generar archivo unificado desde cero

Ya existe un generador listo para usarse en:

```
packages/shared-data/build_unified_sqlite.py
```

Características principales:
* Fusiona automáticamente los catálogos grandes que ya están en `packages/shared-data/sqlite/` (SEPOMEX, INEGI localidades, SAT clave producto/servicio).
* Recorre todo `packages/shared-data/**.json` (Banxico, SAT, IFT, etc.) y crea una tabla por archivo conservando los campos originales.
* Añade índices útiles (`codigos_postales`, `localidades`, `clave_prod_serv`) y genera tablas FTS5 listas para búsquedas de texto.
* Soporta banderas para controlar la salida:
  - `--output /ruta/al/archivo.sqlite3`
  - `--skip-json` o `--skip-sqlite` si quieres procesar sólo una fuente.

Uso recomendado (desde la raíz del repo):

```bash
cd packages/shared-data
python build_unified_sqlite.py
# genera packages/shared-data/mexico.sqlite3
```

Si prefieres dejar todo automatizado desde el webapp, usa (desde la raíz del repo):

```bash
cd packages/webapp
npm run data:build
```

Importante: el comando se ejecuta dentro de `packages/webapp`, no en la raíz del repo (de lo contrario `npm` no encontrará el `package.json`). Ese script:
1. Ejecuta `build_unified_sqlite.py` (puedes forzar el intérprete con `PYTHON=...`).
2. Copia todos los `.db/.sqlite/.sqlite3` resultantes (incluyendo `mexico.sqlite3`) hacia `packages/webapp/public/data/`.

Para copiar únicamente los archivos ya existentes (sin regenerar), sigue usando `npm run sync:data`.


⸻

⚙️ 5. Crear índices apropiados por catálogo

Después de importar todas las tablas, añade esto en el script:

def create_indexes(conn):
    indexes = [
        "CREATE INDEX idx_cp_cp ON cp(cp);",
        "CREATE INDEX idx_cp_estado ON cp(estado);",
        "CREATE INDEX idx_asen_nombre ON asentamientos(nombre);",
        "CREATE INDEX idx_bancos_banco ON bancos(clave);",
        # agrega más índices según necesidad
    ]

    for idx in indexes:
        try:
            conn.execute(idx)
        except:
            print("No se pudo crear índice:", idx)

    conn.commit()

Luego llámalo:

create_indexes(conn)


⸻

🔍 6. Opcional: FTS5 por catálogo

Ejemplo para catálogo textual:

conn.execute("""
CREATE VIRTUAL TABLE cp_fts USING fts5(
    cp,
    asentamiento,
    municipio,
    estado,
    content='cp'
);
""")

conn.execute("""
INSERT INTO cp_fts(rowid, cp, asentamiento, municipio, estado)
SELECT rowid, cp, asentamiento, municipio, estado FROM cp;
""")

Esto permite búsqueda tipo Google:

SELECT * FROM cp_fts WHERE cp_fts MATCH 'santa';


⸻

🚀 7. Ejecutar el script

Desde tu repo:

python3 build_unified_sqlite.py

Obtendrás:

mexico.sqlite3


⸻

🌐 8. Publicarlo en GitHub Pages

1. Habilita GitHub Pages en branch gh-pages

/docs/
    mexico.sqlite3
    index.html

O estructura:

/gh-pages/
    mexico.sqlite3

2. Haz push del archivo

mkdir docs
cp mexico.sqlite3 docs/
git add docs/mexico.sqlite3
git commit -m "Añadir archivo SQLite unificado"
git push

Tu base quedará accesible vía:

https://openbancor.github.io/catalogmx/mexico.sqlite3


⸻

🖥️ 9. Uso desde navegador (SQLite WASM)

Ejemplo minimal:

<script type="module">
import sqlite3InitModule from "https://unpkg.com/@sqlite.org/sqlite-wasm/dist/sqlite-wasm/jswasm/sqlite3.mjs";

const sqlite3 = await sqlite3InitModule();
const db = new sqlite3.oo1.DB(
  "https://openbancor.github.io/catalogmx/mexico.sqlite3",
  "opfs-http"
);

let r = db.exec("SELECT * FROM cp WHERE cp LIKE '03%';");
console.log(r);
</script>

Y con esto, SQLite solo descargará 20–80 KB, no 40 MB.

⸻

🔁 10. Actualizaciones mensuales

Cada mes:

git pull
python3 build_unified_sqlite.py
cp mexico.sqlite3 docs/
git commit -am "Actualización de febrero 2025"
git push

Los clientes seguirán funcionando porque el schema no cambia.

⸻

🧱 11. Integración con GitHub Actions (opcional)

Puedo darte un workflow automático como este:
	•	descarga CSVs/SQLites originales
	•	genera mexico.sqlite3
	•	sube a GitHub Pages automáticamente

Dime y te lo armo completo.

⸻

🎉 Listo. Tienes un instructivo completo.

Si quieres, puedo también:
	•	revisar el schema de tus SQLite actuales,
	•	hacer un script “universal” que detecta automáticamente las tablas,
	•	crear un archivo build.sh para tu repo,
	•	crear el workflow de GitHub Actions,
	•	crear un demo en HTML/JS que use Range Requests.

¿Quieres que generemos el workflow de Actions o el demo HTML/JS?
