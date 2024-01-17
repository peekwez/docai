<script>
	import 'carbon-components-svelte/css/all.css';
	import {
		Header,
		HeaderUtilities,
		HeaderAction,
		HeaderGlobalAction,
		HeaderPanelLinks,
		HeaderPanelDivider,
		HeaderPanelLink,
		SideNav,
		SideNavItems,
		SideNavMenu,
		SideNavMenuItem,
		SideNavLink,
		SkipToContent,
		Content,
		Grid,
		Row,
		Column
	} from 'carbon-components-svelte';
	import SettingsAdjust from 'carbon-icons-svelte/lib/SettingsAdjust.svelte';
	import UserAvatarFilledAlt from 'carbon-icons-svelte/lib/UserAvatarFilledAlt.svelte';
	import Notification from 'carbon-icons-svelte/lib/Notification.svelte';

	// let theme = 'g10'; // "white" | "g10" | "g80" | "g90" | "g100"

	// $: document.documentElement.setAttribute('theme', theme);

	let isSideNavOpen = false;
	let isOpen1 = false;
	let isOpen2 = false;
</script>

<Header company="" platformName="Document Artificial Intelligence" bind:isSideNavOpen>
	<svelte:fragment slot="skip-to-content">
		<SkipToContent />
	</svelte:fragment>
	<HeaderUtilities>
		<HeaderGlobalAction aria-label="Settings" icon={SettingsAdjust} />
		<HeaderGlobalAction aria-label="Notifications" icon={Notification} />
		<HeaderAction bind:isOpen={isOpen1} icon={UserAvatarFilledAlt} closeIcon={UserAvatarFilledAlt}>
			<HeaderPanelLinks>
				<HeaderPanelDivider>Switcher subject 1</HeaderPanelDivider>
				<HeaderPanelLink>Switcher item 1</HeaderPanelLink>
				<HeaderPanelLink>Switcher item 2</HeaderPanelLink>
				<HeaderPanelLink>Switcher item 3</HeaderPanelLink>
				<HeaderPanelLink>Switcher item 4</HeaderPanelLink>
				<HeaderPanelDivider>Switcher subject 2</HeaderPanelDivider>
				<HeaderPanelLink>Switcher item 1</HeaderPanelLink>
				<HeaderPanelLink>Switcher item 2</HeaderPanelLink>
				<HeaderPanelDivider>Switcher subject 3</HeaderPanelDivider>
				<HeaderPanelLink>Switcher item 1</HeaderPanelLink>
			</HeaderPanelLinks>
		</HeaderAction>
		<HeaderAction bind:isOpen={isOpen2}>
			<HeaderPanelLinks>
				<HeaderPanelDivider>Switcher subject 1</HeaderPanelDivider>
				<HeaderPanelLink>Switcher item 1</HeaderPanelLink>
				<HeaderPanelDivider>Switcher subject 2</HeaderPanelDivider>
				<HeaderPanelLink>Switcher item 1</HeaderPanelLink>
				<HeaderPanelLink>Switcher item 2</HeaderPanelLink>
				<HeaderPanelLink>Switcher item 3</HeaderPanelLink>
				<HeaderPanelLink>Switcher item 4</HeaderPanelLink>
				<HeaderPanelLink>Switcher item 5</HeaderPanelLink>
			</HeaderPanelLinks>
		</HeaderAction>
	</HeaderUtilities>
</Header>

<SideNav bind:isOpen={isSideNavOpen}>
	<SideNavItems>
		<SideNavMenu text="Assistants">
			<SideNavMenuItem href="assistants/schema-builder" text="Schema Builder" />
		</SideNavMenu>
		<SideNavLink text="Schemas" href="/schemas" />
		<SideNavLink text="Documents" href="/documents" />
		<SideNavMenu text="Demos">
			<SideNavMenuItem href="/demos/invoice" text="Invoice" />
			<SideNavMenuItem href="/demos/receipt" text="Receipt" />
			<SideNavMenuItem href="/demos/pay-slip" text="Pay Slip" />
			<SideNavMenuItem href="/demos/credit-report" text="Credit Report" />
			<SideNavMenuItem href="/demos/employment-letter" text="Employment Letter" />
			<SideNavMenuItem href="/demos/mortgage-contract" text="Mortgage Contract" />
			<SideNavMenuItem href="/demos/bank-statement" text="Bank Statement" />
			<SideNavMenuItem href="/demos/tax-return" text="Tax Return" />
			<SideNavMenuItem href="/demos/salesforce-notes" text="Salesforce Notes" />
			<SideNavMenuItem href="/demos/call-transcript" text="Call Transcript" />
		</SideNavMenu>
	</SideNavItems>
</SideNav>

<Content>
	<Grid>
		<Row>
			<Column>
				<slot />
			</Column>
		</Row>
	</Grid>
</Content>
