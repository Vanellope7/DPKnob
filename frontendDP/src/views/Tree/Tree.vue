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
             @click="RiskTree"
             style="margin-left: 200px; margin-top: 50px">
    search
  </el-button>

  <svg id="tree" style="position: absolute; right: 0; top: 100px;"></svg>
  <svg id="BSTTree" style="position: absolute; right: 50px; bottom: 20px;"></svg>
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
        isNonNumerical: false,

        treeData: {},
        treeFunc: {},
        selectedAttr: []
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
      MakeTree(svg, nodes, links) {
        let generator = d3
            .linkHorizontal()
            .x(function(d) {
              return d.y;
            })
            .y(function(d) {
              return d.x;
            });
        let TreeLinkG = svg.select(".container .TreeLinkG");
        let TreeNodeG = svg.select(".container .TreeNodeG");
        let TreeLink_DATA = TreeLinkG
            .selectAll(".TreeLinkPath")
            .data(links);
        // 移除旧边
        TreeLink_DATA.exit().remove();
        // 添加新边
        TreeLink_DATA
            .enter()
            .append("path")
            .attr("d", function(d) {
              let start = { x: d.source.x, y: d.source.y };
              let end = { x: d.target.x, y: d.target.y };
              return generator({ source: start, target: end });
            })
            .attr('class', 'TreeLinkPath')
            .attr("fill", "none")
            .attr("stroke", "#000")
            .attr("stroke-width", 1);
        // 统一边位置
        TreeLinkG
            .selectAll(".TreeLinkPath")
            .attr("d", function(d) {
              let start = { x: d.source.x, y: d.source.y };
              let end = { x: d.target.x, y: d.target.y };
              return generator({ source: start, target: end });
            });

        let TreeNode_DATA = TreeNodeG
            .selectAll(".TreeNodePie")
            .data(nodes);

        let Pie = TreeNode_DATA
            .enter()
            .append("g")
            .attr("class", 'TreeNodePie')
            .attr("transform", function(d) {
              let cx = d.x;
              let cy = d.y;
              return "translate(" + cy + "," + cx + ")";
            });

        for (let i = 0; i < nodes.length; i++) { // 取出所有节点默认右键事件
          document.getElementsByClassName("TreeNodePie")[i].oncontextmenu = function () {
            return false;
          };
        }

        svg.selectAll('.TreeNodePie')
            .attr("transform", function(d) {
              let cx = d.x;
              let cy = d.y;
              return "translate(" + cy + "," + cx + ")";
            })
            .on('click', (e, d) => {
              this.ClickNode(svg, d);
            })
            .on("contextmenu", (e, d) => {
              this.ContextmenuNode(d);
            })


        let outerRadius = 10;	//外半径
        let innerRadius = 0;	//内半径，为0则中间没有空白

        let arc = d3.arc()	//弧生成器
            .innerRadius(innerRadius)	//设置内半径
            .outerRadius(outerRadius);	//设置外半径

        let color = ['#d35400', '#81ecec'];

        let arcs = Pie.selectAll(".pie_path")//g用于把相关元素进行组合的容器元素
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


        //绘制文字
        Pie.append("text")
            .attr("x", function(d) {
              return -40;
            })
            .attr("y", -20)
            .attr("dy", 10)
            .style('font-size', '10px')
            .text(function(d) {
              let bitmap = d.data.name;
              if(bitmap === 0) {
                return 'ALL';
              }
              else {
                let i = 1;
                let ret = '';
                while(bitmap) {
                  let x = bitmap & 1;
                  if (x === 1) {
                    ret += String.fromCharCode(i + 64)
                  }
                  i += 1;
                  bitmap = bitmap >> 1
                }
                return ret
              }
            });
      },
      ClickNode(svg, d) {
        axios({
          url: 'http://127.0.0.1:8000/RiskTree/RiskTreeData/',
          method: 'post',
          data: {
            'filename': 'titanic_clean.csv',
            'attrList': this.attrList,
            'bitmap': d.data.name
          }
        }).then((response) => {
          d.data.children = response.data.treeData.children;

          let newTreeData = this.treeFunc(d3.hierarchy(this.treeData).sum(function (d) {
            return d.val;
          }));
          let Nodes = newTreeData.descendants();
          let Links = newTreeData.links();
          this.MakeTree(svg, Nodes, Links);
        })
      },
      RiskTree() {
        axios({
          url: 'http://127.0.0.1:8000/RiskTree/RiskTreeData/',
          method: 'post',
          data: {
            'filename': this.curFile,
            'attrList': this.attrList,
            'bitmap': 0
          }
        }).then((response) => {
          let data = response.data;
          this.treeData = data.treeData;
          console.log(data)
          d3.selectAll('#tree > *').remove();
          //定义边界
          let margin = { top: 10, bottom: 10, left: 10, right: 10 };

          let width=500;
          let height=300;
          let svg = d3
              .select("#tree")
              .attr("width", width + "px")
              .attr("height", height + "px");

          let container = svg
              .append("g")
              .attr("class", 'container')
              .attr("transform", "translate(" + margin.top + "," + margin.left + ")");
          let TreeLinkG = container.append("g").attr("class", 'TreeLinkG')
          let gs = container.append("g").attr("class", 'TreeNodeG')
          let hierarchyData = d3.hierarchy(data.treeData).sum(function(d) {
            return d.val;
          });
          this.treeFunc = d3
              .tree()
              .size([height - 50, width - 200])
              .separation(function(a, b) {
                return (a.parent === b.parent ? 1 : 2);
              });

          let treeData = this.treeFunc(hierarchyData);
          let nodes = treeData.descendants();
          let links = treeData.links();
          this.MakeTree(svg, nodes, links);
        })
      },

      ContextmenuNode(d) {
        axios({
          url: 'http://127.0.0.1:8000/RiskTree/BSTTreeData/',
          method: 'post',
          data: {
            'filename': 'titanic_clean.csv',
            'attrList': this.attrList,
            'bitmap': d.data.name
          }
        }).then((response) => {
          console.log(response)
          let keyMap = response.data.keyMap;
          let data = response.data.data;
          this.selectedAttr = response.data.selectedAttr;
          d3.selectAll('#BSTTree > *').remove();
          //定义边界
          let margin = { top: 90, bottom: 0, left: 10, right: 0 };

          let width=500;
          let height=300;
          let svg = d3
              .select("#BSTTree")
              .attr("width", width + "px")
              .attr("height", height + "px");

          let container = svg
              .append("g")
              .attr("class", 'container')
          // .attr("transform", "translate(" + margin.top + "," + margin.left + ")");

          let TreeLinkG = container.append("g").attr("class", 'TreeLinkG');
          let TreeNodeG = container.append("g").attr("class", 'TreeNodeG');
          let ParentNodeG = container.append("g").attr("class", 'ParentNodeG');
          let parentKeyList = {};
          let hierarchyData = d3.hierarchy(data).sum(function(d) {
            return d.val;
          })
              .each(d => {
                if(d.parent) d.parentKey = `${d.parent.parentKey}-${d.parent.data.key}`
                else d.parentKey = 'parent'

                let dim = d.data.dim;
                parentKeyList[dim] ? "": parentKeyList[dim] = new Set();
                parentKeyList[dim].add(d.parentKey);

              });
          console.log(parentKeyList)
          let treeFunc = d3
              .tree()
              .size([height, width])
              .separation(function(a, b) {
                return (a.parent === b.parent ? 1 : 2) / a.depth;
              });

          let treeData = treeFunc(hierarchyData);
          let nodes = treeData.descendants();
          let links = treeData.links();
          this.MakeBSTTree(svg, nodes, links, keyMap, parentKeyList);
        })
      },
      getDimensionScale(keyMap, height, dimNum, parentKeyList) {
        let keyLen = []
        for(let dimensionData of keyMap) {
          keyLen.push(dimensionData.data.length);
        }
        let dimensionNodeNum = []
        let c = 1;
        for(let len of keyLen) {
          dimensionNodeNum.push(c);
          c *= len;
        }

        let parentNodeScaleList = [];
        let childNodeScaleList = [];
        let parentNodeHeights = [];
        let nodeHeights = [];
        for(let i = 0 ;i< dimNum;i++) {
          let parentNodeHeight = height / keyLen[i];
          let nodeHeight = parentNodeHeight / dimensionNodeNum[i];
          parentNodeHeights.push(parentNodeHeight);
          nodeHeights.push(nodeHeight);
          parentNodeScaleList.push(
              d3.scaleBand()
                  .domain(keyMap[i].data)
                  .range([parentNodeHeight / 2, height + parentNodeHeight / 2])
          )

          childNodeScaleList.push(
              d3.scaleBand()
                  .domain(Array.from(parentKeyList[i]))
                  .range([-parentNodeHeight/2 + nodeHeight / 2, parentNodeHeight/2 - nodeHeight / 2])
          )
        }

        return [parentNodeScaleList, childNodeScaleList, parentNodeHeights, nodeHeights]

      },
      MakeBSTTree(svg, nodes, links, keyMap, parentKeyList) {
        let width=500;
        let height=300;
        let [parentNodeScaleList, childNodeScaleList, parentNodeHeights, nodeHeights] = this.getDimensionScale(keyMap, height, keyMap.length, parentKeyList);


        nodes = nodes.filter(d => d.depth > 0)
        links = links.filter(d => d.source.depth > 0)
        console.log(keyMap)

        let Xscale = d3.scaleLinear()
            .domain([-0.5, keyMap.length-1 + 0.5])
            .range([0, width]);

        let nodeColorScale = d3.scaleLinear()
            .domain([d3.min(nodes, d => d.data.num), d3.max(nodes, d => d.data.num)])
            .range(['#bbbbbb', '#777777'])





        for(let i in nodes) {
          let dim = nodes[i].data.dim;
          nodes[i].y = Xscale(dim);
          keyMap[dim].x = nodes[i].y;
          nodes[i].x = parentNodeScaleList[dim](nodes[i].data.key) + childNodeScaleList[dim](nodes[i].parentKey);
        }
        console.log(nodes)
        let generator = d3
            .linkHorizontal()
            .x(function(d) {
              return d.y;
            })
            .y(function(d) {
              return d.x;
            });
        let TreeLinkG = svg.select(".container .TreeLinkG");
        let TreeNodeG = svg.select(".container .TreeNodeG");
        let ParentNodeG = svg.select(".container .ParentNodeG");
        let ParentNodeG_DATA = ParentNodeG.selectAll(".DimensionNodeG")
            .data(keyMap);
        ParentNodeG_DATA.exit().remove();
        let DimensionG = ParentNodeG_DATA.enter()
            .append("g")
            .attr("class", 'DimensionNodeG')
            .attr("transform", function(d) {
              let cx = d.x;
              let cy = 0;
              return "translate(" + cx + "," + 0 + ")";
            });

        let dimension1 = -1, dimension2 = -1;
        let parentNodes = DimensionG.selectAll(".ParentNode")
            .data(d => d.data)
            .enter()
            .append('rect')
            .attr("class", 'ParentNode')
            .attr("x", d => 15)
            .attr("y", (d, k) => {
              if(k === 0) dimension1 += 1;
              return `${parentNodeScaleList[dimension1](d) - parentNodeHeights[dimension1] / 2}px`
            })
            .attr('width', '40px')
            .attr("height", (d, k) => {
              if(k === 0) dimension2 += 1;
              return `${parentNodeHeights[dimension2] - 5}px`
            })
            .attr('fill', '#e1ffac');
        let dimension3 = -1;
        let parentTextG = DimensionG.selectAll(".ParentText")
            .data(d => d.text)
            .enter()
            .append('g')
            .attr("class", 'ParentText')
            .attr("transform", (d,k) => {
              let cx = 15;
              if(k === 0) dimension3 += 1;
              let cy = parentNodeScaleList[dimension3](keyMap[dimension3].data[k])
              return "translate(" + cx + "," + (cy - 20) + ")";
            });

        parentTextG.append('text')
            .attr("x", 20)
            .attr("y", 10)
            .style('text-anchor', 'middle')
            .text(d => d.split('~')[0]);
        parentTextG.append('text')
            .attr("x", 20)
            .attr("y", 20)
            .style('text-anchor', 'middle')
            .text(d => '~');
        parentTextG.append('text')
            .attr("x", 20)
            .attr("y", 30)
            .style('text-anchor', 'middle')
            .text(d => d.split('~')[1]);



        let TreeLink_DATA = TreeLinkG
            .selectAll(".TreeLinkPath")
            .data(links);
        // 移除旧边
        TreeLink_DATA.exit().remove();
        // 添加新边
        TreeLink_DATA
            .enter()
            .append("path")
            .attr("d", function(d) {
              let start = { x: d.source.x, y: d.source.y };
              let end = { x: d.target.x, y: d.target.y };
              return generator({ source: start, target: end });
            })
            .attr('class', 'TreeLinkPath')
            .attr("fill", "none")
            .attr("stroke", "#000")
            .attr("stroke-width", 1);
        // 统一边位置
        let TreeLinkPath = TreeLinkG.selectAll(".TreeLinkPath")
            .attr("d", function(d) {
              let start = { x: d.source.x, y: d.source.y };
              let end = { x: d.target.x, y: d.target.y };
              return generator({ source: start, target: end });
            });

        let TreeNode_DATA = TreeNodeG
            .selectAll(".TreeNodePie")
            .data(nodes);



        let NodesG = TreeNode_DATA
            .enter()
            .append("g")
            .attr("class", 'TreeNodePie')
            .attr("transform", function(d) {
              let cx = d.x;
              let cy = d.y;
              return "translate(" + cy + "," + cx + ")";
            });
        d3.selectAll('.TreeNodePie')
            .attr("transform", function(d) {
              let cx = d.x;
              let cy = d.y;
              return "translate(" + cy + "," + cx + ")";
            })
            .on('mouseover', (e, d) => {
              TreeLinkPath.filter(link => link.source !== d)
                  .classed('nonHighlightEdge', true);

            })
            .on('mouseout', (e, d) => {
              TreeLinkPath.classed('nonHighlightEdge', false);
            })

        NodesG.append("rect")
            .attr("x", -10)
            .attr("y", d => {
              return `-${nodeHeights[d.data.dim] / 2 - 2.5}`
            })
            .attr("height", d => {
              return `${nodeHeights[d.data.dim] - 5}px`
            })
            .attr("width", '20px')
            .attr('fill', d => {
              let num = d.data.num;
              if(num === 1) {
                return '#c0392b'
              }
              else {
                return nodeColorScale(num)
              }
            })
            .append('title')
            .text(d => d.data.index)
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
        if(this.selectedAttr.includes(column.label)) {
          return {'background-color': '#e17055'}
        }
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

<style>
  .nonHighlightEdge {
    stroke: #cccccc;
  }
</style>