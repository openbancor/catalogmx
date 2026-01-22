import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
	plugins: [sveltekit()],
	optimizeDeps: {
		include: ['sql.js-httpvfs']
	},
	ssr: {
		// Include @faker-js/faker in SSR bundle to avoid resolution issues during build
		noExternal: ['@faker-js/faker']
	}
});
