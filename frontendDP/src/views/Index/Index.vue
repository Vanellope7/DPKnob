<template>
  <el-menu
      class="el-menu-demo"
      mode="horizontal"
      background-color="#545c64"
      text-color="#fff"
      active-text-color="#ffd04b"
  >
    <el-menu-item index="1">
      <router-link to="/Base">BaseDp</router-link>
    </el-menu-item>
    <el-menu-item index="2">
      <router-link to="/DPRisk">DPRisk</router-link>
    </el-menu-item>
    <el-menu-item index="3">
      <router-link to="/DC">DPDecisionMaker</router-link>
    </el-menu-item>
    <el-menu-item index="4">
      <router-link to="/HOPs">HOPs</router-link>
    </el-menu-item>
    <el-menu-item index="5">
      <router-link to="/Tree">Tree</router-link>
    </el-menu-item>
    <el-menu-item index="6">
      <router-link to="/Main">Main</router-link>
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