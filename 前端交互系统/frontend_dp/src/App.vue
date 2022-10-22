<template>
  <el-upload
      v-model:file-list="fileList"
      class="upload-demo"
      action="http://127.0.0.1:8000/fr/"
      :limit="1"
  >
    <el-button type="primary">Click to upload</el-button>
  </el-upload>

  <el-select v-model="selectVal" class="m-2" placeholder="Select" size="large" @change="changeSelect()">
    <el-option
        v-for="item in options"
        :key="item.value"
        :label="item.label"
        :value="item.value"
    />
  </el-select>

  <div id="countScope" v-if="selectVal === 'count'">
<!--    <el-select v-model="scopeDir" class="m-2" placeholder="Select" size="large" @change="changeSelect()">-->
<!--      <el-option :key="'>'" :label="'大于'" :value="'>'"/>-->
<!--      <el-option :key="'<'" :label="'小于'" :value="'<'"/>-->
<!--    </el-select>-->
          <!--用slider替代范围选择-->
    <div class="slider">
      <el-slider v-model="sliderVal" range :min="0" :max="100"/>
    </div>
  </div>
  <el-row>
    <el-button type="primary" @click="search">搜索</el-button>
  </el-row>

  <el-row>
    <div>真实值: {{searchRes.res}}</div>
  </el-row>
  <el-row>
    <div>隐私值: {{searchRes.privateRes}}</div>
  </el-row>
</template>

<script>

import axios from "axios";

export default {
  name: 'App',
  data() {
    return {
      fileList: [],
      selectVal: '',
      sliderVal:[0, 100],
      searchRes: {priavateRes: '', res: ''},
      options: [{
        value: 'sum',
        label: '求和'
      }, {
        value: 'mean',
        label: '均值'
      },{
        value: 'count',
        label: '计数'
      },{
        value: 'max',
        label: '最大值'
      }]
    }
  },
  computed: {
    curFile() {
      return this.fileList === [] ? '' : this.fileList[0].name;
    }
  },
  methods: {
    search() {
      if(this.curFile !== '') {
        axios({
          url: 'http://127.0.0.1:8000/baseDp/',
          method: 'post',
          data: {
            'mechanism': 'laplace',
            'searchWay': {
              way: this.selectVal,
              params: this.sliderVal
            },
            'epsilon': 1.0,
            'filename': this.curFile
          }
        }).then((data) => {
          this.searchRes = data.data;
        })
      }
      else {
        // 提示还未传输文件

      }
    },

    changeSelect() {
      console.log(this.selectVal)
    }
  },
  mounted() {
    // setTimeout(() => {
    //   console.log(this.fileList);
    // }, 10000)
  }
}
</script>

<style>

</style>
