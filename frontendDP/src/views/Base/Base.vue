<template>
  <!-- 选择要操作的文件,即数据库 -->
  <el-row>
    <el-upload
        v-model:file-list="fileList"
        class="upload-demo"
        action="http://127.0.0.1:8000/fr/"
        show-file-list="false"
        :limit="1"
        :on-exceed="handleExceed"
        :on-success="uploadSuccess"
    >
      <el-button type="primary">Click to upload</el-button>
    </el-upload>
  </el-row>

  <el-row>
    <el-col :span="12" :offset="0">
      <el-table
          :data="tableData"
          :header-cell-style="headerCellStyle"
          :cell-style="cellStyle"
          v-fit-columns
          style="width: 100%; height: 350px">
        <el-table-column
            v-for="attr in attrOptions"
            :prop="attr"
            :label="attr"
            align="center"
            width="180">
        </el-table-column>
      </el-table>
    </el-col>

    <el-col :span="3" :offset="3" class="ParamsSelect">
      <el-input v-model="epsilonInput" size="large"  placeholder="Input epsilon"/>
      <el-input v-model="deltaInput" size="large"  placeholder="Input delta"/>
      <el-select v-model="selectedMechType" placeholder="Select mechanism type" size="large">
        <el-option key="numerical" label="数值型" value="numerical"/>
        <el-option key="nonnumerical" label="非数值型" value="nonnumerical"/>
      </el-select>
      <el-select v-model="selectedMech" placeholder="Select mechanism" size="large">
        <el-option key="Laplace" label="拉普拉斯机制" value="Laplace" v-if="selectedMechType === 'numerical'"/>
        <el-option key="Gaussian" label="高斯机制" value="Gaussian" v-if="selectedMechType === 'numerical'"/>
        <el-option key="Exponential" label="指数机制" value="Exponential" v-if="selectedMechType === 'nonnumerical'"/>
      </el-select>

      <el-select v-model="selectedWay" placeholder="Select Way" size="large">
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

      <el-select v-if="attrOptions.length !== 0"  v-model="selectedAttr" placeholder="Select Attribute" size="large" @change="changeHistogram">
        <el-option
            v-for="item in attrOptions"
            :key="item"
            :label="item"
            :value="item"
        />
      </el-select>
    </el-col>

  </el-row>

  <!--计数范围选择器  -->
  <div id="countScope" v-if="selectedWay === 'count'">
    <div class="slider">
      <el-slider v-model="sliderVal" range :min="0" :max="100"/>
    </div>
  </div>

  <el-row>
    <el-col :span="3" :offset="0">
      <el-button type="primary" @click="search" size="large">Search</el-button>
    </el-col>
  </el-row>



  <el-row id="output">
    <el-col :span="6">
      <span>真实值: {{searchRes.res}}</span>
    </el-col>
    <el-col :span="6" :offset="6">
      <span>隐私值: {{searchRes.privateRes}}</span>
    </el-col>
  </el-row>

  <svg id="histogram"  width="300" height="300"></svg>


</template>

<script>

import axios from "axios";
import * as d3 from 'd3';
import {ref} from "vue";
import {genFileId, UploadInstance} from "element-plus";

export default {
  name: 'Base',
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
      searchRes: {priavateRes: '', res: ''},
      tableData: [],
      attrOptions: [],  // 文件的列名数组
      numericalWayOptions: [{
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
      nonnumericalWayOptions: [{
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
    search() {
      if(this.curFile !== '') {
        axios({
          url: 'http://127.0.0.1:8000/baseDp/',
          method: 'post',
          data: {
            mechanismType: this.selectedMechType,
            mechanism: this.selectedMech,
            queryWay: this.selectedWay,
            mechParams: {
              scope: this.sliderVal,
              epsilon: parseFloat(this.epsilonInput),
              delta: parseFloat(this.deltaInput)
            },
            datafile: {
              filename: 'data/' + this.curFile,
              attr: this.selectedAttr,
            }

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
      this.tableData = response.tableData;
      console.log(response.tableData)
      // this.drawHistogram(dataset);

    },
    changeHistogram() {
      axios({
        url: 'http://127.0.0.1:8000/histogram/',
        method: 'post',
        data: {
          filename: 'data/' + this.curFile,
          attr: this.selectedAttr,
        }
      }).then((data) => {
        console.log(data.data.data)
        this.drawHistogram(data.data.data)
      })
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

      d3.selectAll('#histogram > *')
        .remove();

      svg.selectAll('rect')
          .data(dataset)
          .join("rect")
          .attr("y", d => y(d.height))
          .attr('height', d => h - padding - y(d.height))
          .attr("x", d => x(d.x0))
          .attr("width", d => x(d.x1) - x(d.x0)) //x.bandwidth()失效了
          .attr("fill", d => '#54a0ff')
          .attr("stroke", d => '#ffffff')
          .attr("stroke-width", 5);

      let xAxis = d3.axisBottom().scale(x);
      svg.append("g")
          .attr("class", "axis")
          .attr("transform", "translate(0," + (h - padding) + ")")
          .call(xAxis);

      let yAxis = d3.axisLeft().scale(y).ticks();
      svg.append("g")
          .attr("class", "axis")
          .attr("transform", "translate(" + (padding) + ",0)")
          .call(yAxis);
    },
    handleExceed(files) {
      const upload = ref<UploadUserFile>([]);
      upload.value.clearFiles()
      const file = files[0]
      file.uid = genFileId()
      upload.value.handleStart(file)
    },
    cellStyle({row, column, rowIndex, columnIndex}) {
      // if(column.label === this.modeColumnMap[this.mode]) {
      //   return {'background-color': '#ffdcdc'}
      // }
    },
    headerCellStyle({ row, column, rowIndex, columnIndex }) {
      if(column.label === this.selectedAttr) {
        return {'background-color': '#909399'}
      }
    }
  },
  mounted() {
  }
}
</script>



<style scoped>
.el-row {
  margin-top: 50px;
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
</style>
