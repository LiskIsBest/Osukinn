<script>
	import axios from "axios";
	import { createEventDispatcher } from "svelte";

	const dispatch = createEventDispatcher();

  export let username_list;

	function endpoint(username) {
    return `${location.origin}/users/${username}`;
  }

	function makeRequests(username_list){
		let requests = [];
		username_list.forEach(async(username)=>{
			requests.push(axios.put(endpoint(username), {username: "updated"}))
		});
		return requests
	}

	function refresh(){
		axios.all(makeRequests(username_list)).then((responses) => {
			responses.forEach((resp) => {
				console.log(resp.data)
			})
		}).finally(()=>{
			dispatch("ResetUsers");
		})
	}

</script>

<div class="d-flex row justify-content-center">
	<button class="col-2 text-center" on:click={refresh}>Refresh Users</button>
</div>
