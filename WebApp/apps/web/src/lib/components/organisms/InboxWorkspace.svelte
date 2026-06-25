<script>
	import InboxTable from './InboxTable.svelte';
	import ClassificationPanel from './ClassificationPanel.svelte';

	/** @type {{
	 *   emails?: import('$lib/data/inbox').InboxEmail[];
	 *   selectedId?: string | null;
	 *   onSelect?: (id: string) => void;
	 * }} */
	let { emails = [], selectedId = null, onSelect } = $props();

	const selected = $derived(emails.find((email) => email.id === selectedId) ?? emails[0]);
</script>

<div class="workspace">
	<InboxTable {emails} {selectedId} {onSelect} />

	{#if selected}
		<ClassificationPanel
			subject={selected.subject}
			sender={selected.sender}
			classification={selected.classification}
			tone={selected.tone}
			confidence={selected.confidence ?? 0}
			reasons={selected.reasons ?? []}
			rules={selected.rules ?? []}
		/>
	{/if}
</div>

<style>
	.workspace {
		display: flex;
		gap: 16px;
		margin-top: 18px;
	}
</style>
