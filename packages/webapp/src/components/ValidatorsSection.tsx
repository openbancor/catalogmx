import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { CheckCircle, XCircle, Wand2 } from 'lucide-react';
import { validateRFC, generateRFC, validateCURP, generateCURP, validateCLABE, validateNSS } from '@/lib/validators';

export default function ValidatorsSection() {
  return (
    <div className="space-y-8">
      <div className="text-center max-w-2xl mx-auto">
        <h2 className="text-3xl font-bold mb-2">Mexican Data Validators</h2>
        <p className="text-muted-foreground">
          Validate and generate RFC, CURP, CLABE, and NSS with detailed breakdowns
        </p>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <RFCValidator />
        <CURPValidator />
        <CLABEValidator />
        <NSSValidator />
      </div>
    </div>
  );
}

function RFCValidator() {
  const [input, setInput] = useState('');
  const [result, setResult] = useState<ReturnType<typeof validateRFC> | null>(null);
  const [genData, setGenData] = useState({ nombre: '', paterno: '', materno: '', fecha: '' });
  const [generated, setGenerated] = useState('');

  const handleValidate = () => {
    if (input.trim()) setResult(validateRFC(input));
  };

  const handleGenerate = () => {
    if (genData.nombre && genData.paterno && genData.materno && genData.fecha) {
      const rfc = generateRFC({
        nombre: genData.nombre,
        paterno: genData.paterno,
        materno: genData.materno,
        fecha: new Date(genData.fecha)
      });
      setGenerated(rfc);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          RFC
          <Badge variant="outline" className="font-normal">Registro Federal de Contribuyentes</Badge>
        </CardTitle>
        <CardDescription>Tax ID for individuals and companies in Mexico</CardDescription>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="validate">
          <TabsList className="grid w-full grid-cols-2 mb-4">
            <TabsTrigger value="validate">Validate</TabsTrigger>
            <TabsTrigger value="generate">Generate</TabsTrigger>
          </TabsList>

          <TabsContent value="validate" className="space-y-4">
            <div className="flex gap-2">
              <Input
                placeholder="e.g., GODE561231GR8"
                value={input}
                onChange={(e) => setInput(e.target.value.toUpperCase())}
                maxLength={13}
                className="font-mono"
              />
              <Button onClick={handleValidate}>Validate</Button>
            </div>

            {result && (
              <div className={`p-4 rounded-lg border ${result.isValid ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'}`}>
                <div className="flex items-center gap-2 mb-3">
                  {result.isValid ? (
                    <CheckCircle className="h-5 w-5 text-green-600" />
                  ) : (
                    <XCircle className="h-5 w-5 text-red-600" />
                  )}
                  <span className="font-semibold">
                    {result.isValid ? 'Valid RFC' : 'Invalid RFC'}
                  </span>
                  {result.type !== 'invalid' && (
                    <Badge variant={result.isValid ? 'success' : 'destructive'}>
                      {result.type.replace('_', ' ')}
                    </Badge>
                  )}
                </div>

                <div className="grid grid-cols-3 gap-2 text-sm">
                  <ValidationCheck label="Format" valid={result.details.format} />
                  <ValidationCheck label="Date" valid={result.details.date} />
                  <ValidationCheck label="Checksum" valid={result.details.checksum} />
                </div>

                {result.parsed && (
                  <div className="mt-3 pt-3 border-t text-sm font-mono">
                    <div className="grid grid-cols-4 gap-2">
                      <div className="text-center p-2 bg-white rounded">
                        <div className="text-xs text-muted-foreground">Initials</div>
                        <div className="font-bold">{result.parsed.initials}</div>
                      </div>
                      <div className="text-center p-2 bg-white rounded">
                        <div className="text-xs text-muted-foreground">Date</div>
                        <div className="font-bold">{result.parsed.date}</div>
                      </div>
                      <div className="text-center p-2 bg-white rounded">
                        <div className="text-xs text-muted-foreground">Homoclave</div>
                        <div className="font-bold">{result.parsed.homoclave}</div>
                      </div>
                      <div className="text-center p-2 bg-white rounded">
                        <div className="text-xs text-muted-foreground">Check</div>
                        <div className="font-bold">{result.parsed.checkDigit}</div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}
          </TabsContent>

          <TabsContent value="generate" className="space-y-4">
            <div className="grid grid-cols-2 gap-3">
              <Input placeholder="First name" value={genData.nombre} onChange={(e) => setGenData({...genData, nombre: e.target.value})} />
              <Input placeholder="Paternal surname" value={genData.paterno} onChange={(e) => setGenData({...genData, paterno: e.target.value})} />
              <Input placeholder="Maternal surname" value={genData.materno} onChange={(e) => setGenData({...genData, materno: e.target.value})} />
              <Input type="date" value={genData.fecha} onChange={(e) => setGenData({...genData, fecha: e.target.value})} />
            </div>
            <Button onClick={handleGenerate} className="w-full">
              <Wand2 className="h-4 w-4 mr-2" />
              Generate RFC
            </Button>
            {generated && (
              <div className="p-4 bg-muted rounded-lg text-center">
                <div className="text-xs text-muted-foreground mb-1">Generated RFC</div>
                <div className="text-2xl font-mono font-bold">{generated}</div>
              </div>
            )}
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
}

function CURPValidator() {
  const [input, setInput] = useState('');
  const [result, setResult] = useState<ReturnType<typeof validateCURP> | null>(null);
  const [genData, setGenData] = useState({ nombre: '', paterno: '', materno: '', fecha: '', sexo: 'H', estado: 'DF' });
  const [generated, setGenerated] = useState('');

  const handleValidate = () => {
    if (input.trim()) setResult(validateCURP(input));
  };

  const handleGenerate = () => {
    if (genData.nombre && genData.paterno && genData.materno && genData.fecha) {
      const curp = generateCURP({
        nombre: genData.nombre,
        paterno: genData.paterno,
        materno: genData.materno,
        fecha: new Date(genData.fecha),
        sexo: genData.sexo as 'H' | 'M',
        estado: genData.estado
      });
      setGenerated(curp);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          CURP
          <Badge variant="outline" className="font-normal">Clave Única de Registro de Población</Badge>
        </CardTitle>
        <CardDescription>Unique population registry code for Mexican residents</CardDescription>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="validate">
          <TabsList className="grid w-full grid-cols-2 mb-4">
            <TabsTrigger value="validate">Validate</TabsTrigger>
            <TabsTrigger value="generate">Generate</TabsTrigger>
          </TabsList>

          <TabsContent value="validate" className="space-y-4">
            <div className="flex gap-2">
              <Input
                placeholder="e.g., GODE561231HDFRRL09"
                value={input}
                onChange={(e) => setInput(e.target.value.toUpperCase())}
                maxLength={18}
                className="font-mono"
              />
              <Button onClick={handleValidate}>Validate</Button>
            </div>

            {result && (
              <div className={`p-4 rounded-lg border ${result.isValid ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'}`}>
                <div className="flex items-center gap-2 mb-3">
                  {result.isValid ? <CheckCircle className="h-5 w-5 text-green-600" /> : <XCircle className="h-5 w-5 text-red-600" />}
                  <span className="font-semibold">{result.isValid ? 'Valid CURP' : 'Invalid CURP'}</span>
                </div>

                <div className="grid grid-cols-2 gap-2 text-sm mb-3">
                  <ValidationCheck label="Format" valid={result.details.format} />
                  <ValidationCheck label="Check Digit" valid={result.details.checkDigit} />
                </div>

                {result.parsed && (
                  <div className="grid grid-cols-2 gap-3 text-sm">
                    <InfoRow label="Birth Date" value={result.parsed.birthDate} />
                    <InfoRow label="Gender" value={result.parsed.gender} />
                    <InfoRow label="State" value={result.parsed.stateName} />
                    <InfoRow label="Initials" value={result.parsed.initials} />
                  </div>
                )}
              </div>
            )}
          </TabsContent>

          <TabsContent value="generate" className="space-y-4">
            <div className="grid grid-cols-2 gap-3">
              <Input placeholder="First name" value={genData.nombre} onChange={(e) => setGenData({...genData, nombre: e.target.value})} />
              <Input placeholder="Paternal surname" value={genData.paterno} onChange={(e) => setGenData({...genData, paterno: e.target.value})} />
              <Input placeholder="Maternal surname" value={genData.materno} onChange={(e) => setGenData({...genData, materno: e.target.value})} />
              <Input type="date" value={genData.fecha} onChange={(e) => setGenData({...genData, fecha: e.target.value})} />
              <select className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm" value={genData.sexo} onChange={(e) => setGenData({...genData, sexo: e.target.value})}>
                <option value="H">Male (H)</option>
                <option value="M">Female (M)</option>
              </select>
              <select className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm" value={genData.estado} onChange={(e) => setGenData({...genData, estado: e.target.value})}>
                <option value="DF">Ciudad de México</option>
                <option value="AS">Aguascalientes</option>
                <option value="BC">Baja California</option>
                <option value="NL">Nuevo León</option>
                <option value="JC">Jalisco</option>
              </select>
            </div>
            <Button onClick={handleGenerate} className="w-full">
              <Wand2 className="h-4 w-4 mr-2" />
              Generate CURP
            </Button>
            {generated && (
              <div className="p-4 bg-muted rounded-lg text-center">
                <div className="text-xs text-muted-foreground mb-1">Generated CURP</div>
                <div className="text-xl font-mono font-bold">{generated}</div>
              </div>
            )}
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
}

function CLABEValidator() {
  const [input, setInput] = useState('');
  const [result, setResult] = useState<ReturnType<typeof validateCLABE> | null>(null);

  const handleValidate = () => {
    if (input.trim()) setResult(validateCLABE(input));
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          CLABE
          <Badge variant="outline" className="font-normal">Clave Bancaria Estandarizada</Badge>
        </CardTitle>
        <CardDescription>18-digit standardized bank account number for SPEI transfers</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex gap-2">
          <Input
            placeholder="e.g., 002010077777777771"
            value={input}
            onChange={(e) => setInput(e.target.value.replace(/\D/g, ''))}
            maxLength={18}
            className="font-mono"
          />
          <Button onClick={handleValidate}>Validate</Button>
        </div>

        {result && (
          <div className={`p-4 rounded-lg border ${result.isValid ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'}`}>
            <div className="flex items-center gap-2 mb-3">
              {result.isValid ? <CheckCircle className="h-5 w-5 text-green-600" /> : <XCircle className="h-5 w-5 text-red-600" />}
              <span className="font-semibold">{result.isValid ? 'Valid CLABE' : 'Invalid CLABE'}</span>
            </div>

            <div className="grid grid-cols-2 gap-2 text-sm mb-3">
              <ValidationCheck label="Format (18 digits)" valid={result.details.format} />
              <ValidationCheck label="Check Digit" valid={result.details.checkDigit} />
            </div>

            {result.parsed && (
              <div className="grid grid-cols-5 gap-1 font-mono text-center mt-4">
                <div className="p-2 bg-blue-100 rounded">
                  <div className="text-xs text-blue-600">Bank</div>
                  <div className="font-bold">{result.parsed.bankCode}</div>
                </div>
                <div className="p-2 bg-purple-100 rounded">
                  <div className="text-xs text-purple-600">Branch</div>
                  <div className="font-bold">{result.parsed.branchCode}</div>
                </div>
                <div className="p-2 bg-gray-100 rounded col-span-2">
                  <div className="text-xs text-gray-600">Account</div>
                  <div className="font-bold text-sm">{result.parsed.accountNumber}</div>
                </div>
                <div className="p-2 bg-green-100 rounded">
                  <div className="text-xs text-green-600">Check</div>
                  <div className="font-bold">{result.parsed.checkDigit}</div>
                </div>
              </div>
            )}

            {result.parsed && (
              <div className="mt-3 pt-3 border-t text-sm">
                <InfoRow label="Bank" value={result.parsed.bankName} />
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

function NSSValidator() {
  const [input, setInput] = useState('');
  const [result, setResult] = useState<ReturnType<typeof validateNSS> | null>(null);

  const handleValidate = () => {
    if (input.trim()) setResult(validateNSS(input));
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          NSS
          <Badge variant="outline" className="font-normal">Número de Seguridad Social</Badge>
        </CardTitle>
        <CardDescription>IMSS Social Security Number (11 digits)</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex gap-2">
          <Input
            placeholder="e.g., 12345678903"
            value={input}
            onChange={(e) => setInput(e.target.value.replace(/\D/g, ''))}
            maxLength={11}
            className="font-mono"
          />
          <Button onClick={handleValidate}>Validate</Button>
        </div>

        {result && (
          <div className={`p-4 rounded-lg border ${result.isValid ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'}`}>
            <div className="flex items-center gap-2 mb-3">
              {result.isValid ? <CheckCircle className="h-5 w-5 text-green-600" /> : <XCircle className="h-5 w-5 text-red-600" />}
              <span className="font-semibold">{result.isValid ? 'Valid NSS' : 'Invalid NSS'}</span>
            </div>

            <div className="grid grid-cols-2 gap-2 text-sm mb-3">
              <ValidationCheck label="Format (11 digits)" valid={result.details.format} />
              <ValidationCheck label="Check Digit (Luhn)" valid={result.details.checkDigit} />
            </div>

            {result.parsed && (
              <div className="grid grid-cols-5 gap-1 font-mono text-center mt-4">
                <div className="p-2 bg-blue-100 rounded">
                  <div className="text-[10px] text-blue-600">Subdel</div>
                  <div className="font-bold text-sm">{result.parsed.subdelegation}</div>
                </div>
                <div className="p-2 bg-purple-100 rounded">
                  <div className="text-[10px] text-purple-600">Reg.</div>
                  <div className="font-bold text-sm">{result.parsed.registrationYear}</div>
                </div>
                <div className="p-2 bg-orange-100 rounded">
                  <div className="text-[10px] text-orange-600">Birth</div>
                  <div className="font-bold text-sm">{result.parsed.birthYear}</div>
                </div>
                <div className="p-2 bg-gray-100 rounded">
                  <div className="text-[10px] text-gray-600">Seq</div>
                  <div className="font-bold text-sm">{result.parsed.sequential}</div>
                </div>
                <div className="p-2 bg-green-100 rounded">
                  <div className="text-[10px] text-green-600">Check</div>
                  <div className="font-bold text-sm">{result.parsed.checkDigit}</div>
                </div>
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

function ValidationCheck({ label, valid }: { label: string; valid: boolean }) {
  return (
    <div className="flex items-center gap-1.5">
      {valid ? (
        <CheckCircle className="h-3.5 w-3.5 text-green-600" />
      ) : (
        <XCircle className="h-3.5 w-3.5 text-red-600" />
      )}
      <span className={valid ? 'text-green-700' : 'text-red-700'}>{label}</span>
    </div>
  );
}

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between py-1">
      <span className="text-muted-foreground">{label}:</span>
      <span className="font-medium">{value}</span>
    </div>
  );
}
