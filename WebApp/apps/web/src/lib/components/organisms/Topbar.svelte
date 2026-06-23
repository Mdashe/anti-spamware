<script>
	import SearchInput from '../molecules/SearchInput.svelte';
	import Badge from '../atoms/Badge.svelte';

	let {
		context = 'Inbox',
		userInitials = 'JM',
		connectionLabel = 'Gmail connected'
	} = $props();
</script>

<header class="topbar">
	<div class="brand">
		<div class="logo" aria-hidden="true">S</div>
		<strong>Signal</strong>
		<span>/ {context}</span>
	</div>

	<SearchInput />

	<div class="right">
		<Badge variant="safe" label={connectionLabel} />
		<div class="avatar" aria-label="User menu">{userInitials}</div>
	</div>
</header>

<style>
	.topbar {
		height: 50px;
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: var(--space-6);
		padding: 0 var(--space-4);
		background: var(--surface);
		border-bottom: 1px solid var(--border);
	}

	.brand,
	.right {
		display: flex;
		align-items: center;
		gap: 10px;
	}

	.brand span {
		color: var(--text-soft);
		font-size: 12px;
		font-weight: 400;
	}

	.brand strong {
		font-size: 13px;
		font-weight: 500;
	}

	.logo {
		width: 24px;
		height: 24px;
		border-radius: 7px;
		background: var(--primary);
		color: white;
		display: grid;
		place-items: center;
		font-size: 12px;
		font-weight: 600;
	}

	.avatar {
		width: 26px;
		height: 26px;
		border-radius: 999px;
		background: var(--primary-soft);
		color: var(--primary);
		display: grid;
		place-items: center;
		font-size: 11px;
		font-weight: 600;
	}
</style>
