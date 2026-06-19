<script>
	let { label = '', active = false, count = null } = $props();
</script>

<div class="nav-item" class:active>
	<span>{label}</span>
	{#if count}
		<span class="count">{count}</span>
	{/if}
</div>

<style>
	.nav-item {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 7px 8px;
		border-radius: var(--radius-md);
		color: var(--text-muted);
		font-size: 13px;
		cursor: pointer;
	}

	.active {
		color: var(--primary);
		background: var(--primary-soft);
		font-weight: 500;
	}

	.count {
		background: var(--danger-soft);
		color: var(--danger);
		border-radius: 999px;
		padding: 1px 6px;
		font-size: 10px;
		font-weight: 500;
	}
</style>
