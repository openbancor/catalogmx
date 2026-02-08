import type { EntryGenerator, PageLoad } from './$types';

type KnownLadaData = {
	ciudad: string;
	estado: string;
	tipo: string;
	region: string;
};

const KNOWN_LADA_DATA: Record<string, KnownLadaData> = {
	'55': { ciudad: 'Ciudad de México', estado: 'CDMX', tipo: 'metropolitana', region: 'centro' },
	'33': { ciudad: 'Guadalajara', estado: 'Jalisco', tipo: 'metropolitana', region: 'occidente' },
	'81': { ciudad: 'Monterrey', estado: 'Nuevo León', tipo: 'metropolitana', region: 'noreste' },
	'222': { ciudad: 'Puebla', estado: 'Puebla', tipo: 'metropolitana', region: 'centro' },
	'999': { ciudad: 'Mérida', estado: 'Yucatán', tipo: 'metropolitana', region: 'sureste' },
	'998': { ciudad: 'Alfredo V. Bonfil', estado: 'Quintana Roo', tipo: 'normal', region: 'sureste' },
	'664': { ciudad: 'Tijuana', estado: 'Baja California', tipo: 'fronteriza', region: 'noroeste' },
	'656': { ciudad: 'Ciudad Juárez', estado: 'Chihuahua', tipo: 'fronteriza', region: 'norte' }
};

export const prerender = true;
export const csr = true;

export const entries: EntryGenerator = () =>
	Object.keys(KNOWN_LADA_DATA).map((lada) => ({ lada }));

export const load: PageLoad = ({ params }) => {
	const lada = params.lada.trim();
	return {
		lada,
		knownLadaData: KNOWN_LADA_DATA[lada] ?? null
	};
};
