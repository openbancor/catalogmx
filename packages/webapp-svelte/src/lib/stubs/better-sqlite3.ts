// Browser stub for better-sqlite3 (Node.js native addon)
// The webapp uses sql.js / sql.js-httpvfs for browser SQLite
export default function Database(): never {
  throw new Error('better-sqlite3 is not available in the browser. Use sql.js instead.');
}
