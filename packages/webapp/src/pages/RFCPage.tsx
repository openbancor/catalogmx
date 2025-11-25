import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Check, X, Building2, User, AlertCircle } from 'lucide-react';
import { validateRFC, generateRFC, type RFCValidationResult } from '@/lib/validators';
import { useLocale } from '@/lib/locale';

export default function RFCPage() {
  const { t } = useLocale();
  const [rfcInput, setRfcInput] = useState('');
  const [result, setResult] = useState<RFCValidationResult | null>(null);

  // Generator state
  const [genNombre, setGenNombre] = useState('');
  const [genPaterno, setGenPaterno] = useState('');
  const [genMaterno, setGenMaterno] = useState('');
  const [genFecha, setGenFecha] = useState('');
  const [generatedRFC, setGeneratedRFC] = useState('');

  const handleValidate = () => {
    if (rfcInput.trim()) {
      setResult(validateRFC(rfcInput));
    }
  };

  const handleGenerate = () => {
    if (genNombre && genPaterno && genFecha) {
      const fecha = new Date(`${genFecha}T00:00:00`);
      if (!Number.isNaN(fecha.getTime())) {
        const rfc = generateRFC({
          nombre: genNombre,
          paterno: genPaterno,
          materno: genMaterno || 'X',
          fecha
        });
        setGeneratedRFC(rfc);
      } else {
        setGeneratedRFC('');
      }
    }
  };

  return (
    <div className="space-y-6 max-w-4xl">
      <div>
        <h1 className="text-2xl sm:text-3xl font-bold">{t('validators.rfc.title')}</h1>
        <p className="text-muted-foreground mt-1 text-sm sm:text-base">
          {t('validators.rfc.subtitle')}
        </p>
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Validator */}
        <Card>
          <CardHeader>
            <CardTitle>{t('validators.rfc.card.validate')}</CardTitle>
            <CardDescription>
              {t('validators.rfc.card.validate.desc')}
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="text-sm font-medium mb-2 block">{t('validators.rfc.label')}</label>
              <Input
                placeholder={t('validators.rfc.placeholder')}
                value={rfcInput}
                onChange={(e) => setRfcInput(e.target.value.toUpperCase())}
                className="font-mono"
              />
            </div>
            <Button onClick={handleValidate} className="w-full">
              {t('validators.rfc.button.validate')}
            </Button>

            {result && (
              <div className="space-y-4 pt-4 border-t">
                {/* Status */}
                <div className={`p-4 rounded-lg flex items-center gap-3 ${
                  result.isValid ? 'bg-green-50 text-green-800 dark:bg-green-950 dark:text-green-200' : 'bg-red-50 text-red-800 dark:bg-red-950 dark:text-red-200'
                }`}>
                  {result.isValid ? <Check className="h-5 w-5" /> : <X className="h-5 w-5" />}
                  <span className="font-medium">
                    {result.isValid ? t('validators.rfc.status.valid') : t('validators.rfc.status.invalid')}
                  </span>
                  {result.type !== 'invalid' && (
                    <Badge variant="outline" className="ml-auto">
                      {result.type === 'persona_fisica' && <><User className="h-3 w-3 mr-1" /> PF</>}
                      {result.type === 'persona_moral' && <><Building2 className="h-3 w-3 mr-1" /> PM</>}
                      {result.type === 'generic' && <><AlertCircle className="h-3 w-3 mr-1" /> Generic</>}
                    </Badge>
                  )}
                </div>

                {/* Validation Details */}
                <div className="space-y-2">
                  <div className="text-sm font-medium">{t('validators.rfc.details')}</div>
                  <div className="grid grid-cols-3 gap-2">
                    <div className={`p-2 rounded text-center text-sm ${result.details.format ? 'bg-green-100 dark:bg-green-900' : 'bg-red-100 dark:bg-red-900'}`}>
                      <div className="font-medium">{t('validators.rfc.format')}</div>
                      <div>{result.details.format ? '✓' : '✗'}</div>
                    </div>
                    <div className={`p-2 rounded text-center text-sm ${result.details.date ? 'bg-green-100 dark:bg-green-900' : 'bg-red-100 dark:bg-red-900'}`}>
                      <div className="font-medium">{t('validators.rfc.date')}</div>
                      <div>{result.details.date ? '✓' : '✗'}</div>
                    </div>
                    <div className={`p-2 rounded text-center text-sm ${result.details.checksum ? 'bg-green-100 dark:bg-green-900' : 'bg-red-100 dark:bg-red-900'}`}>
                      <div className="font-medium">{t('validators.rfc.checksum')}</div>
                      <div>{result.details.checksum ? '✓' : '✗'}</div>
                    </div>
                  </div>
                </div>

                {/* Parsed Components */}
                {result.parsed && (
                  <div className="space-y-2">
                    <div className="text-sm font-medium">{t('validators.rfc.parsed')}</div>
                    <div className="grid grid-cols-2 gap-2 text-sm">
                      <div className="p-2 bg-muted rounded">
                        <div className="text-muted-foreground">{t('validators.rfc.initials')}</div>
                        <div className="font-mono font-medium">{result.parsed.initials}</div>
                      </div>
                      <div className="p-2 bg-muted rounded">
                        <div className="text-muted-foreground">{t('validators.rfc.date')}</div>
                        <div className="font-mono font-medium">{result.parsed.date}</div>
                      </div>
                      <div className="p-2 bg-muted rounded">
                        <div className="text-muted-foreground">{t('validators.rfc.homoclave')}</div>
                        <div className="font-mono font-medium">{result.parsed.homoclave}</div>
                      </div>
                      <div className="p-2 bg-muted rounded">
                        <div className="text-muted-foreground">{t('validators.rfc.checkDigit')}</div>
                        <div className="font-mono font-medium">{result.parsed.checkDigit}</div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Generator */}
        <Card>
          <CardHeader>
            <CardTitle>{t('validators.rfc.generate.title')}</CardTitle>
            <CardDescription>
              {t('validators.rfc.generate.desc')}
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label className="text-sm font-medium mb-1 block">{t('validators.rfc.generate.name')}</label>
                <Input
                  placeholder="Juan"
                  value={genNombre}
                  onChange={(e) => setGenNombre(e.target.value)}
                />
              </div>
              <div>
                <label className="text-sm font-medium mb-1 block">{t('validators.rfc.generate.paterno')}</label>
                <Input
                  placeholder="Garcia"
                  value={genPaterno}
                  onChange={(e) => setGenPaterno(e.target.value)}
                />
              </div>
              <div>
                <label className="text-sm font-medium mb-1 block">{t('validators.rfc.generate.materno')}</label>
                <Input
                  placeholder="Lopez"
                  value={genMaterno}
                  onChange={(e) => setGenMaterno(e.target.value)}
                />
              </div>
              <div>
                <label className="text-sm font-medium mb-1 block">{t('validators.rfc.generate.birthdate')}</label>
                <Input
                  type="date"
                  value={genFecha}
                  onChange={(e) => setGenFecha(e.target.value)}
                />
              </div>
            </div>
            <Button onClick={handleGenerate} className="w-full">
              {t('validators.rfc.generate.button')}
            </Button>

            {generatedRFC && (
              <div className="p-4 bg-primary/10 rounded-lg text-center">
                <div className="text-sm text-muted-foreground mb-1">{t('validators.rfc.generate.result')}</div>
                <div className="text-2xl font-mono font-bold tracking-wider">
                  {generatedRFC}
                </div>
                <div className="text-xs text-muted-foreground mt-2">
                  {t('validators.rfc.generate.note')}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Documentation */}
      <Card>
        <CardHeader>
          <CardTitle>{t('validators.rfc.docs.title')}</CardTitle>
        </CardHeader>
        <CardContent className="prose prose-sm dark:prose-invert max-w-none">
          <ul>
            <li><strong>{t('validators.rfc.docs.pf')}</strong></li>
            <li><strong>{t('validators.rfc.docs.pm')}</strong></li>
          </ul>
          <p>{t('validators.rfc.docs.special')}</p>
          <ul>
            <li><code className="text-sm">XAXX010101000</code> - {t('validators.rfc.docs.generic')}</li>
            <li><code className="text-sm">XEXX010101000</code> - {t('validators.rfc.docs.foreign')}</li>
          </ul>
        </CardContent>
      </Card>
    </div>
  );
}
