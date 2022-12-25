<script>
  import User from "./User.svelte";
  import Refresh from "./Refresh.svelte";

  const queryString = window.location.search;
  const urlParams = new URLSearchParams(queryString);
  let usernames = urlParams.get("usernames");
  let mode = urlParams.get("mode");
  
  if(usernames == null || usernames == ""){
    usernames = "None";
  }
  if(mode == null || usernames == ""){
    mode="mania";
  }

  let username_list = usernames.split(",");
  username_list = username_list.map(username => username.trim());
</script>

<main>

<body>

  <div class="row d-flex">
    <form class="col-12 text-center" method="get" action="/">
      <label for="usernames">Enter usernames (ex: username1, username2, etc..) </label> <br />
      <div class="d-inline-flex">
        <select name="mode">
          <option value="mania" >Mania</option>
          <option value="osu" >Standard</option>
          <option value="taiko">Taiko</option>
          <option value="fruits">Ctb</option>
          <option value="all">All</option>
        </select>
        <input type="hidden" id="mode">
        <input type="text" id="usernames" name="usernames"><br />
      </div>
    </form>
  </div>

  <div class="d-flex row justify-content-center border border-secondary">
    <h1 class="text-center">User</h1>
    <User class="col-md-6 col-sm-6 col-lg-3 border border-primary" username_list={username_list} mode={mode}/>
  </div>

  <Refresh username_list={username_list} mode={mode}/>

  <div class="col-12 row d-flex">
    <h3 class="text-center">Work in progress</h3>
  </div>
  <div class="col-12 row d-flex">
    <ul class="text-center">
      <li>Mode selector: choose which gamemode to use when showing rank.</li>
      <li>The "all" gamemode option lists all ranks for each gamemode per player.</li>
      <li>If any other gamemode is selected with more than one user entered, the highest ranked user will be shown above the others.</li>
      <li>Text box: enter Osu! profile usernames seperated by commas. EX: "jakads, whitecat"</li>
      <li>Refresh button: refreshes data for each user listed.</li>
    </ul>
  </div>
</body>

</main>

<style>
</style>
