<script lang="ts">
  import { onMount } from 'svelte';

  export let label: string;
  let count = 0;

  function increment(step: number): number {
    count += step;
    return count;
  }

  onMount(() => {
    increment(1);
  });
</script>

<button on:click={() => increment(2)}>
  {label}: {count}
</button>

<style>
  button { color: red; }
</style>
