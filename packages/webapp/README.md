# catalogmx Demo Web Application

Interactive demonstration and documentation for the catalogmx library - a comprehensive Mexican data validation and catalog library.

## Features

- **Validators Demo**: Interactive validation and generation for RFC, CURP, CLABE, and NSS
- **Catalog Browser**: Browse 58 official Mexican government catalogs with 470,000+ records
- **Tax Calculators**: ISR, IVA, IEPS calculation tools
- **Code Examples**: TypeScript, Python, and Dart usage examples
- **Installation Guide**: Setup instructions for all supported platforms

## Quick Start

### Development

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

Open http://localhost:5173 in your browser.

### Production Build

```bash
# Build for production
npm run build

# Preview production build
npm run preview
```

### Deploy to Static Server

The `dist/` folder contains all files needed for deployment. Simply copy to any static hosting:

```bash
# Example: Copy to nginx
cp -r dist/* /var/www/html/

# Example: Upload to GitHub Pages, Netlify, Vercel, etc.
```

## Directory Structure

```
webapp/
├── src/
│   ├── main.ts      # Application logic
│   └── styles.css   # Styles
├── index.html       # Entry point
├── vite.config.ts   # Build configuration
├── tsconfig.json    # TypeScript config
└── dist/            # Production build output
```

## Catalog Categories

### Banxico (Banco de Mexico)
- Banks (150+ Mexican banks with SPEI support)
- Currencies (ISO 4217 codes)
- UDI Values (Unidades de Inversion)
- Financial Institutions

### INEGI (Instituto Nacional de Estadistica)
- States (32 Mexican states with CURP codes)
- Municipalities (2,458 municipalities)
- Localities (300K+ with GPS coordinates)

### SEPOMEX (Servicio Postal Mexicano)
- Postal Codes (157K+ codes)

### SAT CFDI 4.0 (Electronic Invoicing)
- Tax Regimes
- Invoice Usage
- Payment Methods
- Document Types
- Tax Types
- Unit Codes
- Products/Services (8,000+ codes)

### SAT Comercio Exterior 2.0
- Incoterms
- Countries

### SAT Carta Porte 3.0
- Airports
- Seaports
- Hazardous Materials

### SAT Nomina 1.2
- Contract Types
- Work Shifts
- Payment Frequency
- Job Risk Levels

### IFT (Telecomunicaciones)
- Area Codes (LADA)
- Mobile Operators

### Mexico (National)
- Minimum Wages
- UMA Values
- Hoy No Circula CDMX

## License

BSD-2-Clause
