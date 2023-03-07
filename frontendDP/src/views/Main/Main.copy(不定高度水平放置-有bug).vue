<template>
  <div id="Container">
    <div class="RowPartMain">
      <div id="DifferentialRiskIdentification" class="BaseMain">
        <div class="MainLabel">Differential Risk Identification</div>

        <div id="TreeView">
          <div id="AttributeSet">
            <div class="SecondaryLabel">Attribute Set Tree</div>
            <svg id="AttributeSetTree"></svg>
          </div>

          <el-divider direction="vertical" border-style="dashed" style="height: 100%"/>

          <div id="DifferentialQueryList">
            <div class="SecondaryLabel">Differential Query List</div>
            <div id="DQTreeContainer">
              <svg id="DifferentialQueryTree"></svg>
            </div>
          </div>
        </div>

      </div>

      <div id="DataExploration" class="BaseMain">
        <div class="MainLabel">Data Exploration</div>
        <svg id="DataDistribution"></svg>
      </div>
    </div>

    <div class="RowPartMain BaseMain">
      <div class="MainLabel">Data Query Simulation</div>


      <div id="DPS_Panel" class="Panel">
        <div>DP settings</div>
        <el-divider direction="vertical" border-style="dashed" class="TextDivider"/>
        <span>&epsilon;: </span>
        <el-input-number
            v-model="epsilon"
            :min="0.01"
            :max="1"
            :step="0.01"
            class="EpsilonInput"
            controls-position="right"
        />
        <span>Sensitivity calculation: </span>
        <el-select v-model="SensitivityCalculationWay" class="SCWO" placeholder="Select">
          <el-option
              v-for="item in SensitivityCalculationWayOption"
              :key="item.value"
              :label="item.label"
              :value="item.value"
          />
        </el-select>
      </div>


      <div id="QT_Panel" class="Panel">
        <div style="margin-right: 7px">Query Test</div>
        <el-divider direction="vertical" border-style="dashed" class="TextDivider"/>
        <span>Attribute: </span>
        <el-select v-model="QueryAttr" placeholder="Select" style="width: 100px">
          <el-option
              v-for="item in QueryAttrOption"
              :key="item.value"
              :label="item.label"
              :value="item.value"
          />
        </el-select>

        <span style="padding-left: 20px">Type: </span>
        <el-select v-model="QueryType" placeholder="Select" style="width: 100px">
          <el-option
              v-for="item in QueryTypeOption"
              :key="item.value"
              :label="item.label"
              :value="item.value"
          />
        </el-select>

        <span style="padding-left: 20px">Interval: </span>
        <el-input-number
            v-model="IntervalLeft"
            :min="0.01"
            :max="10"
            :step="0.01"
            controls-position="right"
            style="width: 100px"
        />
        <span>~</span>
        <el-input-number
            v-model="IntervalRight"
            :min="0.01"
            :max="10"
            :step="0.01"
            controls-position="right"
            style="width: 100px"
        />
      </div>


      <div class="SecondaryLabel">Attack Simulation</div>
      <div id="AS_Panel" class="Panel">
        <div >Recommendation</div>
        <el-divider direction="vertical" border-style="dashed" class="TextDivider"/>
        <span>Deviation: &plusmn;</span>
        <el-input-number
            v-model="PrivacyDeviation"
            :min="0"
            :max="MaxMap[QueryAttr] === undefined ? 1 : MaxMap[QueryAttr]"
            :step="0.01"
            controls-position="right"
            style="width: 100px"
        />

        <span>Successful rate threshold: </span>
        <el-input-number
            v-model="AttackSRT"
            :min="0.01"
            :max="1"
            :step="0.01"
            controls-position="right"
            style="width: 80px"
        />
        <el-button type="primary" class="rightEdgeBtn" @click="UpdateEpsilonWithPrivacy">Update &epsilon;</el-button>
      </div>
      <div id="AttackSimulationViews" class="SimulationViews">
        <svg id="FirstQuery" class="AS_view QueryView"><text x="5" y="20">1st query</text></svg>
        <svg id="SecondQuery" class="AS_view QueryView"><text x="5" y="20">2nd query</text></svg>
        <svg id="DA_Output" class="AS_view QueryView"><text x="5" y="20">Differential attack</text></svg>
      </div>



      <div class="SecondaryLabel">General Query Simulation</div>
      <div id="GQS_Panel" class="Panel">
        <div >Recommendation</div>
        <el-divider direction="vertical" border-style="dashed" class="TextDivider"/>
        <span>Deviation: &plusmn;</span>
        <el-input-number
            v-model="AccuracyDeviation"
            :min="0"
            :max="MaxMap[QueryAttr] === undefined ? 1 : MaxMap[QueryAttr]"
            :step="0.01"
            controls-position="right"
            style="width: 100px"
        />
        <span>Successful rate threshold: </span>
        <el-input-number
            v-model="AccuracySRT"
            :min="0.01"
            :max="1"
            :step="0.01"
            controls-position="right"
            style="width: 80px"
        />
        <el-button type="primary" class="rightEdgeBtn" @click="UpdateEpsilonWithAccuracy">Update &epsilon;</el-button>
      </div>

      <div id="GeneralQuerySimulationViews" class="SimulationViews">
        <svg id="GeneralQuery" class="GQS_view QueryView"><text x="5" y="20">General query</text></svg>
        <div id="SchemeHistory">
          <div class="MainLabel">Scheme History</div>
        </div>
      </div>

    </div>


  </div>

  <div class="InitialOverLay" v-if="DataInputVisible">
    <div class="SystemName">SystemName</div>
    <div class="DataInput">
      <DataInput
          @inputData="initializeTree"/>
    </div>
  </div>

</template>

<script>
import * as d3 from 'd3';
import DataInput from "./DataInput/DataInput";
import axios from "axios";

export default {
    name: "Main",
    components: {
      DataInput
    },
    data() {
      return {
        curFile: '',
        attrList: [],
        DataInputVisible: true,
        treeData: {},
        LineData: [],
        TableData: [],
        keyMap: {},  //key 与 value的转化, 例如 0 -- [0, 20]
        curIndices: [],
        curAttr: [],
        scale_Xscale: {},
        scaleMap: {},
        curIndex: [],

        MaxMap: {}, //记录属性的最大值 类别型属性用count最大值替代
        dimNodeCnt: [],


        // 决策变量
        firstQueryData: [],
        secondQueryData: [],
        curB: 0,
        curSensitivity: 0,
        epsilon: 1.0,
        SensitivityCalculationWayOption: ['Global sensitivity', 'Local sensitivity'],
        SensitivityCalculationWay: 'Global sensitivity',
        QueryAttrOption: [],
        QueryAttr: '',
        QueryTypeOption: ['sum', 'count', 'avg', 'mode'],
        QueryType: 'sum',
        IntervalLeft: 5,
        IntervalRight: 35,
        PrivacyDeviation: 10,
        AttackSRT: 0.5,
        AccuracyDeviation: 10,
        AccuracySRT: 0.5,


        DA_OutputXscale: {},
        ExactVal: {'firstQuery': 0, 'secondQuery': 0}
      }
    },
    methods: {
      //属性集树方法
      initializeTree([data, curFile, attrList]) {
        this.DataInputVisible = false;
        this.treeData = data.treeData;
        this.curFile = curFile;
        this.attrList = attrList;
        this.QueryAttrOption = attrList.map((d) => d.Name)
        this.QueryAttr = this.QueryAttrOption[0]
        d3.selectAll('#AttributeSetTree > *').remove();
        //定义边界
        let margin = { top: 10, bottom: 10, left: 10, right: 10 };
        let svg = d3
            .select("#AttributeSetTree");
        let width=svg.style('width').split('px')[0];
        let height=svg.style('height').split('px')[0];

        let container = svg
            .append("g")
            .attr("class", 'container')
            .attr("transform", "translate(" + margin.left + "," + margin.top + ")");
        let TreeLinkG = container.append("g").attr("class", 'TreeLinkG')
        let gs = container.append("g").attr("class", 'TreeNodeG')
        let hierarchyData = d3.hierarchy(data.treeData).sum(function(d) {
          return d.val;
        });
        this.treeFunc = d3
            .tree()
            .size([height- 50, width - 50])
            .separation(function(a, b) {
              return (a.depth === b.depth ? 1 : 2);
            });

        let treeData = this.treeFunc(hierarchyData);
        let nodes = treeData.descendants();
        let links = treeData.links();
        [nodes, links] = this.PruningAndLayout(nodes, links, width, height, 3)
        this.MakeTree(svg, nodes, links);
        this.initializeDataDistribution();
        this.initializeAttackSimulationViews();
        this.initializeGeneralQuerySimulationView();
      },
      MakeTree(svg, nodes, links) {
        let that = this;
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
            .attr("stroke", "rgba(175, 175, 175, 0.8)")
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

        TreeNode_DATA.exit().remove();

        let Pie = TreeNode_DATA
            .enter()
            .append("g")
            .attr('id', d => `TreeNodePie${d.data.name}`)
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
            .on('click', function(e, d) {
              that.ClickNode(svg, d);
            })
            .on("contextmenu", function (e, d) {
              that.ContextmenuNode(d);
            })
            .on('mouseover', (e, d) => {
              let bitmap = d.data.name;
              let i = 0;
              let indices = [];
              while(bitmap) {
                let x = bitmap & 1;
                if (x === 1) {
                  indices.push(i)
                }
                i += 1;
                bitmap = bitmap >> 1
              }
              if(indices.length !== 1) {
                for (let index of indices) {
                  svg.select(`#highlightTextRect${1 << index}`)
                      .style('opacity', 1);
                }
              }
            })
            .on('mouseout', (e, d) => {
                svg.selectAll(`.highlightTextRect`)
                    .style('opacity', 0);
            })


        let outerRadius = 10;	//外半径
        let innerRadius = 0;	//内半径，为0则中间没有空白

        let arc = d3.arc()	//弧生成器
            .innerRadius(innerRadius)	//设置内半径
            .outerRadius(outerRadius);	//设置外半径

        let color = ['rgba(234, 134, 133, 0.6)', 'rgba(64, 158, 255, 0.6)'];

        Pie.append('circle')
           .attr('class', 'strokeCircle')
           .attr('id', d => 'strokeCircle' + d.data.name)
           .attr('r', 10)
           .attr('cx', 0)
           .attr('cy', 0)
           .attr('fill', 'None')
           .attr('stroke', 'None')
           .attr('stroke-width', '5px')


        let arcs = Pie.selectAll(".pie_path") //g用于把相关元素进行组合的容器元素
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

        let highlightText = Pie.append('g')
                               .attr('class', 'highlightText')
                               .attr("transform","translate("+ 20 +","+ 3 +")")


        //绘制文字
        Pie.append("text")
            .attr('id', d => `attrName${d.data.name}`)
            .attr("x", function(d) {
              return 20;
            })
            .attr("y", 5)
            .style('font-size', '10px')
            .text((d) => {
              if(d.depth === 1) {
                let bitmap = d.data.name;
                let i = -1;
                while(bitmap) {
                  i += 1;
                  bitmap = bitmap >> 1
                }
                return this.attrList[i].Name
              }
              else {
                return '';
              }
            });
        highlightText.append('rect')
                     .attr('class', `highlightTextRect`)
                     .attr('id', d => `highlightTextRect${d.data.name}`)
                     .attr('x', 0)
                     .attr('y', -12)
                     .attr('width', d => {
                       // 只针对单属性有效
                       return d3.select(`#attrName${d.data.name}`).node().getComputedTextLength();
                     })
                     .attr('height', 20)
                     .attr('fill', 'rgba(234, 134, 133, 0.6)')
                     .style('opacity', 0)
      },
      PruningAndLayout(nodes, links, width, height, maxLayer) {
        let padding = 20;
        nodes = nodes.filter(d => d.depth > 0)
        links = links.filter(d => nodes.includes(d.source) && nodes.includes(d.target))

        let Xscale = d3.scaleLinear()
            .domain([-0.5, maxLayer - 0.5])
            .range([0, width]);
        let YscaleList = []
        let YscaleIndex = []
        for(let i=0;i<maxLayer;i++) {
          let size = nodes.filter(node => node.depth === i+1).length
          YscaleList.push(d3.scaleLinear([-0.5, size - 0.5], [0, height - padding]))
          YscaleIndex.push(0)
        }
        for (let i in nodes) {
          let dim = nodes[i].depth - 1;
          nodes[i].y = Xscale(dim);
          nodes[i].x = YscaleList[dim](YscaleIndex[dim]);
          YscaleIndex[dim] += 1;
        }
        return [nodes, links]
      },
      ClickNode(svg, d) {
        if(d.data.children.length === 0) {
          // 生成节点
          axios({
            url: 'http://127.0.0.1:8000/RiskTree/RiskTreeData/',
            method: 'post',
            data: {
              'filename': this.curFile,
              'attrList': this.attrList,
              'bitmap': d.data.name
            }
          }).then((response) => {
            d.data.children = response.data.treeData.children;
            this.curIndices = response.data.Indices;
            this.curAttr = this.curIndices.map(d => this.attrList[d].Name);

            let newTreeData = this.treeFunc(d3.hierarchy(this.treeData).sum(function (d) {
              return d.val;
            }));
            let width = parseFloat(svg.style('width').split('px')[0]);
            let height = parseFloat(svg.style('height').split('px')[0]);
            let Nodes = newTreeData.descendants();
            let Links = newTreeData.links();
            [Nodes, Links] = this.PruningAndLayout(Nodes, Links, width, height, 3)
            this.MakeTree(svg, Nodes, Links);
          })
        }
        else {
          // 收起节点
          d.data.children = [];
          let newTreeData = this.treeFunc(d3.hierarchy(this.treeData).sum(function (d) {
            return d.val;
          }));
          let width = svg.style('width').split('px')[0];
          let Nodes = newTreeData.descendants();
          let Links = newTreeData.links();
          [Nodes, Links] = this.PruningAndLayout(Nodes, Links, width, 3)
          this.MakeTree(svg, Nodes, Links);
        }
      },

      // 查询集树方法
      ContextmenuNode(d) {
        d3.selectAll('.strokeCircle').attr('stroke', 'None')
        d3.select("#strokeCircle" + d.data.name).attr('stroke', '#e58e26')
        this.initializeDifferQueryTree(d.data.name);
      },
      initializeDifferQueryTree(bitmap) {
        axios({
          url: 'http://127.0.0.1:8000/RiskTree/BSTTreeData/',
          method: 'post',
          data: {
            'filename': this.curFile,
            'attrList': this.attrList,
            'bitmap': bitmap
          }
        }).then((response) => {
          this.curIndices = response.data.Indices;
          this.curAttr = this.curIndices.map(d => this.attrList[d].Name);
          let keyMap = this.keyMap = response.data.keyMap;
          let data = response.data.data;
          this.selectedAttr = response.data.selectedAttr;
          d3.selectAll('#DifferentialQueryTree > *').remove();
          //定义边界
          let margin = { top: 10, bottom: 0, left: 10, right: 0 };


          let svg = d3.select("#DifferentialQueryTree")
          let width = parseFloat(svg.style('width').split('px')[0]);
          let height = parseFloat(svg.style('width').split('px')[0]);
          let container = svg
              .append("g")
              .attr("class", 'container')
              .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

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
          this.MakeDifferQueryTree(svg, nodes, links, keyMap, parentKeyList);
        })


      },
      getDimensionScale(keyMap, height, dimNum, parentKeyList) {
        let keyLen = []
        for(let dimensionData of keyMap) {
          keyLen.push(dimensionData.data.length);
        }
        let dimensionNodeNum = this.dimNodeCnt;
        let parentNodeScaleList = [];
        let childNodeScaleList = [];
        let parentNodeHeights = [];
        let nodeHeights = [];
        for(let i = 0 ;i< dimNum;i++) {
          let parentNodeHeight = height / keyLen[i];
          let nodeHeight = height / dimensionNodeNum[i];
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
      MakeDifferQueryTree(svg, nodes, links, keyMap, parentKeyList) {
        let width=300;
        let height=300;
        let NodeWidth = 50;
        [nodes, keyMap] = this.TreePruning(nodes, keyMap);
        nodes = nodes.filter(d => d.depth > 0)
        links = links.filter(d => nodes.includes(d.source) && nodes.includes(d.target))
        let [parentNodeScaleList, childNodeScaleList, parentNodeHeights, nodeHeights] = this.getDimensionScale(keyMap, height, keyMap.length, parentKeyList);


        let Xscale = d3.scaleLinear()
            .domain([-0.5, 2.5])
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

        let TreeLink_DATA = TreeLinkG
            .selectAll(".TreeLinkPath")
            .data(links);
        // 移除旧边
        TreeLink_DATA.exit().remove();
        // 添加新边
        TreeLink_DATA
            .enter()
            .append("path")
            .attr('class', 'TreeLinkPath')

        // 统一边位置
        let TreeLinkPath = TreeLinkG.selectAll(".TreeLinkPath")
            .attr("d", function(d) {
              let start = { x: d.source.x, y: d.source.y + NodeWidth};
              let end = { x: d.target.x, y: d.target.y };
              return generator({ source: start, target: end });
            })
            .attr("fill", "none")
            .attr("stroke", "#000")
            .attr("stroke-width", 1);

        let TreeNode_DATA = TreeNodeG
            .selectAll(".TreeNodePie")
            .data(nodes);



        let NodesG = TreeNode_DATA
            .enter()
            .append("g")
            .attr("class", 'TreeNodePie')
            .on('click', (e, d) => {
              this.clickQueryNode(d);
            })

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
            .attr("x", 0)
            .attr("y", d => {
              return `-${nodeHeights[d.data.dim] / 2}`
            })
            .attr("height", d => {
              return `${nodeHeights[d.data.dim]}px`
            })
            .attr("width", NodeWidth)
            .attr('stroke', '#555')
            .attr('fill', d => {
              let num = d.data.num;
              if(num === 1) {
                return 'rgba(234, 134, 133,0.6)'
              }
              else {
                return nodeColorScale(num)
              }
            })
            .append('title')
            .text(d => d.data.index);
        NodesG.append('text')
              .style('text-anchor', 'middle')
              .text(d => {
                let dim = d.data.dim;
                let index = this.keyMap[dim].data.indexOf(d.data.key);
                return this.keyMap[dim].text[index];
              })

      },
      TreePruning(nodes, keyMap) {
        let root = nodes[0];
        let leaves = root.leaves();
        let nodeSet = new Set();
        for(let leaf of leaves) {
          if(leaf.data.isBST) {
            for (let ancestor of leaf.ancestors()) {
              nodeSet.add(ancestor)
            }
          }
        }
        this.dimNodeCnt = []
        nodes = nodes.filter(d => d.depth > 0)
        nodeSet.delete(root)
        let keepIndex = Array([],[],[]);
        for(let node of nodeSet) {
          keepIndex[node.depth - 1].push(keyMap[node.depth - 1].data.indexOf(node.data.key));
        }
        for(let i in [0,1,2]) { //去重
          this.dimNodeCnt[i] = keepIndex[i].length;
          keepIndex[i] = Array.from(new Set(keepIndex[i]))
        }

        let new_keyMap = [];
        for(let i in keyMap) {
          if(keepIndex[i].length === 0) {
            break;
          }
          new_keyMap[i] = {data: [], text: []};
          for(let index of keepIndex[i]) {
            new_keyMap[i].data.push(keyMap[i].data[index])
            new_keyMap[i].text.push(keyMap[i].text[index])
          }
        }
        return [Array.from(nodeSet), new_keyMap]
      },

      //平行坐标图方法
      initializeDataDistribution() {
        axios({
          url: 'http://127.0.0.1:8000/RiskTree/DataDistribution/',
          method: 'post',
          data: {
            'filename': this.curFile,
            'attrList': this.attrList,
          }
        }).then(response => {
          let data = response.data;
          let ScaleData = data.ScaleData;
          this.MaxMap = data.MaxMap;
          let TableData = this.TableData = data.TableData;
          let width = d3.select('#DataDistribution').style('width').split('px')[0];
          let height = d3.select('#DataDistribution').style('height').split('px')[0];
          let padding = 20;
          let scale_Xscale = this.scale_Xscale = d3.scaleLinear().domain([-0.5, ScaleData.length - 0.5]).range([0, width]);
          let svg = d3.select('#DataDistribution');
          let scaleMap = this.scaleMap = {};


          for(let S of ScaleData) {
            if(S.type === 'numerical') {
              scaleMap[S.name] = d3.scaleLinear().domain(S.domain).range([height - padding, padding]);
            }
            else {
              scaleMap[S.name] = d3.scaleBand().domain(S.domain).range([height - padding, padding]);
            }
          }
          let axisG = svg.selectAll('.axis')
             .data(ScaleData)
             .enter()
             .append('g')
             .attr('class', 'axis')
             .attr('transform', (d, k) => `translate(${scale_Xscale(k)}, ${0})`)
             .each(function(d, k) {
               d3.select(this).call(d3.axisLeft().scale(scaleMap[d.name]).ticks(0));
             });
          axisG.append('text')
               .attr("x", 0)
               .attr('y', 10)
               .style('text-anchor', 'middle')
               .style('fill', '#777777')
               .text(d => d.name);
          let Line = d3.line()
              .x(function (d) {
                return d.x;
              })
              .y(function (d) {
                return d.y;
              });

          // TableData 转 LineData
          let LineData = this.LineData = TableData.map(d => {
            let temp = []
            for(let [i, key] of Object.entries(Object.keys(d))) {
              temp.push({
                x: scale_Xscale(i),
                y: ScaleData[i].type === 'numerical'? scaleMap[key](d[key]) : scaleMap[key](d[key]) + scaleMap[key].bandwidth() / 2
              })
            }
            return {'pathD': Line(temp)};
          });
          svg.append("g")
             .attr('class', 'LineContainer')
             .selectAll('.LineG')
             .data(LineData)
             .enter()
             .append('g')
             .attr('class', 'LineG')
             .append("path")
             .attr('class', 'LinePath')
             .attr("d", d => d.pathD)
             .attr("stroke", 'rgba(190,190,190,0.2)')
             .attr("stroke-width", 1)
             .attr("fill", "none");



        })
      },
      clickQueryNode(d) {
        //高亮节点
        this.curIndex = d.data.index;
        for(let d of this.LineData) {
          d['highlight'] = false;
        }
        for(let i of this.curIndex) {
          this.LineData[i]['highlight'] = true;
        }
        d3.selectAll('.LinePath')
            .attr('stroke', d => d.highlight ? 'rgba(234, 134, 133, 1.0)' : 'rgba(190,190,190,0.2)')

        if(d.data.index.length === 1) {
          this.setAttackTarget(this.TableData[d.data.index[0]])
        }


        let keyList, valueList = [];
        if(d.parentKey === 'parent-0') //单层节点
        {
          keyList = [d.data.key];
        }
        else {
          keyList = d.parentKey.split('parent-0-')[1].split('-');
          keyList.push(d.data.key);
        }
        for(let [i, key] of Object.entries(keyList)) {
          key = parseInt(key);
          let obj = this.keyMap[i];
          let text = obj.text[obj.data.indexOf(key)]
          if (obj.type === 'numerical') {
            let splitEdge = text.split('~');
            splitEdge = splitEdge.map(d => parseInt(d))
            valueList.push(splitEdge);
          } else {
            valueList.push(text)
          }
        }
        let svg = d3.select('#DataDistribution');
        let MaskNodeData = svg.selectAll('.MaskNodeG').data(valueList);
        MaskNodeData.exit().remove();
        let NewMaskNodeG = MaskNodeData.enter()
            .append('g')
            .attr('class', 'MaskNodeG');
        let MaskNodeG = d3.selectAll(".MaskNodeG")
            .attr('transform', (d, k) =>{
              let x
              if(typeof d !== 'string')
                x = d[0]
              else
                x = d
              return `translate(${this.scale_Xscale(this.curIndices[k])}, ${this.scaleMap[this.curAttr[k]](x)})`
            });
        NewMaskNodeG.append('rect')
            .attr("class", 'MaskNode');
        MaskNodeG.select('rect')
            .attr("x", -10)
            .attr("y", (d, k) => {
              if(typeof d !== 'string') {
                return this.scaleMap[this.curAttr[k]](d[1]) - this.scaleMap[this.curAttr[k]](d[0])
              }
              else {
                return 0
              }
            })
            .attr('width', '20px')
            .attr("height", (d, k) => {
              if(typeof d !== 'string') {
                return this.scaleMap[this.curAttr[k]](d[0]) - this.scaleMap[this.curAttr[k]](d[1])
              }
              else {
                return this.scaleMap[this.curAttr[k]].bandwidth();
              }
            })
            .attr('fill', 'rgba(255,255,172,0.8)')
            .style('stroke', '#aaaaaa')

      },

      // 攻击模拟方法
      initializeAttackSimulationViews() {
        axios({
          url: 'http://127.0.0.1:8000/AttackSimulation/GetNoisyDataDistribution/',
          method: 'post',
          data: {
            'FileName': this.curFile,
            'QueryType': this.QueryType,
            'QueryAttr': this.QueryAttr,
            'Interval': [this.IntervalLeft, this.IntervalRight],
            'epsilon': this.epsilon,
            'sensitivityWay': this.SensitivityCalculationWay
          }
        }).then(response => {
          this.ExactVal['firstQuery'] = response.data.ExactVal;
          this.curB = response.data.b;
          this.curSensitivity = response.data.b;
          let svg = d3.select('#FirstQuery');
          let lineData = this.firstQueryData = response.data.distribution;
          this.MakeResultDistribution(svg, lineData, 'top-half');
        })
      },
      setAttackTarget(data) {
        // 假设攻击目标满足条件
        let targetResult = data[this.QueryAttr]
        this.ExactVal['secondQuery'] = this.ExactVal['firstQuery'] - targetResult;
        this.secondQueryData = this.firstQueryData.map(d => {
          return [d[0] - targetResult, d[1]];
        });
        let svg = d3.select('#SecondQuery');
        this.MakeResultDistribution(svg, this.secondQueryData, 'top-half');
        // 画差分结果分布图
        axios({
          url: 'http://127.0.0.1:8000/AttackSimulation/GetPrivacyDistribution/',
          method: 'post',
          data: {
            'b': this.curB,
            'targetResult': targetResult,
          }
        }).then(response => {
          let svg = d3.select('#DA_Output');
          let lineData = response.data.distribution;
          this.DA_OutputXscale = this.MakeResultDistribution(svg, lineData, 'overall', true, 'clip-privacy');
          this.openDA_OutputBrush(svg, 'clip-privacy');
        })

      },
      openDA_OutputBrush(svg, clipId) {
        let brush = d3.brush()
                      .on('start', (e) => {
                        svg.select('.brush').style('display', 'visible')
                      })
                      .on('brush', (e) => {
                        let selection = e.selection;
                        svg.select(`#${clipId} rect`)
                            .attr("x", selection[0][0])
                            .attr("width", selection[1][0] - selection[0][0]);
                      })
                      .on('end', (e) => {
                        let selection = e.selection;
                        let [left, right] = [selection[0][0], selection[1][0]]
                        let [X0, X1] = [this.DA_OutputXscale.invert(left), this.DA_OutputXscale.invert(right)]
                        console.log([left, right], [X0, X1] )
                        this.MakeOppositeProbability([X0, X1])
                        svg.select('.brush').style('visibility', 'hidden')
                      })
                  // .extent([
                  //   [padding, 0],
                  //   [w - padding, h - padding]
                  // ])
        svg.append('g').attr('class', 'brush').call(brush);

      },
      MakeOppositeProbability(interval) {
        axios({
          url: 'http://127.0.0.1:8000/AttackSimulation/GetOppositeProbability/',
          method: 'post',
          data: {
            'ExactVal': this.ExactVal,
            'interval': interval,
            'b': this.curB,
            'domainDeviation': this.curSensitivity
          }
        }).then((response) => {
          let firstLineData = response.data.firstRes;
          let secondLineData = response.data.secondRes;
          this.MakeResultDistribution(d3.select("#FirstQuery"), firstLineData, 'bottom-half',);
          this.MakeResultDistribution(d3.select("#SecondQuery"), secondLineData, 'bottom-half',);
        })
      },
      MakeResultDistribution(svg, lineData, position, brushAble=false, clipId='') {
        let padding = 40, w = parseFloat(svg.style('width').split('px')[0]);
        let h = parseFloat(svg.style('height').split('px')[0]);
        let yRange;
        switch (position) {
          case 'top-half':
            yRange = [h / 2, padding]
            break;
          case 'bottom-half':
            yRange = [h / 2, h - 2 *padding]
            break;
          case 'overall':
            yRange = [h - padding, padding]
        }
        let svgId = svg.attr('id');
        svg.selectAll(`#container-${position}`).remove();
        let x = d3.scaleLinear()
            .domain([d3.min(lineData, d => d[0]), d3.max(lineData, d => d[0])])
            .range([padding, w - padding])
            .clamp(true);  //原因是定义域为止  暂时这么做为了保险
        let y = d3.scaleLinear()
            .domain([0, d3.max(lineData, d => d[1])])
            .range(yRange);
        let cg = d3.line()
            .x(d => x(d[0]))
            .y(d => y(d[1]));

        let container = svg.append('g').attr('id', 'container-' + position);
        container.append('path')
            .attr('d', cg(lineData))
            .attr('stroke', 'gray')
            .attr('stroke-width', 2)
            .attr('fill', 'none');

        let xAxis = d3.axisBottom().scale(x).ticks(0);
        container.append("g")
            .attr("class", "x axis")
            .attr("transform", `translate(0, ${position === 'overall'? h - padding : h / 2})`)
            .call(xAxis);
        container.select('.x.axis')
                 .append('text')
                 .attr('x', w - padding)
                 .attr('y', 20)
                 .style('fill', 'black')
                 .text('Query result')

        let yAxis = d3.axisLeft().scale(y).ticks(3);
        container.append("g")
            .attr("class", "y axis")
            .attr("transform", `translate(${padding}, 0)`)
            .call(yAxis);

        if(brushAble) {
          svg.append("clipPath")
              .attr("id", clipId)
              .append("rect")
              .attr("x", 200)
              .attr("y", 0)
              .attr("width", 0)
              .attr("height", h);

          container.append("path")
              .attr("stroke", "grey")
              .attr('d', cg(lineData))
              .attr("fill", "yellowgreen")
              .attr("fill-opacity", 0.5)
              .attr("fill-rule", "evenodd")
              .attr('clip-path', `url(#${clipId})`);
        }
        return x;
      },

      // 常规查询模拟方法
      initializeGeneralQuerySimulationView() {
        axios({
          url: 'http://127.0.0.1:8000/AttackSimulation/GetNoisyDataDistribution/',
          method: 'post',
          data: {
            'FileName': this.curFile,
            'QueryType': this.QueryType,
            'QueryAttr': this.QueryAttr,
            'Interval': [this.IntervalLeft, this.IntervalRight],
            'epsilon': this.epsilon,
            'sensitivityWay': this.SensitivityCalculationWay
          }
        }).then(response => {
          this.curB = response.data.b;
          let svg = d3.select('#GeneralQuery');
          let lineData = response.data.distribution;
          this.MakeResultDistribution(svg, lineData, 'overall', true, 'clip-accuracy');
          this.openGeneralQueryBrush(svg, 'clip-accuracy');
        })
      },
      openGeneralQueryBrush(svg, clipId) {
        let brush = d3.brush()
            .on('start', (e) => {
              svg.select('.brush').style('visibility', 'visible')
            })
            .on('brush', (e) => {
              let selection = e.selection;
              svg.select(`#${clipId} rect`)
                  .attr("x", selection[0][0])
                  .attr("width", selection[1][0] - selection[0][0]);
            })
            .on('end', (e) => {
              svg.select('.brush').style('visibility', 'hidden')
            })
        // .extent([
        //   [padding, 0],
        //   [w - padding, h - padding]
        // ])
        let brushG = svg.append('g').attr('class', 'brush');
        brushG.call(brush)
      },

      // 攻击模拟决策方法
      UpdateEpsilonWithPrivacy() {
        axios({
          url: 'http://127.0.0.1:8000/DpDecisionMaker/UpdateEpsilonWithPrivacy/',
          method: 'post',
          data: {
            'Deviation': this.PrivacyDeviation,
            'SRT': this.AttackSRT,
            'Sensitivity': this.curSensitivity
          }
        }).then(response => {
          this.epsilon = response.data.epsilon;
        })
      },

      // 常规查询决策方法
      UpdateEpsilonWithAccuracy() {
        axios({
          url: 'http://127.0.0.1:8000/DpDecisionMaker/UpdateEpsilonWithAccuracy/',
          method: 'post',
          data: {
            'Deviation': this.AccuracyDeviation,
            'SRT': this.AccuracySRT,
            'Sensitivity': this.curSensitivity
          }
        }).then(response => {
          this.epsilon = response.data.epsilon;
        })
      },

      resetEpsilon() {
        this.epsilon = 1.0;
      },


    },
    mounted() {
      let width = d3.select('.AS_view').style('width');
      d3.selectAll('.AS_view').style('height', width);
      d3.selectAll('.GQS_view').style('height', 180);

    }
  }
</script>

<style scoped>
  /***************** 容器style ******************/
  #Container {
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: row;
    background-color: #eff7fe;
  }
  .RowPartMain {
    width: calc(50% - 15px);
    height: calc(100% - 20px);
    margin: 10px;
  }
  .RowPartMain:first-child {
    margin-right: 5px;
  }
  .RowPartMain:nth-child(2) {
    margin-left: 5px;
  }
  
  .BaseMain {
    background-color: #fff;
  }
  
  #DifferentialRiskIdentification {
    width: 100%;
    height: calc(60% - 10px);
    margin-bottom: 10px;
  }

  #DataExploration {
    width: 100%;
    height: 40%;
  }
  /************************************************/

  /***************** 统一通用style ******************/
  .MainLabel {
    font-weight: bold;
    font-size: 20px;
    padding: 10px;
  }
  .SecondaryLabel {
    font-weight: bold;
    font-size: 15px;
    padding: 10px;
  }
  .Panel {
    width: calc(100% - 20px);
    height: 2em;
    line-height: 2em;

    padding: 0 0 0 10px;
    margin: 0 10px;
    border-radius: 10px;

    background-color: #efefef;


    display: flex;
    flex-direction: row;
  }

  .TextDivider {
    height: 100%;
    border-color: #333333
  }

  .rightEdgeBtn {
    border-top-right-radius: inherit;
    border-bottom-right-radius: inherit;
    margin-right: 0;
  }
  /***************** 树视图style ******************/
  #AttributeSet {
    width: 50%;
    height: 100%;
  }
  #AttributeSetTree {
    height: calc(100% - 37px);
    width: 100%;
  }
  #TreeView {
    display: flex;
    flex-direction: row;
    height: calc(100% - 40px);
  }
  #DifferentialQueryList {
    width: calc(50% - 1px);
  }

  #DataDistribution {
    width: 100%;
    height: calc(100% - 43px);
  }

  #DQTreeContainer {
    width: 100%;
    height: calc(100% - 37px);
  }

  #DifferentialQueryTree {
    width: 100%;
    height: 100%;
  }
  /**********************************************/

  .AS_view {
    flex: 1;
  }
  .QueryView {
    margin: 10px;
    border: #333333 2px dashed;

  }
  .SimulationViews {
    margin: 0 20px;
    display: flex;
    flex-direction: row;
  }

/****************************************/
  #SchemeHistory {
    border: 10px #eff7fe solid;
    flex: 1;
  }




  .InitialOverLay {
    z-index: 2001;
    background-color: rgba(240,240,240,0.8) !important;
    width: 100vw;
    height: 100vh;
    position: absolute;
    top: 0;
  }

  .SystemName {
    text-align: center;
    font-size: 50px;
    margin-top: 8vh;
  }

  .DataInput {
    width: 70%;
    height: 70vh;
    margin: 0 auto;
    margin-top: 15px;
    padding: 20px;
    background-color: #fff;
    border: 3px solid #afafaf;
    border-radius: 20px;

  }


  /**************************************/
  #DPS_Panel {
    margin-bottom: 20px;
  }
  .EpsilonInput {
    margin: 0 20px;
    width: 100px;
    border-radius: 7px;
  }
  .SCWO {
    border-radius: 7px;
  }
</style>