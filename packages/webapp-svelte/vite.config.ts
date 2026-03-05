import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
	plugins: [sveltekit()],
	optimizeDeps: {
		include: ['sql.js-httpvfs'],
		exclude: ['better-sqlite3', 'libxmljs2', 'xslt-processor']
	},
	resolve: {
		alias: {
			'better-sqlite3': '/src/lib/stubs/better-sqlite3.ts',
			'libxmljs2': '/src/lib/stubs/libxmljs2.ts',
			'xslt-processor': '/src/lib/stubs/xslt-processor.ts',
		}
	},
	assetsInclude: ['**/*.wasm']
});
