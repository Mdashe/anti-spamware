<script>
	import Badge from '../atoms/Badge.svelte';

	/** @type {{
	 *   sender?: string;
	 *   subject?: string;
	 *   classification?: string;
	 *   tone?: 'fraud' | 'suspicious' | 'safe' | 'spam';
	 *   received?: string;
	 *   selected?: boolean;
	 *   onclick?: () => void;
	 * }} */
	let {
		sender = '',
		subject = '',
		classification = '',
		tone = 'safe',
		received = '',
		selected = false,
		onclick
	} = $props();

	/** @type {Record<string, string>} */
	const indicators = {
		fraud: '!',
		suspicious: '?',
		safe: '✓',
		spam: '·'
	};

	/** @type {Record<string, 'fraud' | 'suspicious' | 'safe' | 'spam'>} */
	const badgeVariant = {
		fraud: 'fraud',
		suspicious: 'suspicious',
		safe: 'safe',
		spam: 'spam'
	};
</script>

<button
	type="button"
	class="row {tone}"
	class:selected
	{onclick}
	aria-pressed={selected}
>
	<span class="indicator {tone}" aria-hidden="true">{indicators[tone]}</span>
	<span class="sender" class:emphasis={tone === 'fraud' || tone === 'suspicious'}>{sender}</span>
	<span class="subject">{subject}</span>
	<Badge variant={badgeVariant[tone]} label={classification} />
	<span class="received">{received}</span>
</button>

<style>
	.row {
		display: grid;
		grid-template-columns: 16px 1.3fr 1.6fr 0.9fr 0.6fr;
		gap: 10px;
		width: 100%;
		padding: 11px 14px;
		align-items: center;
		border: none;
		border-bottom: 1px solid var(--border);
		background: var(--surface);
		color: var(--text);
		text-align: left;
		cursor: pointer;
		font: inherit;
		font-size: 13px;
	}

	.row:last-child {
		border-bottom: none;
	}

	.row.fraud {
		background: var(--danger-soft);
		border-left: 2px solid var(--danger);
	}

	.row.suspicious {
		background: var(--warning-soft);
	}

	.row.selected {
		outline: 2px solid var(--primary);
		outline-offset: -2px;
	}

	.indicator {
		display: grid;
		place-items: center;
		font-size: 12px;
		font-weight: 700;
		line-height: 1;
	}

	.indicator.fraud {
		color: var(--danger);
	}

	.indicator.suspicious {
		color: var(--warning);
	}

	.indicator.safe {
		color: var(--safe);
	}

	.indicator.spam {
		color: var(--text-muted);
	}

	.sender.emphasis {
		font-weight: 500;
	}

	.row.spam .sender {
		color: var(--text-muted);
	}

	.subject {
		color: var(--text-muted);
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
	}

	.row.spam .subject {
		color: var(--text-soft);
	}

	.received {
		color: var(--text-soft);
		font-size: 11px;
	}
</style>
