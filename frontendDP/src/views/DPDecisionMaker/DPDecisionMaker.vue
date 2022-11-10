<template>
  <el-row>
    <el-col :span=3>
      <span>Confidence value Input</span>
      <el-input v-model="CV_input" placeholder="Please input confidence value" />
    </el-col>
  </el-row>

  <el-row>
    <el-col>
      <svg id="LD" width="500" height="500"></svg>
    </el-col>
  </el-row>
  <!--暂时只考虑单区间  -->
  <el-row id="countScope">
    <div class="slider">
      <el-slider v-model="sliderVal" range show-stops :min="-10" :max="10"/>
    </div>
    <span>{{sliderVal}}</span>
  </el-row>
  <el-row>
    <el-col :offset="3">
      <el-button type="primary" @click="getEpsilon">Search</el-button>
    </el-col>
  </el-row>

  <el-col>
    <span>b = {{recommendEpsilon}}</span>
  </el-col>
</template>

<script>
import axios from "axios";
import * as d3 from 'd3';

export default {
  name: "DPDecisionMaker",
  data() {
    return {
      CV_input: 0.2,
      sliderVal: [-1, 2],
      recommendEpsilon: {num: 0, val: [], 'Epsilon': []},
      xScale: {},
      yScale: {},

    }
  },
  methods:{
    Laplace_f(x, b) {
      return 1 / (2 * b) * Math.exp(-Math.abs(x) / b)
    },
    getLapalceData(b) {
      let lineData = [];
      for(let i = -10; i <= 10; i += 0.1) {
        lineData.push([i, this.Laplace_f(i, b)])
      }
      return lineData;
    },
    drawLaplaceDistribution(b) {
      let svg = d3.select('#LD');
      let padding = 50, w = 500, h = 500;
      d3.selectAll('#LD > *').remove();  // 清空svg里的所有元素

      let lineData = this.getLapalceData(b);
      let x = this.xScale = d3.scaleLinear()
                              .domain([d3.min(lineData, d => d[0]), d3.max(lineData, d => d[0])])
                              .range([padding, w - padding])
                              .clamp(true);  //原因是定义域为止  暂时这么做为了保险
      let y = this.yScale = d3.scaleLinear()
          .domain([0, d3.max(lineData, d => d[1])])
          .range([h - padding, padding]);
      let cg = d3.line()
                 .x(d => x(d[0]))
                 .y(d => y(d[1]));

      let container = svg.append('g').attr('id', 'container');
      container.append('path')
              .attr('d', cg(lineData))
              .attr('stroke', 'gray')
              .attr('stroke-width', 2)
              .attr('fill', 'none');

      let xAxis = d3.axisBottom().scale(x);
      svg.append("g")
          .attr("class", "axis")
          .attr("transform", "translate(0," + (h - padding) + ")")
          .call(xAxis);

      svg.append("clipPath")
          .attr("id", "clip-th")
          .append("rect")
          .attr("x", x(this.sliderVal[0]))
          .attr("y", y(d3.max(lineData, d => d[1])))
          .attr("width", x(this.sliderVal[1]) - x(this.sliderVal[0]))
          .attr("height", h - 2 * padding)
          .attr("fill", 'blue');
      console.log(y)

      container.append("path")
          .attr("stroke", "grey")
          .attr('d', cg(lineData))
          .attr("fill", "yellowgreen")
          .attr("fill-opacity", 0.5)
          .attr("fill-rule", "evenodd")
          .attr('clip-path', "url(#clip-th)");

    },
    getEpsilon() {
      axios({
        url: 'http://127.0.0.1:8000/dpdc/',
        method: 'post',
        data: {
          'deviation': this.sliderVal,
          'confidenceVal': parseFloat(this.CV_input)
        }
      }).then((data) => {
        this.recommendEpsilon.num = data.data.num;
        this.recommendEpsilon.val = data.data.val;
        for (let i in this.recommendEpsilon.val) {
          this.recommendEpsilon.Epsilon[i] = 1 / this.recommendEpsilon.val[i];
        }
        console.log(this.recommendEpsilon)
      })
    }
  },
  watch: {
    sliderVal(newV) {
      let x = this.xScale;
      d3.select('#clip-th rect')
        .attr("x", x(newV[0]))
        .attr("width", x(newV[1]) - x(newV[0]));
    }
  },
  mounted() {
    this.drawLaplaceDistribution(1.0);
  }

}
</script>

<style scoped>
 .slider {
   width: 460px;

 }
</style>