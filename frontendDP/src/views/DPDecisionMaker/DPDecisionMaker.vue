<template>
  <el-row>
    <el-col :span=2>
      <span style="line-height: 30px">MODE</span>
    </el-col>

    <el-radio-group v-model="mode">
      <el-radio-button label="noise search" />
      <el-radio-button label="fine-tune &epsilon;" />
      <el-radio-button label="privacy search" />
    </el-radio-group>

  </el-row>

  <el-row>
    <el-table :data="tableData" style="width: 600px" :cell-style="cellStyle">
      <el-table-column prop="ncv" label="noise confidence value" width="200px"/>
      <el-table-column prop="b" label="b" width="200px" />
      <el-table-column prop="pcv" label="privacy confidence value" width="200px"/>
    </el-table>
  </el-row>

  <el-row>
    <el-col :span=3 v-if="mode !== 'fine-tune &epsilon;'">
      <span>Confidence value Input</span>
      <el-input v-model="ncv" v-show="mode === 'noise search'"/>
      <el-input v-model="pcv" v-show="mode === 'privacy search'"/>
    </el-col>

    <el-col :span=12>
      <el-row id="epsilonScope" class="noMarginRow" v-if="mode === 'fine-tune &epsilon;'">
        <span style="margin-right: 30px">b区间</span>
        <div class="slider">
          <el-slider v-model="b" show-stops :min="0" :max="10" step="0.1"/>
        </div>
        <span>{{b}}</span>
      </el-row>

      <el-row id="countScope" class="noMarginRow">
        <span>准确度区间</span>
        <div class="slider">
          <el-slider v-model="accuracyScope" range show-stops :min="-10" :max="10"/>
        </div>
        <span>{{accuracyScope}}</span>
      </el-row>

      <el-row id="privacyScope" class="noMarginRow">
        <span>隐私暴露区间</span>
        <div class="slider">
          <el-slider v-model="privacyScope" range show-stops :min="-10" :max="10"/>
        </div>
        <span>{{privacyScope}}</span>
      </el-row>
    </el-col>
  </el-row>



  <el-row>
    <el-col :span="6">
      <svg id="LD" width="300" height="300"></svg>
    </el-col>

    <el-col :offset="3" :span="3" style="margin-top: 120px">
      <el-button type="primary" @click="getEpsilon">Search</el-button>
    </el-col>

    <span>{{recommendEpsilon}}</span>
  </el-row>

</template>

<script>
import axios from "axios";
import * as d3 from 'd3';

export default {
  name: "DPDecisionMaker",
  data() {
    return {
      accuracyScope: [-1, 2],
      privacyScope: [-1, 2],
      recommendEpsilon: {},
      xScale: {},
      yScale: {},

      ncv: 0.2,
      b: 1.0,
      pcv: 0.9,
      mode: 'noise search',
      tableData: [{
        'ncv': 0.2,
        'b': 1.0,
        'pcv': 0.9
      }],
      modeColumnMap: {
        'noise search': 'noise confidence value',
        'privacy search': 'privacy confidence value',
        'fine-tune ε': 'b',
      }
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
      let padding = 50, w = svg.attr("width"), h = svg.attr("height");
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
          .attr("id", "clip-th-accuracy")
          .append("rect")
          .attr("x", x(this.accuracyScope[0]))
          .attr("y", y(d3.max(lineData, d => d[1])))
          .attr("width", x(this.accuracyScope[1]) - x(this.accuracyScope[0]))
          .attr("height", h - 2 * padding);

      container.append("path")
          .attr("stroke", "grey")
          .attr('d', cg(lineData))
          .attr("fill", "yellowgreen")
          .attr("fill-opacity", 0.5)
          .attr("fill-rule", "evenodd")
          .attr('clip-path', "url(#clip-th-accuracy)");

      svg.append("clipPath")
          .attr("id", "clip-th-privacy")
          .append("rect")
          .attr("x", x(this.privacyScope[0]))
          .attr("y", y(d3.max(lineData, d => d[1])))
          .attr("width", x(this.privacyScope[1]) - x(this.privacyScope[0]))
          .attr("height", h - 2 * padding);

      container.append("path")
          .attr("stroke", "grey")
          .attr('d', cg(lineData))
          .attr("fill", "red")
          .attr("fill-opacity", 0.5)
          .attr("fill-rule", "evenodd")
          .attr('clip-path', "url(#clip-th-privacy)");

    },
    getEpsilon() {
      axios({
        url: 'http://127.0.0.1:8000/dpdc/',
        method: 'post',
        data: {
          'mode': this.mode,
          'deviation': this.accuracyScope,
          'privacyScope': this.privacyScope,
          'confidenceVal': this.mode === 'noise search' ? parseFloat(this.ncv) : parseFloat(this.pcv)
        }
      }).then((data) => {
        this.recommendEpsilon = data.data;
        console.log(data.data)
      })
    },
    cellStyle({row, column, rowIndex, columnIndex}) {
      let cellStyle = {
        style: {
          background: "#ffdcdc"
        }
      }
      if(column.label === this.modeColumnMap[this.mode]) {
        return {'background-color': '#ffdcdc'}
      }
    },
    getNCV(b) {
      let [m, n] = this.accuracyScope;
      let pm = 1 / 2 + Math.sign(m) / 2 * (1 - Math.exp(-Math.abs(m) / b));
      let pn = 1 / 2 + Math.sign(n) / 2 * (1 - Math.exp(-Math.abs(n) / b));
      return (pn - pm).toFixed(5);
    },
    getPCV(b) {
      let [m, n] = this.privacyScope;
      let pm = 1 / 2 + Math.sign(m) / 2 * (1 - Math.exp(-Math.abs(m) / b)) - m / (4 * b) * Math.exp(-Math.abs(m) / b);
      let pn = 1 / 2 + Math.sign(n) / 2 * (1 - Math.exp(-Math.abs(n) / b)) - n / (4 * b) * Math.exp(-Math.abs(n) / b);
      return (pn - pm).toFixed(5);
    }
  },
  watch: {
    accuracyScope(newV) {
      let x = this.xScale;
      d3.select('#clip-th-accuracy rect')
        .attr("x", x(newV[0]))
        .attr("width", x(newV[1]) - x(newV[0]));
    },
    privacyScope(newV) {
      let x = this.xScale;
      d3.select('#clip-th-privacy rect')
          .attr("x", x(newV[0]))
          .attr("width", x(newV[1]) - x(newV[0]));
    },
    ncv(newV) {
      this.tableData[0].ncv = newV;
    },
    b(newV) {
      this.tableData[0].b = newV;
      if(this.mode === 'fine-tune ε') {
        console.log('xxxx')
        this.ncv = this.getNCV(newV);
        this.pcv = this.getPCV(newV);
      }
    },
    pcv(newV) {
      this.tableData[0].pcv = newV;
    }
  },
  mounted() {
    this.drawLaplaceDistribution(1.0);
  }

}
</script>

<style scoped>
  .el-row {
    margin: 20px;
  }
  .noMarginRow {
    margin: 0 !important;
  }
 .slider {
   width: 460px;
 }
  .chosen {
    background-color: red;
  }
</style>