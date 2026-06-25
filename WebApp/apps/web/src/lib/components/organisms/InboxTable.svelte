<script>
	import EmailRow from '../molecules/EmailRow.svelte';

	/** @type {{
	 *   emails?: import('$lib/data/inbox').InboxEmail[];
	 *   selectedId?: string | null;
	 *   onSelect?: (id: string) => void;
	 * }} */
	let { emails = [], selectedId = null, onSelect } = $props();
</script>

<section class="inbox">
	<div class="header">
		<span class="title">Inbox</span>
		<span class="sort">Sorted by risk</span>
	</div>

	<div class="table" role="table" aria-label="Inbox messages">
		<div class="columns" role="row">
			<span role="columnheader"></span>
			<span role="columnheader">Sender</span>
			<span role="columnheader">Subject</span>
			<span role="columnheader">Classification</span>
			<span role="columnheader">Received</span>
		</div>

		{#each emails as email (email.id)}
			<EmailRow
				sender={email.sender}
				subject={email.subject}
				classification={email.classification}
				tone={email.tone}
				received={email.received}
				selected={selectedId === email.id}
				onclick={() => onSelect?.(email.id)}
			/>
		{/each}
	</div>
</section>

<style>
	.inbox {
		flex: 1.6;
		min-width: 0;
	}

	.header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		margin-bottom: 8px;
	}

	.title {
		font-weight: 500;
		font-size: 13px;
	}

	.sort {
		color: var(--text-soft);
		font-size: 11px;
	}

	.table {
		background: var(--surface);
		border: 1px solid var(--border);
		border-radius: var(--radius-lg);
		overflow: hidden;
	}

	.columns {
		display: grid;
		grid-template-columns: 16px 1.3fr 1.6fr 0.9fr 0.6fr;
		gap: 10px;
		padding: 8px 14px;
		background: var(--surface-muted);
		border-bottom: 1px solid var(--border);
		font-size: 11px;
		color: var(--text-muted);
	}
</style>
