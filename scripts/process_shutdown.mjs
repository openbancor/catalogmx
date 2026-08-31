function waitForExit(child, timeoutMs) {
  if (child.exitCode !== null || child.signalCode !== null) {
    return Promise.resolve(true);
  }

  return new Promise((resolveExit) => {
    const onExit = () => {
      clearTimeout(timer);
      resolveExit(true);
    };
    const timer = setTimeout(() => {
      child.off("exit", onExit);
      resolveExit(false);
    }, timeoutMs);
    child.once("exit", onExit);

    if (child.exitCode !== null || child.signalCode !== null) {
      child.off("exit", onExit);
      clearTimeout(timer);
      resolveExit(true);
    }
  });
}

export async function terminateChild(
  child,
  { graceMs = 5_000, killMs = 5_000 } = {},
) {
  if (child.exitCode !== null || child.signalCode !== null) return;

  child.kill("SIGTERM");
  if (await waitForExit(child, graceMs)) return;

  child.kill("SIGKILL");
  if (await waitForExit(child, killMs)) return;

  throw new Error("Child process did not exit after SIGKILL.");
}
