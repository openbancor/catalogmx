import type { EntryGenerator, PageLoad } from './$types';

type KnownPostalData = {
	asentamientoPrincipal: string;
	municipio: string;
	estado: string;
	ciudad: string;
	zona: string;
};

const KNOWN_POSTAL_DATA: Record<string, KnownPostalData> = {
	'03650': {
		asentamientoPrincipal: 'Letrán Valle',
		municipio: 'Benito Juárez',
		estado: 'Ciudad de México',
		ciudad: 'Ciudad de México',
		zona: 'Urbano'
	}
};

export const prerender = true;
export const csr = true;

export const entries: EntryGenerator = () => [{ cp: '03650' }];

export const load: PageLoad = ({ params }) => {
	const cp = params.cp.trim();
	return {
		cp,
		knownPostalData: KNOWN_POSTAL_DATA[cp] ?? null
	};
};
