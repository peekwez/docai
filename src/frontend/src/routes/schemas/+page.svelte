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
		CheckmarkFilled,
		StringInteger,
		StringText,
		CalendarHeatMap,
		Term,
		Parameter
	} from 'carbon-icons-svelte';

	export let data;
	const headers = [
		{ key: 'schema_name', value: 'Name' },
		{ key: 'schema_description', value: 'Description' },
		{ key: 'schema_version', value: 'Version' },
		{ key: 'number_of_tokens', value: 'Tokens' },
		{ key: 'schema_definition', value: 'Fields' },
		{ key: 'schema_status', value: 'Status' },
		{
			key: 'created_at',
			value: 'Created At',
			display: (value) => new Date(value).toLocaleString(),
			sort: (a, b) => new Date(a) - new Date(b)
		}
	];

	let page = 1;
	let { rows } = data;
	let selectedRowIds = [];

	let pageSize = 10;

	let title = 'Schema Definitions';
	let description =
		"A collection of your organization's active schemas used for extracting structured data from documents. Use the dropdown menu to view the schema details.";

	let typeIcons = {
		string: StringText,
		number: StringInteger,
		date: CalendarHeatMap,
		object: Parameter,
		array: Term
	};

	let typeColors = {
		string: 'blue',
		number: 'green',
		date: 'purple',
		object: 'high-contrast',
		array: 'magenta'
	};

	let getDataType = (field) => {
		let { type } = field;
		if (typeof type === 'object') {
			type = type.find((el) => el !== 'null');
		}
		return type;
	};
	let typeIconsFn = (field) => {
		return typeIcons[getDataType(field)];
	};

	let typeColorsFn = (field) => {
		return typeColors[getDataType(field)];
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
				{@const icon = typeIconsFn(field_object)}
				{@const color = typeColorsFn(field_object)}
				<Tag {icon} type={color}>{field_name}</Tag>
			{/each}
		{:else if cell.key === 'schema_status'}
			<CheckmarkFilled size={20} fill="green" />
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
