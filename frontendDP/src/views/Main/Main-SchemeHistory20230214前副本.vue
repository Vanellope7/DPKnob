<template>
  <div id="Container">
    <div class="RowPartMain">
      <div id="DifferentialRiskIdentification" class="BaseMain">
        <div class="MainLabel">Differential Risk Identification</div>

        <div id="TreeView">
          <div id="AttributeSet">
            <div class="SecondaryLabel">Attribute Set Tree</div>
            <svg id="AttributeSetTreeLegend">
              <rect x="30" y="20" width="10" height="10" :fill="colorMap['grey-normal']"></rect>
              <text x="45" y="29">Non-Risk</text>
              <rect x="100" y="20" width="10" height="10" :fill="colorMap['risk']"></rect>
              <text x="115" y="29">Risk</text>
            </svg>

            <svg id="AttributeSetTree"></svg>

          </div>

          <el-divider direction="vertical" border-style="dashed" style="height: 100%"/>

          <div id="DifferentialQueryList">
            <div class="SecondaryLabel">Query Condition List</div>
            <svg id="DifferentialQueryTreeLegend">
<!--              <rect x="30" y="0" width="10" height="10" :fill="colorMap['grey-normal']"></rect>-->
<!--              <text x="45" y="9">Normal query condition</text>-->
              <rect x="30" y="5" width="10" height="10" :fill="colorMap['risk']"></rect>
              <text x="45" y="14">Differential query condition</text>
              <rect v-for="(d, i) in queryNumLegend"
                    :x="45+i"
                    :y="18"
                    width="1.5"
                    height="10"
                    :fill="d"
              ></rect>
              <text x="40" y="27" text-anchor="end">{{MinRecordsNum}}</text>
              <text x="150" y="27">{{MaxRecordsNum}}</text>
              <text x="40" y="37"># Records in query result</text>
            </svg>
            <svg id="DQTreeAttrTitle"></svg>
            <div id="DQTreeContainer">
              <svg id="DifferentialQueryTree"></svg>
            </div>
            <el-divider border-style="dashed" style="margin: 0" />
            <div id="CorrespondingSQLCommands">
              <div class="SecondaryLabel" style="margin-bottom: 0">Corresponding SQL Commands</div>

              <div class="SQL_panel">
                <div id="firstQuery" class="SQL">
                  <span id="firstSqlTitle" class="SqlTitle">1st query</span>
                  <el-divider direction="vertical" border-style="dashed" class="TextDivider"/>
                  <div id="FirstQueryText" class="SQLText"></div>
                </div>
                <div id="secondQuery" class="SQL">
                  <span id="secondSqlTitle" class="SqlTitle">2nd query</span>
                  <el-divider direction="vertical" border-style="dashed" class="TextDivider"/>
                  <div id="SecondQueryText" class="SQLText"></div>
                </div>
              </div>
            </div>
          </div>
        </div>

      </div>

      <div id="DataExploration" class="BaseMain">
        <div class="MainLabel">Data Exploration</div>
        <el-button-group class="DataExplorationSwitch">
          <el-button :class="{chosenBtn: DataExplorationStatus === 'RT'}" type="primary" size="small"
           @click="switch2RecordTable">Record Table</el-button>
          <el-button :class="{chosenBtn: DataExplorationStatus === 'DD'}" type="primary" size="small"
          @click="switch2DataDistribution">Data Distribution</el-button>
        </el-button-group>

        <div class="tickSwitch">
          <el-switch
              v-model="DE_tick"
              class="switchTick"
              active-text="Show tick"
              inactive-text="Hide tick"
              @change="changeTickStatus"
          />
        </div>

        <svg id="DataExplorationLegend">
          <line x1="5" x2="35" y1="10" y2="10" :stroke="colorMap['risk']" class="legendLine"></line>
          <text x="40" y="13">Differential record: {{DifferentialRecordNum}}</text>
          <line x1="5" x2="35" y1="30" y2="30" :stroke="colorMap['blue-normal']" class="legendLine"></line>
          <text x="40" y="33">Other records: {{OtherRecordNum}}</text>
        </svg>
        <svg id="DataDistribution" v-show="DataExplorationStatus === 'DD'"></svg>
        <el-table :data="DifferentialRecordTableData"
                  :row-style="rowStyle"
                  :header-cell-style="headerCellStyle"
                  border
                  style="width: 100%; height: calc(100% - 43px)"
                  v-show="DataExplorationStatus !== 'DD'"
        >
          <el-table-column
              v-for="attr in DifferentialRecordTableColumn"
              :prop="attr"
              :label="attr"
              align="center">
          </el-table-column>
        </el-table>
      </div>
    </div>

    <div class="RowPartMain BaseMain">
      <div class="MainLabel" style="margin-bottom: 10px">Data Query Simulation</div>


      <div id="DPS_Panel" class="Panel">
        <div>DP settings</div>
        <el-divider direction="vertical" border-style="dashed" class="PanelTextDivider"/>
        <span>&epsilon;: </span>
        <el-input-number
            v-model="epsilon"
            :min="0.01"
            :max="10"
            :step="0.01"
            class="EpsilonInput"
            controls-position="right"
        />
        <span class="paddingLeft10px">Sensitivity calculation: </span>
        <el-select v-model="SensitivityCalculationWay" class="SCWO" placeholder="Select">
          <el-option
              v-for="(item, index) in SensitivityCalculationWayOption"
              :key="item"
              :label="item + ': ' + this.SensitivityList[index]"
              :value="item"
          />
        </el-select>
        <el-button type="primary" class="rightEdgeBtn" @click="RecordEpsilon">Record &epsilon;</el-button>
      </div>


      <div id="QT_Panel" class="Panel">
        <div style="margin-right: 7px">Query Test</div>
        <el-divider direction="vertical" border-style="dashed" class="PanelTextDivider"/>
        <span>Attribute: </span>
        <el-select class="marginLeft10px" v-model="QueryAttr" placeholder="Select" style="width: 100px">
          <el-option
              v-for="item in QueryAttrOption"
              :key="item"
              :label="item"
              :value="item"
          />
        </el-select>

        <span style="padding-left: 20px">Type: </span>
        <el-select class="marginLeft10px" v-model="QueryType" placeholder="Select" style="width: 100px">
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

      <div class="flexLayout">
        <div class="SecondaryLabel">Attack Simulation</div>
        <div class="SecondaryLabel" style="margin-left: 215px">General Query Simulation</div>
      </div>
      <div class="flexLayout">
        <div id="AS_Panel" class="Panel halfPanel">
<!--          <el-divider direction="vertical" border-style="dashed" class="TextDivider"/>-->
          <div v-if="QueryAttrType !== 'categorical'">
            <span>Deviation:</span>
            <span class="paddingLeft10px">&plusmn;</span>
            <el-input-number
                v-model="PrivacyDeviation"
                :min="0"
                :max="isPercentage1 ? 100 :(MaxMap[QueryAttr] === undefined ? 10 : MaxMap[QueryAttr])"
                :step="0.01"
                controls-position="right"
                class="deviationInput"
            />
            <span class="percentageMasker" :class="{hidden: !isPercentage1}">%</span>
            <el-button type="primary" @click="switchPercentage1" class="refreshBtn"><el-icon><Refresh /></el-icon></el-button>
          </div>
          <div class="flexLayout marginTop5px">
            <span>Succ rate threshold: </span>
            <el-input-number
                v-model="AttackSRT"
                :min="0.01"
                :max="1"
                :step="0.01"
                controls-position="right"
                label="%nasajioasjaiosaiso"
                class="thresholdInput"
            />
          </div>
          <el-button type="primary" class="rightEdgeBtn" @click="Update2PE">Update &epsilon; <br>to {{privacyEpsilon}}</el-button>
        </div>
        <div id="GQS_Panel" class="Panel halfPanel">
<!--          <el-divider direction="vertical" border-style="dashed" class="TextDivider"/>-->
          <div v-if="QueryAttrType !== 'categorical'">
            <span>Deviation:</span>
            <span class="paddingLeft10px">&plusmn;</span>
            <el-input-number
                v-model="AccuracyDeviation"
                :min="0"
                :max="isPercentage2 ? 100 : (MaxMap[QueryAttr] === undefined ? 10 : MaxMap[QueryAttr])"
                :step="0.01"
                controls-position="right"
                class="deviationInput"
            />
            <span class="percentageMasker" :class="{hidden: !isPercentage2}">%</span>
            <el-button type="primary" @click="switchPercentage2" class="refreshBtn"><el-icon><Refresh /></el-icon></el-button>
          </div>
          <div class="flexLayout marginTop5px">
            <span>Accuracy threshold: </span>
            <el-input-number
                v-model="AccuracySRT"
                :min="0.01"
                :max="1"
                :step="0.01"
                controls-position="right"
                class="thresholdInput"
            />
          </div>
          <el-button type="primary" class="rightEdgeBtn" @click="Update2AE">Update &epsilon; <br>to {{accuracyEpsilon}}</el-button>
        </div>
      </div>

      <div id="AttackSimulationViews" class="SimulationViews">
        <svg id="FirstQuerySVG" class="AS_view QueryView">
          <text x="5" y="15">1st query</text>
          <text x="25" y="30">Probability density</text>
        </svg>
        <svg id="DA_OutputSVG" class="AS_view QueryView">
          <text x="5" y="15">Differential attack</text>
          <text x="25" y="30">Probability density</text>
          <text x="180" y="20">{{deviationP1.toFixed(3)}}</text>
        </svg>
        <svg id="GeneralQuery" class="GQS_view QueryView">
          <text x="5" y="15">General query</text>
          <text x="25" y="30">Probability density</text>
          <text x="180" y="20">{{deviationP2.toFixed(3)}}</text>
        </svg>
      </div>




      <div id="SchemeHistory">
        <div class="MainLabel">Scheme History</div>

        <el-table
            :data="SchemeHistory"
            table-layout="fixed"
            class="SchemeHistoryTable"
            @cell-mouse-enter="CellMouseEnter"
            @cell-mouse-leave="CellMouseLeave"
            style="width: 100%; height: calc(100% - 43px)">
          <el-table-column
              v-for="(attr, i) in SchemeHistoryColumn"
              :prop="attr"
              :label="attr"
              :min-width="attr !== 'Epsilon' ? 150 : 90"
              align="center">
            <template #header v-if="attr !== 'Epsilon'">
              <span>{{attr}}</span>
            </template>
            <template #default="scope" v-if="attr !== 'Epsilon'">
              <svg class="barChart" :key="scope.row[attr]">
                <g v-if="scope.row[attr]">
                  <g v-if="scope.row[attr].type === 'numerical'">
                    <line :x1="4+10*(Math.floor(AttackSRT*10))"
                          :x2="4+10*(Math.floor(AttackSRT*10))"
                          y1="5"
                          y2="30"
                          :stroke="colorMap['risk']"
                    ></line>
                    <rect x="0" y="0" fill="none" stroke="#999"
                          stroke-width="1px" stroke-dasharray="3, 2"
                          width="118" height="30"
                    ></rect>
                    <rect
                        v-for="(d, i) in scope.row[attr].data"
                        :x="5+i*10-1"
                        :y="30-Math.min(d/10*3, 30)"
                        :width="8"
                        :height="Math.min(d/10*3, 30)"
                        :fill="i < (Math.floor(AttackSRT*10)) ? colorMap['grey-normal'] : colorMap['risk']"
                    ></rect>
                  </g>
                  <g v-else>
                    <text x="40" y="20" style="font-size: 15px">{{scope.row[attr].data}}</text>
                  </g>
                </g>
              </svg>
            </template>
          </el-table-column>

          <el-table-column fixed="right" label=" " width="30" align="center">
            <template #default="scope">
              <el-button size="small" class="closeRow" @click="deleteSchemeHistoryRow(scope.$index, scope.row)"><el-icon><Close /></el-icon></el-button>
            </template>
          </el-table-column>
        </el-table>

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
        colorMap: {'blue-normal':      'rgba(52, 152, 219,1.0)',
                   'risk':             'rgba(234,120,119, 1.0)',
                   'grey-normal':      'rgb(176,176,176)',
                   'risk-stroke':      'rgba(243, 156, 18,1.0)',
                   'selected':         'rgba(236, 204, 104,1.0)'},

        curFile: '',
        attrList: [],
        DataInputVisible: true,
        RiskRatioMap: {},
        BSTMap: {},
        riskRecord: [],
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

        queryNumLegend: [],
        MinRecordsNum: 0,
        MaxRecordsNum: 0,

        MaxMap: {}, //记录属性的最大值 类别型属性用count最大值替代
        dimNodeCnt: [],
        DE_tick: true,
        PCP_tick_func: [],

        DataExplorationStatus: 'DD',
        DifferentialRecordNum: 0,
        OtherRecordNum: 0,

        // 决策变量
        firstQueryData: [],
        secondQueryData: [],
        curB: 0,
        curB2: 0, //第二次查询的拉普拉斯参数 b
        curSensitivity1: 0,
        curSensitivity2: 0,
        SensitivityList: [0, 0],
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
        AttackSRT: 0.6,
        AccuracyDeviation: 1,
        AccuracySRT: 0.9,
        privateVal: 0,
        QueryAccurateVal: 0,
        DeviationPrecision1: 0.1,
        isPercentage1: true,
        isPercentage2: true,
        DeviationPrecision2: 0.1,


        privacyEpsilon: '1.0',
        accuracyEpsilon: '1.0',
        deviationP1: 0,
        deviationP2: 0,


        DA_OutputXscale: {},
        GQueryXscale: {},
        DA_OutputYscale: {},
        GQueryYscale: {},
        brush: {},


        ExactVal: {'firstQuery': 0, 'secondQuery': 0},

        SchemeHistory: [],
        SchemeHistoryColumn: ['Epsilon'],
        SchemeHistoryColumnSensitivity: {},
        SchemeHistoryEpsilon: {},
        initialSchemeHistory: false,
        DifferentialRecordTableData: [],


        getNewAvgRiskPRunning: false,
      }
    },
    computed: {
      DifferentialRecordTableColumn() {
        return this.DifferentialRecordTableData.length === 0 ? [] : Object.keys(this.DifferentialRecordTableData[0]);
      },
      QueryAttrIndex() {
        return this.attrList.findIndex(d => d.Name === this.QueryAttr);
      },
      QueryAttrType() {
        if(this.QueryAttrIndex === -1) return '';
        return this.attrList[this.QueryAttrIndex].Type;
      },
      QueryTypeOption() {
        // queryType 默认选择第一个
        if(this.QueryAttrType === 'numerical') {
          this.QueryType = 'sum';
          return ['sum', 'count']//, 'avg']
        }
        else if(this.QueryAttrType === 'categorical'){
          this.QueryType = 'count';
          if(this.QueryAttrIndex !== -1) {
            this.QueryCountCondition = this.attrList[this.QueryAttrIndex].Range[0];
          }
          return ['count'];
        } else {
          return []
        }
      },
      PrivacyDeviationVal() {
        let res;
        if(this.isPercentage1) {
          res = this.PrivacyDeviation * this.privateVal / 100;
        }
        else {
          res = this.PrivacyDeviation;
        }
        return res
      },
      PrivacyDeviationPercent() {
        let res;
        if(this.isPercentage1) {
          res = this.PrivacyDeviation;
        }
        else {
          res = ((this.PrivacyDeviation / this.privateVal) * 100).toFixed(0);
        }
        return res
      },
      AccuracyDeviationVal() {
        let res;
        let ratio = this.QueryAccurateVal / 100;
        if(this.isPercentage2) {
          res = this.AccuracyDeviation * ratio;
        }
        else {
          res = this.AccuracyDeviation;
        }
        return res
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

      // 暂时还没考虑敏感度
      isUpdateColumn({ QueryAttr, PrivacyDeviationPercent, SensitivityCalculationWay }) {
        return {QueryAttr, PrivacyDeviationPercent, SensitivityCalculationWay};
      },

      // 是否更新AvgRiskP 结果
      isUpdateAvgRiskP({initialSchemeHistory}) {
        return {initialSchemeHistory}
      }
    },
    methods: {
      //属性集树方法
      initializeTree([data, curFile, attrList]) {
        this.riskRecord = data.riskRecord;
        console.log(this.riskRecord)
        this.BSTMap = data.BSTMap;
        this.RiskRatioMap = data.RiskRatioMap;
        this.DataInputVisible = false;
        this.treeData = data.treeData;
        this.curFile = curFile;
        this.attrList = attrList;
        this.QueryAttrOption = attrList.map((d) => d.Name)
        this.QueryAttr = this.QueryAttrOption[0];
        //this.PrivacyDeviationVal = attrList[0]['DAable Window Width']
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


        this.ContextmenuNode(nodes[0])
        // 暂没考虑第一轮没有风险的情况
      },
      MakeTree(svg, nodes, links) {
        let outerRadius = 13;	//外半径
        let innerRadius = 7;	//内半径，为0则中间没有空白
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
            .attr("stroke", this.colorMap["grey-normal"])
            .attr("stroke-width", 1);
        // 统一边位置
        TreeLinkG
            .selectAll(".TreeLinkPath")
            .attr("d", function(d) {
              let start = { x: d.source.x + outerRadius / 2, y: d.source.y };
              let end;
              if(d.target.depth === 3) {
                end = { x: d.target.x - outerRadius / 3, y: d.target.y };
              }
              else {
                end = { x: d.target.x - outerRadius / 2 * 3, y: d.target.y };
              }
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
              console.log('mouseover')
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
            .attr('r', 0)
            .attr('cx', -outerRadius / 2)
            .attr('cy', 0)
            .attr('fill', this.colorMap['selected'])


        let outerPieColor = [this.colorMap["risk"], this.colorMap["grey-normal"]];
        let innerPieColor = [this.colorMap["risk"], this.colorMap["grey-normal"]];


        let childNodeRiskPie = Pie.selectAll(".childNodeRiskPie_path") //g用于把相关元素进行组合的容器元素
            .data(d => d3.pie().sort(null)(d.data.childNodeRiskPie))
            .enter()
            .append("g")
            .attr('class', 'childNodeRiskPie_path')
            .attr("transform","translate("+ -outerRadius / 2 +","+ 0 +")")
        let childNodeRiskArc = d3.arc()	//弧生成器
            .innerRadius(innerRadius + 2)	//设置内半径
            .outerRadius(outerRadius);	//设置外半径
        childNodeRiskPie
            .append("path")
            .attr("fill",function(d,i){
              return outerPieColor[i];
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
              return innerPieColor[i];
            })

            .attr("d",function(d){
              return curNodeRiskArc(d);
            })
            .attr('stroke',function(d,i){
              if(i === 0) {
                return innerPieColor[i];
              }
            })
            .attr('stroke-width', '1px')

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
                     .attr('fill', this.colorMap["risk-stroke"])
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
        if(d.depth !== 3) {
          if (d.data.children.length === 0) {
            // 生成节点
            axios({
              url: 'http://127.0.0.1:8000/RiskTree/RiskTreeData/',
              method: 'post',
              data: {
                'filename': this.curFile,
                'attrList': this.attrList,
                'indices': d.data.indices,
                'RiskRatioMap': this.RiskRatioMap
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
          } else {
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
        }
      },

      // 查询集树方法
      ContextmenuNode(d) {
        d3.selectAll('.strokeCircle').attr('r', 0);
        d3.select("#strokeCircle" + d.data.name).attr('r', 18);
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
          let height = parseFloat(svg.style('height').split('px')[0]);
          let container = svg
              .append("g")
              .attr("class", 'container')
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
              .attr('fill', this.colorMap["grey-normal"]);//箭头颜色

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
        let NodeHeight = 20;
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
        [this.MinRecordsNum, this.MaxRecordsNum] = [d3.min(nodes, d => d.data.num), d3.max(nodes, d => d.data.num)]
        let nodeColorScale = d3.scaleLinear()
            .domain([this.MinRecordsNum, this.MaxRecordsNum])
            .range(['#ddd', '#777'])


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
            .attr('cx', '10px')
            .attr('y', 0)
            .attr('width', DimensionG_width / 2)
            .attr('height', DimensionTextHeight)
            .attr('stroke', this.colorMap['grey-normal'])
            .attr('fill', this.colorMap["grey-normal"])
            .attr('fill-opacity', 0);

        DimensionNodeG.append('text')
            .attr('x', 0)
            .attr('y', 18)
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
              let node = d;
              while(node.parent.data.isBST) {
                node = node.parent;
              }
              this.clickQueryNode(node);
            })

        svg.selectAll('.TreeNodePie')
            .attr("transform", function(d) {
              let cx = d.x;
              let cy = d.y;
              return "translate(" + cx + "," + cy + ")";
            })

        NodesG.append("rect")
            .attr('class', 'strokeRectNode')
            .attr("x", -NodeWidth / 2)
            .attr("y", -NodeHeight / 2)
            .attr("height", NodeHeight)
            .attr("width", NodeWidth)
            .attr('stroke', this.colorMap["selected"])
            .attr('stroke-width', '10px')

        NodesG.append("rect")
            .attr('class', 'RectNode')
            .attr("x", -NodeWidth / 2)
            .attr("y", -NodeHeight / 2)
            .attr("height", NodeHeight)
            .attr("width", NodeWidth)
            .attr('fill', d => {
              let num = d.data.num;
              if(num === 1) {
                return this.colorMap["risk"]
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
              .attr('y', 3)
              .text(d => {
                let dim = d.data.dim;
                let index = this.keyMap[dim].data.indexOf(d.data.key);
                return this.keyMap[dim].text[index];
              });


        NodesG.append('g')
             .attr("transform", (d) => {
               let dim = d.data.dim;
               let px;
               let index = this.keyMap[dim].data.indexOf(d.data.key);
               if(this.keyMap[dim].text[index].indexOf('~') === -1) {
                //类别型
                 px = this.scaleMap[this.curAttr[d.data.dim]](this.keyMap[dim].text[index]) + this.scaleMap[this.curAttr[d.data.dim]].bandwidth() / 2;
               }
               else {
                 let splitArray = this.keyMap[dim].text[index].split('~').map(d => parseFloat(d));
                 px = this.scaleMap[this.curAttr[d.data.dim]]((splitArray[0] + splitArray[1]) / 2);
               }
               let height = parseFloat(d3.select('#DataDistribution').style('height').split('px')[0]);
               let padding = 20;
               px = px / (height - 2 * padding) * NodeWidth;


               //
               return `translate(${37 - px}, ${5})`
              })
             .append('polygon')
             .attr('points', '0,10 10,10 5, 0')
             .attr('fill', '#333')

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
        d3.selectAll('.strokeRectNode').attr('stroke-width', 0);
        d3.selectAll('.strokeRectNode').filter(node => node === d).attr('stroke-width', '10px');


        // 先不考虑单节点情况
        // 蓝色条件下的index集合
        this.curIndex = d.parent.data.index;
        let temp = [this.TableData[d.data.index[0]]];
        temp.push(...this.curIndex.map(d => this.TableData[d]));
        this.DifferentialRecordTableData = temp;
        this.OtherRecordNum = this.curIndex.length;
        this.DifferentialRecordNum = 1;
        for(let d of this.LineData) {
          d['highlight'] = false;
        }
        for(let i of this.curIndex) {
          this.LineData[i]['highlight'] = this.colorMap["blue-normal"];
        }
        this.LineData[d.data.index[0]]['highlight'] = this.colorMap["risk"]
        d3.selectAll('.cloneLineG').remove();


        // 保证红线在蓝色上面
        let blueCloneLinePath = d3.selectAll('.LineG')
            .filter(d => d.highlight === this.colorMap["blue-normal"])
            .select(function() {
              return this.parentNode.insertBefore(this.cloneNode(true), null);
            })
            .attr('class', 'cloneLineG blueLine')

        let resCloneLinePath = d3.selectAll('.LineG')
            .filter(d => d.highlight === this.colorMap["risk"])
            .select(function() {
              return this.parentNode.insertBefore(this.cloneNode(true), null);
            })
            .attr('class', 'cloneLineG redLine')



        d3.selectAll('.cloneLineG')
            .select('path')
            .attr('stroke', d => d.highlight)
            .attr('stroke-opacity', d => d.highlight === this.colorMap["blue-normal"] ? 0.2 : 1.0)
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
        let finalAttr = this.curIndices[d.data.dim]//this.curIndices[this.curIndices.length - 1];
        let finalAttrName = this.curAttr[d.data.dim]//this.curAttr[this.curAttr.length - 1]
        let largerFinalKeyScope = [0, -1], smallerFinalKeyScope = [0, -1];
        let upperScope = [0, 0], lowerScope = [0, 0];
        let obj = this.keyMap[d.data.dim];
        for(let index of this.curIndex) {
          finalKeyList.add(this.TableKeyData[index][finalAttr])
        }

        let SecondQueryText = FirstQueryText;
        this.SecondQueryCondition = JSON.parse(JSON.stringify(this.FirstQueryCondition));
        // 删除风险节点的key
        finalKeyList.delete(this.TableKeyData[RiskIndex][finalAttr]);
        finalKeyList = Array.from(finalKeyList)

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
            SecondQueryText += `<br/>AND <span class="redFont">${finalAttrName} IN (${SQL_in_list.join(' ')})</span>`;
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
                SecondQueryText += `<br/><span class="redFont">OR ${finalAttrName} BETWEEN ${lowerScope[0]} AND ${lowerScope[1]})</span>`
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

        let offset = 3;

        d3.select("#SecondQueryText")
            .html(SecondQueryText)

        let finalMaskData = [upperScope, lowerScope];
        if(upperScope[0] === 0 && upperScope[1] === 0) {
          finalMaskData = [lowerScope]
        }
        if(lowerScope[0] === 0 && lowerScope[1] === 0) {
          finalMaskData = [upperScope]
        }
        // 单独合成最后一个键
        let svg = d3.select('#DataDistribution');
        svg.select('.maskG')
            .selectAll('.finalMaskG')
            .remove();
        let finalMaskG = svg.select('.maskG')
            .selectAll('.finalMaskG')
            .data(finalMaskData)
            .join('g')
            .attr('class', 'finalMaskG')
            .attr('transform', (d) =>{
              let x = d[0];
              return `translate(${this.scale_Xscale(finalAttr)}, ${this.scaleMap[finalAttrName](x)})`
            });
        finalMaskG
            .append('rect')
            .attr("x", -10)
            .attr("y", (d) => {
              if (obj.type === 'numerical') {
                return this.scaleMap[finalAttrName](d[1]) - this.scaleMap[finalAttrName](d[0]) + offset
              }
              else {
                return 0
              }
            })
            .attr('width', '20px')
            .attr("height", (d, k) => {
              if (obj.type === 'numerical') {
                return this.scaleMap[finalAttrName](d[0]) - this.scaleMap[finalAttrName](d[1]) - offset;
              }
              else {
                return this.scaleMap[finalAttrName].bandwidth() * d[1];
              }
            })
            .attr('fill', this.colorMap["selected"])
            .style('stroke', 'none')

        // rect 上下边界线
        svg.select('.tickLine > *')
            .remove();
        let finalTickLineG = svg.select('.tickLine')
            .selectAll('.finalTickLineG')
            .data(finalMaskData)
            .join('g')
            .attr('class', 'finalTickLineG')
            .attr('transform', (d) =>{
              let x = d[0];
              return `translate(${this.scale_Xscale(finalAttr)}, ${this.scaleMap[finalAttrName](x)})`
            });

        finalTickLineG.append('line')
            .attr('stroke-width', '2px')
            .attr('x1', -10)
            .attr('x2', 10)
                  .attr('y1', d => {
                    if (obj.type === 'numerical') {
                      return this.scaleMap[finalAttrName](d[1]) - this.scaleMap[finalAttrName](d[0]) + offset;
                    }
                    else {
                      return 0
                    }
                  })
                  .attr('y2', d => {
                    if (obj.type === 'numerical') {
                      return this.scaleMap[finalAttrName](d[1]) - this.scaleMap[finalAttrName](d[0]) + offset
                    }
                    else {
                      return 0
                    }
                  })
                  .style('stroke', this.colorMap["grey-normal"]);
        finalTickLineG.append('line')
            .attr('stroke-width', '2px')
            .attr('x1', -10)
            .attr('x2', 10)
            .attr('y1', d => {
              if (obj.type === 'numerical') {
                return 0
              }
              else {
                return this.scaleMap[finalAttrName].bandwidth() * d[1]
              }
            })
            .attr('y2', d => {
              if (obj.type === 'numerical') {
                return 0
              }
              else {
                return this.scaleMap[finalAttrName].bandwidth() * d[1]
              }
            })
            .style('stroke', this.colorMap["grey-normal"]);




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
                return this.scaleMap[this.curAttr[k]](d[1]) - this.scaleMap[this.curAttr[k]](d[0]) + offset
              }
              else {
                return 0
              }
            })
            .attr('width', '20px')
            .attr("height", (d, k) => {
              if(typeof d !== 'string') {
                return this.scaleMap[this.curAttr[k]](d[0]) - this.scaleMap[this.curAttr[k]](d[1]) - offset
              }
              else {
                return this.scaleMap[this.curAttr[k]].bandwidth();
              }
            })
            .attr('fill', this.colorMap["selected"])
            .style('stroke', 'none');

        // rect 上边界线
        svg.select('.tickLine')
            .selectAll('.TickLineG')
            .remove();
        let TickLineG = svg.select('.tickLine')
            .selectAll('.TickLineG')
            .data(valueList)
            .join('g')
            .attr('class', 'TickLineG')
            .attr('transform', (d, k) =>{
              let x
              if(typeof d !== 'string')
                x = d[0]
              else
                x = d
              return `translate(${this.scale_Xscale(this.curIndices[k])}, ${this.scaleMap[this.curAttr[k]](x)})`
            });
        TickLineG.append('line')
            .attr('stroke-width', '2px')
            .attr('x1', -10)
            .attr('x2', 10)
            .attr('y1', (d, k) => {
              if(typeof d !== 'string') {
                return this.scaleMap[this.curAttr[k]](d[1]) - this.scaleMap[this.curAttr[k]](d[0]) + offset;
              }
              else {
                return 0
              }
            })
            .attr('y2', (d, k) => {
              if(typeof d !== 'string') {
                return this.scaleMap[this.curAttr[k]](d[1]) - this.scaleMap[this.curAttr[k]](d[0]) + offset
              }
              else {
                return 0
              }
            })
            .style('stroke', this.colorMap["grey-normal"]);
        // rect 下边界线
        TickLineG.append('line')
            .attr('stroke-width', '2px')
            .attr('x1', -10)
            .attr('x2', 10)
            .attr('y1', (d, k) => {
              if (typeof d !== 'string') {
                return 0
              }
              else {
                return this.scaleMap[this.curAttr[k]].bandwidth();
              }
            })
            .attr('y2', (d, k) => {
              if (typeof d !== 'string') {
                return 0
              }
              else {
                return this.scaleMap[this.curAttr[k]].bandwidth();
              }
            })
            .style('stroke', this.colorMap["grey-normal"]);


        console.log(this.FirstQueryCondition);
        console.log(this.SecondQueryCondition);

        this.initializeAttackSimulationViews(d);
        this.curAttackTarget = d;
      },
      switch2RecordTable() {
        this.DataExplorationStatus = 'RT';
      },
      switch2DataDistribution() {
        this.DataExplorationStatus = 'DD';
      },
      rowStyle({row, rowIndex}) {
        let style;
        if(rowIndex === 0) {
          style = {"background": `${this.colorMap['risk']} !important`};
        }
        else {
          style = {"background": `${this.colorMap['blue-normal']} !important`};
        }
        return style;
      },
      headerCellStyle({ row, column, rowIndex, columnIndex }) {
        if(this.curIndices.includes(columnIndex)) {
          return {'background': `${this.colorMap["selected"]}`};
        }
      },
      changeTickStatus() {
        let ticks = this.DE_tick ? 5 : 0;
        let that = this;
        if(ticks) {
          d3.selectAll('#DataDistribution .axis')
              .each(function(d, k) {
                d3.select(this).call(that.PCP_tick_func[k]);
              });
        }
        else {
          d3.selectAll('#DataDistribution .axis > g').remove();
        }
        d3.selectAll('#DataDistribution .axis')
            .select('path')
            .attr('stroke', this.colorMap["grey-normal"])
            .attr("marker-end","url(#arrow)");

      },
      initializeDataDistribution(response) {

        let data = response.data;
        let ScaleData = data.ScaleData;
        this.MaxMap = data.MaxMap;
        let TableData = this.TableData = data.TableData;
        this.TableKeyData = data.TableKeyData;
        let width = parseFloat(d3.select('#DataDistribution').style('width').split('px')[0]);
        let height = parseFloat(d3.select('#DataDistribution').style('height').split('px')[0]);
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
            .attr('fill', this.colorMap["grey-normal"]);//箭头颜色


        this.PCP_tick_func = []
        let that = this;
        let maskG = svg.append('g').attr('class', 'maskG');
        let axisG = svg.selectAll('.axis')
           .data(ScaleData)
           .enter()
           .append('g')
           .attr('class', 'axis')
           .attr('transform', (d, k) => `translate(${scale_Xscale(k)}, ${0})`)
           .each(function(d, k) {
             let tickfunc = d3.axisLeft().scale(scaleMap[d.name]).tickSize(0).ticks(5);
             d3.select(this).call(tickfunc);
             that.PCP_tick_func.push(tickfunc)
           });
        svg.selectAll('.axis')
           .select('path')
          .attr('stroke', this.colorMap["grey-normal"])
          .attr("marker-end","url(#arrow)");


        axisG.append('text')
             .attr("x", 0)
             .attr('y', 10)
             .style('text-anchor', 'middle')
             .style('fill', this.colorMap["grey-normal"])
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
           .attr("stroke", this.colorMap["grey-normal"])
           .attr('stroke-opacity', 0.7)
           .attr("stroke-width", 1)
           .attr("fill", "none");

        svg.append('g')
           .attr('class', 'tickLine')
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
                  'sensitivityWay': this.SensitivityCalculationWay,
                  'scope': -1
                }
              }).then(response1 => {
                axios({
                  url: 'http://127.0.0.1:8000/AttackSimulation/GetNoisyDataDistribution/',
                  method: 'post',
                  data: {
                    'FileName': this.curFile,
                    'QueryType': this.QueryType,
                    'QueryAttr': this.QueryAttr,
                    'Interval': this.QueryAttrType === 'numerical' ? [this.IntervalLeft, this.IntervalRight] : this.QueryCountCondition,
                    'QueryCondition': this.SecondQueryCondition,
                    'epsilon': this.epsilon,
                    'sensitivityWay': this.SensitivityCalculationWay,
                    'scope': response1.data.scope  // 获取第一次得到的范围
                  }
                }).then(response2 => {
                  let data1 = response1.data;
                  let data2 = response2.data;
                  this.ExactVal['firstQuery'] = data1.ExactVal;
                  this.ExactVal['secondQuery'] = data2.ExactVal;
                  this.curB = data1.b;
                  this.curB2 = data2.b;
                  this.SensitivityList = [data1.sensitivities[0] + ', ' + data2.sensitivities[0], data1.sensitivities[1] + ', ' + data2.sensitivities[1]];
                  [this.curSensitivity1, this.curSensitivity2] = [data1.sensitivity, data2.sensitivity];
                  d3.select('#FirstQuerySVG');
                  this.firstQueryData = data1.distribution;
                  this.secondQueryData = data2.distribution;
                  if(d.data.index.length === 1) {
                    this.setAttackTarget(this.TableData[d.data.index[0]])
                  }
                  // 初始化常规查询视图
                  this.initializeGeneralQuerySimulationView()
                })
              })
      },
      setAttackTarget(data) {
        // 假设攻击目标满足条件
        if(this.QueryType === 'count') {
          if(this.QueryAttrType === 'numerical') {
            this.privateVal = ((data[this.QueryAttr] > this.IntervalLeft) && (data[this.QueryAttr] < this.IntervalRight)) ? 1 : 0;
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
        let svg = d3.select('#FirstQuerySVG');
        this.MakeResultDistribution(svg, this.firstQueryData, 'overall', false, '', this.secondQueryData);
        // 画差分结果分布图
        axios({
          url: 'http://127.0.0.1:8000/AttackSimulation/GetPrivacyDistribution/',
          method: 'post',
          data: {
            'b1': this.curB,
            'b2': this.curB2,
            'targetResult': targetResult,
          }
        }).then(response => {
          let svg = d3.select('#DA_OutputSVG');
          let lineData = response.data.distribution;
          let brushAble = this.QueryAttrType === 'numerical';
          [this.DA_OutputXscale, this.DA_OutputYscale] = this.MakeResultDistribution(svg, lineData, 'overall', brushAble,'clip-privacy');
        })
      },
      MakeResultDistribution(svg, lineData, position, brushAble, clipId='', externalData=[]) {
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
        svg.selectAll('.clipG').remove();
        let x = d3.scaleLinear()
            .domain([externalData.length !== 0 ? externalData[0][0] : lineData[0][0], lineData[lineDataLen - 1][0]])
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
        container.append('g').attr('class', 'historyPath')
        container.append('path')
            .attr('d', cg(lineData))
            .attr('stroke', this.colorMap["blue-normal"])
            .attr('stroke-width', 2)
            .attr('fill', 'none');
        if (externalData.length !== 0) {
          container.append('path')
              .attr('d', cg(externalData))
              .attr('stroke', this.colorMap["blue-normal"])
              .attr('stroke-width', 2)
              .attr('fill', 'none');
        }

        let trueVal = (lineData[0][0] + lineData[lineDataLen - 1][0]) / 2;

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

        svg.selectAll('.axis path,line')
            .attr('stroke', this.colorMap["grey-normal"]);
        svg.selectAll('.axis path')
            .attr("marker-end","url(#arrow)");

        if(brushAble) {
          let deviation = clipId === 'clip-accuracy'? this.AccuracyDeviationVal : this.PrivacyDeviationVal;
          let func = clipId === 'clip-accuracy'? this.laplace_f : this.laplace_dv_f;
          // brush的边界
          let clipG = svg.append('g').attr('class', 'clipG');

          let rectX = x(trueVal - deviation);
          let rectWidth = x(trueVal + deviation) - x(trueVal - deviation)
          clipG.append("clipPath")
              .attr("id", clipId)
              .append("rect")
              .attr("x", rectX)
              .attr("y", 0)
              .attr("width", rectWidth)
              .attr("height", h);

          clipG.append("path")
              .attr("stroke", "#aaa")
              .attr('d', cg(lineData))
              .attr("fill", this.colorMap["risk"])
              .attr("fill-rule", "evenodd")
              .attr('clip-path', `url(#${clipId})`);

          clipG.append("rect")
              .attr('class', 'bottomClipRect')
              .attr("x", rectX)
              .attr("y", y(ymin)-1)
              .attr("height", yRange[0] - y(ymin)+1)
              .attr("width", rectWidth)
              .attr("fill", this.colorMap["risk"])
              .attr('stroke', 'none')
              .attr('stroke-dasharray', '3, 2')
        }
        return [x, y, trueVal];
      },

      // 常规查询模拟方法
      initializeGeneralQuerySimulationView() {
        let svg = d3.select('#GeneralQuery');
        let lineData = this.firstQueryData;
        let brushAble = this.QueryAttrType === 'numerical';
        [this.GQueryXscale, this.GQueryYscale, this.QueryAccurateVal] = this.MakeResultDistribution(svg, lineData, 'overall', brushAble, 'clip-accuracy');

        let cg = d3.line()
            .x(d => this.GQueryXscale(d[0]))
            .y(d => this.GQueryYscale(d[1]));

        let container = svg.select('.container-overall .historyPath');
        for(let e in this.SchemeHistoryEpsilon) {
          container.append('path')
              .attr('d', cg(this.SchemeHistoryEpsilon[e]))
              .attr('stroke', this.colorMap["grey-normal"])
              .attr('stroke-width', 1)
              .attr('fill', 'none')
              .attr('id', `historyPath${e}`);
        }
      },

      // 攻击模拟决策方法
      UpdateEpsilonWithPrivacy() {
        axios({
          url: 'http://127.0.0.1:8000/DpDecisionMaker/UpdateEpsilonWithPrivacy/',
          method: 'post',
          data: {
            'Deviation': this.PrivacyDeviationVal,
            'SRT': this.AttackSRT,
            'Sensitivity': this.curSensitivity1,
            'QueryType': this.QueryType,
            'b1': this.curB,
            'b2': this.curB2
          }
        }).then(response => {
          this.initialSchemeHistory = true;
          this.privacyEpsilon = response.data.epsilon;
          this.deviationP1 = response.data.dp;
        })
      },
      switchPercentage1() {
        this.isPercentage1 = !this.isPercentage1;
        if(this.isPercentage1) {
          this.PrivacyDeviation = (this.PrivacyDeviation / this.privateVal).toFixed(4) * 100;
        }
        else {
          this.PrivacyDeviation = (this.PrivacyDeviation * this.privateVal / 100).toFixed(2);
        }
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
            'Deviation': this.AccuracyDeviationVal,
            'SRT': this.AccuracySRT,
            'QueryType': this.QueryType,
            'Sensitivity': this.curSensitivity1,
            'b': this.curB
          }
        }).then(response => {
          this.accuracyEpsilon = response.data.epsilon;
          this.deviationP2 = response.data.dp;
        })
      },
      switchPercentage2() {
        this.isPercentage2 = !this.isPercentage2;
        if(this.isPercentage2) {
          this.AccuracyDeviation = (this.AccuracyDeviation / this.privateVal).toFixed(4) * 100;
        }
        else {
          this.AccuracyDeviation = this.AccuracyDeviation * this.privateVal / 100;
        }
      },
      Update2AE() {
        this.epsilon = this.accuracyEpsilon;
      },

      getNewAvgRiskP() {
        if(this.getNewAvgRiskPRunning) return;
        else {
          this.getNewAvgRiskPRunning = true;
        }
        this.SchemeHistory.push({
          'Epsilon': this.epsilon,
        })
        let temp = this.SchemeHistory[this.SchemeHistory.length-1];

        for(let i = 1;i<this.SchemeHistoryColumn.length;i++) {
          let column = this.SchemeHistoryColumn[i];
          let splitA = this.SchemeHistoryColumn[i].split('-');
          let attr, type, deviationRatio;
          if(splitA.length === 3) {
            attr = splitA[0]
            type = splitA[1]
            deviationRatio = parseInt(splitA[2].split('%')[0]) / 100
          }
          else {
            // 类别型或count
            attr = splitA[0]
            type = splitA[1].split(' (')[0]
            deviationRatio = 0
          }
          let attrType = this.attrList.find(d => d.Name === attr).Type;
          let attrParams = this.attrList.find(d => d.Name === attr);

          axios({
            url: 'http://127.0.0.1:8000/RiskTree/AvgRiskP/',
            method: 'post',
            data: {
              'filename': this.curFile,
              'deviationRatio': deviationRatio,
              'attrParams': attrParams,
              'attr': attr,
              'epsilon': this.epsilon,
              'BSTMap': this.BSTMap,
              'type': type, // type更改用监听select事件来弄,因为attr修改会直接引起type修改,不能对type监听
              'sensitivity': this.SchemeHistoryColumnSensitivity[column],
              'riskRecord': this.riskRecord
            }
          }).then(response => {
            if (attrType !== 'categorical' && type !== 'count') {
              let avgRiskP = response.data.avgRiskP;
              // let ATD = `${this.QueryAttr}-${this.QueryType} (${(deviationRatio * 100).toFixed(0)}%)`;
              this.getNewAvgRiskPRunning = false;
              let newIndex = this.SchemeHistory.length;
              temp[this.SchemeHistoryColumn[i]] = {};
              temp[this.SchemeHistoryColumn[i]].data = Object.values(avgRiskP);
              temp[this.SchemeHistoryColumn[i]].type = 'numerical';
            } else {
              // 类别型数据
              temp[this.SchemeHistoryColumn[i]] = {};
              temp[this.SchemeHistoryColumn[i]].data = (response.data.avgRiskP * 100).toFixed(0) + '%';
              temp[this.SchemeHistoryColumn[i]].type = 'categorical';
              this.getNewAvgRiskPRunning = false;
            }

          })
        }
        // this.SchemeHistory.push(temp)
      },
      refreshAvgRiskP() {
        for(let j = 0;j<this.SchemeHistory.length;j++) {
          for (let i = 1; i < this.SchemeHistoryColumn.length; i++) {
            let column = this.SchemeHistoryColumn[i];
            let splitA = this.SchemeHistoryColumn[i].split('-');
            let attr, type, deviationRatio;
            if(splitA.length === 3) {
              attr = splitA[0]
              type = splitA[1]
              deviationRatio = parseInt(splitA[2].split('%')[0]) / 100
            }
            else {
              // 类别型或count
              attr = splitA[0]
              type = splitA[1].split(' (')[0]
              deviationRatio = 0
            }
            let attrType = this.attrList.find(d => d.Name === attr).Type;
            let attrParams = this.attrList.find(d => d.Name === attr);

            axios({
              url: 'http://127.0.0.1:8000/RiskTree/AvgRiskP/',
              method: 'post',
              data: {
                'filename': this.curFile,
                'deviationRatio': deviationRatio,
                'attrParams': attrParams,
                'attr': attr,
                'epsilon': this.epsilon,
                'BSTMap': this.BSTMap,
                'type': type, // type更改用监听select事件来弄,因为attr修改会直接引起type修改,不能对type监听
                'sensitivity': this.SchemeHistoryColumnSensitivity[column],
                'riskRecord': this.riskRecord
              }
            }).then(response => {
              if (attrType !== 'categorical' && type !== 'count') {
                let avgRiskP = response.data.avgRiskP;
                // let ATD = `${this.QueryAttr}-${this.QueryType} (${(deviationRatio * 100).toFixed(0)}%)`;
                this.getNewAvgRiskPRunning = false;
                let newIndex = this.SchemeHistory.length;
                let temp = this.SchemeHistory[j];
                temp[this.SchemeHistoryColumn[i]] = {};
                temp[this.SchemeHistoryColumn[i]].data = Object.values(avgRiskP);
                temp[this.SchemeHistoryColumn[i]].type = 'numerical';
              } else {
                // 类别型数据
                let temp = this.SchemeHistory[j];
                temp[this.SchemeHistoryColumn[i]] = {};
                temp[this.SchemeHistoryColumn[i]].data = (response.data.avgRiskP * 100).toFixed(0) + '%';
                temp[this.SchemeHistoryColumn[i]].type = 'categorical';
                this.getNewAvgRiskPRunning = false;
              }

            })
          }
        }
        // this.SchemeHistory.push(temp)
      },

      deleteSchemeHistoryRow(index, row) {
        delete this.SchemeHistoryEpsilon[this.SchemeHistory[index].Epsilon]
        this.SchemeHistory.splice(index, 1);
      },
      CellMouseEnter(row) {
        d3.select(`#historyPath${row.Epsilon}`.replace('.', '\\.'))
          .classed('hoverPath', true);
      },
      CellMouseLeave(row) {
        d3.select(`#historyPath${row.Epsilon}`.replace('.', '\\.'))
            .classed('hoverPath', false);
      },

      RecordEpsilon() {
        this.getNewAvgRiskP();
      },

      laplace_f(x) {
        let b = this.curB;
        return 1 / (2 * b) * Math.exp(-Math.abs(x) / b)
      },
      laplace_dv_f(x) {
        let b = this.curB;
        return this.laplace_f(x) / 2 + Math.abs(x) / (4 * b * b) * Math.exp(-Math.abs(x) / b)
      }
    },
    watch: {
      'PrivacyDeviationVal': {
        handler(newVal, oldVal) {
          if(oldVal !== 0) {
            let svg = d3.select('#DA_OutputSVG')
            let x = this.DA_OutputXscale(this.privateVal - newVal);
            let width = this.DA_OutputXscale(this.privateVal + newVal) - this.DA_OutputXscale(this.privateVal - newVal)
            svg.select('.clipG .bottomClipRect')
                .attr("x", x)
                .attr("width", width);

            svg.select('clipPath rect')
                .attr("x", x)
                .attr("width", width);
            this.UpdateEpsilonWithPrivacy();
          }
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
      'AccuracyDeviationVal': {
        handler(newVal, oldVal) {
          let svg = d3.select('#GeneralQuery');
          let x = this.GQueryXscale(this.QueryAccurateVal - newVal);
          let width = this.GQueryXscale(this.QueryAccurateVal + newVal) - this.GQueryXscale(this.QueryAccurateVal - newVal)
          svg.select('.bottomClipRect')
              .attr("x", x)
              .attr("width", width);

          svg.select('clipPath rect')
              .attr("x", x)
              .attr("width", width);
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
      'curSensitivity1': {
        handler(newVal, oldVal) {
          this.UpdateEpsilonWithAccuracy();
          this.UpdateEpsilonWithPrivacy();
        },
        deep: true,
        immediate: false
      },
      'curSensitivity2': {
        handler(newVal, oldVal) {
          this.UpdateEpsilonWithAccuracy();
          this.UpdateEpsilonWithPrivacy();
        },
        deep: true,
        immediate: false
      },
      'isFreshSimulationView': {
        handler(newVal, oldVal) {
          if(Object.keys(this.curAttackTarget).length !== 0) {
            if (this.QueryAttrType !== 'numerical' && this.QueryType === 'sum') {

            } else {
              this.initializeAttackSimulationViews(this.curAttackTarget);
            }
          }
        },
        deep: true,
        immediate: false
      },
      'isUpdateColumn': {
        handler(newVal, oldVal) {
          let temp = [];
          for(let type of this.QueryTypeOption) {
            if(type === 'count') {
              temp.push(`${this.QueryAttr}-${type}`)
            }
            else {
              temp.push(`${this.QueryAttr}-${type}-${this.PrivacyDeviationPercent}%`)
            }
          }
          // this.SchemeHistory = [];
          this.SchemeHistoryColumn = ['Attribute', 'Epsilon'];
          this.SchemeHistoryColumn.push(...temp)
          axios({
            url: 'http://127.0.0.1:8000/RiskTree/getSensitivity/',
            method: 'post',
            data: {
              'filename': this.curFile,
              'columns': temp,
              'sensitivityWay': this.SensitivityCalculationWay
            }
          }).then((response) => {
            let flag = true;
            if(Object.keys(this.SchemeHistoryColumnSensitivity).length === 0) {
              // 第一次不进行表格刷新
              flag = false
            }

            this.SchemeHistoryColumnSensitivity = response.data.sensitivityMap;
            let index = 1;
            for(let [column, s] of Object.entries(this.SchemeHistoryColumnSensitivity)) {
              let newColumn = this.SchemeHistoryColumn[index] += ' (\u0394f = ' + `${s})`;
              // 将旧的敏感度map的key修改为新格式
              this.SchemeHistoryColumnSensitivity[newColumn] = s;
              delete this.SchemeHistoryColumnSensitivity[column];
              index += 1;
            }
            if(flag) {
              this.refreshAvgRiskP();
            }
          })
        },
        deep: true,
        immediate: false
      },
      'isUpdateAvgRiskP': {
        handler(newVal, oldVal) {
          // if(newVal['epsilon'] !== oldVal['epsilon']) {
          //   this.SchemeHistoryEpsilon[oldVal['epsilon']] = this.firstQueryData;
          // }
          this.getNewAvgRiskP();
        },
        deep: true,
        immediate: false
      }
    },
    mounted() {
      let width = d3.select('.QueryView').style('width');
      d3.selectAll('.QueryView').style('height', width);


      let ColorScale = d3.scaleLinear()
          .domain([0, 99])
          .range(['#ddd', '#777'])
      for(let i = 0;i<=99;i++) {
        this.queryNumLegend.push(ColorScale(i))
      }
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
    font-size: 14px;
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
    top: 3px;
    right: 440px;
    width: 130px;
  }

  .switchTick {
    position: absolute;
    top: 7px;
    right: 230px;
    width: 200px;
  }

  .DataExplorationSwitch {
    position: absolute;
    top: 10px;
    right: 20px;
  }

  .DataExplorationSwitch button{
    background-color: #999;
  }
  .chosenBtn {
    background-color: #5988cf !important;
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
    font-weight: bold;
    font-size: 16px;
    padding: 0 10px;
    margin: 15px 0;
  }
  .Panel {
    width: calc(100% - 20px);
    line-height: 32px;


    padding: 5px 0 5px 10px;
    margin: 0 10px;
    border-radius: 10px;

    background-color: #efefef;

    position: relative;
    display: flex;
    flex-direction: row;
  }

  .halfPanel {
    width: calc(50% - 20px) !important;
    flex-direction: column;
  }

  .TextDivider {
    height: 100%;
    border-color: #333333;
    margin: 0 10px;
  }

  .PanelTextDivider {
    height: 34px;
    border-color: #333333;
    margin: 0 10px;
  }

  .rightEdgeBtn {
    border-top-right-radius: inherit;
    border-bottom-right-radius: inherit;
    margin-right: 0;

    width: 80px;
    position: absolute;
    right: 0;
    top: -1px;
    height: 100%;
  }

  .SQL {
    border-radius: 10px;
    background-color: #efefef;
    margin: 0 10px;
  }

  .SqlTitle {
    font-size: 14px;
    width: 25%;
    padding-left: 10px;
    text-align: center;
  }

  .SQLText {
    font-size: 10px;
  }

  .paddingLeft5px {
    padding-left: 5px;
  }

  .paddingLeft10px {
    padding-left: 10px;
  }

  .marginLeft10px {
    margin-left: 10px;
  }

  .marginTop5px {
    margin-top: 5px;
  }

  .percentageMasker {
    position: relative;
    right: 50px;
    z-index: 101;
  }

  .hidden {
    visibility: hidden;
  }

  .flexLayout {
    display: flex;
  }
  /***************** 树视图style ******************/
  #AttributeSet {
    width: 50%;
    height: 100%;
    position: relative;
  }
  #AttributeSetTree {
    height: calc(100% - 48px);
    width: 100%;
  }
  #AttributeSetTreeLegend {
    position: absolute;
    top: 0;
    right: 5px;
    width: 200px;
    height: 32px;
  }

  #DifferentialQueryTreeLegend {
    position: absolute;
    top: 0;
    right: 5px;
    width: 180px;
    height: 50px;
  }

  #TreeView {
    display: flex;
    flex-direction: row;
    height: calc(100% - 40px);
  }
  #DifferentialQueryList {
    position: relative;
    width: calc(50% - 1px);
  }

  #DataDistribution {
    width: 100%;
    height: calc(100% - 43px);
  }

  #DQTreeContainer {
    width: 100%;
    height: calc(100% - 37px - 40px - 30px - 120px - 10px);
    overflow-x: hidden;
    overflow-y: hidden;
    position: relative;
  }


  #DifferentialQueryTree {
    width: 100%;
    height: 100%;
  }
  #DQTreeAttrTitle {
    width: 100%;
    height: 30px;
    margin-top: 10px;
  }
  #CorrespondingSQLCommands {
    height: 120px;
  }

  #firstQuery {
    margin-bottom: 10px;
  }

  #firstQuery, #secondQuery {
    display: flex;
    align-items: center;
  }



  /**********************************************/

  .AS_view {
    flex: 1;
  }
  .QueryView {
    margin: 10px;
    border: #333333 2px dashed;
    flex: 1;
  }
  .SimulationViews {
    margin: 10px 20px;
    display: flex;
    flex-direction: row;
  }

/****************************************/
  #SchemeHistory {
    border-top: 10px #eff7fe solid;
    flex: 1;

    position: relative;
    left: 0;
    top: 10px;
    right: 0;
    height: 307px;
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
    margin: 0 0 0 10px;
    width: 100px;
    border-radius: 7px;
  }
  .SCWO {
    margin-left: 10px;
    border-radius: 7px;
  }

  .SQL_panel {
    display: flex;
    flex-direction: column;
    justify-content: space-evenly;
    height: calc(100% - 17px);
  }

  .barChart {
    margin-top: 8px;
    width: 120px;
    height: 30px;
  }



  .closeRow {
    border: none;
    padding: 5px !important;
    margin-top: 3px;
    margin-left: -10px;
    width: 24px !important;
    height: 24px !important;
  }
  /*.closeRow:hover {*/
  /*  background-color: rgba(236, 204, 104,0.5);*/
  /*}*/

  .refreshBtn {
    width: 32px;
    margin-left: -12px;
  }

  .thresholdInput {
    width: 100px;
    margin-left: 10px;
  }

  .deviationInput {
    width: 120px;
  }

</style>

<style>
  svg text {
    font-size: 10px;
    color: rgba(104, 104, 104,1.0);
    font-family: "Helvetica Neue",Helvetica,"PingFang SC","Hiragino Sans GB","Microsoft YaHei","微软雅黑",Arial,sans-serif;
  }

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

  .TreeNodePie {
    cursor: pointer;
  }

  .DimensionNodeG {
    cursor: pointer;
  }

  #DataExploration  span{
    font-size: 10px !important;
  }

  .hoverPath {
    stroke: rgba(236, 204, 104,1.0);
  }
  .el-table__body .el-table__row.hover-row td{
    background-color: rgba(236, 204, 104,0.5) !important;
  }

  .Panel .el-icon {
    font-size: 25px !important;
  }

</style>