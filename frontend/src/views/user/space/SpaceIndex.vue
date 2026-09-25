<script setup>
import {useRoute,useRouter} from "vue-router";

const  route = useRoute()


</script>

<template>
  <div>个人空间:{{ route.params.user_id}}</div>
</template>

<style scoped>

</style>
