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
			// GitHub Pages needs /catalogmx base, Cloudflare Pages uses root
			base: process.env.DEPLOY_TARGET === 'github-pages' ? '/catalogmx' : '',
		},
		prerender: {
			handleHttpError: ({ path, referrer, message }) => {
				// Ignore 404s for routes not yet implemented
				if (message.includes('404') || message.includes('Not found')) {
					console.warn(`Ignoring 404 for ${path} (referrer: ${referrer})`);
					return;
				}
				// Ignore 500s from pages using sql.js-httpvfs or TanStack Table (SSR incompatible)
				if (message.includes('500')) {
					console.warn(`Ignoring 500 for ${path} - SSR incompatible page (sql.js or TanStack Table)`);
					return;
				}
				throw new Error(message);
			},
			handleMissingId: 'warn',
			// Handle dynamic routes that aren't discovered during prerender crawl
			handleUnseenRoutes: 'warn',
		},
		alias: {
			catalogmx: path.resolve('../typescript/src'),
		},
	},
};

export default config;
