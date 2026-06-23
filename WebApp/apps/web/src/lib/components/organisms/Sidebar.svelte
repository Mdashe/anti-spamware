<script>
	import NavItem from '../molecules/NavItem.svelte';

	let {
		activeItem = 'Overview',
		accountEmail = 'j.martin@gmail.com',
		priorityCount = '7'
	} = $props();
</script>

<aside class="sidebar">
	<div class="section">Workspace</div>
	<NavItem label="Overview" active={activeItem === 'Overview'} />
	<NavItem label="All mail" active={activeItem === 'All mail'} />
	<NavItem label="Priority review" count={priorityCount} active={activeItem === 'Priority review'} />
	<NavItem label="Rules" active={activeItem === 'Rules'} />
	<NavItem label="Patterns" active={activeItem === 'Patterns'} />

	<div class="section">Accounts</div>
	<NavItem label={accountEmail} active={activeItem === accountEmail} />
	<NavItem label="Connect account" active={activeItem === 'Connect account'} />

	<div class="spacer"></div>

	<div class="footer">
		<NavItem label="Settings" active={activeItem === 'Settings'} />
	</div>
</aside>

<style>
	.sidebar {
		width: 220px;
		background: var(--surface);
		border-right: 1px solid var(--border);
		padding: var(--space-4) 10px;
		display: flex;
		flex-direction: column;
		gap: 2px;
	}

	.section {
		padding: 0 8px 10px;
		margin-top: 8px;
		color: var(--text-soft);
		font-size: 11px;
		font-weight: 600;
		text-transform: uppercase;
		letter-spacing: 0.04em;
	}

	.section:first-child {
		margin-top: 0;
	}

	.spacer {
		flex: 1;
	}

	.footer {
		border-top: 1px solid var(--border);
		margin-top: 8px;
		padding-top: 8px;
	}
</style>
