import adapter from '@sveltejs/adapter-static';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';
import path from 'path';

/** @type {import('@sveltejs/kit').Config} */
const config = {
	// Consult https://svelte.dev/docs/kit/integrations
	// for more information about preprocessors
	preprocess: vitePreprocess(),

	kit: {
		adapter: adapter({
			// GitHub Pages deployment
			pages: 'build',
			assets: 'build',
			fallback: '404.html',
			precompress: false,
			strict: false, // Allow missing pages during prerender
		}),
		paths: {
			// For GitHub Pages subdirectory deployment
			base: process.env.NODE_ENV === 'production' ? '/catalogmx' : '',
		},
		prerender: {
			handleHttpError: ({ path, referrer, message }) => {
				// Ignore 404s for routes not yet implemented
				if (message.includes('404') || message.includes('Not found')) {
					console.warn(`Ignoring 404 for ${path} (referrer: ${referrer})`);
					return;
				}
				// Also ignore 500s from pages using TanStack Table (Svelte 5 incompatibility)
				if (message.includes('500') && path.includes('/sat/cfdi')) {
					console.warn(`Ignoring 500 for ${path} - TanStack Table Svelte 5 issue`);
					return;
				}
				throw new Error(message);
			},
			handleMissingId: 'warn',
		},
		alias: {
			catalogmx: path.resolve('../typescript/src'),
		},
	},
};

export default config;
