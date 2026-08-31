import assert from "node:assert/strict";
import { spawn } from "node:child_process";
import test from "node:test";

import { terminateChild } from "./process_shutdown.mjs";

test("terminateChild escalates when a child ignores SIGTERM", async () => {
  const child = spawn(
    process.execPath,
    [
      "-e",
      "process.on('SIGTERM', () => {}); console.log('ready'); setInterval(() => {}, 1_000);",
    ],
    { stdio: ["ignore", "pipe", "inherit"] },
  );

  await new Promise((resolveReady, reject) => {
    child.once("error", reject);
    child.stdout.once("data", resolveReady);
  });

  await terminateChild(child, { graceMs: 50, killMs: 1_000 });

  assert.equal(child.signalCode, "SIGKILL");
});
