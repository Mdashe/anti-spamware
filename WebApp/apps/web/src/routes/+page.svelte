<script>
	import DashboardShell from '$lib/components/templates/DashboardShell.svelte';
	import MetricGrid from '$lib/components/organisms/MetricGrid.svelte';
	import InboxWorkspace from '$lib/components/organisms/InboxWorkspace.svelte';
	import { inboxEmails } from '$lib/data/inbox.js';

	let selectedId = $state(inboxEmails[0]?.id ?? null);

	function selectEmail(id) {
		selectedId = id;
	}
</script>

<svelte:head>
	<title>Signal — Inbox</title>
</svelte:head>

<DashboardShell context="Inbox" activeItem="Overview">
	<MetricGrid />
	<InboxWorkspace emails={inboxEmails} {selectedId} onSelect={selectEmail} />
</DashboardShell>
