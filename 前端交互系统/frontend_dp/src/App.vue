<template>
  <!-- 选择要操作的文件,即数据库 -->
  <el-upload
      v-model:file-list="fileList"
      class="upload-demo"
      action="http://127.0.0.1:8000/fr/"
      :limit="1"
      :on-success="uploadSuccess"
      style="margin-bottom: 50px"
  >
    <el-button type="primary">Click to upload</el-button>
  </el-upload>

  <!--  选择列名  -->
  <el-select v-if="attrOptions.length !== 0"  v-model="selectedAttr" placeholder="Select Attribute" size="large" style="margin-bottom: 50px">
    <el-option
        v-for="item in attrOptions"
        :key="item"
        :label="item"
        :value="item"
    />
  </el-select>

  <el-row>
    <span>epsilon</span>
    <el-input v-model="epsilonInput" placeholder="Please input" style="margin-bottom: 50px; width: 200px"/>
  </el-row>
  <!-- 数据库查询选择(获取统计数据) -->
  <el-row>
    <el-select v-model="selectedWay" placeholder="Select Way" size="large" style="margin-bottom: 50px">
      <el-option
          v-for="item in wayOptions"
          :key="item.value"
          :label="item.label"
          :value="item.value"
      />
    </el-select>

    <el-button type="primary" @click="search" size="large">搜索</el-button>
  </el-row>

  <!--计数范围选择器  -->
  <div id="countScope" v-if="selectedWay === 'count'">
    <div class="slider">
      <el-slider v-model="sliderVal" range :min="0" :max="100"/>
    </div>
  </div>

  <div id="output">
    <div>真实值: {{searchRes.res}}</div>
    <div>隐私值: {{searchRes.privateRes}}</div>
  </div>

  <svg id="histogram"  width="300" height="300"></svg>

  
</template>

<script>

import axios from "axios";
import * as d3 from 'd3';

export default {
  name: 'App',
  data() {
    return {
      fileList: [],
      selectedWay: '',
      selectedAttr: '',
      sliderVal:[0, 100],
      epsilonInput: "1.0",  //epsilon 输入值
      searchRes: {priavateRes: '', res: ''},
      attrOptions: [],  // 文件的列名数组
      wayOptions: [{
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
      },{
        value: 'min',
        label: '最小值'
      },{
        value: 'variance',
        label: '方差'
      },{
        value: 'stdev',
        label: '标准差'
      },{
        value: 'median',
        label: '中位数'
      },
      //   {
      //   value: 'percentile',
      //   label: '百分位数'
      // }
      ]
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
              attr: this.selectedAttr,
              way: this.selectedWay,
              params: {
                scope: this.sliderVal,
                epsilon: parseFloat(this.epsilonInput),
              }
            },

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

    uploadSuccess(response, file, fileList) {
      this.attrOptions = response.attr;
      console.log(response.data);

      let dataset = response.data;
      this.drawHistogram(dataset);

    },
    // 画直方图
    drawHistogram(dataset) {
      let svg = d3.select('#histogram');
      let w = parseInt(svg.attr("width")), h = parseInt(svg.attr("height"));
      let padding = 30;
      let x = d3.scaleLinear()
          .domain([d3.min(dataset, (d) => d.x0), d3.max(dataset, (d) => d.x1)])
          .range([padding, w - padding]);
      let y = d3.scaleLinear()
          .domain([0, d3.max(dataset, (d) => d.height)])
          .range([h - padding, padding]);

      svg.selectAll('rect')
         .remove();
      svg.selectAll('g')
          .remove();

      svg.selectAll('rect')
          .data(dataset)
          .join("rect")
          .attr("y", d => y(d.height))
          .attr('height', d => h - padding - y(d.height))
          .attr("x", d => x(d.x0))
          .attr("width", d => x(d.x1 - d.x0) - padding) //x.bandwidth()失效了
          .attr("fill", d => '#54a0ff')
          .attr("stroke", d => '#ffffff')
          .attr("stroke-width", 5);

      let xAxis = d3.axisBottom().scale(x);
      svg.append("g")
          .attr("class", "axis")
          .attr("transform", "translate(0," + (h - padding) + ")")
          .call(xAxis);

      let yAxis = d3.axisLeft().scale(y).ticks(10);
      svg.append("g")
          .attr("class", "axis")
          .attr("transform", "translate(" + (padding) + ",0)")
          .call(yAxis);
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
  #output {
    border: #aaaaaa solid 3px;
    width: 300px;
  }
</style>
