#!/usr/bin/env node

import { execFileSync, spawn } from "node:child_process";
import {
  existsSync,
  mkdtempSync,
  readFileSync,
  rmSync,
  writeFileSync,
} from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { createServer } from "node:net";

import { terminateChild } from "./process_shutdown.mjs";

const repoRoot = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const typescriptDir = join(repoRoot, "packages", "typescript");
const wranglerBin = join(
  repoRoot,
  "packages",
  "api-worker",
  "node_modules",
  ".bin",
  "wrangler",
);
const scratchDir = mkdtempSync(join(tmpdir(), "catalogmx-package-contract-"));

function run(command, args, options = {}) {
  return execFileSync(command, args, {
    cwd: options.cwd ?? repoRoot,
    encoding: "utf8",
    stdio: options.capture ? ["ignore", "pipe", "inherit"] : "inherit",
  });
}

async function availablePort() {
  const server = createServer();
  await new Promise((resolveReady, reject) => {
    server.once("error", reject);
    server.listen(0, "127.0.0.1", resolveReady);
  });
  const address = server.address();
  const port = typeof address === "object" && address ? address.port : null;
  await new Promise((resolveClosed) => server.close(resolveClosed));
  if (port === null)
    throw new Error("Could not allocate a local Worker test port.");
  return port;
}

async function exerciseWorker(wrangler, config, cwd) {
  const port = await availablePort();
  const child = spawn(
    wrangler,
    ["dev", "--config", config, "--ip", "127.0.0.1", "--port", String(port)],
    { cwd, stdio: ["ignore", "pipe", "pipe"] },
  );
  let output = "";
  child.stdout.on("data", (chunk) => {
    output += chunk;
  });
  child.stderr.on("data", (chunk) => {
    output += chunk;
  });

  try {
    const deadline = Date.now() + 30_000;
    while (Date.now() < deadline) {
      if (child.exitCode !== null) {
        throw new Error(`Wrangler exited before the runtime smoke:\n${output}`);
      }
      try {
        const response = await fetch(`http://127.0.0.1:${port}/`);
        if (!response.ok)
          throw new Error(`Worker returned HTTP ${response.status}`);
        const result = await response.json();
        for (const [name, value] of Object.entries(result)) {
          if (value !== true)
            throw new Error(`Worker catalog check failed: ${name}`);
        }
        return;
      } catch (error) {
        if (Date.now() >= deadline) throw error;
        await new Promise((resolveDelay) => setTimeout(resolveDelay, 250));
      }
    }
    throw new Error(`Worker did not become ready:\n${output}`);
  } finally {
    await terminateChild(child);
  }
}

try {
  if (!existsSync(wranglerBin)) {
    throw new Error(
      "Run npm ci in packages/api-worker before the package contract check.",
    );
  }

  run("npm", ["run", "build"], { cwd: typescriptDir });
  const packResult = JSON.parse(
    run("npm", ["pack", "--json", "--pack-destination", scratchDir], {
      cwd: typescriptDir,
      capture: true,
    }),
  );
  const tarball = join(scratchDir, packResult[0].filename);
  const consumerDir = join(scratchDir, "consumer");

  run(
    "npm",
    [
      "install",
      "--ignore-scripts",
      "--no-audit",
      "--no-fund",
      "--prefix",
      consumerDir,
      tarball,
    ],
    { cwd: repoRoot },
  );

  const commonJsContract = `
    const root = require('catalogmx');
    const fiscal = require('catalogmx/fiscal');
    const catalogs = require('catalogmx/catalogs');
    const cfdi = require('catalogmx/cfdi');
    for (const [name, value] of Object.entries({
      validateRfc: root.validateRfc,
      fiscalManifest: fiscal.fiscalManifest,
      BankCatalog: catalogs.BankCatalog,
      EstadoCfdiCatalog: catalogs.EstadoCfdiCatalog,
      TipoRegimenCatalog: catalogs.TipoRegimenCatalog,
      FormaPagoCatalog: catalogs.FormaPagoCatalog,
      NominaCfdiCatalog: catalogs.NominaCfdiCatalog,
      PaisCatalog: catalogs.PaisCatalog,
      buildUnsignedCfdiXml: cfdi.buildUnsignedCfdiXml,
    })) {
      if (typeof value !== 'function') throw new Error('Missing CommonJS export: ' + name);
    }
    if (!catalogs.BankCatalog.isValidCode('002')) throw new Error('Missing Banxico bank 002');
    if (!catalogs.TipoRegimenCatalog.isValid('02')) throw new Error('Missing Nomina regimen 02');
    if (!catalogs.FormaPagoCatalog.isValid('03')) throw new Error('Missing CFDI payment form 03');
    if (!catalogs.EstadoCfdiCatalog.isValid('CMX')) throw new Error('Missing CFDI state CMX');
    if (!catalogs.PaisCatalog.isValid('MEX')) throw new Error('Missing country MEX');
    if (!catalogs.NominaCfdiCatalog.isValidClaveProdServ('84111505')) {
      throw new Error('Missing payroll CFDI product/service 84111505');
    }
  `;
  run(process.execPath, ["-e", commonJsContract], { cwd: consumerDir });

  const esmContract = `
    import { validateRfc } from 'catalogmx';
    import { fiscalManifest } from 'catalogmx/fiscal';
    import {
      BankCatalog,
      EstadoCfdiCatalog,
      FormaPagoCatalog,
      NominaCfdiCatalog,
      PaisCatalog,
      TipoRegimenCatalog,
    } from 'catalogmx/catalogs';
    import { buildUnsignedCfdiXml } from 'catalogmx/cfdi';
    for (const [name, value] of Object.entries({
      validateRfc,
      fiscalManifest,
      BankCatalog,
      EstadoCfdiCatalog,
      FormaPagoCatalog,
      PaisCatalog,
      TipoRegimenCatalog,
      buildUnsignedCfdiXml,
    })) {
      if (typeof value !== 'function') throw new Error('Missing ESM export: ' + name);
    }
    if (!BankCatalog.isValidCode('002')) throw new Error('Missing Banxico bank 002');
    if (!TipoRegimenCatalog.isValid('02')) throw new Error('Missing Nomina regimen 02');
    if (!FormaPagoCatalog.isValid('03')) throw new Error('Missing CFDI payment form 03');
    if (!EstadoCfdiCatalog.isValid('CMX')) throw new Error('Missing CFDI state CMX');
    if (!PaisCatalog.isValid('MEX')) throw new Error('Missing country MEX');
    if (!NominaCfdiCatalog.isValidClaveProdServ('84111505')) {
      throw new Error('Missing payroll CFDI product/service 84111505');
    }
  `;
  run(process.execPath, ["--input-type=module", "-e", esmContract], {
    cwd: consumerDir,
  });

  writeFileSync(
    join(consumerDir, "worker.mjs"),
    `
      import { validateRfc } from 'catalogmx';
      import { fiscalManifest } from 'catalogmx/fiscal';
      import {
        BankCatalog,
        EstadoCfdiCatalog,
        FormaPagoCatalog,
        NominaCfdiCatalog,
        PaisCatalog,
        TipoRegimenCatalog,
      } from 'catalogmx/catalogs';
      import { preloadSmallCatalogData } from 'catalogmx/catalogs/preload';
      import { buildUnsignedCfdiXml } from 'catalogmx/cfdi';

      preloadSmallCatalogData();

      export default {
        fetch() {
          return Response.json({
            root: validateRfc('XAXX010101000'),
            fiscal: fiscalManifest().manifest_id.length > 0,
            bank: BankCatalog.isValidCode('002'),
            nomina: TipoRegimenCatalog.isValid('02'),
            cfdiCatalog: FormaPagoCatalog.isValid('03'),
            estado: EstadoCfdiCatalog.isValid('CMX'),
            pais: PaisCatalog.isValid('MEX'),
            nominaClaveProdServ: NominaCfdiCatalog.isValidClaveProdServ('84111505'),
            cfdi: typeof buildUnsignedCfdiXml === 'function',
          });
        },
      };
    `,
  );
  writeFileSync(
    join(consumerDir, "wrangler.jsonc"),
    `${JSON.stringify(
      {
        name: "catalogmx-package-contract",
        main: "worker.mjs",
        compatibility_date: "2026-08-28",
      },
      null,
      2,
    )}\n`,
  );

  const workerDist = join(consumerDir, "dist");
  run(
    wranglerBin,
    [
      "deploy",
      "--dry-run",
      "--config",
      join(consumerDir, "wrangler.jsonc"),
      "--outdir",
      workerDist,
    ],
    { cwd: consumerDir },
  );
  const workerBundle = join(workerDist, "worker.js");
  if (
    !existsSync(workerBundle) ||
    readFileSync(workerBundle, "utf8").length === 0
  ) {
    throw new Error("Wrangler did not produce the expected Worker bundle.");
  }
  await exerciseWorker(
    wranglerBin,
    join(consumerDir, "wrangler.jsonc"),
    consumerDir,
  );

  console.log(
    "Packed catalogmx passed CommonJS, ESM, and Cloudflare Worker contracts.",
  );
} finally {
  rmSync(scratchDir, { recursive: true, force: true });
}
