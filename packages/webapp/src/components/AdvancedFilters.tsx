import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Filter, X, ChevronDown, ChevronUp } from 'lucide-react';

interface FieldFilter {
  field: string;
  value: string;
}

interface AdvancedFiltersProps {
  columns: Array<{ key: string; label: string }>;
  searchColumns: string[];
  onFilter: (filters: FieldFilter[]) => void;
  disabled?: boolean;
}

export default function AdvancedFilters({ columns, searchColumns, onFilter, disabled }: AdvancedFiltersProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [filters, setFilters] = useState<FieldFilter[]>([]);

  const searchableColumns = columns.filter(col => searchColumns.includes(col.key));

  const addFilter = () => {
    if (searchableColumns.length > 0) {
      setFilters([...filters, { field: searchableColumns[0].key, value: '' }]);
    }
  };

  const removeFilter = (index: number) => {
    const newFilters = filters.filter((_, i) => i !== index);
    setFilters(newFilters);
    onFilter(newFilters);
  };

  const updateFilter = (index: number, field: string, value: string) => {
    const newFilters = [...filters];
    newFilters[index] = { field, value };
    setFilters(newFilters);
  };

  const applyFilters = () => {
    const activeFilters = filters.filter(f => f.value.trim() !== '');
    onFilter(activeFilters);
  };

  const clearFilters = () => {
    setFilters([]);
    onFilter([]);
  };

  if (searchableColumns.length <= 1) {
    return null; // Don't show advanced filters if there's only one searchable column
  }

  const activeCount = filters.filter(f => f.value.trim() !== '').length;

  return (
    <Card className="border-dashed">
      <CardHeader className="pb-3 cursor-pointer" onClick={() => setIsExpanded(!isExpanded)}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Filter className="h-4 w-4 text-muted-foreground" />
            <CardTitle className="text-sm font-medium">Filtros por Campo</CardTitle>
            {activeCount > 0 && (
              <Badge variant="secondary" className="ml-2">
                {activeCount} activo{activeCount > 1 ? 's' : ''}
              </Badge>
            )}
          </div>
          {isExpanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
        </div>
        {!isExpanded && (
          <CardDescription className="text-xs">
            Filtra por campos específicos: {searchableColumns.map(c => c.label).join(', ')}
          </CardDescription>
        )}
      </CardHeader>

      {isExpanded && (
        <CardContent className="space-y-3">
          {filters.length === 0 && (
            <p className="text-sm text-muted-foreground">
              Agrega filtros específicos por campo para una búsqueda más precisa.
            </p>
          )}

          {filters.map((filter, index) => (
            <div key={index} className="flex gap-2">
              <select
                value={filter.field}
                onChange={(e) => updateFilter(index, e.target.value, filter.value)}
                className="h-10 rounded-md border bg-background px-3 text-sm min-w-[140px]"
                disabled={disabled}
              >
                {searchableColumns.map((col) => (
                  <option key={col.key} value={col.key}>
                    {col.label}
                  </option>
                ))}
              </select>

              <Input
                placeholder="Valor a buscar..."
                value={filter.value}
                onChange={(e) => updateFilter(index, filter.field, e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && applyFilters()}
                disabled={disabled}
                className="flex-1"
              />

              <Button
                variant="ghost"
                size="icon"
                onClick={() => removeFilter(index)}
                disabled={disabled}
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
          ))}

          <div className="flex gap-2 pt-2">
            <Button
              variant="outline"
              size="sm"
              onClick={addFilter}
              disabled={disabled}
              className="flex-1"
            >
              <Filter className="h-3 w-3 mr-1" />
              Agregar Filtro
            </Button>

            {filters.length > 0 && (
              <>
                <Button
                  size="sm"
                  onClick={applyFilters}
                  disabled={disabled}
                >
                  Aplicar
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={clearFilters}
                  disabled={disabled}
                >
                  Limpiar
                </Button>
              </>
            )}
          </div>
        </CardContent>
      )}
    </Card>
  );
}
