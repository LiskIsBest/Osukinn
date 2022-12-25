<script>
  import {onMount} from "svelte";

  export let username_list;

  export let mode;

  let className = ''
  export { className as class}

  function addCommas(number){
    if(number == 9_999_999_999){
        return "No Rank"
    }
    const numFor = Intl.NumberFormat("en-US");
    const numWithCommas = numFor.format(number)
    return numWithCommas
  }

  function endpoint(username){
    return `${location.origin}/users/${username}`
  }

  let user_data = [];

  onMount(async function(){
    username_list.forEach(async (username)=>{
      console.log(`fetching data for user:${username}`)
      const response = await fetch(endpoint(username));
      const data = await response.json();
      user_data.push(data);
      user_data = user_data;
    })
  })

</script>

{#each user_data as user}
<div class="{className}">
  <h2 class="text-center">{user.username}</h2>
  <a href="https://osu.ppy.sh/users/{user._id}" target="_blank" rel="noreferrer">
    <img
      src={user.avatar_url}
      class="rounded mx-auto d-block"
      alt=""
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
