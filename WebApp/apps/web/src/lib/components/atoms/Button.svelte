<script>
	/** @type {'secondary' | 'primary' | 'danger'} */
	let { variant = 'secondary', children } = $props();
</script>

<button class="button {variant}" type="button">
	{@render children?.()}
</button>

<style>
	.button {
		border: 1px solid var(--border);
		border-radius: var(--radius-md);
		padding: 8px 12px;
		background: var(--surface);
		color: var(--text);
		cursor: pointer;
		font-size: 12px;
		font-weight: 500;
	}

	.primary {
		background: var(--primary);
		color: white;
		border-color: var(--primary);
	}

	.danger {
		background: var(--danger);
		color: white;
		border-color: var(--danger);
	}
</style>
