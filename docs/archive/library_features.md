# Analysis of the `catalogmx` Library Features

`catalogmx` is a comprehensive, multi-language library available in both Python and TypeScript. It is designed to provide tools for validating Mexican identifiers and accessing official catalogs from various Mexican government agencies.

### Core Features:

1.  **Validators for Mexican Identifiers**:
    *   **RFC** (Registro Federal de Contribuyentes): For individuals (`Persona Física`) and companies (`Persona Moral`), including `homoclave` and check digit validation.
    *   **CURP** (Clave Única de Registro de Población): Includes validation and generation, handling of inconvenient words, and extraction of data like birth date and gender.
    *   **CLABE** (Clave Bancaria Estandarizada): 18-digit bank account validation with check digit algorithm and integration with Banxico's bank catalog.
    *   **NSS** (Número de Seguridad Social): 11-digit IMSS number validation.

2.  **Official Mexican Catalogs**:
    The library provides access to over 40 official catalogs, containing more than 170,000 records.
    *   **SAT** (Servicio de Administración Tributaria): Includes catalogs for CFDI 4.0, Comercio Exterior 2.0, Carta Porte 3.0, and Nómina 1.2.
    *   **INEGI** (Instituto Nacional de Estadística y Geografía): Provides geographic data, including municipalities, localities with GPS coordinates, and population data from the 2020 census. It also supports geographic searches.
    *   **SEPOMEX** (Servicio Postal Mexicano): A complete catalog of Mexican postal codes.
    *   **Banxico** (Banco de México): Information on financial institutions.

3.  **Multi-language Support**:
    *   It offers identical APIs for both **Python** (3.10+) and **TypeScript** (5.0+), making it versatile for different development stacks.

4.  **Production-Ready**:
    *   The library is type-safe, well-documented, tested, and actively maintained.
    *   It uses a lazy-loading architecture and JSON-based storage for catalogs. For larger catalogs, an SQLite-based storage is planned to improve performance and reduce memory usage.

### Technical Details:

*   **Dependencies**: The core validators have zero external dependencies.
*   **Data Size**: The complete set of catalogs is around 50 MB.
*   **Project Structure**: The project is organized into Python and TypeScript packages, with shared data for the catalogs. It also includes scripts for processing and updating the catalog data.

### Future Development (Roadmap):

*   **SQLite Integration**: For faster queries and better handling of large datasets.
*   **Additional Validators**: For things like ISAN, license plates, etc.
*   **More Catalogs**: From IFT, IMSS, and TIGIE.
*   **Automation**: Automated updates for catalogs.
*   **API Examples**: REST and GraphQL API server examples.

In summary, `catalogmx` is a powerful and extensive library for developers working with Mexican data, providing essential validation functions and a large repository of official information in an easy-to-use format for both Python and TypeScript environments.
