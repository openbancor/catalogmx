/**
 * The default data mode is offline: the updater never downloads unless asked.
 */
import * as fs from 'fs';
import * as os from 'os';
import * as path from 'path';

import { DataUpdater } from '../src/data/updater';

// eslint-disable-next-line @typescript-eslint/no-require-imports -- same CJS object the updater uses
const https = require('https');

describe('DataUpdater default is offline', () => {
  let home: string;
  let getSpy: jest.SpyInstance;
  const originalHome = process.env.HOME;
  const originalProfile = process.env.USERPROFILE;

  beforeEach(() => {
    home = fs.mkdtempSync(path.join(os.tmpdir(), 'catalogmx-updater-'));
    process.env.HOME = home;
    process.env.USERPROFILE = home;
    getSpy = jest.spyOn(https, 'get').mockImplementation((() => {
      throw new Error('network access attempted');
    }) as never);
  });

  afterEach(() => {
    getSpy.mockRestore();
    process.env.HOME = originalHome;
    if (originalProfile === undefined) delete process.env.USERPROFILE;
    else process.env.USERPROFILE = originalProfile;
    fs.rmSync(home, { recursive: true, force: true });
  });

  it('does not touch the network by default', async () => {
    try {
      await new DataUpdater().getDatabasePath();
    } catch {
      // No packaged database in the test environment: failing closed is acceptable.
    }
    expect(getSpy).not.toHaveBeenCalled();
  });

  it('downloads only when autoUpdate is explicitly enabled', async () => {
    try {
      await new DataUpdater({ autoUpdate: true }).getDatabasePath();
    } catch {
      // The mocked download fails; only the attempt matters here.
    }
    expect(getSpy).toHaveBeenCalled();
  });
});
