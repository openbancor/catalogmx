import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useLocale } from '@/lib/locale';
import RFCPage from './RFCPage';
import CURPPage from './CURPPage';
import CLABEPage from './CLABEPage';
import NSSPage from './NSSPage';

export default function ValidatorsPage() {
  const { t } = useLocale();

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-2">
        <h1 className="text-3xl font-bold tracking-tight">{t('nav.validators.title')}</h1>
        <p className="text-muted-foreground">
          Herramientas de validación y generación de identificadores mexicanos.
        </p>
      </div>

      <Tabs defaultValue="rfc" className="w-full space-y-6">
        <div className="overflow-x-auto pb-2 -mx-4 px-4 sm:mx-0 sm:px-0 sm:pb-0">
          <TabsList className="w-full sm:w-auto justify-start bg-transparent sm:bg-muted p-0 sm:p-1 gap-2 sm:gap-1 h-auto">
            <TabsTrigger 
              value="rfc" 
              className="data-[state=active]:bg-primary/10 data-[state=active]:text-primary data-[state=active]:shadow-none border border-transparent data-[state=active]:border-primary/20 bg-muted/50 min-w-[80px]"
            >
              RFC
            </TabsTrigger>
            <TabsTrigger 
              value="curp" 
              className="data-[state=active]:bg-primary/10 data-[state=active]:text-primary data-[state=active]:shadow-none border border-transparent data-[state=active]:border-primary/20 bg-muted/50 min-w-[80px]"
            >
              CURP
            </TabsTrigger>
            <TabsTrigger 
              value="clabe" 
              className="data-[state=active]:bg-primary/10 data-[state=active]:text-primary data-[state=active]:shadow-none border border-transparent data-[state=active]:border-primary/20 bg-muted/50 min-w-[80px]"
            >
              CLABE
            </TabsTrigger>
            <TabsTrigger 
              value="nss" 
              className="data-[state=active]:bg-primary/10 data-[state=active]:text-primary data-[state=active]:shadow-none border border-transparent data-[state=active]:border-primary/20 bg-muted/50 min-w-[80px]"
            >
              NSS
            </TabsTrigger>
          </TabsList>
        </div>

        <TabsContent value="rfc" className="mt-0 focus-visible:ring-0">
          <RFCPage />
        </TabsContent>
        <TabsContent value="curp" className="mt-0 focus-visible:ring-0">
          <CURPPage />
        </TabsContent>
        <TabsContent value="clabe" className="mt-0 focus-visible:ring-0">
          <CLABEPage />
        </TabsContent>
        <TabsContent value="nss" className="mt-0 focus-visible:ring-0">
          <NSSPage />
        </TabsContent>
      </Tabs>
    </div>
  );
}

