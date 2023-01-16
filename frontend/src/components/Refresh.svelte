<script>
	import { userList } from "../stores";
	import axios from "axios";
  import User from "./User.svelte";

  let className = "";
  export { className as class };

  export let username_list;
  // export let mode;

	function endpoint(username) {
    return `${location.origin}/users/${username}`;
  }
	async function refresh(){
		username_list.forEach(async (username) => {
			let response = await axios.put(endpoint(username))
			console.log(JSON.parse(response.data))
		});
		userList.update(contents => [...contents])
	}
</script>

<div>
	<button class={className} on:click={refresh}>Refresh Users</button>
</div>
