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
			handleHttpError: 'warn',
			handleMissingId: 'warn',
		},
		alias: {
			catalogmx: path.resolve('../typescript/src'),
		},
	},
};

export default config;
