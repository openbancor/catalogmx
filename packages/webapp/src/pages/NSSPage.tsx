import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Check, X, Shield } from 'lucide-react';
import { validateNSS, type NSSValidationResult } from '@/lib/validators';

export default function NSSPage() {
  const [nssInput, setNssInput] = useState('');
  const [result, setResult] = useState<NSSValidationResult | null>(null);

  const handleValidate = () => {
    if (nssInput.trim()) {
      setResult(validateNSS(nssInput));
    }
  };

  return (
    <div className="space-y-6 max-w-4xl">
      <div>
        <h1 className="text-2xl font-bold">NSS Validator</h1>
        <p className="text-muted-foreground mt-1">
          Numero de Seguridad Social - Mexican Social Security Number (IMSS)
        </p>
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Validator */}
        <Card>
          <CardHeader>
            <CardTitle>Validate NSS</CardTitle>
            <CardDescription>
              Enter an 11-digit NSS to validate and extract registration info
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="text-sm font-medium mb-2 block">NSS</label>
              <Input
                placeholder="12345678901"
                value={nssInput}
                onChange={(e) => setNssInput(e.target.value.replace(/\D/g, ''))}
                className="font-mono"
                maxLength={11}
              />
              <div className="text-xs text-muted-foreground mt-1">
                {nssInput.length}/11 digits
              </div>
            </div>
            <Button onClick={handleValidate} className="w-full">
              Validate
            </Button>

            {result && (
              <div className="space-y-4 pt-4 border-t">
                {/* Status */}
                <div className={`p-4 rounded-lg flex items-center gap-3 ${
                  result.isValid ? 'bg-green-50 text-green-800 dark:bg-green-950 dark:text-green-200' : 'bg-red-50 text-red-800 dark:bg-red-950 dark:text-red-200'
                }`}>
                  {result.isValid ? <Check className="h-5 w-5" /> : <X className="h-5 w-5" />}
                  <span className="font-medium">
                    {result.isValid ? 'Valid NSS' : 'Invalid NSS'}
                  </span>
                </div>

                {/* Validation Details */}
                <div className="grid grid-cols-2 gap-2">
                  <div className={`p-2 rounded text-center text-sm ${result.details.format ? 'bg-green-100 dark:bg-green-900' : 'bg-red-100 dark:bg-red-900'}`}>
                    <div className="font-medium">Format</div>
                    <div>{result.details.format ? 'Valid' : 'Invalid'}</div>
                  </div>
                  <div className={`p-2 rounded text-center text-sm ${result.details.checkDigit ? 'bg-green-100 dark:bg-green-900' : 'bg-red-100 dark:bg-red-900'}`}>
                    <div className="font-medium">Check Digit</div>
                    <div>{result.details.checkDigit ? 'Valid' : 'Invalid'}</div>
                  </div>
                </div>

                {/* Parsed Information */}
                {result.parsed && (
                  <div className="space-y-3">
                    <div className="text-sm font-medium">Registration Information</div>
                    <div className="grid grid-cols-2 gap-2 text-sm">
                      <div className="p-3 bg-muted rounded">
                        <div className="text-muted-foreground">Subdelegation</div>
                        <div className="font-mono font-medium text-lg">{result.parsed.subdelegation}</div>
                        <div className="text-xs text-muted-foreground">IMSS regional office</div>
                      </div>
              <div className="p-3 bg-muted rounded">
                <div className="text-muted-foreground">Registration Year</div>
                <div className="font-mono font-medium text-lg">19{result.parsed.registrationYear}</div>
                <div className="text-xs text-muted-foreground">or 20{result.parsed.registrationYear}</div>
              </div>
              <div className="p-3 bg-muted rounded">
                <div className="text-muted-foreground">Birth Year</div>
                <div className="font-mono font-medium text-lg">19{result.parsed.birthYear}</div>
                <div className="text-xs text-muted-foreground">or 20{result.parsed.birthYear}</div>
              </div>
                      <div className="p-3 bg-muted rounded">
                        <div className="text-muted-foreground">Sequential Number</div>
                        <div className="font-mono font-medium text-lg">{result.parsed.sequential}</div>
                        <div className="text-xs text-muted-foreground">Secuencial</div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Structure Info */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Shield className="h-5 w-5" />
              NSS Structure
            </CardTitle>
            <CardDescription>
              11-digit IMSS Social Security Number
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="font-mono text-lg p-4 bg-muted rounded text-center tracking-widest">
              <span className="text-blue-600">SS</span>
              <span className="text-green-600">AA</span>
              <span className="text-purple-600">BB</span>
              <span className="text-orange-600">NNNN</span>
              <span className="text-red-600">C</span>
            </div>
            <div className="space-y-2 text-sm">
              <div className="flex items-center gap-2">
                <Badge className="bg-blue-600">SS</Badge>
                <span>Subdelegation (2 digits) - IMSS office code</span>
              </div>
              <div className="flex items-center gap-2">
                <Badge className="bg-green-600">AA</Badge>
                <span>Registration Year (2 digits)</span>
              </div>
              <div className="flex items-center gap-2">
                <Badge className="bg-purple-600">BB</Badge>
                <span>Birth Year (2 digits)</span>
              </div>
              <div className="flex items-center gap-2">
                <Badge className="bg-orange-600">NNNN</Badge>
                <span>Sequential (4 digits)</span>
              </div>
              <div className="flex items-center gap-2">
                <Badge className="bg-red-600">C</Badge>
                <span>Check Digit (1 digit)</span>
              </div>
            </div>

            <div className="border-t pt-4">
              <div className="text-sm font-medium mb-2">Check Digit Algorithm (Luhn Variant)</div>
              <div className="text-sm text-muted-foreground">
                <ol className="list-decimal list-inside space-y-1">
                  <li>Take first 10 digits in reverse order</li>
                  <li>Double every other digit (starting from first)</li>
                  <li>If result &gt; 9, sum the digits</li>
                  <li>Sum all digits</li>
                  <li>Check digit = (10 - (sum mod 10)) mod 10</li>
                </ol>
              </div>
            </div>

            <div className="border-t pt-4">
              <div className="text-sm font-medium mb-2">About IMSS</div>
              <p className="text-sm text-muted-foreground">
                Instituto Mexicano del Seguro Social (IMSS) is Mexico's social security institution.
                The NSS is assigned to workers when they first register with IMSS and remains
                the same throughout their working life.
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
