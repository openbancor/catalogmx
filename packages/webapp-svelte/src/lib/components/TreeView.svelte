<script lang="ts" generics="T extends { id: string; label: string; hasChildren?: boolean; children?: T[] }">
	import { ChevronRight, Loader2 } from 'lucide-svelte';

	interface Props {
		items: T[];
		level?: number;
		selectedId?: string | null;
		expandedIds?: Set<string>;
		loadingIds?: Set<string>;
		onSelect?: (item: T) => void;
		onExpand?: (item: T) => Promise<T[] | void>;
		renderLabel?: (item: T) => string;
		renderMeta?: (item: T) => string;
	}

	let {
		items,
		level = 0,
		selectedId = null,
		expandedIds = $bindable(new Set<string>()),
		loadingIds = $bindable(new Set<string>()),
		onSelect,
		onExpand,
		renderLabel = (item: T) => item.label,
		renderMeta,
	}: Props = $props();

	async function toggleExpand(item: T) {
		if (loadingIds.has(item.id)) return;

		if (expandedIds.has(item.id)) {
			const newExpanded = new Set(expandedIds);
			newExpanded.delete(item.id);
			expandedIds = newExpanded;
		} else {
			// If we need to load children
			if (onExpand && item.hasChildren && (!item.children || item.children.length === 0)) {
				const newLoading = new Set(loadingIds);
				newLoading.add(item.id);
				loadingIds = newLoading;

				try {
					const children = await onExpand(item);
					if (children) {
						item.children = children;
					}
				} finally {
					const newLoading = new Set(loadingIds);
					newLoading.delete(item.id);
					loadingIds = newLoading;
				}
			}

			const newExpanded = new Set(expandedIds);
			newExpanded.add(item.id);
			expandedIds = newExpanded;
		}
	}

	function handleSelect(item: T) {
		onSelect?.(item);
	}

	function handleKeyDown(event: KeyboardEvent, item: T) {
		if (event.key === 'Enter' || event.key === ' ') {
			event.preventDefault();
			if (item.hasChildren || item.children?.length) {
				toggleExpand(item);
			} else {
				handleSelect(item);
			}
		}
	}
</script>

<ul class="tree-list" role="tree" aria-label="Tree view">
	{#each items as item (item.id)}
		{@const isExpanded = expandedIds.has(item.id)}
		{@const isLoading = loadingIds.has(item.id)}
		{@const isSelected = selectedId === item.id}
		{@const hasExpandableContent = item.hasChildren || (item.children && item.children.length > 0)}

		<li role="treeitem" aria-expanded={hasExpandableContent ? isExpanded : undefined}>
			<div
				class="tree-item group"
				class:selected={isSelected}
				style="padding-left: {level * 1.25}rem"
				tabindex="0"
				onclick={() => hasExpandableContent ? toggleExpand(item) : handleSelect(item)}
				onkeydown={(e) => handleKeyDown(e, item)}
				role="button"
			>
				<!-- Expand/collapse icon -->
				<span class="tree-icon">
					{#if isLoading}
						<Loader2 class="h-4 w-4 animate-spin text-slate-400" />
					{:else if hasExpandableContent}
						<ChevronRight
							class={`h-4 w-4 text-slate-400 transition-transform duration-200 ${isExpanded ? 'rotate-90' : ''}`}
						/>
					{:else}
						<span class="w-4"></span>
					{/if}
				</span>

				<!-- Item content -->
				<span class="tree-content">
					<span class="tree-id font-mono text-xs text-slate-500 dark:text-slate-400 mr-2">
						{item.id}
					</span>
					<span class="tree-label text-slate-900 dark:text-white">
						{renderLabel(item)}
					</span>
					{#if renderMeta}
						<span class="tree-meta text-xs text-slate-400 dark:text-slate-500 ml-auto">
							{renderMeta(item)}
						</span>
					{/if}
				</span>
			</div>

			<!-- Children (recursive) -->
			{#if isExpanded && item.children && item.children.length > 0}
				<svelte:self
					items={item.children}
					level={level + 1}
					{selectedId}
					bind:expandedIds
					bind:loadingIds
					{onSelect}
					{onExpand}
					{renderLabel}
					{renderMeta}
				/>
			{/if}
		</li>
	{/each}
</ul>

<style>
	.tree-list {
		list-style: none;
		margin: 0;
		padding: 0;
	}

	.tree-item {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.5rem 0.75rem;
		cursor: pointer;
		border-radius: 0.375rem;
		transition: background-color 0.15s ease;
	}

	.tree-item:hover {
		background-color: rgb(248 250 252); /* slate-50 */
	}

	:global(.dark) .tree-item:hover {
		background-color: rgb(30 41 59 / 0.5); /* slate-800/50 */
	}

	.tree-item.selected {
		background-color: rgb(219 234 254); /* blue-100 */
	}

	:global(.dark) .tree-item.selected {
		background-color: rgb(30 58 138 / 0.3); /* blue-900/30 */
	}

	.tree-item:focus {
		outline: 2px solid rgb(59 130 246); /* blue-500 */
		outline-offset: -2px;
	}

	.tree-icon {
		flex-shrink: 0;
		display: flex;
		align-items: center;
		justify-content: center;
		width: 1.25rem;
		height: 1.25rem;
	}

	.tree-content {
		display: flex;
		align-items: center;
		flex: 1;
		min-width: 0;
		overflow: hidden;
	}

	.tree-label {
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}
</style>
