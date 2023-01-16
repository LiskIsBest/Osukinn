<script>
	import axios from "axios";
	import { createEventDispatcher } from "svelte";

	const dispatch = createEventDispatcher()

  let className = "";
  export { className as class };

  export let username_list;

	function endpoint(username) {
    return `${location.origin}/users/${username}`;
  }

	function refresh(){
		username_list.forEach(async (username) => {
			const response = await axios.put(endpoint(username))
			console.log(response.status)
		});
		dispatch("ResetUsers")
	}

</script>

<div>
	<button class={className} on:click={refresh}>Refresh Users</button>
</div>
