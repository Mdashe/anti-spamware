<script>
	import MetricCard from '../molecules/MetricCard.svelte';

	/** @type {{ label: string; value: string; tone?: 'default' | 'safe' | 'warning' | 'danger' }[]} */
	let {
		metrics = [
			{ label: 'Scanned today', value: '1,248' },
			{ label: 'Safe', value: '1,109', tone: 'safe' },
			{ label: 'Suspicious', value: '52', tone: 'warning' },
			{ label: 'Fraud detected', value: '7', tone: 'danger' },
			{ label: 'Rules active', value: '14' }
		]
	} = $props();
</script>

<section class="grid" aria-label="Overview metrics">
	{#each metrics as metric (metric.label)}
		<MetricCard {...metric} />
	{/each}
</section>

<style>
	.grid {
		display: grid;
		grid-template-columns: repeat(5, minmax(0, 1fr));
		gap: 10px;
	}
</style>
