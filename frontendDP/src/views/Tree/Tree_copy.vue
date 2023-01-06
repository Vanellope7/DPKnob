<template>
  <el-row>
    <el-upload
        v-model:file-list="fileList"
        class="upload-demo"
        action="http://127.0.0.1:8000/RiskTree/FileReceive/"
        show-file-list="false"
        :limit="1"
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
          :row-syule="rowStyle"
          v-fit-columns
          style="width: 100%; height: 200px">
        <el-table-column
            v-for="attr in attrOptions"
            :prop="attr"
            :label="attr"
            align="center"
            width="100">
        </el-table-column>
      </el-table>
    </el-col>
  </el-row>

<!--  <div>-->
<!--    <el-checkbox-group v-model="nonIdentifiableAttrs" size="large">-->
<!--      <el-checkbox-button v-for="attr in attrOptions" :key="attr" :label="attr">-->
<!--        {{ attr }}-->
<!--      </el-checkbox-button>-->
<!--    </el-checkbox-group>-->
<!--  </div>-->

  <!-- 属性选择模块 -->
  <el-row>
   <el-col :span="12">

      <el-transfer v-model="NonIdAttrs"
                   :data="transferData"
                   :titles="['Identifiable attributes', 'Non-Identifiable attributes']"
                   style="width: 100%"/>
   </el-col>
  </el-row>
  <el-button type="primary" @click="getSelectedAttrInfo">Confirm</el-button>


  <el-row>
   <el-col :span="10">
     <el-table
         :data="attrList"
         v-fit-columns
         style="width: 100%; height: 200px">
       <el-table-column
           v-for="attr in attrListColumn"
           :prop="attr"
           :label="attr"
           align="center"
           width="120">
       </el-table-column>
      <!--    操作列   -->
       <el-table-column fixed="right" label="Operations" width="120" v-if="attrListColumn.length">
         <template #default="scope">
           <el-button link type="primary" size="small" @click="EditProp(scope.$index)">Edit</el-button>
         </template>
       </el-table-column>
     </el-table>
   </el-col>

    <el-col :span="2" v-show="showEditBar">
      <!-- fine-tune component -->
      <div>搜索最小宽度：{{formatTooltip(widthSliderVal)}}</div>
      <el-slider v-model="widthSliderVal"
                 :format-tooltip="formatTooltip"
                 :disabled="isNonNumerical"
                 @input="syncWidthVal"
                 show-stops :max="0" :min="-5" />
      <div>步长比例：{{ratioSliderVal}}</div>
      <el-slider v-model="ratioSliderVal"
                 :disabled="isNonNumerical"
                 @input="syncRatioVal"
                 :max="1" :min="0" :step="0.05"/>
    </el-col>
  </el-row>


  <el-button type="primary"
             @click="searchRiskTree"
             style="margin-left: 200px; margin-top: 50px">
    search
  </el-button>

  <svg id="tree" style="position: absolute; right: 0; top: 100px;"></svg>
</template>

<script>
  import * as d3 from 'd3';
  import axios from "axios";

  export default {
    name: "Tree",
    data() {
      return {
        fileList: [],
        tableData: [],

        nonIdentifiableAttrs: [],
        bstMap: {},
        curRiskList: [],
        curRiskColumns: [],
        attrOptions: [],
        NonIdAttrs: [],
        attrList: [],
        showEditBar: false,
        widthSliderVal: -1,
        ratioSliderVal: 0.5,
        curEditIndex: -1,
        isNonNumerical: false
      }
    },
    methods: {
      uploadSuccess(response, file, fileList) {
        // if(typeof response === 'string') {
        //   response = JSON.parse(response)
        // }
        this.attrOptions = response.attr;
        this.transferData = response.attr.map((v, i) => {
          return {
            'key': i,
            'label': v
          }
        });
        this.NonIdAttrs = response.NonIdAttr;
        this.tableData = response.tableData;
        this.nonIdentifiableAttrs = [] //this.attrOptions;


      },
      searchRiskTree() {
        console.log(this.IdAttrs, this.NonIdAttrs)
        axios({
          url: 'http://127.0.0.1:8000/RiskTree/RiskTreeData/',
          method: 'post',
          data: {
            'filename': this.curFile,
            'attrList': this.attrList
          }
        }).then((response) => {
            let data = response.data;
            this.bstMap = data.riskRecordMap;
            d3.selectAll('#tree > *').remove();


            //定义边界
            var margin = { top: 90, bottom: 0, left: 10, right: 0 };

            var width=700;
            var height=700;
            var svg = d3
                .select("#tree")
                .attr("width", width + "px")
                .attr("height", height + "px");

            var g = svg
                .append("g")
                .attr("transform", "translate(" + margin.top + "," + margin.left + ")");

            var scale = svg
                .append("g")
                .attr("transform", "translate(" + margin.top + "," + margin.left + ")");

            // 创建一个层级布局
            var hierarchyData = d3.hierarchy(data.treeData).sum(function(d) {
              return d.val;
            });
            // $('#nodeVal').text(hierarchyData.value)
            // 创建一个树状图
            var tree = d3
                .tree()
                .size([height - 50, width - 200])
                .separation(function(a, b) {
                  return (a.parent === b.parent ? 1 : 2) / a.depth;
                });

            var treeData = tree(hierarchyData);
            console.log(treeData)
            var nodes = treeData.descendants();
            var links = treeData.links();
            var generator = d3
                .linkHorizontal()
                .x(function(d) {
                  return d.y;
                })
                .y(function(d) {
                  return d.x;
                });
            g.append("g")
                .selectAll("path")
                .data(links)
                .enter()
                .append("path")
                .attr("d", function(d) {
                  var start = { x: d.source.x, y: d.source.y };
                  var end = { x: d.target.x, y: d.target.y };
                  return generator({ source: start, target: end });
                })
                .attr("fill", "none")
                .attr("stroke", "#000")
                .attr("stroke-width", 1);
            var gs = g
                .append("g")
                .selectAll("g")
                .data(nodes)
                .enter()
                .append("g")
                .attr("class", 'gs')
                .attr("transform", function(d) {
                  var cx = d.x;
                  var cy = d.y;
                  return "translate(" + cy + "," + cx + ")";
                })
                .on('click', (e, d) => {
                  this.curRiskList = this.bstMap[d.data.name];
                  this.curRiskColumns = this.getBitmapColumns(d.data.name)
                  console.log(this.curRiskColumns)
                  console.log(this.curRiskList)
                });

            var outerRadius = 20;	//外半径
            var innerRadius = 0;	//内半径，为0则中间没有空白

            var arc = d3.arc()	//弧生成器
                .innerRadius(innerRadius)	//设置内半径
                .outerRadius(outerRadius);	//设置外半径

            var color = ['#d35400', '#81ecec'];

            var arcs = gs.selectAll("g")//g用于把相关元素进行组合的容器元素
                .data(d => d3.pie()(d.data.pie))
                .enter()
                .append("g")
                .attr('class', 'pie_path')
                .attr("transform","translate("+ 0 +","+ 0 +")")


            arcs
                .append("path")
                .attr("fill",function(d,i){
                  return color[i];
                })
                .attr("d",function(d){
                  return arc(d);
                });


            arcs.append("text")
                .attr("transform",function(d){
                  return "translate(" + arc.centroid(d) + ")";
                })
                .attr("text-anchor","middle")
                .text(function(d) {
                  return d.data;
                })



            //绘制文字
            gs.append("text")
                .attr("x", function(d) {
                  return d.children ? -20 : 10;
                })
                .attr("y", -5)
                .attr("dy", 10)
                .style('font-size', '10px')
                .text(function(d) {
                  return d.data.name;
                })
                .on("mouseover", function(d) {    //交互
                  d3.select(this)
                      .attr("fill", "red")
                })
                .on("mouseout",function(){
                  d3.select(this)
                      .attr("fill", "#000")
                })

        })
      },
      getBitmapColumns(bitmap) {
        let index = 0;
        let columns = [];
        while (bitmap) {
          let c = bitmap & 1;
          if(c === 1) {
            columns.push(this.nonIdentifiableAttrs[index])
          }
          bitmap = bitmap >> 1;
          index++
        }
        return columns
      },
      rowStyle({row, rowIndex}) {
        // if(this.curRiskList.includes(rowIndex)) {
        //   return {'border': '3px solid #ff0000'}
        // }
      },
      cellStyle({row, column, rowIndex, columnIndex}) {
        if (this.curRiskList.includes(rowIndex)) {
          let style = {'border-top': '3px solid #ff0000', 'border-bottom': '3px solid #ff0000'}
          if(this.curRiskColumns.includes(column.label)) {
            style['background-color'] = '#ffc8c8'

            if(columnIndex === 0) {
              style['border-left'] = '3px solid #ff0000'
            }
            if(columnIndex === this.attrOptions.length - 1) {
              style['border-right'] = '3px solid #ff0000'
            }
          }
          return style
        }

      },
      headerCellStyle({ row, column, rowIndex, columnIndex }) {

      },
      getSelectedAttrInfo() {
        axios({
          url: 'http://127.0.0.1:8000/RiskTree/AttrParams/',
          method: 'post',
          data: {
            'filename': this.curFile,
            'keepAttr': this.NonIdAttrs
          }
        }).then((response) => {
          this.attrList = response.data.data;
        })
      },
      formatTooltip(val) {
        return (10 ** val).toFixed(-val)
      },
      EditProp(index) {
        this.showEditBar = true;
        this.curEditIndex = index;

        if(this.attrList[index]['Type'] === 'numerical') {
          this.isNonNumerical = false;
          let domain = this.attrList[this.curEditIndex]['Max'] - this.attrList[this.curEditIndex]['Min'];
          this.widthSliderVal = Math.round(Math.log10(this.attrList[index]['Search_minimum_width'] / domain));
          console.log(this.widthSliderVal)
          this.ratioSliderVal = this.attrList[index]['Step_ratio'];
        }
        else {
          this.isNonNumerical = true;
        }

      },
      syncWidthVal() {
        let domain = this.attrList[this.curEditIndex]['Max'] - this.attrList[this.curEditIndex]['Min'];
        this.attrList[this.curEditIndex]['Search_minimum_width'] = domain * this.formatTooltip(this.widthSliderVal);
      },
      syncRatioVal() {
        this.attrList[this.curEditIndex]['Step_ratio'] = this.ratioSliderVal;
      }
    },
    computed: {
      curFile() {
        return this.fileList === [] ? '' : this.fileList[0].name;
      },
      attrListColumn() {
        return this.attrList.length === 0 ? [] : Object.keys(this.attrList[0]);
      }
    },
  }
</script>

<style scoped>

</style>