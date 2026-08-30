import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";

const routeUrl = new URL(
  "../src/routes/calculadoras/imss/+page.svelte",
  import.meta.url,
);
const source = await readFile(fileURLToPath(routeUrl), "utf8");

assert.doesNotMatch(source, /value: 'modalidad10'/);
assert.doesNotMatch(source, /calcularModalidad10/);
assert.doesNotMatch(source, /Cuotas actualizadas 2024-2026/);
assert.match(source, /pendiente de auditoría/i);
assert.match(
  source,
  /https:\/\/github\.com\/openbancor\/catalogmx\/issues\/97/,
);
