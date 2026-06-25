<script>
	import Badge from '../atoms/Badge.svelte';
	import Button from '../atoms/Button.svelte';

	/** @type {{
	 *   subject?: string;
	 *   sender?: string;
	 *   classification?: string;
	 *   tone?: 'fraud' | 'suspicious' | 'safe' | 'spam';
	 *   confidence?: number;
	 *   reasons?: string[];
	 *   rules?: string[];
	 * }} */
	let {
		subject = '',
		sender = '',
		classification = '',
		tone = 'fraud',
		confidence = 0,
		reasons = [],
		rules = []
	} = $props();

	/** @type {Record<string, 'fraud' | 'suspicious' | 'safe' | 'spam'>} */
	const badgeVariant = {
		fraud: 'fraud',
		suspicious: 'suspicious',
		safe: 'safe',
		spam: 'spam'
	};
</script>

<section class="panel">
	<h2 class="heading">Why this was flagged</h2>

	<div class="card {tone}">
		<div class="summary">
			<div>
				<div class="subject">{subject}</div>
				<div class="sender">from {sender}</div>
			</div>
			<Badge variant={badgeVariant[tone]} label="{classification} · {confidence}%" />
		</div>

		{#if reasons.length}
			<div class="block">
				<div class="label">Reasons</div>
				<ul class="list">
					{#each reasons as reason}
						<li>{reason}</li>
					{/each}
				</ul>
			</div>
		{/if}

		{#if rules.length}
			<div class="block">
				<div class="label">Matching rules</div>
				{#each rules as rule}
					<div class="rule">{rule}</div>
				{/each}
			</div>
		{/if}

		<div class="actions">
			<Button variant="danger">Report & delete</Button>
			<Button variant="secondary">Mark safe</Button>
		</div>
	</div>
</section>

<style>
	.panel {
		flex: 1;
		min-width: 0;
	}

	.heading {
		font-weight: 500;
		font-size: 13px;
		margin: 0 0 8px;
	}

	.card {
		background: var(--surface);
		border: 1px solid var(--border);
		border-radius: var(--radius-lg);
		padding: 14px;
	}

	.card.fraud {
		border-color: var(--danger);
	}

	.card.suspicious {
		border-color: var(--warning);
	}

	.summary {
		display: flex;
		align-items: flex-start;
		justify-content: space-between;
		gap: 12px;
		margin-bottom: 10px;
	}

	.subject {
		font-weight: 500;
		font-size: 13px;
	}

	.sender {
		color: var(--text-soft);
		font-size: 11px;
		margin-top: 2px;
	}

	.block {
		border-top: 1px solid var(--border);
		padding-top: 10px;
		margin-top: 10px;
	}

	.label {
		color: var(--text-muted);
		font-size: 11px;
		font-weight: 500;
		margin-bottom: 6px;
	}

	.list {
		margin: 0;
		padding: 0;
		list-style: none;
	}

	.list li {
		display: flex;
		gap: 6px;
		align-items: flex-start;
		font-size: 12px;
		margin-bottom: 6px;
	}

	.list li::before {
		content: '•';
		color: var(--danger);
		font-size: 10px;
		line-height: 1.6;
	}

	.card.suspicious .list li::before {
		color: var(--warning);
	}

	.card.safe .list li::before,
	.card.spam .list li::before {
		color: var(--text-muted);
	}

	.rule {
		display: inline-flex;
		align-items: center;
		background: var(--surface-muted);
		padding: 5px 9px;
		border-radius: var(--radius-sm);
		font-size: 12px;
	}

	.actions {
		display: flex;
		gap: 8px;
		margin-top: 14px;
	}

	.actions :global(.button) {
		flex: 1;
	}
</style>
