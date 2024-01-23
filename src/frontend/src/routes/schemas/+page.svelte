<script>
	import {
		DataTable,
		Toolbar,
		ToolbarContent,
		ToolbarSearch,
		CodeSnippet,
		Button,
		Tag,
		Pagination,
		ToolbarBatchActions
	} from 'carbon-components-svelte';

	import {
		TrashCan,
		Email,
		StringInteger,
		StringText,
		CalendarHeatMap,
		Term,
		Parameter
		// CheckmarkFilled,
	} from 'carbon-icons-svelte';

	export let data;
	const options = {
		year: 'numeric',
		month: 'short',
		day: 'numeric',
		hour: 'numeric',
		minute: 'numeric'
	};
	const headers = [
		{ key: 'schema_name', value: 'Name' },
		{ key: 'schema_description', value: 'Description' },
		{ key: 'schema_version', value: 'Version' },
		{ key: 'number_of_tokens', value: 'Tokens' },
		{ key: 'schema_definition', value: 'Fields' },
		// { key: 'schema_status', value: 'Status' },
		{
			key: 'created_at',
			value: 'Created At',
			display: (value) => new Date(value).toLocaleString('en-CA', options),
			sort: (a, b) => new Date(a) - new Date(b)
		}
	];

	let page = 1;
	let pageSize = 10;
	let { rows } = data;
	let selectedRowIds = [];
	let title = 'Schema Definitions';
	let description =
		"A collection of your organization's active schemas used for extracting structured data from documents. Use the dropdown menu to view the schema details.";

	let tagProps = {
		string: { icon: StringText, type: 'blue' },
		number: { icon: StringInteger, type: 'green' },
		date: { icon: CalendarHeatMap, type: 'purple' },
		object: { icon: Parameter, type: 'high-contrast' },
		email: { icon: Email, type: 'red' },
		array: { icon: Term, type: 'magenta' },
		null: { icon: null, type: 'cyan' }
	};

	let getTagProps = (field) => {
		let { type, format } = field;
		if (typeof type === 'object') {
			type = type.find((el) => el !== 'null');
		}
		return format ? tagProps[format] : tagProps[type];
	};

	$: console.log(selectedRowIds);
</script>

<h2>Schema Management</h2>
<DataTable
	{title}
	{description}
	batchExpansion
	batchSelection
	bind:selectedRowIds
	{headers}
	{pageSize}
	{page}
	{rows}
>
	<Toolbar>
		<ToolbarBatchActions>
			<Button
				icon={TrashCan}
				disabled={selectedRowIds.length === 0}
				on:click={() => {
					rows = rows.filter((row) => !selectedRowIds.includes(row.id));
					selectedRowIds = [];
				}}
			>
				Delete
			</Button>
		</ToolbarBatchActions>
		<ToolbarContent>
			<ToolbarSearch />
			<Button>Add new schema</Button>
		</ToolbarContent>
	</Toolbar>

	<svelte:fragment slot="expanded-row" let:row>
		<CodeSnippet type="multi" expanded feedback="Copied to clipboard">
			{JSON.stringify(row.schema_definition, null, 2)}
		</CodeSnippet>
	</svelte:fragment>

	<svelte:fragment slot="cell" let:cell>
		{#if cell.key === 'schema_definition'}
			{#each Object.entries(cell.value.properties) as [field_name, field_object]}
				<Tag {...getTagProps(field_object)}>{field_name}</Tag>
			{/each}
		{:else if cell.key == 'created_at'}
			{cell.display(cell.value)}
		{:else}
			{cell.value}
		{/if}
	</svelte:fragment>
</DataTable>

<Pagination bind:pageSize bind:page totalItems={rows.length} pageSizeInputDisabled />

<style>
	h2 {
		margin-bottom: 1em;
	}
</style>
