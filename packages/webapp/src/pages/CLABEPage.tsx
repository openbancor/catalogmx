import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Check, X, Building, CreditCard, Copy, RefreshCw, Zap } from 'lucide-react';
import { validateCLABE, generateCLABE, generateCLABERandom, getBankOptions, formatCLABE, type CLABEValidationResult } from '@/lib/validators';

export default function CLABEPage() {
  const [clabeInput, setClabeInput] = useState('');
  const [result, setResult] = useState<CLABEValidationResult | null>(null);

  // Generator state
  const [genBankCode, setGenBankCode] = useState('');
  const [genBranchCode, setGenBranchCode] = useState('');
  const [genAccountNumber, setGenAccountNumber] = useState('');
  const [generatedClabe, setGeneratedClabe] = useState('');
  const [generatedResult, setGeneratedResult] = useState<CLABEValidationResult | null>(null);

  const bankOptions = getBankOptions();

  const handleValidate = () => {
    if (clabeInput.trim()) {
      setResult(validateCLABE(clabeInput));
    }
  };

  const handleGenerate = () => {
    try {
      let clabe: string;
      if (genBankCode || genBranchCode || genAccountNumber) {
        // Use provided values, with defaults for missing
        const bankCode = genBankCode || '012';
        const branchCode = genBranchCode || Math.floor(Math.random() * 999 + 1).toString().padStart(3, '0');
        const accountNumber = genAccountNumber || Math.floor(Math.random() * 99999999999 + 1).toString().padStart(11, '0');
        clabe = generateCLABE(bankCode, branchCode, accountNumber);
      } else {
        clabe = generateCLABERandom();
      }
      setGeneratedClabe(clabe);
      setGeneratedResult(validateCLABE(clabe));
    } catch {
      setGeneratedClabe('Error generating CLABE');
      setGeneratedResult(null);
    }
  };

  const handleGenerateRandom = () => {
    const clabe = generateCLABERandom();
    setGeneratedClabe(clabe);
    setGeneratedResult(validateCLABE(clabe));
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  return (
    <div className="space-y-6 max-w-4xl">
      <div>
        <h1 className="text-2xl font-bold">CLABE Validator & Generator</h1>
        <p className="text-muted-foreground mt-1">
          Clave Bancaria Estandarizada - Validar y generar CLABEs
        </p>
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Validator */}
        <Card>
          <CardHeader>
            <CardTitle>Validar CLABE</CardTitle>
            <CardDescription>
              Ingresa una CLABE de 18 dígitos para validar
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="text-sm font-medium mb-2 block">CLABE</label>
              <Input
                placeholder="002010077777777771"
                value={clabeInput}
                onChange={(e) => setClabeInput(e.target.value.replace(/\D/g, ''))}
                className="font-mono"
                maxLength={18}
              />
              <div className="text-xs text-muted-foreground mt-1">
                {clabeInput.length}/18 dígitos
              </div>
            </div>
            <Button onClick={handleValidate} className="w-full">
              Validar
            </Button>

            {result && (
              <div className="space-y-4 pt-4 border-t">
                {/* Status */}
                <div className={`p-4 rounded-lg flex items-center gap-3 ${
                  result.isValid ? 'bg-green-50 text-green-800 dark:bg-green-950 dark:text-green-200' : 'bg-red-50 text-red-800 dark:bg-red-950 dark:text-red-200'
                }`}>
                  {result.isValid ? <Check className="h-5 w-5" /> : <X className="h-5 w-5" />}
                  <span className="font-medium">
                    {result.isValid ? 'CLABE Válida' : 'CLABE Inválida'}
                  </span>
                </div>

                {/* Validation Details */}
                <div className="grid grid-cols-2 gap-2">
                  <div className={`p-2 rounded text-center text-sm ${result.details.format ? 'bg-green-100 dark:bg-green-900' : 'bg-red-100 dark:bg-red-900'}`}>
                    <div className="font-medium">Formato</div>
                    <div>{result.details.format ? 'Válido' : 'Inválido'}</div>
                  </div>
                  <div className={`p-2 rounded text-center text-sm ${result.details.checkDigit ? 'bg-green-100 dark:bg-green-900' : 'bg-red-100 dark:bg-red-900'}`}>
                    <div className="font-medium">Dígito Verificador</div>
                    <div>{result.details.checkDigit ? 'Válido' : 'Inválido'}</div>
                  </div>
                </div>

                {/* Parsed Information */}
                {result.parsed && (
                  <div className="space-y-3">
                    <div className="text-sm font-medium">Información del Banco</div>
                    <div className="p-4 bg-muted rounded space-y-3">
                      <div className="flex items-center gap-3">
                        <Building className="h-5 w-5 text-muted-foreground" />
                        <div>
                          <div className="text-sm text-muted-foreground">Banco</div>
                          <div className="font-medium">{result.parsed.bankName}</div>
                          <div className="text-sm text-muted-foreground">Código: {result.parsed.bankCode}</div>
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        <CreditCard className="h-5 w-5 text-muted-foreground" />
                        <div>
                          <div className="text-sm text-muted-foreground">Plaza/Sucursal</div>
                          <div className="font-mono font-medium">{result.parsed.branchCode}</div>
                        </div>
                      </div>
                    </div>
                    <div className="grid grid-cols-2 gap-2 text-sm">
                      <div className="p-2 bg-muted rounded">
                        <div className="text-muted-foreground">Número de Cuenta</div>
                        <div className="font-mono font-medium">{result.parsed.accountNumber}</div>
                      </div>
                      <div className="p-2 bg-muted rounded">
                        <div className="text-muted-foreground">Dígito Verificador</div>
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
            <CardTitle className="flex items-center gap-2">
              <Zap className="h-5 w-5" />
              Generar CLABE
            </CardTitle>
            <CardDescription>
              Genera CLABEs válidas con parámetros opcionales
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="text-sm font-medium mb-2 block">Banco (opcional)</label>
              <Select value={genBankCode} onValueChange={setGenBankCode}>
                <SelectTrigger>
                  <SelectValue placeholder="Seleccionar banco o aleatorio" />
                </SelectTrigger>
                <SelectContent className="max-h-[300px]">
                  <SelectItem value="">Aleatorio</SelectItem>
                  {bankOptions.map((bank) => (
                    <SelectItem key={bank.code} value={bank.code}>
                      {bank.code} - {bank.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div>
              <label className="text-sm font-medium mb-2 block">Plaza/Sucursal (opcional)</label>
              <Input
                placeholder="Ej: 010 (aleatorio si vacío)"
                value={genBranchCode}
                onChange={(e) => setGenBranchCode(e.target.value.replace(/\D/g, '').slice(0, 3))}
                className="font-mono"
                maxLength={3}
              />
            </div>

            <div>
              <label className="text-sm font-medium mb-2 block">Número de Cuenta (opcional)</label>
              <Input
                placeholder="Ej: 12345678901 (aleatorio si vacío)"
                value={genAccountNumber}
                onChange={(e) => setGenAccountNumber(e.target.value.replace(/\D/g, '').slice(0, 11))}
                className="font-mono"
                maxLength={11}
              />
            </div>

            <div className="grid grid-cols-2 gap-2">
              <Button onClick={handleGenerate} className="w-full">
                Generar
              </Button>
              <Button onClick={handleGenerateRandom} variant="outline" className="w-full">
                <RefreshCw className="h-4 w-4 mr-2" />
                Aleatorio
              </Button>
            </div>

            {generatedClabe && (
              <div className="space-y-3 pt-4 border-t">
                <div className="text-sm font-medium">CLABE Generada</div>
                <div className="p-4 bg-muted rounded-lg">
                  <div className="flex items-center justify-between gap-2">
                    <code className="text-lg font-mono font-bold tracking-wider">
                      {formatCLABE(generatedClabe)}
                    </code>
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => copyToClipboard(generatedClabe)}
                    >
                      <Copy className="h-4 w-4" />
                    </Button>
                  </div>
                  <div className="text-xs text-muted-foreground mt-2">
                    Sin formato: {generatedClabe}
                  </div>
                </div>

                {generatedResult?.parsed && (
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    <div className="p-2 bg-muted rounded">
                      <div className="text-muted-foreground">Banco</div>
                      <div className="font-medium">{generatedResult.parsed.bankName}</div>
                    </div>
                    <div className="p-2 bg-muted rounded">
                      <div className="text-muted-foreground">Plaza</div>
                      <div className="font-mono">{generatedResult.parsed.branchCode}</div>
                    </div>
                  </div>
                )}

                <div className={`p-2 rounded text-center text-sm ${
                  generatedResult?.isValid ? 'bg-green-100 dark:bg-green-900' : 'bg-red-100 dark:bg-red-900'
                }`}>
                  {generatedResult?.isValid ? 'CLABE válida' : 'Error en generación'}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Structure Info */}
      <Card>
        <CardHeader>
          <CardTitle>Estructura CLABE</CardTitle>
          <CardDescription>
            18 dígitos estandarizados para cuentas bancarias mexicanas
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="font-mono text-lg p-4 bg-muted rounded text-center tracking-widest">
            <span className="text-blue-600">XXX</span>
            <span className="text-green-600">YYY</span>
            <span className="text-purple-600">ZZZZZZZZZZZ</span>
            <span className="text-orange-600">C</span>
          </div>
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4 text-sm">
            <div className="flex items-start gap-2">
              <Badge className="bg-blue-600 mt-0.5">XXX</Badge>
              <div>
                <div className="font-medium">Código Banco</div>
                <div className="text-muted-foreground">3 dígitos asignados por Banxico</div>
              </div>
            </div>
            <div className="flex items-start gap-2">
              <Badge className="bg-green-600 mt-0.5">YYY</Badge>
              <div>
                <div className="font-medium">Código Plaza</div>
                <div className="text-muted-foreground">3 dígitos de sucursal o plaza</div>
              </div>
            </div>
            <div className="flex items-start gap-2">
              <Badge className="bg-purple-600 mt-0.5">ZZZ...</Badge>
              <div>
                <div className="font-medium">Número Cuenta</div>
                <div className="text-muted-foreground">11 dígitos de cuenta</div>
              </div>
            </div>
            <div className="flex items-start gap-2">
              <Badge className="bg-orange-600 mt-0.5">C</Badge>
              <div>
                <div className="font-medium">Dígito Verificador</div>
                <div className="text-muted-foreground">1 dígito de validación</div>
              </div>
            </div>
          </div>

          <div className="border-t pt-4">
            <div className="text-sm font-medium mb-2">Algoritmo del Dígito Verificador</div>
            <div className="text-sm text-muted-foreground">
              <p className="mb-2">El dígito verificador se calcula usando una suma ponderada con factores [3, 7, 1] repetidos:</p>
              <ol className="list-decimal list-inside space-y-1">
                <li>Multiplicar cada dígito por su peso (módulo 10)</li>
                <li>Sumar todos los productos</li>
                <li>Dígito = (10 - (suma mod 10)) mod 10</li>
              </ol>
            </div>
          </div>

          <div className="border-t pt-4">
            <div className="text-sm font-medium mb-2">Códigos de Bancos Comunes</div>
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2 text-sm">
              <div className="p-2 bg-muted rounded">
                <span className="font-mono">002</span> - BANAMEX
              </div>
              <div className="p-2 bg-muted rounded">
                <span className="font-mono">012</span> - BBVA
              </div>
              <div className="p-2 bg-muted rounded">
                <span className="font-mono">014</span> - SANTANDER
              </div>
              <div className="p-2 bg-muted rounded">
                <span className="font-mono">021</span> - HSBC
              </div>
              <div className="p-2 bg-muted rounded">
                <span className="font-mono">072</span> - BANORTE
              </div>
              <div className="p-2 bg-muted rounded">
                <span className="font-mono">127</span> - AZTECA
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
