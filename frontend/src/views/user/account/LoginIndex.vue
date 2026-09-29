<script setup>

</script>

<template>
  <div class="flex justify-center mt-35">
    <fieldset class="fieldset bg-base-200 border-base-300 rounded-box w-xs border p-4">

      <label class="label">用户名</label>
      <input type="text" class="input" placeholder="用户名" />

      <label class="label">密码</label>
      <input type="password" class="input" placeholder="密码" />

      <button class="btn btn-neutral mt-4">登录</button>

      <div class="flex justify-end">
        <RouterLink :to="{name: 'user-account-register-index'}" class="btn btn-small btn-ghost text-gray-300">
          注册
        </RouterLink>
      </div>

    </fieldset>
  </div>
</template>

<style scoped>

</style>
