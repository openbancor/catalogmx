export const NAVIGATION_EVENT = 'catalogmx:navigate';

export function emitNavigation(pageId: string) {
  if (typeof window === 'undefined') return;
  window.dispatchEvent(new CustomEvent<string>(NAVIGATION_EVENT, { detail: pageId }));
}
