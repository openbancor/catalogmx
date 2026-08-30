import { FISCAL_DATASET_IDS, FISCAL_MANIFEST } from './manifest.generated';

export type FiscalDataStatus = 'verified' | 'pending_review' | 'legacy_unverified';
export type FiscalDatasetId = (typeof FISCAL_DATASET_IDS)[number];

export interface FiscalSource {
  authority?: string;
  title?: string;
  published_at?: string;
  url?: string;
}

export interface FiscalManifestEntry {
  exercise: number;
  status: FiscalDataStatus;
  valid_from: string | null;
  valid_to: string | null;
  source_ids: readonly string[];
  values: unknown;
  sha256: string;
  notes?: string;
}

export interface FiscalDatasetManifest {
  owner: string;
  kind: string;
  entries: Record<string, FiscalManifestEntry>;
}

export interface FiscalManifest {
  schema_version: number;
  manifest_id: string;
  content_sha256: string;
  policy: Record<FiscalDataStatus, string>;
  sources: Record<string, FiscalSource>;
  datasets: Record<FiscalDatasetId, FiscalDatasetManifest>;
}

const MANIFEST = FISCAL_MANIFEST as unknown as FiscalManifest;

/**
 * Return the immutable, build-time fiscal manifest.
 *
 * The manifest is statically bundled and therefore works in Workers/browser
 * runtimes without fs, network access or repository-relative paths.
 */
export function fiscalManifest(): Readonly<FiscalManifest> {
  return MANIFEST;
}

/** Return one fiscal dataset entry for an exercise, if present. */
export function fiscalEntry(
  datasetId: FiscalDatasetId,
  exercise: number
): FiscalManifestEntry | undefined {
  return MANIFEST.datasets[datasetId].entries[String(exercise)];
}

/**
 * Return all fiscal entries that exist for one exercise.
 * Historical datasets remain separate instead of being collapsed into a
 * single "current fiscal year" object.
 */
export function fiscalManifestForExercise(exercise: number): {
  exercise: number;
  content_sha256: string;
  entries: Partial<Record<FiscalDatasetId, FiscalManifestEntry>>;
} {
  const entries: Partial<Record<FiscalDatasetId, FiscalManifestEntry>> = {};

  for (const datasetId of Object.keys(MANIFEST.datasets) as FiscalDatasetId[]) {
    const candidate = fiscalEntry(datasetId, exercise);
    if (candidate) entries[datasetId] = candidate;
  }

  return {
    exercise,
    content_sha256: MANIFEST.content_sha256,
    entries,
  };
}

/** Resolve the provenance records referenced by one fiscal entry. */
export function fiscalSources(
  datasetId: FiscalDatasetId,
  exercise: number
): Array<{ id: string; source: FiscalSource | undefined }> {
  const candidate = fiscalEntry(datasetId, exercise);
  if (!candidate) return [];
  return candidate.source_ids.map((id) => ({ id, source: MANIFEST.sources[id] }));
}

/**
 * Require source-audited fiscal data.
 *
 * Audited payroll consumers should call this before using a dataset. Legacy or
 * pending-review history remains queryable, but cannot be mistaken for
 * verified regulatory inputs.
 */
export function assertFiscalDataVerified(
  datasetId: FiscalDatasetId,
  exercise: number
): FiscalManifestEntry {
  const candidate = fiscalEntry(datasetId, exercise);
  if (!candidate) {
    throw new Error(`No fiscal data for ${datasetId} exercise ${exercise}`);
  }
  if (candidate.status !== 'verified') {
    throw new Error(
      `Fiscal data ${datasetId} exercise ${exercise} is ${candidate.status}, not verified`
    );
  }
  return candidate;
}
