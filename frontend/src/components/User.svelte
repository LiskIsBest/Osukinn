<script>
  import { onMount } from "svelte";
  import axios from "axios";

  export let username_list;
  export let mode;
  let className = "";
  export { className as class };

	const valid_modes = ["mania","osu","taiko","fruits"]

  function addCommas(number) {
    if (number == 9_999_999_999) {
      return "No Rank";
    }
    const numFor = Intl.NumberFormat("en-US");
    const numWithCommas = numFor.format(number);
    return numWithCommas;
  }

  function endpoint(username) {
    return `${location.origin}/users/${username}`;
  }

  let user_data = [];

  onMount(function () {
    let requests = [];

    username_list.forEach(async (username) => {
      requests.push(axios.get(endpoint(username)));
    });

    axios
      .all(requests)
      .then((responses) => {
        responses.forEach(async (resp) => {
          const data = await JSON.parse(resp.data);
          user_data.push(data);
        });
      })
      .finally(() => {
				if (valid_modes.includes(mode)){
					user_data.sort((a,b) => a[`${mode}_rank`] - b[`${mode}_rank`])
				}
        user_data = user_data;
      });
  });
</script>

{#each user_data as user}
  <div class={className}>
    <h2 class="text-center">{user.username}</h2>
    <a
      href="https://osu.ppy.sh/users/{user.public_id}"
      target="_blank"
      rel="noreferrer"
    >
      <img
        src={user.avatar_url}
        class="rounded mx-auto d-block"
        alt="User profile pitcure"
        width="200px"
        height="200px"
      />
    </a>
    {#if mode == "mania"}
      <p class="text-center">Mania rank: {addCommas(user.mania_rank)}</p>
    {:else if mode == "osu"}
      <p class="text-center">Standard rank: {addCommas(user.osu_rank)}</p>
    {:else if mode == "taiko"}
      <p class="text-center">Taiko rank: {addCommas(user.taiko_rank)}</p>
    {:else if mode == "fruits"}
      <p class="text-center">Ctb rank: {addCommas(user.fruits_rank)}</p>
    {:else}
      <p class="text-center">Mania rank: {addCommas(user.mania_rank)}</p>
      <p class="text-center">Standard rank: {addCommas(user.osu_rank)}</p>
      <p class="text-center">Taiko rank: {addCommas(user.taiko_rank)}</p>
      <p class="text-center">Ctb rank: {addCommas(user.fruits_rank)}</p>
    {/if}
    <p class="text-center">Last queried(UTC): {user.last_time_refreshed}</p>
  </div>
{/each}
