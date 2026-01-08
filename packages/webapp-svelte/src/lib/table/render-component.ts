import type { Component, ComponentProps, Snippet } from 'svelte';

/**
 * A helper class to make it easy to identify Svelte components in
 * `columnDef.cell` and `columnDef.header` properties.
 */
export class RenderComponentConfig<TComponent extends Component> {
	constructor(
		public component: TComponent,
		public props: ComponentProps<TComponent> | Record<string, never> = {}
	) {}
}

/**
 * A helper class to make it easy to identify Svelte Snippets in
 * `columnDef.cell` and `columnDef.header` properties.
 */
export class RenderSnippetConfig<TProps> {
	constructor(
		public snippet: Snippet<[TProps]>,
		public params: TProps
	) {}
}

/**
 * A helper function to help create cells from Svelte components through
 * ColumnDef's `cell` and `header` properties.
 *
 * @param component A Svelte component
 * @param props The props to pass to `component`
 * @returns A `RenderComponentConfig` object
 */
export const renderComponent = <
	// eslint-disable-next-line @typescript-eslint/no-explicit-any
	TComponent extends Component<any>,
	TProps extends ComponentProps<TComponent>
>(
	component: TComponent,
	props: TProps
) => new RenderComponentConfig(component, props);

/**
 * A helper function to help create cells from Svelte Snippets through
 * ColumnDef's `cell` and `header` properties.
 *
 * @param snippet The Svelte snippet
 * @param params The parameters to pass to the snippet
 * @returns A `RenderSnippetConfig` object
 */
export const renderSnippet = <TProps>(snippet: Snippet<[TProps]>, params: TProps) =>
	new RenderSnippetConfig(snippet, params);
