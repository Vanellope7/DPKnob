<template>
  <div id="Container">
    <div class="RowPartMain">
      <div id="DifferentialRiskIdentification" class="BaseMain">
        <div class="MainLabel">Differential Risk Identification</div>

        <div id="TreeView">
          <div id="AttributeSet">
            <div class="SecondaryLabel">Attribute Set Tree</div>
            <svg id="AttributeSetTreeLegend">
              <line x1="5" x2="35" y1="10" y2="10" stroke="rgb(234,120,119)" class="legendLine"></line>
              <text x="40" y="15">Non-Risk</text>
              <line x1="5" x2="35" y1="30" y2="30" stroke="rgb(136,192,203)" class="legendLine"></line>
              <text x="40" y="35">Risk</text>
            </svg>

            <svg id="AttributeSetTree"></svg>

          </div>

          <el-divider direction="vertical" border-style="dashed" style="height: 100%"/>

          <div id="DifferentialQueryList">
            <div class="SecondaryLabel">Query Condition List</div>
            <svg id="DQTreeAttrTitle"></svg>
            <div id="DQTreeContainer">
<!--              <svg id="DifferentialQueryTreeLegend">-->
<!--                <line x1="5" x2="35" y1="10" y2="10" stroke="rgb(234,120,119)" class="legendLine"></line>-->
<!--                <text x="40" y="15">Non-Risk</text>-->
<!--                <line x1="5" x2="35" y1="30" y2="30" stroke="rgb(136,192,203)" class="legendLine"></line>-->
<!--                <text x="40" y="35">Risk</text>-->
<!--              </svg>-->
              <svg id="DifferentialQueryTree"></svg>
            </div>
            <el-divider border-style="dashed" style="margin: 0" />
            <div id="CorrespondingSQLCommands">
              <div class="SecondaryLabel" style="text-align: center">Corresponding SQL Commands</div>

              <div id="firstQuery">
                <span id="firstSqlTitle" class="SqlTitle">1st query</span>
                <div id="FirstQueryText" class="SQLText"></div>
              </div>
              <el-divider border-style="dashed" style="margin: 0" />
              <div id="secondQuery">
                <span id="secondSqlTitle" class="SqlTitle">2nd query</span>
                <div id="SecondQueryText" class="SQLText"></div>
              </div>
            </div>
          </div>
        </div>

      </div>

      <div id="DataExploration" class="BaseMain">
        <div class="MainLabel">Data Exploration</div>
        <svg id="DataExplorationLegend">
          <line x1="5" x2="35" y1="10" y2="10" stroke="rgb(234,120,119)" class="legendLine"></line>
          <text x="40" y="15">Differential Record</text>
          <line x1="5" x2="35" y1="30" y2="30" stroke="rgb(136,192,203)" class="legendLine"></line>
          <text x="40" y="35">xxxx Record</text>
        </svg>
        <svg id="DataDistribution"></svg>
      </div>
    </div>

    <div class="RowPartMain BaseMain">
      <div class="MainLabel" style="margin-bottom: 10px">Data Query Simulation</div>


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
              :key="item"
              :label="item"
              :value="item"
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
              :key="item"
              :label="item"
              :value="item"
          />
        </el-select>

        <span style="padding-left: 20px">Type: </span>
        <el-select v-model="QueryType" @change="getNewAvgRiskP" placeholder="Select" style="width: 100px">
          <el-option
              v-for="item in QueryTypeOption"
              :key="item"
              :label="item"
              :value="item"
          />
        </el-select>

        <div class="Interval" v-if="QueryType === 'count' && QueryAttrType === 'numerical'">
          <span style="padding-left: 10px">Interval: </span>
          <el-input-number
              v-model="IntervalLeft"
              :min="attrInterval[0]"
              :max="IntervalRight"
              :step="0.01"
              controls-position="right"
              style="width: 100px"
          />
          <span>~</span>
          <el-input-number
              v-model="IntervalRight"
              :min="IntervalLeft"
              :max="attrInterval[1]"
              :step="0.01"
              controls-position="right"
              style="width: 100px"
          />
        </div>
        <div v-if="QueryType === 'count' && QueryAttrType === 'categorical'">
          <span style="padding-left: 20px">Category: </span>
          <el-select v-model="QueryCountCondition" placeholder="Select" style="width: 100px">
            <el-option
                v-for="item in attrList[QueryAttrIndex].Range"
                :key="item"
                :label="item"
                :value="item"
            />
          </el-select>
        </div>
      </div>


      <div class="SecondaryLabel">Attack Simulation</div>
      <div id="AS_Panel" class="Panel">
        <div >Recommendation</div>
        <el-divider direction="vertical" border-style="dashed" class="TextDivider"/>
        <span>Deviation: &plusmn;</span>
        <el-input-number
            v-model="PrivacyDeviation"
            :min="0"
            :max="MaxMap[QueryAttr] === undefined ? 10 : MaxMap[QueryAttr]"
            :step="0.01"
            controls-position="right"
            style="width: 80px"
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
        <el-button type="primary" class="rightEdgeBtn" @click="Update2PE">Update &epsilon; to {{privacyEpsilon}}</el-button>
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
            :max="MaxMap[QueryAttr] === undefined ? 10 : MaxMap[QueryAttr]"
            :step="0.01"
            controls-position="right"
            style="width: 80px"
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
        <el-button type="primary" class="rightEdgeBtn" @click="Update2AE">Update &epsilon; to {{accuracyEpsilon}}</el-button>
      </div>

      <div id="GeneralQuerySimulationViews" class="SimulationViews">
        <svg id="GeneralQuery" class="GQS_view QueryView"><text x="5" y="20">General query</text></svg>
        <div id="SchemeHistory">
          <div class="MainLabel">Scheme History</div>

          <el-table
              v-fit-columns
              :data="SchemeHistory"
              style="width: 100%; height: calc(100% - 43px)">
            <el-table-column
                v-for="attr in SchemeHistoryColumn"
                :prop="attr"
                :label="attr"
                align="center">
            </el-table-column>
          </el-table>

        </div>
      </div>

    </div>


  </div>

  <div class="InitialOverLay" v-if="DataInputVisible">
    <div class="SystemName">SystemName</div>
    <div class="DataInput">
      <DataInput
          @inputData="initializeTree"
          @drawPCP="initializeDataDistribution"
      />
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
        RiskMap: {},
        BSTMap: {},
        treeData: {},
        LineData: [],
        TableData: [],
        TableKeyData: [],
        keyMap: {},  //key 与 value的转化, 例如 0 -- [0, 20]
        curIndices: [],
        curAttrPos: [],
        curAttr: [],
        scale_Xscale: {},
        scaleMap: {},
        curIndex: [],
        curAttackTarget: {}, //记录攻击目标, 因为同一个攻击目标可以被不同的查询内容攻击

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
        QueryType: 'sum',
        QueryCountCondition: '',
        FirstQueryCondition: {},
        SecondQueryCondition: {},
        IntervalLeft: 5,
        IntervalRight: 35,
        PrivacyDeviation: 10,
        AttackSRT: 0.5,
        AccuracyDeviation: 10,
        AccuracySRT: 0.5,
        privateVal: 0,
        QueryAccurateVal: 0,

        privacyEpsilon: '1.0',
        accuracyEpsilon: '1.0',


        DA_OutputXscale: {},
        GQueryXscale: {},


        ExactVal: {'firstQuery': 0, 'secondQuery': 0},

        SchemeHistory: []
      }
    },
    computed: {
      QueryAttrIndex() {
        return this.attrList.findIndex(d => d.Name === this.QueryAttr);
      },
      QueryAttrType() {
        if(this.QueryAttrIndex === -1) return '';
        return this.attrList[this.QueryAttrIndex].Type;
      },
      SchemeHistoryColumn() {
        return this.SchemeHistory.length === 0 ? [] : Object.keys(this.SchemeHistory[0]);
      },
      QueryTypeOption() {
        // queryType 默认选择第一个
        if(this.QueryAttrType === 'numerical') {
          this.QueryType = 'sum';
          return ['sum', 'count', 'avg']
        }
        else if(this.QueryAttrType === 'categorical'){
          this.QueryType = 'count';
          if(this.QueryAttrIndex !== -1) {
            this.QueryCountCondition = this.attrList[this.QueryAttrIndex].Range[0];
          }
          return ['count', 'mode'];
        } else {
          return []
        }
      },
      attrInterval() {
        let index = this.attrList.findIndex(d => d.Name === this.QueryAttr);
        if(this.attrList[index].Type === 'numerical') {
          let scope = this.attrList[index].Range.split('~').map(d => parseFloat(d));
          [this.IntervalLeft, this.IntervalRight] = scope;
          return scope;
        }
        else {
          return []
        }
      },
      isFreshSimulationView({ QueryType, QueryAttr, IntervalLeft, IntervalRight, QueryCountCondition, FirstQueryCondtion, epsilon, SensitivityCalculationWay}) {
        // 集合Simulation View 刷新的变量 用于watch
        return { QueryType, QueryAttr, IntervalLeft, IntervalRight, QueryCountCondition, FirstQueryCondtion, epsilon, SensitivityCalculationWay};
      },
      // 是否更新AvgRiskP 结果
      isUpdateAvgRiskP({ QueryAttr, epsilon, curSensitivity}) {
        return { QueryAttr, epsilon, curSensitivity}
      }
    },
    methods: {
      //属性集树方法
      initializeTree([data, curFile, attrList]) {
        this.BSTMap = data.BSTMap;
        this.RiskMap = data.RiskMap;
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


        for(let node of nodes) {
          let bitmap = node.data.name;
          if(this.RiskMap[bitmap]) {
            this.ContextmenuNode(node)
            break;
          }
        }
        // 暂没考虑第一轮没有风险的情况
      },
      MakeTree(svg, nodes, links) {
        let outerRadius = 10;	//外半径
        let innerRadius = 5;	//内半径，为0则中间没有空白
        let that = this;
        let generator = d3
            .linkHorizontal()
            .x(function(d) {
              return d.x;
            })
            .y(function(d) {
              return d.y;
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
            .attr("fill", "none")
            .attr("stroke", "rgba(175, 175, 175, 0.8)")
            .attr("stroke-width", 1);
        // 统一边位置
        TreeLinkG
            .selectAll(".TreeLinkPath")
            .attr("d", function(d) {
              let start = { x: d.source.x + outerRadius / 2, y: d.source.y };
              let end = { x: d.target.x - outerRadius * 3 / 2, y: d.target.y };
              return generator({ source: start, target: end });
            })

        let TreeNode_DATA = TreeNodeG
            .selectAll(".TreeNodePie")
            .data(nodes);

        TreeNode_DATA.exit().remove();

        let Pie = TreeNode_DATA
            .enter()
            .append("g")
            .attr('id', d => `TreeNodePie${d.data.name}`)
            .attr("class", 'TreeNodePie');

        for (let i = 0; i < nodes.length; i++) { // 取出所有节点默认右键事件
          document.getElementsByClassName("TreeNodePie")[i].oncontextmenu = function () {
            return false;
          };
        }

        svg.selectAll('.TreeNodePie')
            .attr("transform", function(d) {
              let cx = d.x;
              let cy = d.y;
              return "translate(" + cx + "," + cy + ")";
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

        // 选中圆stroke
        Pie.append('circle')
            .attr('class', 'strokeCircle')
            .attr('id', d => 'strokeCircle' + d.data.name)
            .attr('r', 10)
            .attr('cx', -outerRadius / 2)
            .attr('cy', 0)
            .attr('fill', 'None')
            .attr('stroke', '#ccc')
            .attr('stroke-width', 0);

        // 风险圆stroke
        Pie.append('circle')
            .attr('class', 'RiskCircle')
            .attr('r', 10)
            .attr('cx', -outerRadius / 2)
            .attr('cy', 0)
            .attr('fill', 'None')
            .attr('stroke', '#e58e26')
            .attr('stroke-width', d => this.RiskMap[d.data.name] ? '5px' : 0);


        let color = ['rgba(234, 134, 133, 1.0)', 'rgba(64, 158, 255, 1.0)'];


        let childNodeRiskPie = Pie.selectAll(".childNodeRiskPie_path") //g用于把相关元素进行组合的容器元素
            .data(d => d3.pie().sort(null)(d.data.childNodeRiskPie))
            .enter()
            .append("g")
            .attr('class', 'childNodeRiskPie_path')
            .attr("transform","translate("+ -outerRadius / 2 +","+ 0 +")")
        let childNodeRiskArc = d3.arc()	//弧生成器
            .innerRadius(innerRadius)	//设置内半径
            .outerRadius(outerRadius);	//设置外半径
        childNodeRiskPie
            .append("path")
            .attr("fill",function(d,i){
              return color[i];
            })
            .attr("d",function(d){
              return childNodeRiskArc(d);
            });

        let curNodeRiskPie = Pie.selectAll(".curNodeRiskPie_path") //g用于把相关元素进行组合的容器元素
            .data(d => d3.pie().sort(null)(d.data.curNodeRiskPie))
            .enter()
            .append("g")
            .attr('class', 'curNodeRiskPie_path')
            .attr("transform","translate("+ -outerRadius / 2 +","+ 0 +")")
        let curNodeRiskArc = d3.arc()	//弧生成器
            .innerRadius(0)	//设置内半径
            .outerRadius(innerRadius);	//设置外半径
        curNodeRiskPie
            .append("path")
            .attr("fill",function(d,i){
              return color[i];
            })
            .attr("d",function(d){
              return curNodeRiskArc(d);
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
          nodes[i].x = Xscale(dim);
          nodes[i].y = YscaleList[dim](YscaleIndex[dim]);
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
              'indices': d.data.indices,
              'RiskMap': this.RiskMap
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
          let width = parseFloat(svg.style('width').split('px')[0]);
          let height = parseFloat(svg.style('height').split('px')[0]);
          let Nodes = newTreeData.descendants();
          let Links = newTreeData.links();
          [Nodes, Links] = this.PruningAndLayout(Nodes, Links, width, height, 3)
          this.MakeTree(svg, Nodes, Links);
        }
      },

      // 查询集树方法
      ContextmenuNode(d) {
        d3.selectAll('.strokeCircle').attr('stroke-width', 0);
        d3.select("#strokeCircle" + d.data.name).attr('stroke-width', '10px');
        this.initializeDifferQueryTree(d.data.indices);

      },
      initializeDifferQueryTree(indices) {
        axios({
          url: 'http://127.0.0.1:8000/RiskTree/BSTTreeData/',
          method: 'post',
          data: {
            'filename': this.curFile,
            'attrList': this.attrList,
            'indices': indices
          }
        }).then((response) => {
          this.curIndices = response.data.Indices;
          this.curAttr = this.curIndices.map(d => this.attrList[d].Name);
          let keyMap = this.keyMap = response.data.keyMap;
          let data = response.data.data;
          this.selectedAttr = response.data.selectedAttr;
          d3.selectAll('#DifferentialQueryTree > *').remove();


          let svg = d3.select("#DifferentialQueryTree")
          let width = parseFloat(svg.style('width').split('px')[0]);
          let height = parseFloat(svg.style('width').split('px')[0]);
          let container = svg
              .append("g")
              .attr("class", 'container')

          let TreeLinkG = container.append("g").attr("class", 'TreeLinkG');
          let TreeNodeG = container.append("g").attr("class", 'TreeNodeG');
          let DimensionG = container.append("g").attr("class", 'DimensionG');
          let hierarchyData = d3.hierarchy(data).sum(function(d) {
            return d.val;
          })
          .each(d => {
            if(d.parent) d.finalKey = `${d.parent.finalKey}-${d.data.key}`
            else d.finalKey = 'parent'
          });

          let treeFunc = d3
              .tree()
              .size([height, width])
              .separation(function(a, b) {
                return (a.parent === b.parent ? 1 : 2) / a.depth;
              });

          let treeData = treeFunc(hierarchyData);
          let nodes = treeData.descendants();
          let links = treeData.links();
          this.MakeDifferQueryTree(svg, nodes, links, keyMap, indices);
        })


      },
      getYScale(NodeHeight, NodePadding, leavesNum) {
        return d3.scaleLinear()
            .domain([1, leavesNum])
            .range([NodeHeight, (NodeHeight + NodePadding) * leavesNum])
      },
      encodeYIndex(nodes, dimNum) {
        let dimCurIndex = []
        for(let i = 0 ;i<dimNum; i++) {
          dimCurIndex.push(0);
        }
        for(let node of nodes) {
          let dim = node.data.dim;
          let val = node.value;
          node.yIndex = dimCurIndex[dim] + (1 + val) / 2;
          dimCurIndex[dim] += val;

        }
      },
      MakeDifferQueryTree(svg, nodes, links, keyMap, indices) {
        let width = parseFloat(svg.style('width').split('px')[0]);
        let NodeWidth = 70;
        let NodeHeight = 40;
        let NodePadding = 10;
        let DimensionTextHeight = 30;


        [nodes, keyMap] = this.TreePruning(nodes, keyMap);
        nodes = nodes.filter(d => d.depth > 0)
        links = links.filter(d => nodes.includes(d.source) && nodes.includes(d.target))
        // let finalKeyList = this.getFinalKeyList(nodes, keyMap.length);
        let leaves = nodes.filter(d => d.depth === keyMap.length);
        let leavesNum = leaves.length;
        let YScale = this.getYScale(NodeHeight, NodePadding, leavesNum);
        let height = (NodeHeight + NodePadding) * (leavesNum + 1);
        let containerHeight = parseFloat(d3.select('#DQTreeContainer').style('height').split('px')[0]);

        if(height > containerHeight)
          d3.select('#DQTreeContainer').style('overflow-y', 'scroll')
        else
          d3.select('#DQTreeContainer').style('overflow-y', 'hidden')
        svg.style('height', `${height}px`)

        this.encodeYIndex(nodes, keyMap.length);


        let Xscale = d3.scaleBand()
            .domain([-1, ...indices])
            .range([0, width]);

        let nodeColorScale = d3.scaleLinear()
            .domain([d3.min(nodes, d => d.data.num), d3.max(nodes, d => d.data.num)])
            .range(['#bbbbbb', '#777777'])


        for(let i in nodes) {
          let dim = nodes[i].data.dim;
          nodes[i].x = Xscale(indices[dim]);
          nodes[i].y = YScale(nodes[i].yIndex);
        }
        console.log(nodes)
        let generator = d3
            .linkHorizontal()
            .x(function(d) {
              return d.x;
            })
            .y(function(d) {
              return d.y;
            });
        let DimensionG = d3.select("#DQTreeAttrTitle").style('height', DimensionTextHeight + 'px');
        DimensionG.selectAll(".DimensionNodeG").remove();
        let DimensionG_DATA = DimensionG.selectAll(".DimensionNodeG").data(indices);
        let DimensionG_width = width / indices.length;
        let DimensionNodeG = DimensionG_DATA.enter()
            .append("g")
            .attr("class", 'DimensionNodeG')
            .attr("transform", d => `translate(${Xscale(d)}, 0)`)
            .call(this.AttrDrag(DimensionG_width / 2, width, indices.length))
        this.curAttrPos = indices.map((d, i) => i);
        console.log(this.curAttrPos)
        DimensionNodeG.append('rect')
            .attr('x', -DimensionG_width / 4)
            .attr('y', 0)
            .attr('width', DimensionG_width / 2)
            .attr('height', DimensionTextHeight)
            .attr('stroke', '#aaa')
            .attr('fill', 'none');

        DimensionNodeG.append('text')
            .attr('x', 0)
            .attr('y', 20)
            .style('text-anchor', 'middle')
            .text((d, k) => this.curAttr[k])

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
              let start = { x: d.source.x + NodeWidth / 2, y: d.source.y};
              let end = { x: d.target.x - NodeWidth / 2, y: d.target.y };
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

        svg.selectAll('.TreeNodePie')
            .attr("transform", function(d) {
              let cx = d.x;
              let cy = d.y;
              return "translate(" + cx + "," + cy + ")";
            })
            .on('mouseover', (e, d) => {
              TreeLinkPath.filter(link => link.source !== d)
                  .classed('nonHighlightEdge', true);

            })
            .on('mouseout', (e, d) => {
              TreeLinkPath.classed('nonHighlightEdge', false);
            })


        NodesG.append("rect")
            .attr('class', 'RectNode')
            .attr("x", -NodeWidth / 2)
            .attr("y", -NodeHeight / 2)
            .attr("height", NodeHeight)
            .attr("width", NodeWidth)
            .attr('stroke', '#ccc')
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
              .attr('x', 1)
              .attr('y', 5)
              .text(d => {
                let dim = d.data.dim;
                let index = this.keyMap[dim].data.indexOf(d.data.key);
                return this.keyMap[dim].text[index];
              });

        // 自动选取默认攻击目标
        if(leaves.length > 0) {
          let defaultNode = leaves[0];
          // 获取真正的风险节点
          while(defaultNode.parent.data.isBST) {
            defaultNode = defaultNode.parent;
          }
          this.clickQueryNode(defaultNode);
        }


      },
      TreePruning(nodes, keyMap) {
        // 对nodes剪枝
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

        // 对keymap剪枝
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
      AttrDrag(rect_width, width, num) {
        let DimensionG_Pos = width / (num + 1);
        let scale = d3.scaleLinear().domain([0, num - 1]).range([DimensionG_Pos, width - DimensionG_Pos]);
        let that = this;

        function dragged(event, d) {
          let pos = that.curAttrPos;
          let newX = event.x;
          // console.log(newX);
          // console.log(DimensionG_Pos)
          // 调整拖动元素位置
          d3.select(this)
              .attr("transform", (d, i) => `translate(${event.x}, 0)`)
          let preIndex = pos[that.curIndices.indexOf(d)];
          let curIndex = Math.round(scale.invert(newX))

          if (curIndex > num - 1) {
            curIndex = num - 1
          }
          if(curIndex < 0) {
            curIndex = 0
          }
          console.log(preIndex, curIndex, preIndex < curIndex)
          if (preIndex < curIndex) {
            // 右移
            pos.forEach((d, i) => {
              if (d === curIndex) {
                pos[i] -= 1;
              }
              if (d === preIndex) {
                pos[i] = curIndex
              }
            });
            d3.selectAll('.DimensionNodeG')
                .attr("transform", (d, i) => `translate(${scale(pos[i])}, 0)`)
          } else {
            if (preIndex > curIndex) {
              // 左移
              pos.forEach((d, i) => {
                if (d === curIndex) {
                  pos[i] += 1;
                }
                if (d === preIndex) {
                  pos[i] = curIndex
                }
              });
              d3.selectAll('.DimensionNodeG')
                  .attr("transform", (d, i) => {
                    return `translate(${scale(pos[i])}, 0)`
                  })
            }
          }
        }
        function ended() {
          let pos = that.curAttrPos;
          console.log(pos)
          d3.selectAll('.DimensionNodeG')
              .attr("transform", (d, i) => {
                return `translate(${scale(pos[i])}, 0)`
              });
          that.curIndices = that.curIndices.map((d, i, list) => list[pos[i]]);
          that.curAttr = that.curIndices.map(d => that.attrList[d].Name);
          that.initializeDifferQueryTree(that.curIndices);
        }

        let drag = d3.drag()
            .on("drag", dragged)
            .on('end', ended);
        return drag;
      },

      //平行坐标图方法
      clickQueryNode(d) {
        // 高亮节点
        d3.selectAll('.RectNode').attr('stroke-width', 0);
        d3.selectAll('.RectNode').filter(node => node === d).attr('stroke-width', '10px');


        // 先不考虑单节点情况
        this.curIndex = d.parent.data.index;
        for(let d of this.LineData) {
          d['highlight'] = false;
        }
        for(let i of this.curIndex) {
          this.LineData[i]['highlight'] = 'rgb(136,192,203)';
        }
        this.LineData[d.data.index[0]]['highlight'] = 'rgb(234,120,119)'
        d3.selectAll('.cloneLineG').remove();


        // 保证红线在蓝色上面
        let blueCloneLinePath = d3.selectAll('.LineG')
            .filter(d => d.highlight === 'rgb(136,192,203)')
            .select(function() {
              return this.parentNode.insertBefore(this.cloneNode(true), null);
            })
            .attr('class', 'cloneLineG blueLine')
        let resCloneLinePath = d3.selectAll('.LineG')
            .filter(d => d.highlight === 'rgb(234,120,119)')
            .select(function() {
              return this.parentNode.insertBefore(this.cloneNode(true), null);
            })
            .attr('class', 'cloneLineG redLine')
        d3.selectAll('.cloneLineG')
            .select('path')
            .attr('stroke', d => d.highlight)
            .attr('stroke-width', 2);

        let keyList, valueList = [];
        keyList = d.finalKey.split('parent-')[1].split('-');
        keyList.pop();

        let FirstQueryText = 'WHERE ';
        // 条件清空
        this.FirstQueryCondition = {};
        this.SecondQueryCondition = {};
        for(let [i, key] of Object.entries(keyList)) {
          key = parseInt(key);
          let obj = this.keyMap[i];
          let text = obj.text[obj.data.indexOf(key)]
          if (obj.type === 'numerical') {
            let splitEdge = text.split('~');
            splitEdge = splitEdge.map(d => parseInt(d))
            valueList.push(splitEdge);

            FirstQueryText += `<span class="blueFont">${this.curAttr[i]} BETWEEN ${splitEdge[0]} AND ${splitEdge[1]}</span>`
            this.FirstQueryCondition[this.curAttr[i]] ? '' : this.FirstQueryCondition[this.curAttr[i]] = [];
            this.FirstQueryCondition[this.curAttr[i]].push(splitEdge);
          } else {
            valueList.push(text)
            FirstQueryText += `${this.curAttr[i]} = ${text}`;
            this.FirstQueryCondition[this.curAttr[i]] ? '' : this.FirstQueryCondition[this.curAttr[i]] = [];
            this.FirstQueryCondition[this.curAttr[i]].push(text);
          }
          if(parseInt(i) !== keyList.length - 1) {
            FirstQueryText += '<br/>AND '
          }
        }
        // 设置Corresponding SQL Commands
        if(keyList.length === 0) {
          FirstQueryText = 'WHERE 1=1'
        }
        d3.select("#FirstQueryText")
          .html(FirstQueryText)


        let finalKeyList = new Set();
        let RiskIndex = d.data.index[0];
        let finalRiskKey = d.data.key;
        let finalAttr = this.curIndices[this.curIndices.length - 1];
        let finalAttrName = this.curAttr[this.curAttr.length - 1]
        let largerFinalKeyScope = [0, -1], smallerFinalKeyScope = [0, -1];
        let upperScope = [0, 0], lowerScope = [0, 0]
        for(let index of this.curIndex) {
          finalKeyList.add(this.TableKeyData[index][finalAttr])
        }

        let SecondQueryText = FirstQueryText;
        this.SecondQueryCondition = JSON.parse(JSON.stringify(this.FirstQueryCondition));
        // 删除风险节点的key
        finalKeyList.delete(this.TableKeyData[RiskIndex][finalAttr]);
        finalKeyList = Array.from(finalKeyList)
        let obj = this.keyMap[this.curIndices.length - 1];
        let flag = false;
        let largerFinalKeyList = finalKeyList.filter(d => d > finalRiskKey);
        if(largerFinalKeyList.length !== 0) {
          largerFinalKeyScope = [Math.min(...largerFinalKeyList), Math.max(...largerFinalKeyList)];
          let text1 = obj.text[obj.data.indexOf(largerFinalKeyScope[0])]
          let text2 = obj.text[obj.data.indexOf(largerFinalKeyScope[1])]
          if (obj.type === 'numerical') {
            upperScope = [text1.split('~')[0], text2.split('~')[1]]
            if(upperScope[0] !== upperScope[1]) {
              flag = true; //给lower判断是否需要加 or
              SecondQueryText += `<br/>AND <span class="redFont">(${finalAttrName} BETWEEN ${upperScope[0]} AND ${upperScope[1]}</span>`
              this.SecondQueryCondition[finalAttrName] ? '' : this.SecondQueryCondition[finalAttrName] = [];
              this.SecondQueryCondition[finalAttrName].push(upperScope);
            }
          }
          else {
            upperScope = [text2, largerFinalKeyScope[1] - largerFinalKeyScope[0] + 1]

            let SQL_in_list = []
            for(let key of finalKeyList) {
              SQL_in_list.push(`'${obj.text[obj.data.indexOf(key)]}'`)
            }
            SecondQueryText += `<span class="redFont">${finalAttrName} IN (${SQL_in_list.join(' ')})</span>`;
            this.SecondQueryCondition[finalAttrName] ? '' : this.SecondQueryCondition[finalAttrName] = [];
            this.SecondQueryCondition[finalAttrName].push(...SQL_in_list);
          }

        }
        let smallerFinalKeyList = finalKeyList.filter(d => d < finalRiskKey);
        if(smallerFinalKeyList.length !== 0) {
          smallerFinalKeyScope = [Math.min(...smallerFinalKeyList), Math.max(...smallerFinalKeyList)];
          let text1 = obj.text[obj.data.indexOf(smallerFinalKeyScope[0])]
          let text2 = obj.text[obj.data.indexOf(smallerFinalKeyScope[1])]
          if (obj.type === 'numerical') {
            lowerScope = [text1.split('~')[0], text2.split('~')[1]];
            if(lowerScope[0] !== lowerScope[1]) {
              if(flag) {
                SecondQueryText += `<br/>OR <span class="redFont">${finalAttrName} BETWEEN ${lowerScope[0]} AND ${lowerScope[1]})</span>`
              }
              else {
                SecondQueryText += `<br/>AND <span class="redFont">${finalAttrName} BETWEEN ${lowerScope[0]} AND ${lowerScope[1]}</span>`
              }

              this.SecondQueryCondition[finalAttrName] ? '' : this.SecondQueryCondition[finalAttrName] = [];
              this.SecondQueryCondition[finalAttrName].push(lowerScope);
            }
            else {
              if(flag) {
                SecondQueryText.replace('(', '');
              }
            }
          }
          else {
            lowerScope = [text2, smallerFinalKeyScope[1] - smallerFinalKeyScope[0] + 1];
          }
        }



        d3.select("#SecondQueryText")
            .html(SecondQueryText)


        // 单独合成最后一个键
        let svg = d3.select('#DataDistribution');
        svg.select('.maskG')
            .selectAll('.finalMaskG')
            .remove();
        svg.select('.maskG')
            .selectAll('.finalMaskG')
            .data([upperScope, lowerScope])
            .join('g')
            .attr('class', 'finalMaskG')
            .attr('transform', (d) =>{
              let x = d[0];
              return `translate(${this.scale_Xscale(finalAttr)}, ${this.scaleMap[finalAttrName](x)})`
            })
            .append('rect')
            .attr("x", -10)
            .attr("y", (d) => {
              if (obj.type === 'numerical') {
                return this.scaleMap[finalAttrName](d[1]) - this.scaleMap[finalAttrName](d[0])
              }
              else {
                return 0
              }
            })
            .attr('width', '20px')
            .attr("height", (d, k) => {
              if (obj.type === 'numerical') {
                return this.scaleMap[finalAttrName](d[0]) - this.scaleMap[finalAttrName](d[1])
              }
              else {
                return this.scaleMap[finalAttrName].bandwidth() * d[1];
              }
            })
            .attr('fill', 'rgba(255,255,172,0.8)')
            .style('stroke', '#aaaaaa')





        let MaskNodeData = svg.select('.maskG').selectAll('.MaskNodeG').data(valueList);
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


        console.log(this.FirstQueryCondition);
        console.log(this.SecondQueryCondition);

        this.initializeAttackSimulationViews(d);
        this.curAttackTarget = d;
      },
      initializeDataDistribution(response) {

        let data = response.data;
        let ScaleData = data.ScaleData;
        this.MaxMap = data.MaxMap;
        let TableData = this.TableData = data.TableData;
        this.TableKeyData = data.TableKeyData;
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

        svg.append("marker")
            .attr("id", "arrow")
            .attr("markerUnits","strokeWidth")//设置为strokeWidth箭头会随着线的粗细发生变化
            .attr("viewBox", "0 0 12 12")//坐标系的区域
            .attr("refX", 6)//箭头坐标
            .attr("refY", 6)
            .attr("markerWidth", 12)
            .attr("markerHeight", 12)
            .attr("orient", "auto")//绘制方向，可设定为：auto（自动确认方向）和 角度值
            .append("path")
            .attr("d", "M2,2 L10,6 L2,10 L6,6 L2,2")//箭头的路径
            .attr('fill', '#333');//箭头颜色



        let maskG = svg.append('g').attr('class', 'maskG');
        let axisG = svg.selectAll('.axis')
           .data(ScaleData)
           .enter()
           .append('g')
           .attr('class', 'axis')
           .attr('transform', (d, k) => `translate(${scale_Xscale(k)}, ${0})`)
           .each(function(d, k) {
             d3.select(this).call(d3.axisLeft().scale(scaleMap[d.name]).tickSizeOuter(0).ticks(0));
           });
        svg.selectAll('.axis')
           .select('path')
            .attr("marker-end","url(#arrow)");


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
      },

      // 攻击模拟方法
      initializeAttackSimulationViews(d) {
        axios({
          url: 'http://127.0.0.1:8000/AttackSimulation/GetNoisyDataDistribution/',
          method: 'post',
          data: {
            'FileName': this.curFile,
            'QueryType': this.QueryType,
            'QueryAttr': this.QueryAttr,
            'Interval': this.QueryAttrType === 'numerical' ? [this.IntervalLeft, this.IntervalRight] : this.QueryCountCondition,
            'QueryCondition': this.FirstQueryCondition,
            'epsilon': this.epsilon,
            'sensitivityWay': this.SensitivityCalculationWay
          }
        }).then(response => {
          this.ExactVal['firstQuery'] = response.data.ExactVal;
          this.curB = response.data.b;
          this.curSensitivity = response.data.sensitivity;
          let svg = d3.select('#FirstQuery');
          let lineData = this.firstQueryData = response.data.distribution;
          this.MakeResultDistribution(svg, lineData, 'top-half');

          // 画第二次查询和差分结果图
          // 原因: 第二次查询可由第一次查询得到, 差分结果分布需要知道敏感度,由第一次查询得到
          if(d.data.index.length === 1) {
            this.setAttackTarget(this.TableData[d.data.index[0]])
          }
          // 初始化常规查询视图
          this.initializeGeneralQuerySimulationView()
        })
      },
      setAttackTarget(data) {
        // 假设攻击目标满足条件
        if(this.QueryType === 'count') {
          if(this.QueryAttrType === 'numerical') {
            this.privateVal = (data[this.QueryAttr] > this.IntervalLeft) && (data[this.QueryAttr] < this.IntervalRight)
          }
          else {
            this.privateVal = data[this.QueryAttr] === this.QueryCountCondition
          }
        }
        else {
          this.privateVal = data[this.QueryAttr]
        }
        let targetResult = this.privateVal;
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
          [this.DA_OutputXscale] = this.MakeResultDistribution(svg, lineData, 'overall', true, 'clip-privacy');
          this.openDA_OutputBrush(svg, 'clip-privacy');
        })

      },
      openDA_OutputBrush(svg, clipId) {
        let padding = 40, w = parseFloat(svg.style('width').split('px')[0]);
        let h = parseFloat(svg.style('height').split('px')[0]);
        let brush = d3.brushX()
                      .on('start', (e) => {
                        svg.select('.brush').style('visibility', 'hidden')
                      })
                      .on('brush', (e) => {
                        let selection = e.selection;
                        svg.select('.leftBrushEdge')
                            .attr("x1", selection[0])
                            .attr("x2", selection[0]);

                        svg.select('.rightBrushEdge')
                            .attr("x1", selection[1])
                            .attr("x2", selection[1]);
                      })
                      .on('end', (e) => {
                        let selection = e.selection;
                        let [left, right] = [selection[0], selection[1]]
                        let [X0, X1] = [this.DA_OutputXscale.invert(left), this.DA_OutputXscale.invert(right)]
                        console.log([left, right], [X0, X1] )
                        this.MakeOppositeProbability([X0, X1])
                      })
                  .extent([
                    [padding, padding],
                    [w - padding, h - padding]
                  ])
        let initialPos = [this.DA_OutputXscale(this.privateVal - this.PrivacyDeviation), this.DA_OutputXscale(this.privateVal + this.PrivacyDeviation)]
        svg.select('.container-overall').append('g').attr('class', 'brush').call(brush).call(brush.move, initialPos);

      },
      MakeOppositeProbability(interval) {
        axios({
          url: 'http://127.0.0.1:8000/AttackSimulation/GetOppositeProbability/',
          method: 'post',
          data: {
            'ExactVal': this.ExactVal,
            'interval': interval,
            'b': this.curB,
            'domainDeviation': this.curSensitivity * 2
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
            yRange = [h / 2, h - padding]
            break;
          case 'overall':
            yRange = [h - padding, padding]
        }
        let svgId = svg.attr('id');
        let lineDataLen = lineData.length;
        svg.selectAll(`.container-${position}`).remove();
        let x = d3.scaleLinear()
            .domain([lineData[0][0], lineData[lineDataLen - 1][0]])
            .range([padding, w - padding])
            .clamp(true);  //原因是定义域为止  暂时这么做为了保险
        let ymax = d3.max(lineData, d => d[1]);
        let ymin = d3.min(lineData, d => d[1]);
        let y = d3.scaleLinear()
            .domain([0, ymax])
            .range(yRange);
        let cg = d3.line()
            .x(d => x(d[0]))
            .y(d => y(d[1]));


        let container = svg.append('g').attr('class', 'container-' + position);
        container.append('path')
            .attr('d', cg(lineData))
            .attr('stroke', 'gray')
            .attr('stroke-width', 2)
            .attr('fill', 'none');

        let trueVal = (lineData[0][0] + lineData[lineDataLen - 1][0]) / 2;
        if(position !== 'bottom-half') {
          container.append('line')
              .attr('x1', x(trueVal))
              .attr('x2', x(trueVal))
              .attr('y1', y(0))
              .attr('y2', y(ymax))
              .attr('stroke', 'gray')
              .attr('stroke-width', 2)
              .attr('fill', 'none')
              .style('stroke-dasharray', '3, 2')
          container.append('text')
              .attr('font-size', '10px')
              .attr('x', x(trueVal) + 5)
              .attr('y', yRange[0] - 10)
              .text(Math.floor(trueVal));
        }

        let xAxis = d3.axisBottom().scale(x).tickSizeOuter(0).ticks(3);
        container.append("g")
            .attr("class", "x axis")
            .attr("transform", `translate(0, ${position === 'overall'? h - padding : h / 2})`)
            .call(xAxis);
        container.select('.x.axis')
                 .append('text')
                 .attr('x', w - padding)
                 .attr('y', 30)
                 .style('fill', 'black')
                 .text(() => {
                   if(clipId === 'clip-privacy') {
                     return 'Attack result';
                   }
                   else if (clipId === 'clip-accuracy') {
                     return 'Deviation';
                   }
                   else {
                     return 'Query result';
                   }
                 })

        let yAxis = d3.axisLeft().scale(y).tickSizeOuter(0).ticks(3);
        container.append("g")
            .attr("class", "y axis")
            .attr("transform", `translate(${padding}, 0)`)
            .call(yAxis);

        svg.selectAll('.axis')
            .select('path')
            .attr("marker-end","url(#arrow)");

        if(brushAble) {
          let deviation = clipId === 'clip-accuracy'? this.AccuracyDeviation : this.PrivacyDeviation;
          // brush的边界
          if(clipId === 'clip-privacy') {
            container.append('line')
                .attr('x1', x(trueVal - deviation))
                .attr('x2', x(trueVal - deviation))
                .attr('y1', y(0))
                .attr('y2', y(ymax))
                .attr('class', 'leftBrushEdge')
                .attr('stroke', 'gray')
                .attr('stroke-width', 2)
                .attr('fill', 'none')
            container.append('line')
                .attr('x1', x(trueVal + deviation))
                .attr('x2', x(trueVal + deviation))
                .attr('y1', y(0))
                .attr('y2', y(ymax))
                .attr('class', 'rightBrushEdge')
                .attr('stroke', 'gray')
                .attr('stroke-width', 2)
                .attr('fill', 'none');
          }

          // 画deviation边界
          container.append('line')
              .attr('x1', x(trueVal - deviation))
              .attr('x2', x(trueVal - deviation))
              .attr('y1', y(0))
              .attr('y2', y(ymax))
              .attr('class', 'leftDeviationEdge')
              .attr('stroke', 'gray')
              .attr('stroke-width', 2)
              .attr('fill', 'none')
              .attr('stroke-dasharray', '3, 2')
          container.append('line')
              .attr('x1', x(trueVal + deviation))
              .attr('x2', x(trueVal + deviation))
              .attr('y1', y(0))
              .attr('y2', y(ymax))
              .attr('class', 'rightDeviationEdge')
              .attr('stroke', 'gray')
              .attr('stroke-width', 2)
              .attr('fill', 'none')
              .attr('stroke-dasharray', '3, 2')

          // svg.append("clipPath")
          //     .attr("id", clipId)
          //     .append("rect")
          //     .attr("x", 200)
          //     .attr("y", 0)
          //     .attr("width", 0)
          //     .attr("height", h);
          //
          // container.append("path")
          //     .attr("stroke", "#aaa")
          //     .attr('d', cg(lineData))
          //     .attr("fill", 'None')
          //     .attr("fill-opacity", 0.5)
          //     .attr("fill-rule", "evenodd")
          //     .attr('clip-path', `url(#${clipId})`);
          //
          // container.append("rect")
          //     .attr('class', 'bottomClipRect')
          //     .attr("x", 0)
          //     .attr("y", y(ymin))
          //     .attr("height", yRange[0] - y(ymin))
          //     .attr("width", 0)
          //     .attr("fill", "None")
          //     .attr("fill-opacity", 0.5)
          //     .attr('stroke', '#aaa')
          //     .attr('stroke-dasharray', '3, 2')

        }
        return [x, trueVal];
      },

      // 常规查询模拟方法
      initializeGeneralQuerySimulationView() {
        let svg = d3.select('#GeneralQuery');
        let lineData = this.firstQueryData;
        [this.GQueryXscale, this.QueryAccurateVal] = this.MakeResultDistribution(svg, lineData, 'overall', true, 'clip-accuracy');
      },

      // 攻击模拟决策方法
      UpdateEpsilonWithPrivacy() {
        axios({
          url: 'http://127.0.0.1:8000/DpDecisionMaker/UpdateEpsilonWithPrivacy/',
          method: 'post',
          data: {
            'Deviation': this.PrivacyDeviation,
            'SRT': this.AttackSRT,
            'Sensitivity': this.curSensitivity,
            'QueryType': this.QueryType
          }
        }).then(response => {
          this.privacyEpsilon = response.data.epsilon;
        })
      },
      Update2PE() {
        this.epsilon = this.privacyEpsilon;
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
          this.accuracyEpsilon = response.data.epsilon;
        })
      },
      Update2AE() {
        this.epsilon = this.accuracyEpsilon;
      },

      getNewAvgRiskP() {
        axios({
          url: 'http://127.0.0.1:8000/RiskTree/AvgRiskP/',
          method: 'post',
          data: {
            'filename': this.curFile,
            'deviation': this.attrList[this.QueryAttrIndex]['Tolerance Deviation'],
            'attrParams': this.attrList,
            'attr': this.QueryAttr,
            'epsilon': this.epsilon,
            'BSTMap': this.BSTMap,
            'type': this.QueryType, // type更改用监听select事件来弄,因为attr修改会直接引起type修改,不能对type监听
            'sensitivity': this.curSensitivity
          }
        }).then(response => {
          this.SchemeHistory.push({
            'Epsilon': this.epsilon,
            'Attr': this.QueryAttr,
            'Query Type': this.QueryType,
            'Average Risk P': response.data.avgRiskP.toFixed(5)
          })
        })
      }
    },
    watch: {
      'PrivacyDeviation': {
        handler(newVal, oldVal) {
          d3.select('#DA_Output .leftDeviationEdge')
              .attr('x1', this.DA_OutputXscale(this.privateVal - newVal))
              .attr('x2', this.DA_OutputXscale(this.privateVal - newVal))
          d3.select('#DA_Output .rightDeviationEdge')
              .attr('x1', this.DA_OutputXscale(this.privateVal + newVal))
              .attr('x2', this.DA_OutputXscale(this.privateVal + newVal))
          this.UpdateEpsilonWithPrivacy();
        },
        deep: true,
        immediate: false
      },
      'AttackSRT': {
        handler(newVal, oldVal) {
          this.UpdateEpsilonWithPrivacy();
        },
        deep: true,
        immediate: false
      },
      'AccuracyDeviation': {
        handler(newVal, oldVal) {
          d3.select('#GeneralQuery .leftDeviationEdge')
              .attr('x1', this.GQueryXscale(this.QueryAccurateVal - newVal))
              .attr('x2', this.GQueryXscale(this.QueryAccurateVal - newVal))
          d3.select('#GeneralQuery .rightDeviationEdge')
              .attr('x1', this.GQueryXscale(this.QueryAccurateVal + newVal))
              .attr('x2', this.GQueryXscale(this.QueryAccurateVal + newVal))
          this.UpdateEpsilonWithAccuracy();
        },
        deep: true,
        immediate: false
      },
      'AccuracySRT': {
        handler(newVal, oldVal) {
          this.UpdateEpsilonWithAccuracy();
        },
        deep: true,
        immediate: false
      },
      'curSensitivity': {
        handler(newVal, oldVal) {
          this.UpdateEpsilonWithAccuracy();
          this.UpdateEpsilonWithPrivacy();
        },
        deep: true,
        immediate: false
      },
      'isFreshSimulationView': {
        handler(newVal, oldVal) {
          if(Object.keys(this.curAttackTarget).length !== 0)
            this.initializeAttackSimulationViews(this.curAttackTarget);
        },
        deep: true,
        immediate: false
      },
      'isUpdateAvgRiskP': {
        handler(newVal, oldVal) {
          if(this.curSensitivity !== 0) {
            this.getNewAvgRiskP();
          }
        },
        deep: true,
        immediate: false
      }
    },
    mounted() {
      let width = d3.select('.AS_view').style('width');
      d3.selectAll('.AS_view').style('height', width);
      d3.select('#GeneralQuery').style('height', width).style('width', width);
      d3.select('#GeneralQuerySimulationViews').style('height', width)
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
    position: relative;
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

  #DataExplorationLegend {
    position: absolute;
    top: 5px;
    right: 5px;
    width: 200px;
  }

  .legendLine {
    stroke-width: 5px;
  }
  /************************************************/

  /***************** 统一通用style ******************/
  .MainLabel {
    font-weight: bold;
    font-size: 20px;
    padding: 10px;
  }
  .SecondaryLabel {
    margin-top: 1%;
    font-weight: bold;
    font-size: 15px;
    padding: 1%;
  }
  .Panel {
    width: calc(100% - 20px);
    line-height: 2em;

    padding: 5px 0 5px 10px;
    margin: 0 10px;
    border-radius: 10px;

    background-color: #efefef;


    display: flex;
    flex-direction: row;
  }

  .TextDivider {
    height: 2em;
    border-color: #333333
  }

  .rightEdgeBtn {
    border-top-right-radius: inherit;
    border-bottom-right-radius: inherit;
    margin-right: 0;
  }

  .SqlTitle {
    width: 30%;
    padding-left: 10px;
  }

  .SQLText {
    font-size: 10px;
  }


  /***************** 树视图style ******************/
  #AttributeSet {
    width: 50%;
    height: 100%;
    position: relative;
  }
  #AttributeSetTree {
    height: calc(100% - 37px);
    width: 100%;
  }
  #AttributeSetTreeLegend {
    position: absolute;
    top: 30px;
    right: 5px;
    width: 120px;
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
    height: calc(100% - 37px - 30px - 120px);
    overflow-x: hidden;
    overflow-y: hidden;
    position: relative;
  }

  /*#DifferentialQueryTreeLegend {*/
  /*  position: absolute;*/
  /*  top: 30px;*/
  /*  right: 5px;*/
  /*  width: 120px;*/
  /*}*/

  #DifferentialQueryTree {
    width: 100%;
    height: 100%;
  }
  #DQTreeAttrTitle {
    width: 100%;
    height: 30px;
  }
  #CorrespondingSQLCommands {
    height: 120px;
  }

  #firstQuery, #secondQuery {
    display: flex;
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
    margin: 2.5% 20px;
    display: flex;
    flex-direction: row;
  }

/****************************************/
  #SchemeHistory {
    border: 10px #eff7fe solid;
    flex: 1;

    position: relative;
    left: 20px;
    top: 13px;
  }




  .InitialOverLay {
    z-index: 2001;
    background-color: rgba(240,240,240,0.8) !important;
    width: 100%;
    height: 100%;
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
    margin-bottom: 1%;
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

<style>
  .blueFont {
    color: #74b9ff;
    line-height: 1em;
  }
  .redFont {
    color: #ff7675;
    line-height: 1em;
  }
  br {
    height: 0;
  }

</style>