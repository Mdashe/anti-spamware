<script>
	import Topbar from '../organisms/Topbar.svelte';
	import Sidebar from '../organisms/Sidebar.svelte';

	let {
		context = 'Inbox',
		activeItem = 'Overview',
		accountEmail = 'j.martin@gmail.com',
		userInitials = 'JM',
		children
	} = $props();
</script>

<div class="shell">
	<Topbar {context} {userInitials} />

	<div class="body">
		<Sidebar {activeItem} {accountEmail} />
		<main class="content">
			{@render children?.()}
		</main>
	</div>
</div>

<style>
	.shell {
		min-height: 100vh;
		background: var(--bg);
	}

	.body {
		display: flex;
		min-height: calc(100vh - 50px);
	}

	.content {
		flex: 1;
		padding: 18px 20px;
		min-width: 0;
	}
</style>
