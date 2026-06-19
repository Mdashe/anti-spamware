<script>
	/** @type {'default' | 'safe' | 'warning' | 'danger'} */
	let { label = '', value = '', tone = 'default' } = $props();
</script>

<div class="card {tone}">
	<div class="label">{label}</div>
	<div class="value">{value}</div>
</div>

<style>
	.card {
		background: var(--surface);
		border: 1px solid var(--border);
		border-radius: var(--radius-lg);
		padding: 12px 14px;
	}

	.label {
		color: var(--text-muted);
		font-size: 11px;
		margin-bottom: 6px;
	}

	.value {
		font-size: 20px;
		font-weight: 500;
	}

	.safe .value {
		color: var(--safe);
	}

	.warning .value {
		color: var(--warning);
	}

	.danger {
		border-color: var(--danger);
	}

	.danger .label,
	.danger .value {
		color: var(--danger);
	}
</style>
