<template >
  <Navbar />
  <InputForm />
</template>

<script>
import Navbar from './components/MainNavbar.vue'
import InputForm from './components/InputForm.vue'
import '../node_modules/bootstrap/dist/css/bootstrap.min.css'
export default {
  components :{
    Navbar,InputForm
  }
}
</script>