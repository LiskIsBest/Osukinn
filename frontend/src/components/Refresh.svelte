<script>
	import axios from "axios";
	import { createEventDispatcher } from "svelte";

	const dispatch = createEventDispatcher();

  export let username_list;

	function endpoint(username) {
    return `${location.origin}/users/${username}`;
  }

	function refresh(){
		username_list.forEach(async (username) => {
			const response = await axios.put(endpoint(username));
			const data = await JSON.parse(response.data.toString());
			console.log(data);
		});
		dispatch("ResetUsers");
	}

</script>

<div class="d-flex row justify-content-center">
	<button class="col-2 text-center" on:click={refresh}>Refresh Users</button>
</div>
