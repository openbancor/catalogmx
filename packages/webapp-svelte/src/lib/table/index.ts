// Re-export everything from @tanstack/table-core
export * from '@tanstack/table-core';

// Export our Svelte 5 adapter
export { default as FlexRender } from './FlexRender.svelte';
export { renderComponent, renderSnippet } from './render-component';
export { createSvelteTable } from './table.svelte';
