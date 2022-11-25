<template>
  <svg id="HOPs"></svg>
  <el-row>
    <el-slider v-model="b" :max="10" :step="0.1"/>
    <span class="demonstration">{{b}}</span>
  </el-row>
  <svg id="LaplaceDistribution"></svg>
</template>

<script>
import * as d3 from 'd3';
import axios from "axios";

  export default {
    name: "HOPs",
    data() {
      return {
        realVal: 120,
        gap: 20,
        b: 1.0,
        xScale: {},
        yScale: {},
        yAxis: {},

        timer: {},
        timeIndex: 0
      }
    },
    methods: {
      LaplacePDF(b, x, mu = 0) { // 拉普拉斯概率密度函数
        return Math.exp(-Math.abs(x - mu) / b) / (2 * b)
      },
      getLaplaceData(b) { // 获取拉普拉斯分布的数据
        let lineData = [];
        for(let i = -10; i <= 10; i += 0.02) {
          lineData.push([i, this.LaplacePDF(b, i)])
        }
        return lineData;
      },
      drawLaplaceDistribution(b) { // 绘制拉普拉斯分布图
        d3.selectAll('#LaplaceDistribution > *').remove();  // 清空svg里的所有元素
        let svg = d3.select('#LaplaceDistribution');
        let padding = 40, w = 500, h = 500;
        let lineData = this.getLaplaceData(b);
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
            .attr("class", "x axis")
            .attr("transform", `translate(0, ${h - padding})`)
            .call(xAxis);

        let yAxis = this.yAxis = d3.axisLeft().scale(y);
        svg.append("g")
            .attr("class", "y axis")
            .attr("transform", `translate(${padding}, 0)`)
            .call(yAxis);
      },
      restartHOPs() { // 重启HOPs动画
        const w = 500, h = 500, padding = 20;
        let xScale = d3.scaleLinear().domain([this.realVal - this.gap, this.realVal + this.gap]).range([padding, w - padding])
        let yScale = d3.scaleLinear().domain([0, this.LaplacePDF(this.b, 0)]).range([h - padding, padding])

        axios({
          url: 'http://127.0.0.1:8000/HOPs/',
          method: 'post',
          data: {
            'mu': 0,
            'b': this.b,
          }
        }).then((data) => {
          console.log(this.b)
          let noise = data.data['noise'];
          let line = d3.select("#HOPs-line")
          clearInterval(this.timer);
          this.timer = setInterval(() => {
            console.log('..')
            line.attr('x1', xScale(this.realVal + noise[this.timeIndex]))
                .attr('y1', yScale(0))
                .attr('x2', xScale(this.realVal + noise[this.timeIndex]))
                .attr('y2', yScale(this.LaplacePDF(this.b, noise[this.timeIndex])))
            this.timeIndex++;
            if(this.timeIndex === 950) { // 每次只获取1000个噪声数据，接近1000时准备重启HOPs，重新获取数据
              this.timeIndex = 0
              this.restartHOPs();
            }
          }, 800);
        })
      }

    },
    watch: {
      b(newB) { // 修改 b 时改变分布图效果以及HOPs动画效果
        let lineData = this.getLaplaceData(newB);
        let svg = d3.select('#LaplaceDistribution')
        let path = d3.select('#LaplaceDistribution #container path');
        let x = this.xScale, y = this.yScale;
        let cg = d3.line().x(d => x(d[0])).y(d => y(d[1]));
        path.transition()
            .delay(80)
            .duration(1000)
            .ease(d3.easeElasticOut)
            .attr('d', cg(lineData))

        y.domain([0, d3.max(lineData, d => d[1])])

        svg.select('.y.axis')
           .transition()
           .delay(80)
           .duration(1000)
           .call(this.yAxis)

        // 同时变化HOPs的分布
        this.restartHOPs();

      }
    },
    mounted() { //绘制分布图、 HOPs
      const w = 500, h = 500, padding = 20;
      let svg = d3.select('#HOPs');
      let xScale = d3.scaleLinear().domain([this.realVal - this.gap, this.realVal + this.gap]).range([padding, w - padding])
      let yScale = d3.scaleLinear().domain([0, this.LaplacePDF(this.b, 0)]).range([h - padding, padding])
      let xAxis = d3.axisBottom(xScale);
      svg.append("g").attr("class", "axis").attr("transform", `translate(0, ${h - padding})`).call(xAxis);
      let baseLine = svg.append('line')
                        .attr("id", 'baseLine')
                        .attr("stroke", '#000000')
                        .attr('x1', xScale(this.realVal))
                        .attr('y1', h - padding)
                        .attr('x2', xScale(this.realVal))
                        .attr('y2', padding);
      let line = svg.append('line')
                    .attr("id", 'HOPs-line')
                    .attr("stroke", '#f0932b');


      this.drawLaplaceDistribution(this.b)
      this.restartHOPs();
    }
  }
</script>

<style scoped>
  #HOPs {
    width: 500px;
    height: 500px;
  }
  #LaplaceDistribution {
    width: 500px;
    height: 500px;
  }
</style>