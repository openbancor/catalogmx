import { useState } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { FileCheck, Database, Calculator, Code, Package } from 'lucide-react';
import ValidatorsSection from '@/components/ValidatorsSection';
import CatalogsSection from '@/components/CatalogsSection';
import CalculatorsSection from '@/components/CalculatorsSection';
import CodeExamples from '@/components/CodeExamples';
import InstallSection from '@/components/InstallSection';

function App() {
  const [activeTab, setActiveTab] = useState('validators');

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="bg-primary text-primary-foreground">
        <div className="container mx-auto px-4 py-12">
          <div className="max-w-4xl mx-auto text-center">
            <h1 className="text-4xl md:text-5xl font-bold mb-4">catalogmx</h1>
            <p className="text-xl opacity-90 mb-6">
              Comprehensive Mexican Data Validation & Official Catalogs Library
            </p>
            <div className="flex flex-wrap gap-2 justify-center">
              <Badge variant="secondary" className="text-sm">93.78% Test Coverage</Badge>
              <Badge variant="secondary" className="text-sm">1,250+ Tests</Badge>
              <Badge variant="secondary" className="text-sm">58 Catalogs</Badge>
              <Badge variant="secondary" className="text-sm">470K+ Records</Badge>
              <Badge variant="secondary" className="text-sm">Python + TypeScript + Dart</Badge>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-8">
          <TabsList className="grid w-full max-w-3xl mx-auto grid-cols-5 h-auto p-1">
            <TabsTrigger value="validators" className="flex flex-col gap-1 py-3">
              <FileCheck className="h-4 w-4" />
              <span className="text-xs">Validators</span>
            </TabsTrigger>
            <TabsTrigger value="catalogs" className="flex flex-col gap-1 py-3">
              <Database className="h-4 w-4" />
              <span className="text-xs">Catalogs</span>
            </TabsTrigger>
            <TabsTrigger value="calculators" className="flex flex-col gap-1 py-3">
              <Calculator className="h-4 w-4" />
              <span className="text-xs">Calculators</span>
            </TabsTrigger>
            <TabsTrigger value="examples" className="flex flex-col gap-1 py-3">
              <Code className="h-4 w-4" />
              <span className="text-xs">Examples</span>
            </TabsTrigger>
            <TabsTrigger value="install" className="flex flex-col gap-1 py-3">
              <Package className="h-4 w-4" />
              <span className="text-xs">Install</span>
            </TabsTrigger>
          </TabsList>

          <TabsContent value="validators" className="animate-fade-in">
            <ValidatorsSection />
          </TabsContent>

          <TabsContent value="catalogs" className="animate-fade-in">
            <CatalogsSection />
          </TabsContent>

          <TabsContent value="calculators" className="animate-fade-in">
            <CalculatorsSection />
          </TabsContent>

          <TabsContent value="examples" className="animate-fade-in">
            <CodeExamples />
          </TabsContent>

          <TabsContent value="install" className="animate-fade-in">
            <InstallSection />
          </TabsContent>
        </Tabs>
      </main>

      {/* Footer */}
      <footer className="border-t bg-muted/50 mt-12">
        <div className="container mx-auto px-4 py-8">
          <div className="text-center text-sm text-muted-foreground">
            <p className="mb-2">
              <strong>catalogmx</strong> - BSD-2-Clause License
            </p>
            <p>
              <a href="https://github.com/openbancor/catalogmx" className="hover:underline" target="_blank" rel="noopener">GitHub</a>
              {' · '}
              <a href="https://www.npmjs.com/package/catalogmx" className="hover:underline" target="_blank" rel="noopener">npm</a>
              {' · '}
              <a href="https://pypi.org/project/catalogmx/" className="hover:underline" target="_blank" rel="noopener">PyPI</a>
              {' · '}
              <a href="https://pub.dev/packages/catalogmx" className="hover:underline" target="_blank" rel="noopener">pub.dev</a>
            </p>
            <p className="mt-2 opacity-75">
              Maintained by Luis Fernando Barrera
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
