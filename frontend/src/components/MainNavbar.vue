<template>
<nav class="navbar bg-body-tertiary bg-blue-grey-darken-4 d-flex">
  <div class="container-fluid flex-nowrap">
    <a class="navbar-brand ms-5 text-white pa-5" href="#">
      SPOTI-TUBE
    </a>
    <form @submit.prevent="" class="d-flex ms-auto me-5" role="search">
      <input class="form-control me-2" type="search" placeholder="Search" aria-label="Search">
      <button class="btn text-white bg-blue-grey-darken-1" type="submit">Search</button>
    </form>
  </div>
</nav>
</template>

<script>
export default {
  
}
</script>

<style scoped>
.navbar{
  box-shadow: 0px 0px 10px rgba(0,0,0,0.8) !important;
}
</style>