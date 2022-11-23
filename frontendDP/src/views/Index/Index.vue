<template>
  <el-menu
      :default-active="activeIndex2"
      class="el-menu-demo"
      mode="horizontal"
      background-color="#545c64"
      text-color="#fff"
      active-text-color="#ffd04b"
      @select="handleSelect"
  >
    <el-menu-item index="1">
      <router-link to="/Base">BaseDp</router-link>
    </el-menu-item>
    <el-menu-item index="2">
      <router-link to="/DC">DPDecisionMaker</router-link>
    </el-menu-item>
    <el-menu-item index="3">
      <router-link to="/HOPs">HOPs</router-link>
    </el-menu-item>
  </el-menu>

  <router-view/>
</template>

<script>
  export default {
    name: "Index",
  }
</script>

<style scoped>

</style>