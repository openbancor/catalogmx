import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { CheckCircle, Package, Terminal, FileCode } from 'lucide-react';

export default function InstallSection() {
  return (
    <div className="space-y-8">
      <div className="text-center max-w-2xl mx-auto">
        <h2 className="text-3xl font-bold mb-2">Installation</h2>
        <p className="text-muted-foreground">
          Get started with catalogmx in TypeScript, Python, or Dart
        </p>
      </div>

      <div className="grid md:grid-cols-3 gap-6">
        {/* TypeScript */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileCode className="h-5 w-5" />
              TypeScript / JavaScript
            </CardTitle>
            <CardDescription>Node.js 16+ | Browser</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <div className="text-sm font-medium mb-2 flex items-center gap-2">
                <Terminal className="h-4 w-4" />
                Install
              </div>
              <pre className="text-sm"><code>{`# npm
npm install catalogmx

# yarn
yarn add catalogmx

# pnpm
pnpm add catalogmx`}</code></pre>
            </div>

            <div>
              <div className="text-sm font-medium mb-2">Usage</div>
              <pre className="text-sm"><code>{`import {
  validateRfc,
  BankCatalog
} from 'catalogmx';

const isValid = validateRfc('...');
const banks = BankCatalog.getAll();`}</code></pre>
            </div>

            <div className="pt-2">
              <a
                href="https://www.npmjs.com/package/catalogmx"
                target="_blank"
                rel="noopener"
                className="text-sm text-primary hover:underline flex items-center gap-1"
              >
                <Package className="h-3 w-3" />
                View on npm
              </a>
            </div>
          </CardContent>
        </Card>

        {/* Python */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileCode className="h-5 w-5" />
              Python
            </CardTitle>
            <CardDescription>Python 3.10+</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <div className="text-sm font-medium mb-2 flex items-center gap-2">
                <Terminal className="h-4 w-4" />
                Install
              </div>
              <pre className="text-sm"><code>{`# pip
pip install catalogmx

# uv (10-100x faster)
uv pip install catalogmx`}</code></pre>
            </div>

            <div>
              <div className="text-sm font-medium mb-2">Usage</div>
              <pre className="text-sm"><code>{`from catalogmx import (
    validate_rfc,
    BankCatalog
)

is_valid = validate_rfc("...")
banks = BankCatalog.get_all()`}</code></pre>
            </div>

            <div className="pt-2">
              <a
                href="https://pypi.org/project/catalogmx/"
                target="_blank"
                rel="noopener"
                className="text-sm text-primary hover:underline flex items-center gap-1"
              >
                <Package className="h-3 w-3" />
                View on PyPI
              </a>
            </div>
          </CardContent>
        </Card>

        {/* Dart */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileCode className="h-5 w-5" />
              Dart / Flutter
            </CardTitle>
            <CardDescription>Dart 3.0+ | Flutter 3.0+</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <div className="text-sm font-medium mb-2 flex items-center gap-2">
                <Terminal className="h-4 w-4" />
                Install
              </div>
              <pre className="text-sm"><code>{`# pubspec.yaml
dependencies:
  catalogmx: ^0.3.0

# or via CLI
dart pub add catalogmx`}</code></pre>
            </div>

            <div>
              <div className="text-sm font-medium mb-2">Usage</div>
              <pre className="text-sm"><code>{`import 'package:catalogmx/catalogmx.dart';

final isValid = validateRfc('...');
final banks = BankCatalog.getAll();`}</code></pre>
            </div>

            <div className="pt-2">
              <a
                href="https://pub.dev/packages/catalogmx"
                target="_blank"
                rel="noopener"
                className="text-sm text-primary hover:underline flex items-center gap-1"
              >
                <Package className="h-3 w-3" />
                View on pub.dev
              </a>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Features Grid */}
      <Card>
        <CardHeader>
          <CardTitle>What's Included</CardTitle>
          <CardDescription>All features available in every platform</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
            <FeatureGroup
              title="Validators"
              items={[
                'RFC (Tax ID)',
                'CURP (National ID)',
                'CLABE (Bank Account)',
                'NSS (Social Security)'
              ]}
            />
            <FeatureGroup
              title="Banxico Catalogs"
              items={[
                'Banks (150+)',
                'Currencies (ISO 4217)',
                'UDI Values',
                'Financial Institutions'
              ]}
            />
            <FeatureGroup
              title="INEGI Catalogs"
              items={[
                'States (32)',
                'Municipalities (2,458)',
                'Localities (300K+ with GPS)'
              ]}
            />
            <FeatureGroup
              title="SEPOMEX"
              items={[
                'Postal Codes (157K+)',
                'Colonies',
                'Settlement Types'
              ]}
            />
            <FeatureGroup
              title="SAT CFDI 4.0"
              items={[
                'Tax Regimes',
                'Invoice Usage',
                'Payment Methods',
                'Products/Services (8K+)'
              ]}
            />
            <FeatureGroup
              title="Tax Calculators"
              items={[
                'ISR (Income Tax)',
                'IVA (VAT)',
                'IEPS (Excise)',
                'Withholdings'
              ]}
            />
          </div>
        </CardContent>
      </Card>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard value="93.78%" label="Test Coverage" />
        <StatCard value="1,250+" label="Tests Passing" />
        <StatCard value="58" label="Catalogs" />
        <StatCard value="470K+" label="Records" />
      </div>
    </div>
  );
}

function FeatureGroup({ title, items }: { title: string; items: string[] }) {
  return (
    <div>
      <h4 className="font-semibold mb-3">{title}</h4>
      <ul className="space-y-2">
        {items.map((item) => (
          <li key={item} className="flex items-center gap-2 text-sm text-muted-foreground">
            <CheckCircle className="h-4 w-4 text-primary flex-shrink-0" />
            {item}
          </li>
        ))}
      </ul>
    </div>
  );
}

function StatCard({ value, label }: { value: string; label: string }) {
  return (
    <div className="p-6 bg-card border rounded-lg text-center">
      <div className="text-3xl font-bold text-primary">{value}</div>
      <div className="text-sm text-muted-foreground">{label}</div>
    </div>
  );
}
