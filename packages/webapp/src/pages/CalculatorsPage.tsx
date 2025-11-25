import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useLocale } from '@/lib/locale';
import ISRPage from './ISRPage';
import IVAPage from './IVAPage';
import IEPSPage from './IEPSPage';

export default function CalculatorsPage() {
  const { t } = useLocale();

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-2">
        <h1 className="text-3xl font-bold tracking-tight">{t('nav.calculators.title')}</h1>
        <p className="text-muted-foreground">
          Calculadoras fiscales oficiales actualizadas para 2024.
        </p>
      </div>

      <Tabs defaultValue="isr" className="w-full space-y-6">
        <div className="overflow-x-auto pb-2 -mx-4 px-4 sm:mx-0 sm:px-0 sm:pb-0">
          <TabsList className="w-full sm:w-auto justify-start bg-transparent sm:bg-muted p-0 sm:p-1 gap-2 sm:gap-1 h-auto">
            <TabsTrigger 
              value="isr" 
              className="data-[state=active]:bg-primary/10 data-[state=active]:text-primary data-[state=active]:shadow-none border border-transparent data-[state=active]:border-primary/20 bg-muted/50 w-full sm:w-auto"
            >
              ISR (Renta)
            </TabsTrigger>
            <TabsTrigger 
              value="iva" 
              className="data-[state=active]:bg-primary/10 data-[state=active]:text-primary data-[state=active]:shadow-none border border-transparent data-[state=active]:border-primary/20 bg-muted/50 w-full sm:w-auto"
            >
              IVA (Valor Agregado)
            </TabsTrigger>
            <TabsTrigger 
              value="ieps" 
              className="data-[state=active]:bg-primary/10 data-[state=active]:text-primary data-[state=active]:shadow-none border border-transparent data-[state=active]:border-primary/20 bg-muted/50 w-full sm:w-auto"
            >
              IEPS (Especial)
            </TabsTrigger>
          </TabsList>
        </div>

        <TabsContent value="isr" className="mt-0 focus-visible:ring-0">
          <ISRPage />
        </TabsContent>
        <TabsContent value="iva" className="mt-0 focus-visible:ring-0">
          <IVAPage />
        </TabsContent>
        <TabsContent value="ieps" className="mt-0 focus-visible:ring-0">
          <IEPSPage />
        </TabsContent>
      </Tabs>
    </div>
  );
}

