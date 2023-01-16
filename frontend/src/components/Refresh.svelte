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
	
  // username_list = username_list.toString();
	// async function refresh(){
	// 	username_list.forEach(async (username) => {
	// 		const response = await fetch(endpoint(username));
  //     const data = await response.json();
	// 		userList.update(contents => [...contents, JSON.parse(data)])
	// 		userList.subscribe(value => {
	// 			user_data = value
	// 		})
	// 	});
	// }

	async function refresh(){
		username_list.forEach(async (username) => {
			let response = await axios.put(endpoint(username))
			console.log(JSON.parse(response.data))
		});
		userList.update(contents => [...contents])
	}
</script>

<div>
  <!-- <form class={className} method="get" action="/update">
    <button>refresh users</button>
    <input type="hidden" name="mode" id="mode" value={mode} />
    <input
      type="hidden"
      name="usernames"
      id="usernames"
      value={username_list}
    />
  </form> -->
	<button class={className} on:click={refresh}>Refresh Users</button>
</div>
