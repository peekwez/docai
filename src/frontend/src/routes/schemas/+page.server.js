/** @type {import('./$types').PageServerLoad} */

import { DOCUMENT_AI_API_ENDPOINT, DOCUMENT_AI_API_KEY } from '$env/static/private';

export async function load() {
	const url = `${DOCUMENT_AI_API_ENDPOINT}/list-schema`;
	const requestHeaders = {
		'Content-Type': 'application/json',
		'x-api-key': DOCUMENT_AI_API_KEY
	};
	const body = JSON.stringify({ schema_name: 'test_loe' });
	const response = await fetch(url, { method: 'POST', headers: requestHeaders, body });
	const data = await response.json();

	console.log(data);
	const rows = data.result ? data.result.items : [];
	rows.forEach((row) => {
		row.id = row.schema_version;
	});
	return { rows };
}
