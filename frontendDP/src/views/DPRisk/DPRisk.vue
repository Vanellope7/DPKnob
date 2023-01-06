<template>
  <el-row style="background-color: #f5f5f5;" >
    <el-col :span="11" class="leftCol outerCol">
      <!-- 选择要操作的文件,即数据库 -->
      <el-row>
        <el-upload
            v-model:file-list="fileList"
            class="upload-demo"
            action="http://127.0.0.1:8000/fr/"
            :show-file-list="false"
            :limit="1"
            :on-success="uploadSuccess"
        >
          <el-button type="primary">Click to upload</el-button>
        </el-upload>
      </el-row>


      <el-row style="width: 100%;">
        <el-table
            :data="tableData"
            :header-cell-style="headerCellStyle"
            :cell-style="cellStyle"
            v-fit-columns
            style="width: 100%; height: 580px">
          <el-table-column
              v-for="attr in attrOptions"
              :prop="attr"
              :label="attr"
              align="center"
              width="180">
          </el-table-column>
        </el-table>
      </el-row>

    </el-col>

    <el-col :span="11" :offset="1" class="rightCol outerCol">
      <!--  识别并且调整唯一键属性    -->
      <el-row class="rightColRow">
        <el-transfer v-model="IdAttrs"
                     :data="NonIdAttrs"
                     :titles="['non-identifiable attributes', 'identifiable attributes']"
                     style="width: 100%"/>
      </el-row>

<!--      &lt;!&ndash;  检测风险人员    &ndash;&gt;-->
<!--      <el-row class="rightColRow">-->

<!--      </el-row>-->

      <!-- 选择攻击方式   -->
      <el-row class="rightColRow">

        <el-button type="primary" @click="detectRiskRecords">Detection risk records</el-button>

        <!--选择数值型 / 非数值型-->
        <el-col :span="3" :offset="1" class="ParamsSelect">
          <el-select v-model="selectedMechType" placeholder="Select mechanism type" size="large">
            <el-option key="numerical" label="数值型" value="numerical"/>
            <el-option key="nonnumerical" label="非数值型" value="nonnumerical"/>
          </el-select>
        </el-col>
        <!--   选择机制    -->
        <el-col :span="3" :offset="1" class="ParamsSelect">
          <el-select v-model="selectedMech" placeholder="Select mechanism" size="large">
            <el-option key="Laplace" label="拉普拉斯机制" value="Laplace" v-if="selectedMechType === 'numerical'"/>
            <el-option key="Gaussian" label="高斯机制" value="Gaussian" v-if="selectedMechType === 'numerical'"/>
            <el-option key="Exponential" label="指数机制" value="Exponential" v-if="selectedMechType === 'nonnumerical'"/>
          </el-select>
        </el-col>

        <!--   属性选择     -->
        <el-col :span="3" :offset="1" class="ParamsSelect">
          <el-select v-if="attrOptions.length !== 0"  v-model="selectedAttr" placeholder="Select Attribute" size="large">
            <el-option
                v-for="item in attrOptions"
                :key="item"
                :label="item"
                :value="item"
            />
          </el-select>
        </el-col>

        <!--  选择查询方式      -->
        <el-col :span="3" :offset="1" class="ParamsSelect">
          <el-select v-model="selectedWay" placeholder="Select Way" size="large" @change="selectQueryWay()">
            <el-option
                v-for="item in numericalWayOptions"
                :key="item.value"
                :label="item.label"
                :value="item.value"
                v-if="selectedMechType === 'numerical'"
            />
            <el-option
                v-for="item in nonnumericalWayOptions"
                :key="item.value"
                :label="item.label"
                :value="item.value"
                v-if="selectedMechType === 'nonnumerical'"
            />
          </el-select>
        </el-col>

        <!--计数范围选择器  -->
        <div id="countScope" v-if="selectedWay === 'count'">
          <div class="slider">
            <el-slider v-model="sliderVal" range :min="0" :max="100"/>
          </div>
        </div>
      </el-row>

      <!--  HOPs 呈现差分攻击结果  -->
      <el-row class="rightColRow">
        <el-col :span="7">
          <svg id="firstQueryHOPs" class="HOPs"></svg>
          <span class="HOPs_label">First DA query</span>
        </el-col>

        <el-col :span="7" :offset="1">
          <svg id="secondQueryHOPs" class="HOPs"></svg>
          <span class="HOPs_label">Second DA query</span>
        </el-col>

        <el-col :span="7" :offset="1">
          <svg id="privacyHOPs" class="HOPs"></svg>
          <span class="HOPs_label">DP outcome</span>
        </el-col>

        <span id="HOPs_title">Differencing attack simulation</span>




      </el-row>

    </el-col>
  </el-row>
</template>

<script>

import axios from "axios";
import * as d3 from 'd3';
import {ref} from "vue";
import {genFileId, UploadInstance} from "element-plus";

export default {
  name: 'DPRisk',
  data() {
    return {
      fileList: [],
      selectedWay: '',
      selectedAttr: '',
      sliderVal:[0, 100],
      epsilonInput: "",  //epsilon 输入值
      deltaInput: '0.0',
      selectedMechType: '',
      selectedMech: '',
      searchRes: {privateRes: '', res: ''},
      tableData: [],
      timer1: {},
      timer2: {},
      timer3: {},
      attrOptions: [],  // 文件的列名数组
      NonIdAttrs: [],
      IdAttrs: [],
      riskRecordId: [],


      numericalWayOptions: [
          {
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
      ],
      nonnumericalWayOptions: [
          {
          value: 'maxFrequency',
          label: '出现频率最高'
        },
        // {
        //   value: 'minFrequency',
        //   label: '出现频率最低'
        // },
        {
          value: 'maxUtilityPrice',
          label: '最大收益定价'
        },
        // {
        //   value: 'minUtility',
        //   label: '最小收益定价'
        // },

      ]
    }
  },
  computed: {
    curFile() {
      return this.fileList === [] ? '' : this.fileList[0].name;
    }
  },
  methods: {
    uploadSuccess(response, file, fileList) {
      this.attrOptions = response.attr;
      this.tableData = response.tableData;
      this.NonIdAttrs = response.attr.map((v, i) => {
        return {
          'key': i,
          'label': v
        }
      })
      console.log(response.tableData)
    },
    cellStyle({row, column, rowIndex, columnIndex}) {

    },
    headerCellStyle({ row, column, rowIndex, columnIndex }) {
      if(column.label === this.selectedAttr) {
        return {'background-color': 'rgb(224 234 255)'}
      }
    },
    drawHOPs(data, svg, timer, b) {
      // 初始化变量
      let privateRes = data['privateRes'], res = data['res'];
      const w = parseFloat(svg.style("width").substring(0, svg.style("width").indexOf('px')))
      const h = parseFloat(svg.style("height").substring(0, svg.style("height").indexOf('px')))
      const padding = 20;
      console.log(w, h)
      let xScale = d3.scaleLinear().domain([res - 500, res + 500]).range([padding, w - padding])
      let yScale = d3.scaleLinear().domain([0, this.LaplacePDF(b, 0)]).range([h - padding, 3 * padding])
      let xAxis = d3.axisBottom(xScale).ticks(5, ".1s");
      svg.append("g").attr("class", "axis").attr("transform", `translate(0, ${h - padding})`).call(xAxis);
      let baseLine = svg.append('line')
          .attr("class", 'baseLine')
          .attr("stroke", '#000000')
          .attr('x1', xScale(res))
          .attr('y1', h - padding)
          .attr('x2', xScale(res))
          .attr('y2', 3 * padding);
      let line = svg.append('line')
          .attr("class", 'HOPs-line')
          .attr("stroke", '#f0932b');

      // 保证timer 唯一
      clearInterval(timer);
      let timeIndex = 0;
      timer = setInterval(() => {
        line.attr('x1', xScale(privateRes[timeIndex]))
            .attr('y1', yScale(0))
            .attr('x2', xScale(privateRes[timeIndex]))
            .attr('y2', yScale(this.LaplacePDF(b, privateRes[timeIndex] - res)))
        timeIndex++;
        if(timeIndex === 950) { // 每次只获取1000个噪声数据，接近1000时准备重启HOPs，重新获取数据
          timeIndex = 0
          // this.restartHOPs();
        }
      }, 800);
      this.timer1 = timer; // 重定义,因为此时timer1的计时器已经清楚了
    },
    selectQueryWay() {
      axios({
        url: 'http://127.0.0.1:8000/DPRisk/getHOPsData/',
        method: 'post',
        data: {
          'filename': 'data/' + this.curFile,
          'way': this.selectedWay,
          'attr': this.selectedAttr,
          'privacy': 50,
          'mu': 0,
          'epsilon': 1.0,
        }
      }).then((data) => {
        console.log(data);
        let b = data.data['b'];
        let svg1 = d3.select('#firstQueryHOPs');
        this.drawHOPs(data.data['firstQuery'], svg1, this.timer1, b);

        let svg2 = d3.select('#secondQueryHOPs');
        this.drawHOPs(data.data['secondQuery'], svg2, this.timer2, b);

        let svg3 = d3.select('#privacyHOPs');
        this.drawHOPs(data.data['DA'], svg3, this.timer3, b);
      });

    },

    detectRiskRecords() {
      // 数值范围被设定为 1
      let gap = 1;
      // 检测单属性的唯一性
      axios({
        url: 'http://127.0.0.1:8000/DPRisk/testRisk/',
        method: 'post',
        data: {
          'filename': 'data/' + this.curFile,
          'gap': gap,
          'attrs': this.NonIdAttrs
        }
      }).then((data) => {

      })
    },
    LaplacePDF(b, x, mu = 0) { // 拉普拉斯概率密度函数
      return Math.exp(-Math.abs(x - mu) / b) / (2 * b)
    },
  },
  mounted() {

  }
}
</script>



<style scoped>
.outerCol {
  margin: 10px;
  padding: 10px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  align-items: center;

  border: solid 1px #333333;
}

.leftCol {
  padding-right: 5px;
}

.rightCol {
  padding-left: 10px;
}

.rightColRow {
  flex: 1;
  background-color: #ffffff;
  width: 100%;
  margin: 20px;
}

#output {
  border: #aaaaaa solid 3px;
  width: 600px;
}

.ParamsSelect{
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.HOPs {
  width: 100%;
  height: 100%;
}

#HOPs_title {
  position: absolute;
  right: 10px;
  top: 5px;
}

.HOPs_label {
  position: relative;
  left: 50px;
}

</style>

<style>
  .el-transfer-panel {
    width: 37% !important;
  }
  .el-transfer__buttons {
    width: 26% !important;
  }
  .el-transfer {
    height: 200px;
  }
  .el-transfer__button:nth-child(2) {
    margin-left: 20px;
  }
</style>