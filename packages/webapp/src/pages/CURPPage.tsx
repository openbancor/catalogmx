import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Check, X, MapPin, Calendar, User } from 'lucide-react';
import { validateCURP, generateCURP, type CURPValidationResult } from '@/lib/validators';

const STATES = [
  { code: 'AS', name: 'Aguascalientes' }, { code: 'BC', name: 'Baja California' },
  { code: 'BS', name: 'Baja California Sur' }, { code: 'CC', name: 'Campeche' },
  { code: 'CL', name: 'Coahuila' }, { code: 'CM', name: 'Colima' },
  { code: 'CS', name: 'Chiapas' }, { code: 'CH', name: 'Chihuahua' },
  { code: 'DF', name: 'Ciudad de México' }, { code: 'DG', name: 'Durango' },
  { code: 'GT', name: 'Guanajuato' }, { code: 'GR', name: 'Guerrero' },
  { code: 'HG', name: 'Hidalgo' }, { code: 'JC', name: 'Jalisco' },
  { code: 'MC', name: 'Estado de México' }, { code: 'MN', name: 'Michoacán' },
  { code: 'MS', name: 'Morelos' }, { code: 'NT', name: 'Nayarit' },
  { code: 'NL', name: 'Nuevo León' }, { code: 'OC', name: 'Oaxaca' },
  { code: 'PL', name: 'Puebla' }, { code: 'QT', name: 'Querétaro' },
  { code: 'QR', name: 'Quintana Roo' }, { code: 'SP', name: 'San Luis Potosí' },
  { code: 'SL', name: 'Sinaloa' }, { code: 'SR', name: 'Sonora' },
  { code: 'TC', name: 'Tabasco' }, { code: 'TS', name: 'Tamaulipas' },
  { code: 'TL', name: 'Tlaxcala' }, { code: 'VZ', name: 'Veracruz' },
  { code: 'YN', name: 'Yucatán' }, { code: 'ZS', name: 'Zacatecas' },
  { code: 'NE', name: 'Nacido en el extranjero' }
];

export default function CURPPage() {
  const [curpInput, setCurpInput] = useState('');
  const [result, setResult] = useState<CURPValidationResult | null>(null);

  // Generator state
  const [genNombre, setGenNombre] = useState('');
  const [genPaterno, setGenPaterno] = useState('');
  const [genMaterno, setGenMaterno] = useState('');
  const [genFecha, setGenFecha] = useState('');
  const [genSexo, setGenSexo] = useState<'H' | 'M'>('H');
  const [genEstado, setGenEstado] = useState('DF');
  const [generatedCURP, setGeneratedCURP] = useState('');

  const handleValidate = () => {
    if (curpInput.trim()) {
      setResult(validateCURP(curpInput));
    }
  };

  const handleGenerate = () => {
    if (genNombre && genPaterno && genFecha) {
      const fecha = new Date(genFecha);
      const curp = generateCURP({
        nombre: genNombre,
        paterno: genPaterno,
        materno: genMaterno || 'X',
        fecha,
        sexo: genSexo,
        estado: genEstado
      });
      setGeneratedCURP(curp);
    }
  };

  return (
    <div className="space-y-6 max-w-4xl">
      <div>
        <h1 className="text-2xl font-bold">CURP Validator</h1>
        <p className="text-muted-foreground mt-1">
          Clave Unica de Registro de Poblacion - Mexican personal identification number
        </p>
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Validator */}
        <Card>
          <CardHeader>
            <CardTitle>Validate CURP</CardTitle>
            <CardDescription>
              Enter a CURP to validate and extract information
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="text-sm font-medium mb-2 block">CURP</label>
              <Input
                placeholder="GARC850101HDFRRL09"
                value={curpInput}
                onChange={(e) => setCurpInput(e.target.value.toUpperCase())}
                className="font-mono"
                maxLength={18}
              />
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
                    {result.isValid ? 'Valid CURP' : 'Invalid CURP'}
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

                {/* Extracted Information */}
                {result.parsed && (
                  <div className="space-y-3">
                    <div className="text-sm font-medium">Extracted Information</div>
                    <div className="grid gap-2 text-sm">
                      <div className="p-3 bg-muted rounded flex items-center gap-3">
                        <Calendar className="h-4 w-4 text-muted-foreground" />
                        <div>
                          <div className="text-muted-foreground">Birth Date</div>
                          <div className="font-medium">{result.parsed.birthDate}</div>
                        </div>
                      </div>
                      <div className="p-3 bg-muted rounded flex items-center gap-3">
                        <User className="h-4 w-4 text-muted-foreground" />
                        <div>
                          <div className="text-muted-foreground">Gender</div>
                          <div className="font-medium">{result.parsed.gender}</div>
                        </div>
                      </div>
                      <div className="p-3 bg-muted rounded flex items-center gap-3">
                        <MapPin className="h-4 w-4 text-muted-foreground" />
                        <div>
                          <div className="text-muted-foreground">State of Birth</div>
                          <div className="font-medium">{result.parsed.stateName} ({result.parsed.state})</div>
                        </div>
                      </div>
                    </div>
                    <div className="grid grid-cols-3 gap-2 text-sm">
                      <div className="p-2 bg-muted rounded text-center">
                        <div className="text-muted-foreground text-xs">Initials</div>
                        <div className="font-mono font-medium">{result.parsed.initials}</div>
                      </div>
                      <div className="p-2 bg-muted rounded text-center">
                        <div className="text-muted-foreground text-xs">Consonants</div>
                        <div className="font-mono font-medium">{result.parsed.consonants}</div>
                      </div>
                      <div className="p-2 bg-muted rounded text-center">
                        <div className="text-muted-foreground text-xs">Differentiator</div>
                        <div className="font-mono font-medium">{result.parsed.differentiator}</div>
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
            <CardTitle>Generate CURP</CardTitle>
            <CardDescription>
              Generate a CURP from personal data
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-sm font-medium mb-1 block">First Name</label>
                <Input
                  placeholder="Juan"
                  value={genNombre}
                  onChange={(e) => setGenNombre(e.target.value)}
                />
              </div>
              <div>
                <label className="text-sm font-medium mb-1 block">Paternal Surname</label>
                <Input
                  placeholder="Garcia"
                  value={genPaterno}
                  onChange={(e) => setGenPaterno(e.target.value)}
                />
              </div>
              <div>
                <label className="text-sm font-medium mb-1 block">Maternal Surname</label>
                <Input
                  placeholder="Lopez"
                  value={genMaterno}
                  onChange={(e) => setGenMaterno(e.target.value)}
                />
              </div>
              <div>
                <label className="text-sm font-medium mb-1 block">Birth Date</label>
                <Input
                  type="date"
                  value={genFecha}
                  onChange={(e) => setGenFecha(e.target.value)}
                />
              </div>
              <div>
                <label className="text-sm font-medium mb-1 block">Gender</label>
                <select
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                  value={genSexo}
                  onChange={(e) => setGenSexo(e.target.value as 'H' | 'M')}
                >
                  <option value="H">Masculino (H)</option>
                  <option value="M">Femenino (M)</option>
                </select>
              </div>
              <div>
                <label className="text-sm font-medium mb-1 block">State of Birth</label>
                <select
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                  value={genEstado}
                  onChange={(e) => setGenEstado(e.target.value)}
                >
                  {STATES.map(s => (
                    <option key={s.code} value={s.code}>{s.name}</option>
                  ))}
                </select>
              </div>
            </div>
            <Button onClick={handleGenerate} className="w-full">
              Generate
            </Button>

            {generatedCURP && (
              <div className="p-4 bg-primary/10 rounded-lg text-center">
                <div className="text-sm text-muted-foreground mb-1">Generated CURP</div>
                <div className="text-xl font-mono font-bold tracking-wider">
                  {generatedCURP}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Documentation */}
      <Card>
        <CardHeader>
          <CardTitle>CURP Structure (18 characters)</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-3 text-sm">
            <div className="p-3 bg-muted rounded">
              <Badge className="mb-2">1-4</Badge>
              <div className="font-medium">Name Initials</div>
              <div className="text-muted-foreground">First vowel of paternal surname + maternal initial + first name initial</div>
            </div>
            <div className="p-3 bg-muted rounded">
              <Badge className="mb-2">5-10</Badge>
              <div className="font-medium">Birth Date</div>
              <div className="text-muted-foreground">YYMMDD format</div>
            </div>
            <div className="p-3 bg-muted rounded">
              <Badge className="mb-2">11</Badge>
              <div className="font-medium">Gender</div>
              <div className="text-muted-foreground">H = Male, M = Female</div>
            </div>
            <div className="p-3 bg-muted rounded">
              <Badge className="mb-2">12-13</Badge>
              <div className="font-medium">State Code</div>
              <div className="text-muted-foreground">2-letter state abbreviation</div>
            </div>
            <div className="p-3 bg-muted rounded">
              <Badge className="mb-2">14-16</Badge>
              <div className="font-medium">Consonants</div>
              <div className="text-muted-foreground">First internal consonant of each name</div>
            </div>
            <div className="p-3 bg-muted rounded">
              <Badge className="mb-2">17</Badge>
              <div className="font-medium">Differentiator</div>
              <div className="text-muted-foreground">Unique identifier for duplicates</div>
            </div>
            <div className="p-3 bg-muted rounded">
              <Badge className="mb-2">18</Badge>
              <div className="font-medium">Check Digit</div>
              <div className="text-muted-foreground">Verification digit (0-9)</div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
