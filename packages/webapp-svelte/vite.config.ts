import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
	plugins: [sveltekit()],
	optimizeDeps: {
		include: ['sql.js-httpvfs', 'libxml2-wasm']
	},
	assetsInclude: ['**/*.wasm']
});
