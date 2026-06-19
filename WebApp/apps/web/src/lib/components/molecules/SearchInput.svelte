<script>
	let { placeholder = 'Search emails, senders, rules…' } = $props();
</script>

<div class="search" role="search">
	{placeholder}
</div>

<style>
	.search {
		width: 100%;
		max-width: 340px;
		background: var(--surface-muted);
		border: 1px solid var(--border);
		border-radius: var(--radius-md);
		padding: 7px 10px;
		color: var(--text-soft);
		font-size: 12px;
	}
</style>
