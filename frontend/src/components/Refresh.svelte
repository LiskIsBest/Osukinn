<script>
  export let username_list;
  export let mode;

  username_list = username_list.toString();
</script>

<div>
  <form
    class="col-12 text-center"
    method="get"
    action="/update"
  >
    <button>refresh users</button>
    <input type="hidden" name="mode" id="mode" value={mode}/>
    <input type="hidden" name="usernames" id="usernames" value={username_list}/>
  </form>
</div>
