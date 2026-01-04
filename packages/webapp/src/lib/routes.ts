import {
  Code, Calculator, CheckCircle2, Home, Database
} from 'lucide-react';
import { type DatasetPageId } from '@/data/datasets';

export type PageId =
  | 'home'
  | 'validators'
  | 'calculators'
  | 'reference'
  | 'catalogs' // Keep for backwards compatibility or redirects
  | 'tables'
  | 'catalog-list'
  | 'postal-codes' | 'localidades' | 'productos' // Individual catalogs still routable?
  | 'rfc' | 'curp' | 'clabe' | 'nss' // Keep these as they might be used internally by the tabs or direct links
  | 'isr' | 'iva' | 'ieps'
  | 'exchange' | 'inflation' | 'salary' // New calculators
  | DatasetPageId;

export interface NavItem {
  id: PageId;
  label: string;
  icon: React.ElementType;
  path: string;
}

export interface NavSection {
  title?: string;
  items: NavItem[];
}

export const navigation: NavSection[] = [
  {
    items: [
      { id: 'home', label: 'nav.catalogs.title', icon: Home, path: '/' },
      { id: 'catalogs', label: 'Catálogos', icon: Database, path: '/catalogs' },
      { id: 'validators', label: 'nav.validators.title', icon: CheckCircle2, path: '/validators' },
      { id: 'calculators', label: 'nav.calculators.title', icon: Calculator, path: '/calculators' },
      { id: 'reference', label: 'nav.reference.title', icon: Code, path: '/reference' },
    ]
  }
];
