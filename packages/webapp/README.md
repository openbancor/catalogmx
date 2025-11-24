# catalogmx Demo Web Application

Interactive demonstration and documentation for the catalogmx library - a comprehensive Mexican data validation and catalog library.

Built with **React 18**, **TypeScript**, **Tailwind CSS**, and **shadcn/ui** components.

> The SQLite database in `public/data/` now ships with the full catalog set. Regenerate it anytime from `packages/shared-data` with `npm run data:build` (this also syncs the output to `public/data/`).

## Features

- **Validators Demo**: Interactive validation and generation for RFC, CURP, CLABE, and NSS with detailed breakdowns
- **Catalog Browser**: Browse 58 official Mexican government catalogs with search and pagination
- **Tax Calculators**: ISR with step-by-step debugging, IVA, and IEPS calculators
- **Code Examples**: TypeScript, Python, and Dart usage examples with tabs
- **Installation Guide**: Setup instructions for all supported platforms

## Tech Stack

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **Radix UI** - Headless components (shadcn/ui)
- **Lucide React** - Icons

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

The `dist/` folder contains all files needed for deployment:

```bash
# GitHub Pages, Netlify, Vercel, etc.
# Just point to the dist/ folder

# Manual deployment
cp -r dist/* /var/www/html/
```

## Directory Structure

```
webapp/
├── src/
│   ├── components/      # React components
│   │   ├── ui/         # shadcn/ui components
│   │   ├── ValidatorsSection.tsx
│   │   ├── CatalogsSection.tsx
│   │   ├── CalculatorsSection.tsx
│   │   └── ...
│   ├── lib/            # Utilities and validators
│   │   ├── validators.ts
│   │   ├── calculators.ts
│   │   └── utils.ts
│   ├── data/           # Catalog data
│   ├── App.tsx         # Main application
│   └── main.tsx        # Entry point
├── index.html
├── vite.config.ts
├── tailwind.config.js
└── tsconfig.json
```

## Features Detail

### Validators
- **RFC**: Validate and generate RFC with type detection (persona física/moral)
- **CURP**: Validate with birthdate, gender, and state extraction
- **CLABE**: Validate with bank and branch code parsing
- **NSS**: Validate with IMSS structure breakdown

### Tax Calculators
- **ISR Calculator**: Step-by-step calculation with 2024 brackets and subsidy
- **IVA Calculator**: Standard (16%), border zone (8%), and exempt rates
- **IEPS Calculator**: Rates for alcohol, tobacco, fuel, sugary drinks

### Catalog Browser
Searchable catalogs from:
- Banxico (Banks, Currencies, UDI)
- INEGI (States, Municipalities, Localities)
- SEPOMEX (Postal Codes)
- SAT CFDI 4.0 (Tax Regimes, Invoice Usage, Payment Methods)
- SAT Nómina (Contract Types, Job Risk Levels)
- IFT (Area Codes)
- Mexico (Minimum Wages, UMA)

## License

BSD-2-Clause
