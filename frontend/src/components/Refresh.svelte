<script>
	import axios from "axios";
	import { createEventDispatcher } from "svelte";

	const dispatch = createEventDispatcher();

  export let username_list;

	function endpoint(username) {
    return `${location.origin}/users/${username}`;
	}

	function refresh(){
		let requests = [];
		username_list.forEach(async(username)=>{
			requests.push(axios.put(endpoint(username), {username: "updated"}))
		});

		axios.all(requests).then((responses) => {
			responses.forEach(async (resp) => {
				const data = await resp.data
				console.log(data)
			})
		}).finally(()=>{
			dispatch("ResetUsers");
		})
	}

</script>

<div class="d-flex row justify-content-center">
	<button class="col-2 text-center" on:click={refresh}>Refresh Users</button>
</div>
