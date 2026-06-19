<script>
	/** @type {'safe' | 'suspicious' | 'fraud' | 'spam' | 'primary'} */
	let { variant = 'safe', label = '' } = $props();
</script>

<span class="badge {variant}">{label}</span>

<style>
	.badge {
		display: inline-flex;
		align-items: center;
		border-radius: var(--radius-sm);
		padding: 2px 8px;
		font-size: 11px;
		font-weight: 500;
	}

	.safe {
		color: var(--safe);
		background: var(--safe-soft);
	}

	.suspicious {
		color: var(--warning);
		background: var(--warning-soft);
	}

	.fraud {
		color: var(--danger);
		background: var(--danger-soft);
	}

	.spam {
		color: var(--text-muted);
		background: var(--surface-muted);
	}

	.primary {
		color: var(--primary);
		background: var(--primary-soft);
	}
</style>
