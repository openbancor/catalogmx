import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Check, X, Building, CreditCard } from 'lucide-react';
import { validateCLABE, type CLABEValidationResult } from '@/lib/validators';

export default function CLABEPage() {
  const [clabeInput, setClabeInput] = useState('');
  const [result, setResult] = useState<CLABEValidationResult | null>(null);

  const handleValidate = () => {
    if (clabeInput.trim()) {
      setResult(validateCLABE(clabeInput));
    }
  };

  return (
    <div className="space-y-6 max-w-4xl">
      <div>
        <h1 className="text-2xl font-bold">CLABE Validator</h1>
        <p className="text-muted-foreground mt-1">
          Clave Bancaria Estandarizada - Mexican standardized bank account number
        </p>
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Validator */}
        <Card>
          <CardHeader>
            <CardTitle>Validate CLABE</CardTitle>
            <CardDescription>
              Enter an 18-digit CLABE to validate and extract bank information
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
                {clabeInput.length}/18 digits
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
                    {result.isValid ? 'Valid CLABE' : 'Invalid CLABE'}
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
                    <div className="text-sm font-medium">Bank Information</div>
                    <div className="p-4 bg-muted rounded space-y-3">
                      <div className="flex items-center gap-3">
                        <Building className="h-5 w-5 text-muted-foreground" />
                        <div>
                          <div className="text-sm text-muted-foreground">Bank</div>
                          <div className="font-medium">{result.parsed.bankName}</div>
                          <div className="text-sm text-muted-foreground">Code: {result.parsed.bankCode}</div>
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        <CreditCard className="h-5 w-5 text-muted-foreground" />
                        <div>
                          <div className="text-sm text-muted-foreground">Branch</div>
                          <div className="font-mono font-medium">{result.parsed.branchCode}</div>
                        </div>
                      </div>
                    </div>
                    <div className="grid grid-cols-2 gap-2 text-sm">
                      <div className="p-2 bg-muted rounded">
                        <div className="text-muted-foreground">Account Number</div>
                        <div className="font-mono font-medium">{result.parsed.accountNumber}</div>
                      </div>
                      <div className="p-2 bg-muted rounded">
                        <div className="text-muted-foreground">Check Digit</div>
                        <div className="font-mono font-medium">{result.parsed.checkDigit}</div>
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
            <CardTitle>CLABE Structure</CardTitle>
            <CardDescription>
              18-digit standardized bank account number
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="font-mono text-lg p-4 bg-muted rounded text-center tracking-widest">
              <span className="text-blue-600">XXX</span>
              <span className="text-green-600">YYY</span>
              <span className="text-purple-600">ZZZZZZZZZZZ</span>
              <span className="text-orange-600">C</span>
            </div>
            <div className="space-y-2 text-sm">
              <div className="flex items-center gap-2">
                <Badge className="bg-blue-600">XXX</Badge>
                <span>Bank Code (3 digits) - Assigned by Banxico</span>
              </div>
              <div className="flex items-center gap-2">
                <Badge className="bg-green-600">YYY</Badge>
                <span>Branch Code (3 digits) - Branch or plaza</span>
              </div>
              <div className="flex items-center gap-2">
                <Badge className="bg-purple-600">ZZZ...</Badge>
                <span>Account Number (11 digits)</span>
              </div>
              <div className="flex items-center gap-2">
                <Badge className="bg-orange-600">C</Badge>
                <span>Check Digit (1 digit) - Validation</span>
              </div>
            </div>

            <div className="border-t pt-4">
              <div className="text-sm font-medium mb-2">Check Digit Algorithm</div>
              <div className="text-sm text-muted-foreground">
                <p className="mb-2">The check digit is calculated using a weighted sum with factors [3, 7, 1] repeating:</p>
                <ol className="list-decimal list-inside space-y-1">
                  <li>Multiply each digit by its weight (mod 10)</li>
                  <li>Sum all products</li>
                  <li>Check digit = (10 - (sum mod 10)) mod 10</li>
                </ol>
              </div>
            </div>

            <div className="border-t pt-4">
              <div className="text-sm font-medium mb-2">Common Bank Codes</div>
              <div className="grid grid-cols-2 gap-2 text-sm">
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
    </div>
  );
}
