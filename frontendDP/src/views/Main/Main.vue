<template>
  <div id="Container">
    <div class="RowPartMain">
      <div id="DifferentialRiskIdentification" class="BaseMain">
        <div class="MainLabel">Potential Victim Exploration</div>
        <div id="QT_Panel" class="Panel">
          <div style="margin-right: 3px">Query Content</div>
          <el-divider direction="vertical" border-style="dashed" class="PanelTextDivider"/>
          <span>Attribute: </span>
          <el-select class="marginLeft10px" v-model="QueryAttr" placeholder="Select" size="small" style="width: 100px">
            <el-option
                v-for="item in QueryAttrOption"
                :key="item"
                :label="item"
                :value="item"
            />
          </el-select>

          <span style="padding-left: 20px">Type: </span>
          <el-select class="marginLeft10px" v-model="QueryType" placeholder="Select" size="small" style="width: 100px" @change="changeQueryType">
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
                size="small"
                controls-position="right"
                style="width: 100px"
            />
            <span>~</span>
            <el-input-number
                v-model="IntervalRight"
                :min="IntervalLeft"
                :max="attrInterval[1]"
                :step="0.01"
                size="small"
                controls-position="right"
                style="width: 100px"
            />
          </div>
          <div v-if="QueryType === 'count' && QueryAttrType === 'categorical'">
            <span style="padding-left: 20px">Category: </span>
            <el-select v-model="QueryCountCondition" placeholder="Select" style="width: 100px" size="small">
              <el-option
                  v-for="item in attrList[QueryAttrIndex].Range"
                  :key="item"
                  :label="item"
                  :value="item"
              />
            </el-select>
          </div>

          <span style="padding-left: 20px">Top: </span>
          <el-input class="marginLeft10px" v-model="TopNum" size="small" style="width: 50px"></el-input>
          <el-button @click="changeTopNum" type="primary"
                     style="width: 90px;"
                     class="rightEdgeBtn blueBtn">Confirm</el-button>


        </div>
        <div id="DPS_Panel" class="Panel">
          <div style="margin-right: 17px">DP Scheme</div>
          <el-divider direction="vertical" border-style="dashed" class="PanelTextDivider"/>
          <span>&epsilon;: </span>
          <el-input-number
              v-model="epsilon"
              :min="0"
              :max="50"
              :step="0.01"
              precision="2"
              class="EpsilonInput"
              size="small"
              controls-position="right"
          />
          <span class="paddingLeft10px">Sensitivity calculation: </span>
          <el-select v-model="SensitivityCalculationWay" class="SCWO" placeholder="Select" size="small">
            <el-option
                v-for="(item, index) in SensitivityCalculationWayOption"
                :key="item"
                :label="item + (index === 0 ? (': '+this.SensitivityList[index]) : '')"
                :value="item"
            />
          </el-select>
          <el-button type="primary"
                     style="width: 90px;"
                     class="rightEdgeBtn blueBtn" @click="RecordEpsilon">Test</el-button>
        </div>
        <div id="TreeView">
          <div class="VictimGroups">
            <div class="SecondaryLabel">Victim Group List</div>
            <el-radio-group v-model="curVictimGroup" class="VictimGroup">
              <div class="vgc" v-for="vgn in Object.keys(VictimNameMap)">
                <div class="vgn" style="font-size: 12px;">{{vgn}}</div>
                <el-radio :label="vgn" size="large" class="vgcRadio"></el-radio>
              </div>
            </el-radio-group>
            <div class="vgc">
              <div class="addCont" v-if="!isClickAddVictim">
                <el-button class="addClickBtn" @click="clickAddBtn">
                  <el-icon style="width: 40px; height: 40px"><Plus /></el-icon>
                </el-button>
              </div>
              <div class="inputCont" v-else>
                <el-input class="marginLeft10px"
                          v-model="newVictimGroupName"
                          size="small" style="width: 80px; margin-top: 5px"></el-input>
                <el-button style="border: none; background-color:#fff;"
                           @click="RecordVictimGroup"
                           class="confirmVictimBtn"
                ><el-icon><Select /></el-icon></el-button>
              </div>
            </div>

          </div>
          <div class="controlBar">
            <div class="AttrFilters">
              <div class="SecondaryLabel">Attribute Filter</div>
              <div class="controlLabel">
                <div class="ScopeL">
                  <span>Scope</span>
                </div>
                <div class="AttrL">
                  <span>Attribution</span>
                </div>
                <div class="cludeL">
                  <span style="margin-right: 8px">Exclude</span>
                  <span >Include</span>

                </div>
              </div>
              <div class="AttrFilter" v-for="(attr, i) in attrList">
                <div class="AttrGropeFilter">
                  <el-slider v-if="attr['Type'] === 'numerical'"
                             range
                             :model="attrGropeFilter[attr['Name']]"
                             :max="attr['Max']" :min="attr['Min']"></el-slider>
                  <div v-else class="filterSelectGroup">
                    <button v-for="select in attrSelects[attr['Name']]"
                            :class="{'selectFilter': attrGropeFilter[attr['Name']].includes(select)}"
                            @click="attrGropeFilterChange(attr['Name'], select)"
                    >{{select}}</button>
                  </div>
                </div>
                <div class="AttrFilterContent" :style="{'background-color': rankColor[i], 'color': rankFontColor[rankColor[i]]}">{{attr['Name']}}</div>

                <div class="AttrFilterBtnGroup">
                  <el-radio-group v-model="AttrFilterMap[attr['Name']]" class="ml-4">
                    <el-radio label="exclude" size="large" @click.prevent="changeRatio(attr['Name'], 'exclude')"></el-radio>
                    <el-radio label="include" size="large" @click.prevent="changeRatio(attr['Name'], 'include')"></el-radio>
                  </el-radio-group>
                </div>
              </div>
            </div>
          </div>
          <el-divider class="PanelDivider" direction="vertical" border-style="dashed"/>
          <div class="attrRank">
            <div class="SecondaryLabel">Attribute Percent Rank</div>
            <svg id="attrRankPlot"></svg>
          </div>

          <div class="highRisk">
            <div class="SecondaryLabel">High Risk Attack</div>
            <svg id="highRiskPlot">
              <text x="100" y="420">Attack risk</text>
            </svg>
          </div>

        </div>

      </div>
      <div id="SchemeHistory">
        <div class="flexLayout">
          <div class="MainLabel">Scheme History</div>
        </div>

        <img src="icon/example.png" class="examplePng">

        <svg id="SchemeHistoryLegend">
          <g class="heatmapLegend" transform="translate(31, 51)" >
            <path d="M2,2 L10,6 L2,10 L6,6 L2,2" style="transform: rotate(-90deg)"></path>
            <line x1="6" x2="6" y1="-5" y2="48" stroke="#777" stroke-width="2px"></line>
            <text x="0" y="-25">Deviation</text>
            <text x="0" y="-12" style="fill: #777">Relative to the value</text>
            <line x1="6" x2="106" y1="48" y2="48" stroke="#777" stroke-width="2px"></line>
            <text x="58" y="62">Succ rate</text>
            <path d="M2,2 L10,6 L2,10 L6,6 L2,2" transform="translate(96, 42)"></path>
            <!--            <rect x="8" y="-5" width="20" height="21" :fill="colorMap['normal-grey']"></rect>-->
          </g>

          <g transform="translate(19, 142)">
            <rect v-for="(d, i) in attrRiskLegend"
                  :x="20+0.7*i"
                  :y="5"
                  width="2"
                  height="7"
                  :fill="d"
            ></rect>
            <text x="18" y="13" text-anchor="end">0</text>
            <text x="92" y="13">100%</text>
            <text x="65" y="25" style="text-anchor: middle">#Attacks (%)</text>
          </g>

          <g transform="translate(8, 202)">
            <line x1="24" x2="134" y1="0" y2="0" stroke-dasharray="3 2" :stroke="colorMap['deep-grey']" class="SchemeHistoryLegendLine"></line>
            <text x="30" y="14">Deviation threshold</text>
            <!--            <text x="45" y="25">by users</text>-->

          </g>

          <g transform="translate(8, 251)">
            <line x1="25" x2="25" y1="0" y2="20" :stroke="colorMap['risk']" class="SchemeHistoryLegendLine"></line>
            <text x="30" y="13">Succ rate threshold</text>
            <!--            <text x="30" y="20">by users</text>-->
          </g>

        </svg>

        <el-table
            :data="SchemeHistory.filter(d => d['Attribute'] === QueryAttr)"
            table-layout="fixed"
            border
            class="SchemeHistoryTable"
            :row-class-name="hoverRowClassName"
            :cell-class-name="hoverCellClassName"
            @cell-mouse-enter="CellMouseEnter"
            @cell-mouse-leave="CellMouseLeave"
            @cell-click="HeatmapCellClick"
            :scrollbar-always-on="true"
            style="width: 732px; height: calc(100% - 50px)">
          <el-table-column
              prop="DP scheme"
              width="170"
              align="center">
            <template v-slot:header>
              <div class="rightHeader">
                Victim Group
              </div>
              <div class="leftHeader">
                DP scheme
              </div>
            </template>
          </el-table-column>
          <el-table-column
              v-for="(attr, i) in SchemeHistoryColumn"
              :label="attr"
              width="120"
              align="center">

              <template #default="scope" v-if="attr !== 'DP scheme' && QueryType === 'sum'">
                <svg class="barChart" v-if="(typeof scope.row[attr]) === 'object'">
                  <g class="background">
                    <rect x="0" y="0" width="105" height="65"
                          fill="none"
                          :stroke="colorMap['normal-grey']"
                          stroke-width="1px"
                    ></rect>
                  </g>
                  <g class="bodyG" transform="translate(2, -2)">
                    <g class="bodyRectG"
                       v-for="(data, deviationIndex) in scope.row[attr]"
                       :transform="`translate(${0},${60-6*deviationIndex})`"
                    >
                      <rect
                          v-for="(d, i) in data"
                          :x="i*10"
                          :y="0"
                          :width="10"
                          :height="6"
                          :fill="schemeHistoryRectColorScale(d)"
                      ></rect>
                    </g>
                  </g>

                  <g class="decorationG" transform="translate(2, 3)">
                    <line :x1="10*sumAttackSRTPercent/10"
                          :x2="10*sumAttackSRTPercent/10"
                          :y1="60-6*PrivacyDeviationPercent/10"
                          y2="60"
                          :stroke="colorMap['risk']"
                          stroke-width="2px"

                    ></line>
                    <line x1="0"
                          :x2="10*10"
                          :y1="60-6*PrivacyDeviationPercent/10"
                          :y2="60-6*PrivacyDeviationPercent/10"

                          :stroke="colorMap['deep-grey']"
                          stroke-width="2px"
                          stroke-dasharray="3 2"
                    ></line>
                  </g>
                </svg>
  <!--              <span v-if="(typeof scope.row[attr + '-' + secondaryColumn]) === 'string'">{{scope.row[attr + '-' + secondaryColumn]}}</span>-->
                <!--                <span v-if="scope.row[attr + '-' + secondaryColumn] === undefined">In calculation</span>-->
              </template>
              <template #default="scope" v-if="attr !== 'DP scheme' && QueryType === 'count'">
                <svg class="barChart" v-if="(typeof scope.row[attr]) === 'object'">
                  <text x="40" y="14" style="text-anchor: middle; font-size: 14px">{{ 'Avg: ' + (scope.row[attr][0] * 100).toFixed(0) + '%'}}</text>
                  <g class="background">
                    <rect x="0" y="22" width="75" height="80"
                          fill="none"
                          :stroke="colorMap['normal-grey']"
                          stroke-width="1px"
                    ></rect>
                  </g>
                  <g class="bodyG" transform="translate(2, 25)">
                    <g class="bodyRectG"
                       :transform="`translate(${0},${0})`"
                    >
                      <rect
                          v-for="(d, i) in scope.row[attr][1]"
                          :x="i*10"
                          :y="0"
                          :width="10"
                          :height="35"
                          :fill="schemeHistoryRectColorScale(d)"
                      ></rect>
                    </g>
                  </g>

                  <g class="decorationG" transform="translate(2, 5)">
                    <line :x1="10*(Math.floor(countAttackSRTPercent/10))"
                          :x2="10*(Math.floor(countAttackSRTPercent/10))"
                          :y1="20"
                          y2="35"
                          :stroke="colorMap['risk']"
                          stroke-width="2px"

                    ></line>
                  </g>
                </svg>
                <span v-if="(typeof scope.row[attr]) === 'string'">{{scope.row[attr]}}</span>
              </template>
<!--            </el-table-column>-->
          </el-table-column>


          <el-table-column fixed="right" label="Operations" width="100" align="center">
            <template #default="scope">
              <el-button size="small" class="lockRow"
                         @click="lockScheme(scope.row['Attribute'], scope.$index)"
                         v-if="AttrLockMap[scope.row['Attribute']] !== scope.$index">
                <img src="icon/unlock.png" style="width: 12px;"></el-button>
              <el-button size="small" class="lockRow"
                         @click="unlockScheme(scope.row['Attribute'])"
                         v-else><img src="icon/lock.png" style="width: 12px;"></el-button>
              <el-button size="small" class="closeRow" @click="deleteSchemeHistoryRow(scope.$index, scope.row)"><el-icon><Close /></el-icon></el-button>
            </template>
          </el-table-column>

          <!--          <el-table-column fixed="right" label=" " width="30" align="center">-->
          <!--            <template #default="scope">-->
          <!--            </template>-->
          <!--          </el-table-column>-->

        </el-table>

      </div>

    </div>

    <div class="RowPartMain BaseMain">
      <div class="MainLabel">Query Condition for Attack</div>
      <div class="SQL_panel">
        <div id="firstQuery" class="SQL">
          <span id="firstSqlTitle" class="SqlTitle">1st query</span>
          <el-divider border-style="dashed" class="TextDivider"/>
          <div id="FirstQueryText" class="SQLText"></div>
        </div>
        <div id="secondQuery" class="SQL">
          <span id="secondSqlTitle" class="SqlTitle">2nd query</span>
          <el-divider border-style="dashed" class="TextDivider"/>
          <div id="SecondQueryText" class="SQLText" ></div>
<!--          <el-icon v-show="!availableSQL2"-->
<!--                   class="notAvailableIcon"><CircleCloseFilled /></el-icon>-->
        </div>
      </div>
      <div id="DataExploration" class="BaseMain">
        <div class="MainLabel">Data Exploration</div>
        <el-button-group class="DataExplorationSwitch">
          <el-button :class="{chosenBtn: DataExplorationStatus === 'R9T'}" type="primary" size="small"
                     @click="switch2RecordTable">Record table</el-button>
          <el-button :class="{chosenBtn: DataExplorationStatus === 'DD'}" type="primary" size="small"
                     @click="switch2DataDistribution">Data distribution</el-button>
        </el-button-group>

        <svg id="DataExplorationLegend" v-show="DataExplorationStatus === 'DD'">
          <line x1="5" x2="35" y1="8" y2="8" :stroke="colorMap['risk']" class="legendLine"></line>
          <text x="40" y="13">Potential victim</text>
          <line x1="5" x2="35" y1="29" y2="29" :stroke="colorMap['blue-normal']" class="legendLine"></line>
          <text x="40" y="33">Queried group: {{OtherRecordNum}}</text>

          <g transform="translate(30, 0)">
            <line x1="140" x2="170" y1="29" y2="29" :stroke="colorMap['selected']" stroke-width="7px"></line>
            <line x1="140" x2="140" y1="26" y2="32" :stroke="colorMap['deep-grey']" stroke-width="2px"></line>
            <line x1="170" x2="170" y1="26" y2="32" :stroke="colorMap['deep-grey']" stroke-width="2px"></line>
            <text x="175" y="33">Query condition</text>
          </g>
        </svg>

        <div class="tickSwitch" v-show="DataExplorationStatus === 'DD'">
          <el-switch
              size="small"
              v-model="DE_tick"
              class="switchTick"
              active-text="Show ticks"
              inactive-text="Hide ticks"
              @change="changeTickStatus"
          />
        </div>

        <svg id="DataDistribution" v-show="DataExplorationStatus === 'DD'"></svg>
        <el-table :data="DifferentialRecordTableData"
                  :row-style="rowStyle"
                  :header-cell-style="headerCellStyle"
                  border
                  class="RecordTable"
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
      <div class="MainLabel" style="border-top: 10px solid #f0f7fe">Data Query Simulation</div>
      <div class="flexLayout">
        <div class="SecondaryLabel">Attack Simulation</div>
        <div class="SecondaryLabel" style="margin-left: 320px">General Query Simulation</div>
      </div>
      <div class="flexLayout" style="align-items: start">
        <div id="AS_Panel" class="Panel halfPanel">
<!--          <el-divider direction="vertical" border-style="dashed" class="TextDivider"/>-->
          <div v-if="QueryType !== 'count'" class="relativeDiv deviationIntervalPanel">
            <span class="paddingRight5px relativeTop5px" style="color: rgba(241,68,68, 0.7)">Deviation interval:</span>
            <span class="RelativeToDiv">Relative to the value</span>
            <span class="paddingLeft10px">&plusmn;</span>
            <el-input-number
                v-model="PrivacyDeviation"
                :min="0"
                :max="isPercentage1 ? 100 :(MaxMap[QueryAttr] === undefined ? 10 : MaxMap[QueryAttr])"
                :step="1"
                precision="0"
                controls-position="right"
                :class="isPercentage1 ? 'percentDeviationInput' : 'deviationInput'"
                size="small"
            />
            <span style="top: 1.5px" class="percentageMasker" :class="{hidden: !isPercentage1}">%</span>
            <el-button type="primary" @click="switchPercentage1" class="refreshBtn blueBtn">
              <el-icon><Refresh /></el-icon>
              <span class="oppositeDeviation">{{ isPercentage1 ? PrivacyDeviationVal.toFixed(0) : PrivacyDeviationPercent + '%' }}</span>
            </el-button>

          </div>
          <div class="flexLayout relativeDiv thresholdPanel" v-if="QueryType === 'sum'">
            <span class="relativeTop5px">Succ rate threshold: </span>
            <svg class="RelativeToDiv SuccTextSvg">
              <text x="0" y="20" style="font-size: 12px">P</text>
              <text x="6" y="23" style="font-size: 9px">leak</text>
              <text x="27" y="20" style="font-size: 12px">({{ (curAttrRisk * 100).toFixed(0) + '%' }})</text>
              <text :x="curAttrRisk === 1 ? 67 : 61" y="22 ">&times;</text>

              <g :transform="`translate(${curAttrRisk === 1 ? 75 : 70}, 0)`">
                <text x="0" y="20" style="font-size: 12px">P</text>
                <text x="6" y="23" style="font-size: 9px">infer</text>
                <text x="27" y="20" style="font-size: 12px">({{ (deviationP1 * 100).toFixed(0) + '%' }})</text>
              </g>
            </svg>
<!--            <span class="RelativeToDiv" style="width: 400px">P<sub>set_leak</sub> ({{ curAttrRiskStr }})	&times; P<sub>infer_suc</sub> ({{ deviationP1.toFixed(2) * 100 + '%' }})</span>-->
            <el-input-number
                v-model="sumAttackSRTPercent"
                :min="0"
                :max="100"
                :step="1"
                controls-position="right"
                class="thresholdInput"
                size="small"
            />
            <span class="percentageMasker">%</span>
          </div>
          <div class="flexLayout relativeDiv" v-else>
            <span class="relativeTop5px">Succ rate threshold: </span>
            <svg class="RelativeToDiv SuccTextSvg">
              <text x="0" y="20" style="font-size: 12px">P</text>
              <text x="6" y="23" style="font-size: 9px">leak</text>
              <text x="27" y="20" style="font-size: 12px">({{ (curAttrRisk * 100).toFixed(0) + '%' }})</text>
              <text :x="curAttrRisk === 1 ? 67 : 61" y="22 ">&times;</text>

              <g :transform="`translate(${curAttrRisk === 1 ? 75 : 70}, 0)`">
                <text x="0" y="20" style="font-size: 12px">P</text>
                <text x="6" y="23" style="font-size: 9px">infer</text>
                <text x="27" y="20" style="font-size: 12px">({{ (Math.max(...deduceData) * 100).toFixed(0) + '%' }})</text>
              </g>
            </svg>
            <el-input-number
                v-model="countAttackSRTPercent"
                :min="Math.round(curAttrRisk * 100 * 0.5)"
                :max="Math.round(curAttrRisk * 100) - 1"
                :step="1"
                controls-position="right"
                class="thresholdInput"
                size="small"
            />
            <span class="percentageMasker">%</span>
          </div>
          <el-button type="primary" class="rightEdgeBtn"
                     :class="{'blueBtn': epsilon !== privacyEpsilon, 'greyBtn': epsilon === privacyEpsilon}"
                     :style="{width: QueryType !== 'count' ? '90px' : '100px'}"
                     @click="Update2PE">Update &epsilon; <br v-if="QueryType !== 'count'" />to {{privacyEpsilon}}</el-button>
        </div>
        <div id="GQS_Panel" class="Panel halfPanel">
<!--          <el-divider direction="vertical" border-style="dashed" class="TextDivider"/>-->
          <div class="relativeDiv">
            <span class="paddingRight5px relativeTop5px">Deviation interval:</span>
            <span class="RelativeToDiv">Relative to sensitivity</span>
            <span style="padding-left: 15px">&plusmn;</span>
            <el-input-number
                v-model="AccuracyDeviation"
                :min="0"
                :max="isPercentage2 ? 300 : (MaxMap[QueryAttr] === undefined ? 10 : MaxMap[QueryAttr])"
                :step="1"
                :precision="isPercentage2 ? 0 : 1"
                controls-position="right"
                :class="isPercentage2 ? 'percentDeviationInput' : 'deviationInput'"
                size="small"
            />
            <span style="top: 1.5px;"
                  :style="{'right': (isPercentage2 && AccuracyDeviationPercent === 100) ? '37px' : '40px'}"
                  class="percentageMasker" :class="{hidden: !isPercentage2}">%</span>
            <el-button type="primary" @click="switchPercentage2" class="refreshBtn blueBtn" v-if="SensitivityCalculationWay === 'Global sensitivity'">
              <el-icon><Refresh /></el-icon>
              <span class="oppositeDeviation">{{ isPercentage2 ? (QueryType === 'count' ? AccuracyDeviationVal : AccuracyDeviationVal.toFixed(0)) : AccuracyDeviationPercent + '%' }}</span>
            </el-button>
          </div>
          <div class="flexLayout">
            <span>Accuracy threshold: </span>
            <el-input-number
                v-model="AccuracySRTPercent"
                :min="0"
                :max="100"
                :step="1"
                controls-position="right"
                class="thresholdInput"
                style="margin-left: 16.5px"
                size="small"
            />
            <span class="percentageMasker">%</span>
          </div>
          <el-button type="primary" class="rightEdgeBtn"
                     :class="{'blueBtn': epsilon !== accuracyEpsilon, 'greyBtn': epsilon === accuracyEpsilon}"
                     :style="{width: '90px'}"
                     @click="Update2AE">Update &epsilon; <br/>to {{accuracyEpsilon}}</el-button>
        </div>
      </div>

      <div id="AttackSimulationViews" class="SimulationViews">
        <svg id="FirstQuerySVG" class="AS_view QueryView">
<!--          <text x="5" y="15">Attack queries</text>-->
          <text x="5" y="15">{{'Probability density (*10^-' + this.QueryPDensityPrecision + ')'}}</text>
          <g v-if="SensitivityCalculationWay === 'Local sensitivity'">
            <text x="170" y="30" style="text-anchor: end">Sensitivity</text>
            <text x="170" y="45" style="text-anchor: end" :fill="colorMap['deep-grey']">1st: {{curSensitivity1.toFixed(0)}}</text>
            <text x="170" y="60" style="text-anchor: end" :fill="colorMap['normal-grey']">2nd: {{curSensitivity2.toFixed(0)}}</text>
          </g>
          <text x="170" y="245" style="text-anchor: end">Query result</text>
          <marker id="arrow" markerUnits="strokeWidth" viewBox="0 0 12 12"
                  refX="6" refY="6" markerWidth="12" markerHeight="12" orient="auto">
            <path d="M2,2 L10,6 L2,10 L6,6 L2,2" fill="rgb(130,130,130)"></path>
          </marker>
        </svg>
        <svg id="DA_OutputSVG" class="AS_view QueryView">
<!--          <text x="45" y="15">Inference result</text>-->
          <text x="35" y="15">{{'Probability density (*10^-' + this.AttackPDensityPrecision + ')'}}</text>
<!--          <text x="105" y="40" :fill="deviationP1 > AttackSRT ? colorMap['risk'] : colorMap['deep-grey']" style="text-anchor: middle">{{'Succ rate: ' + deviationP1.toFixed(3)}}</text>-->
          <line x1="28" y1="20" x2="28" y2="190" stroke-dasharray="3 2" stroke="#dcdfe6" stroke-width="1px" />
          <text x="200" y="245" style="text-anchor: end">Inference result</text>
        </svg>
        <svg id="GeneralQuery" class="GQS_view QueryView">
          <text x="15" y="15">Deviation / sensitivity</text>
          <text x="250" y="244" style="text-anchor: end">Accuracy</text>
          <text x="420" y="15" style="text-anchor: end">Scheme list</text>
          <g class="historyPointG"></g>
          <g class="curPointG"></g>
          <g class="historyPath"></g>
          <g class="decorationG"></g>
          <g class="container"></g>
          <g class="curEventPoint"></g>
          <g class="historyEventPoint"></g>
        </svg>
      </div>

    </div>

  </div>



  <div class="InitialOverLay" v-if="DataInputVisible">
    <div class="SystemName">DPKnob</div>
    <div class="DataInput">
      <DataInput
          @inputData="initializeTree"
          @drawPCP="initializeDataDistribution"
      />
    </div>
  </div>

  <div class="deviationTooltip hidden">
    deviation: {{this.SchemeHistoryAttrDeviationMap[this.QueryAttr]}}
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
                   'blue-normal-opacity':'rgba(52, 152, 219,0.5)',
                   'risk':             'rgba(234,120,119, 1.0)',
                   'risk-opacity':     'rgba(234,120,119, 0.5)',
                   'deep-red':         'rgb(241,68,68)',
                   'light-grey':      'rgb(220,220,220)',
                   'normal-grey':      'rgb(176,176,176)',
                   'risk-stroke':      'rgba(243, 156, 18,1.0)',
                   'selected':         'rgba(249, 245, 0,1.0)',
                   'deep-grey':        'rgb(130,130,130)',
                   'black':            'rgba(70,70,70,1.0)',
                   'green':            'rgba(120, 224, 143,1.0)'
        },
        greyGradient: ['#efefef', '#777'],
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
        keyMap: {},  //conversion of (key and value scope), example: 0 -- [0, 20]
        curIndices: [],
        curAttrPos: [],
        curAttr: [],
        scale_Xscale: {},
        scaleMap: {},
        curIndex: [],
        curAttackTarget: {}, // Record the attack target, because the same attack target can be attacked by different query contents
        attrRiskMap: {},
        curAttrRisk: 0.5,
        curAttrRiskStr: '0%',
        chosenNodePos: {x: 0, y: 0},


        attrRiskLegend: [],
        queryNumLegend: [],
        MinRecordsNum: 0,
        MaxRecordsNum: 0,

        MaxMap: {}, //Record the maximum value of the attribute, categorical attributes are replaced with the maximum value of count
        MinMap: {},
        dimNodeCnt: [],
        DE_tick: true,
        PCP_tick_func: [],

        DataExplorationStatus: 'DD',
        DifferentialRecordNum: 0,
        OtherRecordNum: 0,

        // recommendation function variable
        firstQueryData: [],
        secondQueryData: [],
        generalQueryLineData: [],
        curB: 1,
        curB2: 1, // the Laplace parameter b of the second query
        curSensitivity1: 0,
        curSensitivity2: 0,
        SensitivityList: [0, 0],
        epsilon: 1.0,
        SensitivityCalculationWayOption: ['Global sensitivity', 'Local sensitivity'],
        SensitivityCalculationWay: 'Global sensitivity',
        QueryAttrOption: [],
        QueryAttrOptionType: [],
        QueryAttr: '',
        QueryType: 'sum',
        QueryCountCondition: '',
        FirstQueryCondition: {},
        SecondQueryCondition: {},
        IntervalLeft: 5,
        IntervalRight: 35,
        PrivacyDeviation: 80,
        sumAttackSRTPercent: 20,
        countAttackSRTPercent: 60,
        AccuracyDeviation: 20,
        AccuracySRTPercent: 50,
        privateVal: 0,
        QueryAccurateVal: 0,
        DeviationPrecision1: 0.1,
        isPercentage1: true,
        isPercentage2: true,
        DeviationPrecision2: 0.1,
        generalQueryFunc: {},


        privacyEpsilon: '1.0',
        accuracyEpsilon: '1.0',
        deviationP1: 0,
        deviationP2: 0,
        deviationP2List: [],


        DA_OutputXscale: {},
        GQueryXscale: {},
        DA_OutputYscale: {},
        GQueryYscale: {},

        brush: {},



        ExactVal: {'firstQuery': 0, 'secondQuery': 0},

        SchemeHistory: [],
        SchemeHistoryColumn: ['All'],
        SchemeHistoryColumnWidth: [170,120],
        SchemeHistorySecondaryColumn: {'DP scheme': ['\u03B5', 'Sensitivity']},
        SchemeHistorySecondaryColumnWidth: [[70,100], [90,110], [90,110]],
        SchemeHistoryColumnSensitivity: {},
        SchemeHistoryEpsilon: {},
        AccuracyEpsilonHistory: {},
        curEpsilonArray: [],
        initialSchemeHistory: false,
        DifferentialRecordTableData: [],
        hoverRowAttr: '',
        hoverColumn: '',
        hoverRowProp: '',

        TopAttrOption: [],
        TopAttr: '',

        SchemeHistoryAttrNumMap: {},
        SchemeHistoryAttrPosMap: {},
        SchemeHistoryAttrDeviationMap: {},
        AttrsKeyMap: [],
        BSTKeyMap: [],

        waitDeviationP1: {},
        waitDeviationP2: {},

        AttrLockMap: {},

        QueryPDensityPrecision: 0,
        AttackPDensityPrecision: 0,
        minSensitivityMap: {},
        curDifferIndex: 0,
        curQueryNodeD: {},
        isMinSQL: false,
        curAttributeSetClickNodes: [],
        curAS_nodes: [],
        waitDifferTreeMake: -1,
        IndividualIconPosList: [],

        deduceData: [0],
        availableSQL2: true,
        curDifferIndices: [],

        // high risk view variable
        histogramFunc: {},
        attrBtnStatus: {},
        IncludeAttr: [],
        ExcludeAttr: [],
        rankColor: [
          '#9b59b6',
          '#fff200',
          '#ff9f1a',
          '#ff3838',
          '#3ae374',
          '#ffb8b8',
          '#B33771',
          '#0fb9b1',
        ],
        rankFontColor: {
          // 白底字
          '#9b59b6': '#eee',
          '#B33771': '#eee',
          // 黑底字
          '#fff200': '#666',
          '#ff9f1a': '#666',
          '#ff3838': '#666',
          '#3ae374': '#666',
          '#ffb8b8': '#666',
          '#0fb9b1': '#666',
        },
        plotZipStatus: [],
        rawData: {},
        attrGropeFilter: {},
        attrSelects: {},
        TopNum: 5,
        AttrIncludeStatus: {},
        AttrFilterMap: {},
        VictimNameMap: {'All': [{}, {}]},
        curVictimGroup: 'All',
        newVictimGroupName: '',
        isClickAddVictim: false,
        riskRecordResolve: 0,
      }
    },
    computed: {
      AttackSRT() {
        return this.AttackSRTPercent / 100;
      },
      AccuracySRT() {
        return this.AccuracySRTPercent / 100;
      },
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
        // queryType (the first one is selected by default)
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
      QueryAttrRange() {
        if(this.QueryAttrIndex === -1) return [];
        return this.attrList[this.QueryAttrIndex]['Search Range'].split('~').map(d => parseFloat(d));
      },
      PrivacyDeviationVal() {
        let res;
        if(this.isPercentage1) {
          res = parseFloat(this.PrivacyDeviation) * this.privateVal / 100;
        }
        else {
          res = parseFloat(this.PrivacyDeviation);
        }
        return res
      },

      PrivacyDeviationPercent() {
        let res;
        if(this.isPercentage1) {
          res = this.PrivacyDeviation;
        }
        else {
          res = parseFloat(((this.PrivacyDeviation / this.privateVal) * 100).toFixed(0));
        }
        return res
      },
      AccuracyDeviationVal() {
        let res;
        let ratio = this.curSensitivity1 / 100;
        if(this.isPercentage2) {
          res = this.AccuracyDeviation * ratio;
        }
        else {
          res = this.AccuracyDeviation;
        }
        return res
      },
      AccuracyDeviationPercent() {
        let res;
        if(this.isPercentage2) {
          res = this.AccuracyDeviation;
        }
        else {
          res = parseFloat(((this.AccuracyDeviation / this.curSensitivity1) * 100).toFixed(0));
        }
        return res
      },
      attrInterval() {
        let index = this.attrList.findIndex(d => d.Name === this.QueryAttr);
        if(this.attrList[index].Type === 'numerical') {
          let scope = this.attrList[index]['Search Range'].split('~').map(d => parseFloat(d));
          [this.IntervalLeft, this.IntervalRight] = [scope[0], scope[0] + this.attrList[index]['Query Granularity']];
          return scope;
        }
        else {
          return []
        }
      },
      isFreshSimulationView({ QueryType, QueryAttr, IntervalLeft, IntervalRight, QueryCountCondition, SecondQueryCondition, epsilon, SensitivityCalculationWay, curAttrRisk}) {
        // combine Simulation View refresh (For Watching)
        return { QueryType, QueryAttr, IntervalLeft, IntervalRight, QueryCountCondition, SecondQueryCondition, epsilon, SensitivityCalculationWay, curAttrRisk};
      },
      isFreshHighRiskView({ QueryContent, SensitivityCalculationWay, epsilon, PrivacyDeviationPercent}) {
        return { QueryContent, SensitivityCalculationWay, epsilon, PrivacyDeviationPercent }
      },
      isFreshSchemeHistory({ QueryContent, QueryType, TopNum}) {
        return { QueryContent, QueryType, TopNum }
      },
      attrRisk() {
        return this.getAttrRisk(this.curIndices);
      },


      // Initialize Scheme History or not
      isInitializeSchemeHistory({initialSchemeHistory}) {
        return {initialSchemeHistory}
      },

      isFreshDeviationP1({ PrivacyDeviationVal, curB, curB2 }) {
        return { PrivacyDeviationVal, curB, curB2 }
      },

      isFreshDeviationP2({ AccuracyDeviationVal, curB }) {
        return { AccuracyDeviationVal, curB }
      },

      isFreshSDCView( {epsilon} ) {
        return {epsilon}
      },
      AttackSRTPercent() {
        if(this.QueryType === 'sum') {
          return this.sumAttackSRTPercent;
        }
        else {
          return this.countAttackSRTPercent;
        }
      }
    },
    methods: {
      // high risk view function
      getKeyMap(resolve) {
        axios({
          url: 'http://127.0.0.1:8000/HighRisk/getKeyMap/',
          method: 'post',
          data: {
            'filename': this.curFile,
            'attrList': this.attrList,
            'indices': this.curIndices
          }
        }).then(response => {
          this.keyMap = response.data.keyMap;
          resolve();
        })
      },
      GetHighRiskData(resolve, QueryContent, QueryType, SensitivityCalculationWay, epsilon, curVictimGroup) {
        axios({
          url: 'http://127.0.0.1:8000/HighRisk/HighRiskData/',
          method: 'post',
          data: {
            'filename': this.curFile,
            'attrList': this.attrList,
            'QueryContent': QueryContent,
            'QueryType': QueryType,
            'sensitivityWay': SensitivityCalculationWay,
            'TopNum': this.TopNum,
            'epsilon': epsilon,
            'deviationRatio': this.PrivacyDeviationPercent / 100,
            'VictimFilter': this.VictimNameMap[curVictimGroup]
          }
        }).then(response => {
          let data = response.data.data;
          let Attacks = data.Attack;
          resolve(Attacks);
        })
      },
      highRiskViewInit(resolve = '') {
        axios({
          url: 'http://127.0.0.1:8000/HighRisk/HighRiskData/',
          method: 'post',
          data: {
            'filename': this.curFile,
            'attrList': this.attrList,
            'QueryContent': this.QueryAttr,
            'QueryType': this.QueryType,
            'sensitivityWay': this.SensitivityCalculationWay,
            'TopNum': this.TopNum,
            'epsilon': this.epsilon,
            'deviationRatio': this.PrivacyDeviationPercent / 100,
            'VictimFilter': this.VictimNameMap[this.curVictimGroup]
          }
        }).then(response => {
          let data = response.data.data;
          console.log(data)
          this.rawData = data;
          let attrs = data.attrs;
          let attrNum = attrs.length;
          if(this.riskRecord.length === 0) {
            this.riskRecord = data.riskRecord;
          }
          if(this.riskRecordResolve !== 0) {
            this.riskRecordResolve();
          }
          let Attacks = data.Attack;
          let svgL = d3.select('#attrRankPlot');
          let svgR = d3.select('#highRiskPlot');
          let svgLWidth = parseInt(svgL.style('width').split('px')[0]);
          let svgHeight = parseInt(svgL.style('height').split('px')[0]);
          let svgRWidth = parseInt(svgR.style('width').split('px')[0]);
          let padding = 20;
          for(let i = 0;i<attrNum;i++) {
            this.attrRiskMap[i] = 1;
          }
          // svgL.selectAll('*').remove();
          // svgR.selectAll('*').remove();
          svgL.append("marker")
              .attr("id", "arrow")
              .attr("markerUnits","strokeWidth")
              .attr("viewBox", "0 0 12 12") //Region of coordinate system
              .attr("refX", 6) // Arrow coordinate
              .attr("refY", 6)
              .attr("markerWidth", 12)
              .attr("markerHeight", 12)
              .attr("orient", "auto")
              .append("path")
              .attr("d", "M2,2 L10,6 L2,10 L6,6 L2,2")
              .attr('fill', this.colorMap["normal-grey"]);
          svgR.append("marker")
              .attr("id", "arrow")
              .attr("markerUnits","strokeWidth")
              .attr("viewBox", "0 0 12 12") //Region of coordinate system
              .attr("refX", 6) // Arrow coordinate
              .attr("refY", 6)
              .attr("markerWidth", 12)
              .attr("markerHeight", 12)
              .attr("orient", "auto")
              .append("path")
              .attr("d", "M2,2 L10,6 L2,10 L6,6 L2,2")
              .attr('fill', this.colorMap["normal-grey"]);


          let xLScale = d3.scaleLinear([0, d3.max(Object.values(Attacks), dl => d3.max(dl, d=>d[6]+0.05))], [0, svgLWidth-2*padding]);
          let xRScale = d3.scaleLinear([0, d3.max(Object.values(Attacks), dl => d3.max(dl, d=>d[6]+0.05))], [padding, svgRWidth-padding]);
          let yScale = d3.scaleLinear([0.5, attrNum+0.5], [svgHeight - 2* padding, 10])

          let histogram = this.histogramFunc = d3.histogram()
              .domain(xRScale.domain())
              .thresholds(xRScale.ticks(20))
              .value(d => d)
          for(let attr of attrs) {
           this.attrBtnStatus[attr] = '-';
          }
          let zipData = this.dataProcessing(data, histogram);
          let violinData = zipData[2];
          let maxNum = 0
          for (let i in violinData){
            let allBins = violinData[i][1]
            let lengths = allBins.map(function(a){return a.length;})
            let longuest = d3.max(lengths)
            if (longuest > maxNum) { maxNum = longuest }
          }
          this.drawPlot(zipData, xLScale, xRScale, yScale, attrs, maxNum)
          this.clickHighRiskPoint('', zipData[4][2])
          if(resolve !== '') {
            resolve()
          }
        })
      },
      dataProcessing(data) {
        let that = this;
        let attrs = data.attrs;
        let attrNum = attrs.length;
        let Attacks = JSON.parse(JSON.stringify(data.Attack));


        if(Object.keys(this.VictimNameMap['All'][0]).length === 0) {
          this.VictimNameMap['All'] = [JSON.parse(JSON.stringify(this.attrGropeFilter)), JSON.parse(JSON.stringify(this.AttrFilterMap))];
        }
        // else {
        //   this.VictimNameMap['..now..'] = [this.attrGropeFilter, this.AttrFilterMap];
        // }
        console.log(this.VictimNameMap)

        let TopLineData = {}
        let attrPercentData = [];
        let attrSumData = [];
        // 初始化计数变量
        for(let i=1;i<=attrNum;i++) {
          TopLineData[i] = 0;
          attrPercentData[i-1] = []
          attrSumData[i-1] = 0
          for(let j in attrs) {
            attrPercentData[i-1].push(0);
          }

        }
        let violinRawData = [];

        for(let i=1;i<=attrNum;i++) {
          if(!Attacks[i]) continue
          for (let as of Attacks[i]) {
            for (let attr of as[1]) {
              attrPercentData[i - 1][attrs.indexOf(attr)] += 1;
              attrSumData[i - 1] += 1
            }
            violinRawData.push({
              'key': i,
              'value': as[6]
            })
          }
        }
        for(let [i, aps] of Object.entries(attrPercentData)) {
          for(let j in aps) {
            if(attrSumData[i]) {
              aps[j] /= attrSumData[i];
            }
          }
        }
        let attrRankData = attrPercentData;
        let highRiskPoint = [];
        let visited = []
        for(let an=1;an<=attrNum;an++) {
          if(!Attacks[an]) highRiskPoint.push(-1)
          else if(Attacks[an].length === 0) {
            highRiskPoint.push(-1)
          }else if(highRiskPoint.length === 0) {
            highRiskPoint.push(Attacks[an][0]);
            visited.push(Attacks[an][0]);
          }
          else {
            for(let at of Attacks[an]) {
              let isSame = false;
              for(let v of visited) {
                if(v[0] === at[0] && at[6] <= v[6]) {
                  let [vas, atas] = [v[1], at[1]];
                  let includeA = true;
                  for(let va of vas) {
                    if(!atas.includes(va)) {
                      includeA = false;
                      break;
                    }
                  }
                  if(includeA) {
                    isSame = true;
                  }
                }
              }
              if(!isSame) {
                highRiskPoint.push(at)
                break;
              }
            }
          }
        }
        let BottomData = [];
        for(let i=0;i<attrNum;i++) {
          BottomData.push(0);
        }
        let violinData = Array.from(d3.group(violinRawData, d => d.key));
        let curMaxRisk = 0
        for(let v of violinData) {
          TopLineData[parseInt(v[0])] = Math.max(curMaxRisk, d3.max(v[1], d => d.value))
          curMaxRisk = Math.max(TopLineData[parseInt(v[0])], curMaxRisk)
        }
        for(let v of violinData) {
          BottomData[parseInt(v[0])] = d3.min(v[1], d => d.value)
        }
        TopLineData = Object.values(TopLineData);
        violinData.forEach(d => {
          let values = d[1]
          let input = values.map(function(g) { return g.value;})    // Keep the variable called Sepal_Length
          d[1] = that.histogramFunc(input)
        })
        console.log(violinData);

        return [TopLineData, BottomData, violinData, attrRankData, highRiskPoint];
      },
      drawPlot(zipData, xLScale, xRScale, yScale, attrs, maxNum) {
        this.plotZipStatus = [xLScale, xRScale, yScale, attrs, maxNum];
        let that = this;
        let svgL = d3.select('#attrRankPlot');
        let svgR = d3.select('#highRiskPlot');
        let [TopLineData, BottomData, violinData, attrRankData, highRiskPoint] = zipData;
        let svgLWidth = parseInt(svgL.style('width').split('px')[0]);
        let svgLHeight = parseInt(svgL.style('height').split('px')[0]);
        let svgRWidth = parseInt(svgR.style('width').split('px')[0]);
        let svgRHeight = parseInt(svgR.style('height').split('px')[0]);
        let padding = 20;
        let attrNum = attrs.length;
        let xBandWidth = (svgRWidth - 2*padding) / attrNum


        let yNum = d3.scaleLinear()
            .range([-xBandWidth/2, xBandWidth/2])
            .domain([-maxNum,maxNum])

        let line=d3.line()
            .x((d, i) => xRScale(d))
            .y((d, i) => yScale(i+1));

        let xAxis = d3.axisBottom().scale(xRScale).ticks(5);
        let yAxis = d3.axisLeft().scale(yScale).ticks(8);

        svgR.select('.rightPanel').remove();
        let rightPanel = svgR.append('g').attr('class', 'rightPanel');

        rightPanel.append('g')
            .attr('class', 'Xaxis')
            .attr('transform', `translate(0, ${svgRHeight-2*padding})`)
            .call(xAxis);
        rightPanel.append('g')
            .attr('class', 'Yaxis')
            .attr('transform', `translate(${padding}, 0)`)
            .call(yAxis);
        rightPanel.select('.Xaxis')
            .select('path')
            .attr('d', (d) => {
              let pathD = rightPanel.select(`.Xaxis path`).attr('d');
              pathD = pathD.replace('V6', '')
              return pathD;
            })
            .attr('stroke', this.colorMap["deep-grey"])
            .attr("marker-end","url(#arrow)");
        rightPanel.select('.Yaxis')
            .select('path')
            .attr('d', (d) => {
              let pathD = rightPanel.select(`.Yaxis path`).attr('d');
              pathD = pathD.replace('H-6', '')
              return pathD;
            })
            .attr('stroke', this.colorMap["deep-grey"])
            .attr("marker-end","url(#arrow)");
        console.log(line(TopLineData))

        rightPanel.append('path')
            .attr('d', line(TopLineData))
            .attr('stroke', '#555')
            .attr('stroke-width', 2)
            .attr('fill', 'none');
        rightPanel.selectAll("myViolin")
            .data(violinData)
            .enter()        // So now we are working group per group
            .append("g")
            .attr("transform", d => `translate(${0}, ${yScale(d[0])})`) // Translation on the right to be at the group position
            .append("path")
            .datum(function(d){ return(d[1])})     // So now we are working bin per bin
            .style("stroke", "none")
            .style("fill","#aaa")
            .attr("d", d3.area()
                .y0(d => { return(yNum(-d.length)) } )
                .y1(d => { return(yNum(d.length)) } )
                .x((d, i, a) => {
                  let idx = violinData.find(d => d[1] === a)[0]-1;
                  if(d.x1 >= TopLineData[idx]) {
                    return xRScale(TopLineData[idx])
                  }
                  else if (d.x0 <= BottomData[idx]){
                    return xRScale(BottomData[idx])
                  }
                  return(xRScale(d.x0))
                })
                .curve(d3.curveCatmullRom)    // This makes the line smoother to give the violin appearance. Try d3.curveStep to see the difference
            )

        // 绘制 Rpanel 虚线
        let rightPanelAlignLineG = rightPanel.append('g').attr('class', 'AlignLine');
        let AlignData = [];
        for(let i = 1 ;i<=attrNum; i++) {
          AlignData.push(i);
        }
        let AlignLine =d3.line()
            .x((d, i) => xRScale(d))
            .y((d, i) => 0);
        rightPanelAlignLineG.selectAll('.AlignLine')
                            .data(AlignData)
                            .join('path')
                            .attr('transform', d => `translate(0, ${yScale(d)})`)
                            .attr('d', (d, i) => AlignLine([0, BottomData[i]]))
                            .attr('stroke', this.colorMap["deep-grey"])
                            .attr('stroke-dasharray', '5 2');


        // 绘制属性排名图
        let rankColor = this.rankColor;
        let RankLineXScale = d3.scaleLinear([0, 1.1], [10, svgLWidth-2*padding]);
        let RankLine =d3.line()
            .x((d, i) => RankLineXScale(d) + 20)
            .y((d, i) => yScale(i+1));
        let AttrRankXAxis = d3.axisBottom().scale(RankLineXScale).ticks(5);
        // 绘制 LPanel 虚线
        svgL.select('.leftPanel').remove()
        let leftPanel = svgL.append('g').attr('class', 'leftPanel');
        AlignLine.x((d, i) => d === 0 ? RankLineXScale(d) : RankLineXScale(d) + 40)
        leftPanel.selectAll('.AlignLine')
            .data(AlignData)
            .join('path')
            .attr('transform', d => `translate(0, ${yScale(d)})`)
            .attr('d', d => AlignLine(RankLineXScale.domain()))
            .attr('stroke', this.colorMap["deep-grey"])
            .attr('stroke-dasharray', '5 2');


        // let AttrRankG = leftPanel.append('g').attr('transform', `translate(${padding}, ${0})`);
        let stack = d3.stack()
            .keys(d3.range(attrNum)) // 数据系列的索引
            .order(d3.stackOrderNone) // 堆叠的顺序
            .offset(d3.stackOffsetNone); // 堆叠的偏移方式

        let stackedData = stack(attrRankData);
        // 创建区域生成器
        let area = d3.area()
            .y((d, i) => { return yScale(i+1) })
            .x0((d) => { return RankLineXScale(d[0]); })
            .x1((d) => { return RankLineXScale(d[1]); });

        // 绘制堆叠面积图
        leftPanel.selectAll(".stackPath")
            .data(stackedData)
            .enter()
            .append("path")
            .attr('class', 'stackPath')
            .attr("d", area)
            .style("fill", (d, i) => rankColor[i]);





        // 绘制最高风险点
        let pie = d3.pie();
        let highRiskPoints = rightPanel.append('g').attr('transform', `translate(${0}, ${0})`).attr('class', 'hrps');
        let arc = d3.arc()
            .innerRadius(0)
            .outerRadius(8)
        highRiskPoints.selectAll('.hrp')
            .data(highRiskPoint)
            .join('g')
            .attr('class', 'hrp')
            .attr('transform', (d, i) => {
              if(d === -1) {
                return `translate(${0}, ${0})`
              }
              else{
                if(d === -1) {
                  return `translate(${0}, ${yScale(i + 1)})`
                } else {
                  return `translate(${xRScale(d[6])}, ${yScale(i + 1)})`
                }
              }
            })
            .on('click', function(e, d) {
              that.clickHighRiskPoint(e, d);
            })
            .filter(d => d !== -1)
            .selectAll('path')
            .data(d => {
              let rawData = [];
              for(let i=0;i<d[1].length;i++) {
                rawData.push(1)
              }
              let pieData = pie(rawData);
              pieData = pieData.map((pd, i) => [d[1][i], pd]);
              return pieData;
            })
            .join('path')
            .attr('d', d => arc(d[1]))
            .attr('class', 'piePath')
            .attr('fill', d => rankColor[attrs.indexOf(d[0])])
      },
      clickHighRiskPoint(e, d) {
        let AttrNames = this.attrList.map(d => d.Name);
        this.curIndices = d[1].map(an => AttrNames.indexOf(an));
        new Promise(resolve => {
          this.getKeyMap(resolve)
        }).then(() => {
          this.clickQueryNode(d);
          this.initializeAttackSimulationViews(d);
        })
      },
      clickAddBtn() {
        this.isClickAddVictim = true;
      },
      // 仅针对 类别型数据
      attrGropeFilterChange(attr, select) {
        if(!this.attrGropeFilter[attr].includes(select)) {
          this.attrGropeFilter[attr].push(select);
        }
        else {
          let removeIdx = this.attrGropeFilter[attr].indexOf(select);
          this.attrGropeFilter[attr].splice(removeIdx, 1);
        }
        let zipData = this.dataProcessing(this.rawData);
        this.drawPlot(zipData, ...this.plotZipStatus);
      },
      changeTopNum() {
        this.highRiskViewInit();
      },
      changeRatio(attr, val) {
        console.log(attr, val, this.AttrFilterMap);
        if(this.AttrFilterMap[attr] === val) {
          this.AttrFilterMap[attr] = 'none';
        }
        else {
          this.AttrFilterMap[attr] = val
        }
      },
      RecordVictimGroup() {
        this.VictimNameMap[this.newVictimGroupName] = [JSON.parse(JSON.stringify(this.attrGropeFilter)), JSON.parse(JSON.stringify(this.AttrFilterMap))];
        // 更新 Scheme History
        this.SchemeHistoryColumn.push(this.newVictimGroupName);
        this.curVictimGroup = this.newVictimGroupName;
        this.newVictimGroupName = '';
        this.isClickAddVictim = false;
        new Promise(resolve => {
          this.highRiskViewInit(resolve)
        }).then(() => {
          let Schemes = this.SchemeHistory.map(d => d['DP scheme']);
          for(let i in Schemes) {
            let Scheme = Schemes[i].split(' ')
            new Promise(resolve => {
              if(this.SensitivityCalculationWay !== Scheme[1]) {
                this.GetHighRiskData(resolve, this.QueryAttr, this.QueryType, Scheme[1], parseFloat(Scheme[0]), this.curVictimGroup);
              }
              else {
                resolve(this.rawData['Attack'])
              }
            }).then(Attack => {
              axios({
                url: 'http://127.0.0.1:8000/RiskTree/initializeSchemeHistory/',
                method: 'post',
                data: {
                  'filename': this.curFile,
                  'deviationRatio': this.PrivacyDeviationPercent / 100,
                  'attrList': this.attrList,
                  'epsilon': parseFloat(Scheme[0]),
                  // 'sensitivity': Scheme[1],
                  'attrOption': this.attrList.map(d => d['Name']),
                  'curAttr': this.QueryAttr,
                  'Attack': Attack,
                  // 'VictimFilter': this.VictimNameMap['All']
                }
              }).then(response => {
                let index = parseInt(i);
                let data = response.data.data;
                let avgRiskP1, attackRiskP1;
                if (data['sum'] === '-') {
                  avgRiskP1 = '-';
                  attackRiskP1 = '-';
                } else {
                  avgRiskP1 = data['sum']['avgRiskList'];
                  attackRiskP1 = data['sum']['attackRiskList'];
                }
                let attackRiskP2 = data['count'][1];
                let attackRiskListP2 = data['count'][2];
                let avgRiskP2 = data['count'][0];
                this.SchemeHistory[index][this.curVictimGroup] = attackRiskP1;
              })
            })

          }

        })


      },

      // Attribute Set Tree function
      initializeTree([data, curFile, attrList, DescriptionNum]) {
        this.DescriptionNum = DescriptionNum;
        // this.riskRecord = data.riskRecord;
        console.log(this.riskRecord)
        this.BSTMap = data.BSTMap;
        this.BSTKeyMap = data.BSTKeyMap;
        console.log(this.BSTKeyMap);
        this.RiskRatioMap = data.RiskRatioMap;
        this.DataInputVisible = false;
        this.treeData = data.treeData;
        this.curFile = curFile;
        this.attrList = attrList;
        this.QueryAttrOption = attrList.filter(d => d['Sensitive attribute']).map((d) => d.Name);
        // this.TopAttrOption = attrList.map((d) => d.Name);
        this.QueryAttrOptionType = attrList.map((d) => d.Type)
        this.QueryAttr = this.QueryAttrOption[0];
        // this.TopAttr = this.QueryAttrOption[0];
        for(let i in this.QueryAttrOption) {
          i = parseInt(i)
          let attr = this.QueryAttrOption[i];
          this.attrRiskMap[1 << i] = parseInt(this.attrList[i]['Leakage Probability'].split('%')[0]) / 100;
          this.AccuracyEpsilonHistory[attr] = {};
          this.AttrLockMap[attr] = -1;
        }
        for(let attrParams of this.attrList) {
          if(attrParams['Type'] === 'numerical') {
            let [min, max] = [parseFloat(attrParams['Range'].split('~')[0]), parseFloat(attrParams['Range'].split('~')[1])]
            this.MinMap[attrParams['Name']] = min;
            this.MaxMap[attrParams['Name']] = max;
            this.attrGropeFilter[attrParams['Name']] = [min, max];

          }
          else {
            this.attrGropeFilter[attrParams['Name']] = attrParams['Range'];
            this.attrSelects[attrParams['Name']] = attrParams['Range'];
          }
          this.AttrFilterMap[attrParams['Name']] = '';


        }

        let margin = { top: 10, bottom: 10, left: 30, right: 10 };

        this.highRiskViewInit();
        // this.initializeGeneralQuerySimulationView();
      },
      MakeTree(svg, nodes, links) {
        this.curAS_nodes = nodes;
        let outerRadius = 13;
        let innerRadius = 7;
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
        // remove old edge
        TreeLink_DATA.exit().remove();
        // add new edge
        TreeLink_DATA
            .enter()
            .append("path")
            .attr('class', 'TreeLinkPath')
            .attr("fill", "none")
            .attr("stroke", this.colorMap["normal-grey"])
            .attr("stroke-width", 1);
        // uniform edge position
        TreeLinkG
            .selectAll(".TreeLinkPath")
            .attr("d", function(d) {
              let start = { x: d.source.x + outerRadius / 2, y: d.source.y };
              let end;
              if(d.target.depth === that.attrList.length) {
                end = { x: d.target.x - outerRadius / 3, y: d.target.y };
              }
              else {
                end = { x: d.target.x - outerRadius / 2 * 3, y: d.target.y };
              }
              return generator({ source: start, target: end });
            })

        let TreeNode_DATA = TreeNodeG
            .selectAll(".TreeNodePie")
            .data(nodes, d => d.data.indices);

        TreeNode_DATA.exit().remove();

        let Pie = TreeNode_DATA
            .enter()
            .append("g")
            .attr('id', d => `TreeNodePie${d.data.name}`)
            .attr("class", 'TreeNodePie');

        svg.selectAll('.TreeNodePie')
            .attr("transform", function(d) {
              let cx = d.x;
              let cy = d.y;
              return "translate(" + cx + "," + cy + ")";
            })

        // selected background stroke circle
        Pie.append('circle')
            .attr('class', 'strokeCircle')
            .attr('id', d => 'strokeCircle' + d.data.name)
            .attr('r', 0)
            .attr('cx', -outerRadius / 2)
            .attr('cy', 0)
            .attr('fill', this.colorMap['selected'])


        let outerPieColor = [this.colorMap["risk"], this.colorMap["normal-grey"]];
        let innerPieColor = [this.colorMap["risk"], this.colorMap["normal-grey"]];


        let childNodeRiskPie = Pie.selectAll(".childNodeRiskPie_path")
            .data(d => d3.pie().sort(null)(d.data.childNodeRiskPie))
            .enter()
            .append("g")
            .attr('class', 'childNodeRiskPie_path')
            .attr("transform","translate("+ -outerRadius / 2 +","+ 0 +")")
        let childNodeRiskArc = d3.arc()
            .innerRadius(innerRadius + 2)
            .outerRadius(outerRadius);
        childNodeRiskPie
            .append("path")
            .attr("fill",function(d,i){
              return outerPieColor[i];
            })
            .attr("d",function(d){
              return childNodeRiskArc(d);
            });

        let curNodeRiskPie = Pie.selectAll(".curNodeRiskPie_path")
            .data(d => {
              let data =  d3.pie().sort(null)(d.data.curNodeRiskPie);
              data[0].key = d.data.indices;
              data[1].key = d.data.indices;
              return data;
            })
            .enter()
            .append("g")
            .attr('class', 'curNodeRiskPie_path')
            .attr("transform","translate("+ -outerRadius / 2 +","+ 0 +")")
        let curNodeRiskArc = d3.arc()
            .innerRadius(0)
            .outerRadius(innerRadius);
        let greyColorScale = d3.scaleLinear()
                               .domain([0, 99])
                               .range(this.greyGradient)
        curNodeRiskPie
            .append("path")
            .attr("fill",(d,i, key) => {
              if(i === 1) {
                let risk = 1;
                let bitmap = d.key.reduce((prev, cur) => {
                  return prev += 1 << cur;
                }, 0);
                if(this.attrRiskMap[bitmap] !== undefined)  {
                  risk = this.attrRiskMap[bitmap];
                }
                else {
                  for(let j of d.key) {
                    risk = Math.min(this.attrRiskMap[1 << j], risk)
                  }
                }
                return greyColorScale(Math.round(risk * 100))
              }
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

        // event circle
        Pie.append('circle')
            .attr('class', 'eventCircle')
            .attr('id', d => 'eventCircle' + d.data.name)
            .attr('r', d => d.depth === this.this.attrList.length ? innerRadius : outerRadius)
            .attr('cx', -outerRadius / 2)
            .attr('cy', 0)
            .attr('fill', 'rgba(255,255,255,0)');
        // Removes the default right-click event of all nodes
        for (let i = 0; i < nodes.length; i++) {
          document.getElementsByClassName("eventCircle")[i].oncontextmenu = function () {
            return false;
          };
        }

        svg.selectAll('.eventCircle')
            .on('click', function(e, d) {
              that.ClickNode(svg, d);
            })
            .on("contextmenu", function (e, d) {
              that.ContextmenuNode(d);
            })
            .on('mouseover', (e, d) => {
              svg.selectAll(`.highlightTextRect`)
                  .style('opacity', 0);
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



        let highlightText = Pie.append('g')
                               .attr('class', 'highlightText')
                               .attr("transform",`translate(-30,3)`)


        //attr name text
        Pie.append("text")
            .attr('id', d => `attrName${d.data.name}`)
            .attr("x", -25)
            .attr("y", 5)
            .style('font-size', '10px')
            .style('text-anchor', 'end')
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

        // attr name text highlight rect (only valid for a single attribute)
        highlightText.append('rect')
                     .attr('class', `highlightTextRect`)
                     .attr('id', d => `highlightTextRect${d.data.name}`)
                     .attr('x', d => 5-d3.select(`#attrName${d.data.name}`).node().getComputedTextLength())
                     .attr('y', -12)
                     .attr('width', d => {
                       return d3.select(`#attrName${d.data.name}`).node().getComputedTextLength();
                     })
                     .attr('height', 20)
                     .attr('fill', this.colorMap["selected"])
                     .style('opacity', 0)
      },
      PruningAndLayout(nodes, links, width, height, maxLayer) {
        let padding = 20;
        nodes = nodes.filter(d => d.depth > 0)
        links = links.filter(d => nodes.includes(d.source) && nodes.includes(d.target))

        // Sort the outer circle proportions of the nodes (if there is no outer circle, use inner circle ratio instead)
        nodes.sort((a, b) => {
          let x, y;
          x = (a.data.childNodeRiskPie[0] === 0 && a.data.childNodeRiskPie[1] === 0) ? a.data.curNodeRiskPie : a.data.childNodeRiskPie;
          y = (b.data.childNodeRiskPie[0] === 0 && b.data.childNodeRiskPie[1] === 0) ? b.data.curNodeRiskPie : b.data.childNodeRiskPie;
          return x[1] * y[0] - x[0] * y[1];
          // a.data.childNodeRiskPie[1] * b.data.childNodeRiskPie[0] - a.data.childNodeRiskPie[0] * b.data.childNodeRiskPie[1]
        })
        let Xscale = d3.scaleLinear()
            .domain([-0.5, maxLayer - 0.5])
            .range([0, width - 60]);
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
      ClickNode(svg, d, resolve=undefined) {
        if(d.depth !== this.attrList.length) {
          if (d.data.children.length === 0) {
            this.curAttributeSetClickNodes.push(d)
            // generate node
            axios({
              url: 'http://127.0.0.1:8000/RiskTree/RiskTreeData/',
              method: 'post',
              data: {
                'filename': this.curFile,
                'attrList': this.attrList,
                'indices': d.data.indices,
                'RiskRatioMap': this.RiskRatioMap,
                'DescriptionNum': this.attrList.length
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
              [Nodes, Links] = this.PruningAndLayout(Nodes, Links, width, height, this.attrList.length)
              this.MakeTree(svg, Nodes, Links);
              if(resolve) {
                resolve(Nodes);
              }
            })
          } else {
            // delete the expansion node record
            this.curAttributeSetClickNodes.splice(this.curAttributeSetClickNodes.indexOf(d), 1);
            // shrinkage node
            d.data.children = [];
            let newTreeData = this.treeFunc(d3.hierarchy(this.treeData).sum(function (d) {
              return d.val;
            }));
            let width = parseFloat(svg.style('width').split('px')[0]);
            let height = parseFloat(svg.style('height').split('px')[0]);
            let Nodes = newTreeData.descendants();
            let Links = newTreeData.links();
            [Nodes, Links] = this.PruningAndLayout(Nodes, Links, width, height, this.attrList.length)
            this.MakeTree(svg, Nodes, Links);
          }
        }
      },
      shrinkageAllASNode() {
        // shrinkage all attribute set node
        // work backwards to avoid problems
        let svg = d3.select("#AttributeSetTree");
        let len = this.curAttributeSetClickNodes.length;
        for(let i = len-1; i>=0; i--) {
          this.ClickNode(svg, this.curAttributeSetClickNodes[i]);
        }
      },
      freshSchemeHistory() {
        let schemeLen = this.SchemeHistory.length;
        let Schemes = this.SchemeHistory.map(d => d['DP scheme']);
        for(let i=0;i < schemeLen;i++) {
          let Scheme = Schemes[i].split(' ')
          for(let column of this.SchemeHistoryColumn) {
            if(column === 'DP scheme') {
              continue
            }
            else {
              new Promise((resolve) => {
                this.GetHighRiskData(resolve, this.QueryAttr, this.QueryType, Scheme[1], parseFloat(Scheme[0]), column);
              }).then(Attack => {
                axios({
                  url: 'http://127.0.0.1:8000/RiskTree/initializeSchemeHistory/',
                  method: 'post',
                  data: {
                    'filename': this.curFile,
                    'deviationRatio': this.PrivacyDeviationPercent / 100,
                    'attrList': this.attrList,
                    'epsilon': parseFloat(Scheme[0]),
                    // 'BSTMap': this.BSTMap,
                    'sensitivity': Scheme[1],
                    'attrOption': this.attrList.map(d => d['Name']),
                    'curAttr': this.QueryAttr,
                    'Attack': Attack,
                    // 'VictimFilter': this.VictimNameMap['All']
                  }
                }).then(response => {
                  let index = parseInt(i);
                  let data = response.data.data;
                  let avgRiskP1, attackRiskP1;
                  if (data['sum'] === '-') {
                    avgRiskP1 = '-';
                    attackRiskP1 = '-';
                  } else {
                    avgRiskP1 = data['sum']['avgRiskList'];
                    attackRiskP1 = data['sum']['attackRiskList'];
                  }
                  let attackRiskP2 = data['count'][1];
                  let attackRiskListP2 = data['count'][2];
                  let avgRiskP2 = data['count'][0];
                  if (this.QueryType === 'sum') {
                    this.SchemeHistory[index][column] = attackRiskP1;
                  }
                  else {
                    this.SchemeHistory[index][column] = [attackRiskP2, attackRiskListP2];
                  }

                })
              })

              // this.SchemeHistory[i][column]
            }
          }
        }
      },
      async clickTargetRecord(index, condition) {
        let svg = d3.select("#AttributeSetTree");
        let indices = condition.indices;
        let bitmap = parseInt(condition.bitmap);
        let curBitmap = 0;
        let pre_indices = JSON.parse(JSON.stringify(indices))
        pre_indices.pop();
        for(let index of pre_indices) {
          curBitmap += 1 << index;
          let node = this.curAS_nodes.find(d => d.data.name === curBitmap);
          await new Promise(resolve => {
            this.ClickNode(svg, node, resolve);
          });
          // The key point is here. Wait for the new node to be drawn before Moving on
        }
        let targetNode = this.curAS_nodes.find(d => d.data.name === bitmap);

        // Wait for the differ query tree to generate
        new Promise(resolve => {
          this.waitDifferTreeMake = resolve;
          this.ContextmenuNode(targetNode);
        }).then((queryNodes) => {
          let targetQueryNode = queryNodes.find(d => {
            return d.data.index.length === 1 && d.data.index[0] === index;
          });

          this.clickQueryNode(targetQueryNode);
          this.convertSQL2HighRisk();
        })
      },


      // Risk Description List (used to be called Differential Query Tree )function
      ContextmenuNode(d) {
        d3.selectAll('.strokeCircle').attr('r', 0);
        d3.select("#strokeCircle" + d.data.name).attr('r', 18);
        this.chosenNodePos.x = parseFloat(d3.select("#TreeNodePie" + d.data.name).attr('transform').split(',')[0].substring(10));
        this.chosenNodePos.y = parseFloat(d3.select("#TreeNodePie" + d.data.name).attr('transform').split(',')[1].split(')')[0]);
        console.log(d3.select('.attrRiskInput'))
        d3.select('.attrRiskInput')
            .style('left', `${this.chosenNodePos.x + 45}px`)
            .style('top', `${this.chosenNodePos.y + 48}px`)
            .classed('hidden', false);

        let minP = 1;
        let bitmap = d.data.indices.reduce((prev, cur) => {
          return prev += 1 << cur;
        }, 0);
        if(this.attrRiskMap[bitmap] !== undefined)  {
          minP = this.attrRiskMap[bitmap]
        }
        else {
          for(let index of d.data.indices) {
            minP = Math.min(minP, this.attrRiskMap[1 << index]);
          }
        }
        this.curAttrRisk = minP;
        this.curIndices = d.data.indices;
        this.curAttrRiskStr = (minP * 100).toFixed(0) + '%';
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
              .attr("markerUnits","strokeWidth")
              .attr("viewBox", "0 0 12 12") //Region of coordinate system
              .attr("refX", 6) // Arrow coordinate
              .attr("refY", 6)
              .attr("markerWidth", 12)
              .attr("markerHeight", 12)
              .attr("orient", "auto")
              .append("path")
              .attr("d", "M2,2 L10,6 L2,10 L6,6 L2,2")
              .attr('fill', this.colorMap["normal-grey"]);

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

          d3.selectAll('.DDHighlightRect')
            .style('opacity', 0);
          for(let index of indices) {
            d3.select(`#DDHighlightRect-${this.QueryAttrOption[index]}`)
                .style('opacity', 1);
          }
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
        let NodeWidth = 80;
        let NodeHeight = 20;
        let NodePadding = 10;
        let DimensionTextHeight = NodeHeight;
        let iconWidth = 40;


        [nodes, keyMap] = this.TreePruning(nodes, keyMap);
        nodes = nodes.filter(d => d.depth > 0)

        links = links.filter(d => nodes.includes(d.source) && nodes.includes(d.target))
        // let finalKeyList = this.getFinalKeyList(nodes, keyMap.length);
        let leaves = nodes.filter(d => d.depth === keyMap.length);
        let leavesNum = leaves.length;
        let YScale = this.getYScale(NodeHeight, NodePadding, leavesNum);
        let height = (NodeHeight + NodePadding) * (leavesNum + 1);
        let containerHeight = parseFloat(d3.select('#DQTreeContainer').style('height').split('px')[0]);

        // if(height > containerHeight)
        //   d3.select('#DQTreeContainer').style('overflow-y', 'scroll')
        // else
        //   d3.select('#DQTreeContainer').style('overflow-y', 'hidden')
        svg.style('height', `${height}px`)

        this.encodeYIndex(nodes, keyMap.length);
        // Layout and then filter out inappropriate nodes
        nodes = nodes.filter(node => node.data.show)
        links = links.filter(d => nodes.includes(d.source) && nodes.includes(d.target))

        let Xscale = d3.scaleBand()
            .domain([-1, ...indices])
            .range([0, width]);
        [this.MinRecordsNum, this.MaxRecordsNum] = [d3.min(nodes.filter(d => d.data.num !== 1), d => d.data.num), d3.max(nodes, d => d.data.num)]
        let nodeColorScale = d3.scaleLinear()
            .domain([this.MinRecordsNum, this.MaxRecordsNum])
            .range(this.greyGradient)

        this.IndividualIconPosList = []
        for(let i in nodes) {
          let dim = nodes[i].data.dim;
          let isBST = nodes[i].data.isBST;
          nodes[i].x = Xscale(indices[dim]) - iconWidth / 2;
          nodes[i].y = YScale(nodes[i].yIndex);
          // leaf node show the individual icon
          if(isBST) {
            this.IndividualIconPosList.push([nodes[i].x + 50, nodes[i].y - 10])
          }
        }
        let generator = d3
            .linkHorizontal()
            .x(function(d) {
              return d.x;
            })
            .y(function(d) {
              return d.y;
            });
        let DimensionG = d3.select("#DQTreeAttrTitle").style('height', DimensionTextHeight + 10 + 'px');
        DimensionG.selectAll(".DimensionNodeG").remove();
        let DimensionG_DATA = DimensionG.selectAll(".DimensionNodeG").data(indices);
        let DimensionG_width = NodeWidth; //width / indices.length;
        let DimensionNodeG = DimensionG_DATA.enter()
            .append("g")
            .attr("class", 'DimensionNodeG')
            .attr("transform", d => `translate(${Xscale(d) - iconWidth / 2}, 10)`)
            .call(this.AttrDrag(DimensionG_width / 2, width, indices.length))
        this.curAttrPos = indices.map((d, i) => i);
        console.log(this.curAttrPos)
        DimensionNodeG.append('rect')
            .attr('x', -DimensionG_width / 2)
            .attr('rx', '10px')
            .attr('y', 0)
            .attr('width', DimensionG_width)
            .attr('height', DimensionTextHeight)
            .attr('stroke', this.colorMap['normal-grey'])
            .attr('fill', this.colorMap["normal-grey"])
            .attr('fill-opacity', 0);

        DimensionNodeG.append('text')
            .attr('x', 0)
            .attr('y', 14)
            .style('text-anchor', 'middle')
            // .style('line-height', DimensionTextHeight)
            .text((d, k) => this.curAttr[k])

        let TreeLinkG = svg.select(".container .TreeLinkG");
        let TreeNodeG = svg.select(".container .TreeNodeG");

        let TreeLink_DATA = TreeLinkG
            .selectAll(".TreeLinkPath")
            .data(links);
        TreeLink_DATA.exit().remove();
        TreeLink_DATA
            .enter()
            .append("path")
            .attr('class', 'TreeLinkPath')
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
              // while(node.parent.data.isBST) {
              //   node = node.parent;
              // }
              if(node.data.isBST) {
                this.clickQueryNode(node);
              }
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
            // .append('title')
            // .text(d => d.data.index);
        NodesG.append('text')
              .style('text-anchor', 'middle')
              .attr('x', 0)
              .attr('y', 3)
              .text(d => {
                let dim = d.data.dim;
                let index = this.keyMap[dim].data.indexOf(d.data.key);
                return this.convert2shortVersion(this.keyMap[dim].text[index]);
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
               return `translate(${42 - px}, ${5})`
              })
             .append('polygon')
             .attr('points', '0,10 10,10 5, 0')
             .attr('fill', '#333')

        // Automatically selects the default attack target  [if No other thread is waiting]
        if(leaves.length > 0 && this.waitDifferTreeMake === -1) {
          let defaultNode = leaves[0];
          // Get the real risk node [useless for now because the parent-child node does not have two risk nodes]
          while(defaultNode.parent.data.isBST) {
            defaultNode = defaultNode.parent;
          }
          this.clickQueryNode(defaultNode);
        }

        // let the waiting thread start
        if(this.waitDifferTreeMake !== -1) {
          this.waitDifferTreeMake(nodes);
          this.waitDifferTreeMake = -1;
        }

      },
      TreePruning(nodes, keyMap) {
        // Pruning the nodes
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

        // Prune keymap
        let keepIndex = Array([],[],[]);
        for(let node of nodeSet) {
          keepIndex[node.depth - 1].push(keyMap[node.depth - 1].data.indexOf(node.data.key));
        }
        for(let i in [0,1,2]) { // Remove Duplicates
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
        let iconWidth = 40;
        let DimensionG_Pos = width / (num + 1);
        let scale = d3.scaleLinear().domain([0, num - 1]).range([DimensionG_Pos - iconWidth / 2, width - DimensionG_Pos - iconWidth / 2]);
        let that = this;

        function dragged(event, d) {
          let pos = that.curAttrPos;
          let newX = event.x;
          // adjust the drag element position
          d3.select(this)
              .attr("transform", (d, i) => `translate(${event.x}, 10)`)
          let preIndex = pos[that.curIndices.indexOf(d)];
          let curIndex = Math.round(scale.invert(newX))

          if (curIndex > num - 1) {
            curIndex = num - 1
          }
          if(curIndex < 0) {
            curIndex = 0
          }
          // console.log(preIndex, curIndex, preIndex < curIndex)
          if (preIndex < curIndex) {
            // right moving
            pos.forEach((d, i) => {
              if (d === curIndex) {
                pos[i] -= 1;
              }
              if (d === preIndex) {
                pos[i] = curIndex
              }
            });
            d3.selectAll('.DimensionNodeG')
                .attr("transform", (d, i) => `translate(${scale(pos[i])}, 10)`)
          } else {
            if (preIndex > curIndex) {
              // left moving
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
                    return `translate(${scale(pos[i])}, 10)`
                  })
            }
          }
        }
        function ended() {
          let pos = that.curAttrPos;
          console.log(pos)
          d3.selectAll('.DimensionNodeG')
              .attr("transform", (d, i) => {
                return `translate(${scale(pos[i])}, 10)`
              });
          let temp = JSON.parse(JSON.stringify(that.curIndices))
          for(let [index, p] of Object.entries(pos)) {
            that.curIndices[p] = temp[index];
          }
          // that.curIndices = that.curIndices.map((d, i, list) => list[pos[i]]);
          console.log(that.curIndices);
          that.curAttr = that.curIndices.map(d => that.attrList[d].Name);
          that.initializeDifferQueryTree(that.curIndices);
        }

        let drag = d3.drag()
            .on("drag", dragged)
            .on('end', ended);
        return drag;
      },

      // Parallel coordinate graph method
      clickQueryNode(d) {
        d = JSON.parse(JSON.stringify(d));
        this.isMinSQL = false;
        let AttrNames = this.attrList.map(d => d.Name);


        // highlight the parallel coordinate attribute name
        d3.selectAll('.DDHighlightRect')
            .style('opacity', 0);
        let attrNames = this.attrList.map(d => d['Name'])
        for(let index of this.curIndices) {
          d3.select(`#DDHighlightRect-${attrNames[index]}`)
              .style('opacity', 1);
        }

        this.curDifferIndices = this.curIndices;
        this.curAttr = this.curIndices.map(idx => AttrNames[idx]);

        // modify curAttrRisk
        let minP = 1;
        let bitmap = this.curIndices.reduce((prev, cur) => {
          return prev += 1 << cur;
        }, 0);
        if(this.attrRiskMap[bitmap] !== undefined)  {
          minP = this.attrRiskMap[bitmap]
        }
        else {
          for(let index of this.curIndices) {
            minP = Math.min(minP, this.attrRiskMap[1 << index]);
          }
        }
        this.curAttrRisk = minP;


        this.curDifferIndex = d[1].indexOf(d[2]);
        this.curQueryNodeD = d;
        let differAttrName = this.curAttr[this.curDifferIndex]


        // (recordIndex) collection in second query condition

        this.curIndex = d[4];
        console.log(this.curIndex)
        let temp = [this.TableData[d[0]]];
        let dataNum = Math.min(this.curIndex.length, 1000);
        this.availableSQL2 = dataNum > 2;
        for(let i = 0;i<dataNum;i++) {
          let index = this.curIndex[i];
          if(index !== d[0]) {
            temp.push(this.TableData[index]);
          }
        }
        let svg = d3.select('#DataDistribution');
        // temp.push(...this.curIndex.map(d => this.TableData[d]));
        this.DifferentialRecordTableData = temp;
        this.OtherRecordNum = this.curIndex.length;
        this.DifferentialRecordNum = 1;
        for(let d of this.LineData) {
          // d['highlight'] = false;
          d['show'] = false;
        }
        let blueLineData = this.curIndex.map((index) => this.LineData[index]);
        // sampling
        if(blueLineData.length > 500) {
          // random sampling
          let N = blueLineData.length;
          let sampleNum = 500;//9999 //Math.floor(N * 0.1)
          let posArray = [];
          for(let i = 0;i<N;i++) {
            posArray.push(i);
          }
          for(let i = 0;i<sampleNum;i++) {
            let newPos = Math.floor(Math.random() * N);
            [posArray[i], posArray[newPos]] = [posArray[newPos], posArray[i]]
          }
          let choseArray = [];//JSON.parse(JSON.stringify(this.riskRecord));
          for(let i = 0;i<sampleNum;i++) {
            choseArray.push(posArray[i]);
          }
          let temp = [];
          for(let i = 0;i<sampleNum;i++) {
            temp.push(blueLineData[choseArray[i]]);
          }
          blueLineData = temp;
        }
        // for(let i of this.curIndex) {
        //   this.LineData[i]['highlight'] = this.colorMap["blue-normal"];
        // }
        this.LineData[d[0]]['show'] = true;
        d3.selectAll('.blueLineContainer > *').remove();
        svg.select('.blueLineContainer')
            .selectAll('.blueLineG')
            .data(blueLineData)
            .enter()
            .append('g')
            .attr('class', 'blueLineG')
            .append("path")
            .attr('class', 'blueLinePath')
            .attr("d", d => d.pathD)
            .attr("stroke", this.colorMap["blue-normal"])
            .attr('stroke-opacity', 0.7)
            .attr("stroke-width", 1)
            .attr("fill", "none");

        let resCloneLinePath = d3.selectAll('.riskLinePath')
            .attr('stroke-opacity', d => d.show ? 1 : 0);



        // d3.selectAll('.cloneLineG')
        //     .select('path')
        //     .attr('stroke', d => d.highlight)
        //     .attr('stroke-opacity', d => d.highlight === this.colorMap["blue-normal"] ? 0.7 : 1.0)
        //     .attr('stroke-width', d => d.highlight === this.colorMap["blue-normal"] ? 1 : 2);

        let keyList, valueList = [];
        keyList = d[5];
        // keyList.splice(this.curDifferIndex, 1)
        let normalIndices = [];
        for(let i in this.curIndices) {
          normalIndices.push(parseInt(i));
        }
        normalIndices.splice(this.curDifferIndex, 1)

        let differObj = this.keyMap[this.curDifferIndex]
        let FirstQueryText = 'WHERE ';
        // condition emptying
        this.FirstQueryCondition = {};
        this.SecondQueryCondition = {};
        for(let [i, key] of Object.entries(keyList)) {
          if(parseInt(i) === this.curDifferIndex) {
            continue
          }
          key = parseInt(key);
          let obj = this.keyMap[i];
          let text = obj.text[obj.data.indexOf(key)]
          if (obj.type === 'numerical') {
            let splitEdge = text.split('~');
            splitEdge = splitEdge.map(d => parseFloat(d))
            valueList.push(splitEdge);

            FirstQueryText += `<span class="blueFont">${this.curAttr[i]} BETWEEN ${splitEdge[0]} AND ${splitEdge[1]}</span>`
            this.FirstQueryCondition[this.curAttr[i]] ? '' : this.FirstQueryCondition[this.curAttr[i]] = [];
            this.FirstQueryCondition[this.curAttr[i]].push(splitEdge);
          } else {
            valueList.push(text)
            FirstQueryText += `<span class="blueFont">${this.curAttr[i]} = ${text}</span>`;
            this.FirstQueryCondition[this.curAttr[i]] ? '' : this.FirstQueryCondition[this.curAttr[i]] = [];
            this.FirstQueryCondition[this.curAttr[i]].push(text);
          }

          FirstQueryText += '<br/>AND ';
        }
        FirstQueryText = FirstQueryText.slice(0, -5);
        // set Corresponding SQL Commands
        if(keyList.length === 0) {
          FirstQueryText = 'WHERE 1=1'
        }

        console.log(FirstQueryText)


        let finalKeyList = new Set();
        let RiskIndex = d[0];
        let finalRiskKey = parseInt(d[5][this.curDifferIndex]);
        let finalAttr = AttrNames.indexOf(d[2])//this.curIndices[this.curIndices.length - 1];
        let finalAttrName = d[2]//this.curAttr[this.curAttr.length - 1]
        let largerFinalKeyScope = [0, -1], smallerFinalKeyScope = [0, -1];
        let upperScope = [0, 0], lowerScope = [0, 0];
        let obj = differObj;
        for(let index of this.curIndex) {
          finalKeyList.add(this.TableKeyData[index][finalAttr])
        }



        let SecondQueryText = JSON.parse(JSON.stringify(FirstQueryText));
        this.SecondQueryCondition = JSON.parse(JSON.stringify(this.FirstQueryCondition));
        // Delete the key of a node at risk
        finalKeyList.add(this.TableKeyData[RiskIndex][finalAttr]);
        let firstFinalKeyList = Array.from(finalKeyList)
        finalKeyList.delete(this.TableKeyData[RiskIndex][finalAttr]);
        finalKeyList = Array.from(finalKeyList)
        // 第二次查询更正
        let flag = false;
        let largerCategoricalFlag = true;
        let largerFinalKeyList = finalKeyList.filter(d => d > finalRiskKey);
        if(largerFinalKeyList.length !== 0) {
          largerFinalKeyScope = [Math.min(...largerFinalKeyList), Math.max(...largerFinalKeyList)];
          let text1 = obj.text[obj.data.indexOf(largerFinalKeyScope[0])]
          let text2 = obj.text[obj.data.indexOf(largerFinalKeyScope[1])]
          if (obj.type === 'numerical') {
            upperScope = [text1.split('~')[0], text2.split('~')[1]]
            if(upperScope[0] !== upperScope[1]) {
              flag = true; // determine whether "or" is necessary for lower part
              SecondQueryText += `<br/>AND <span class="redFont">(${finalAttrName} BETWEEN ${upperScope[0]} AND ${upperScope[1]}</span>`
              this.SecondQueryCondition[finalAttrName] ? '' : this.SecondQueryCondition[finalAttrName] = [];
              this.SecondQueryCondition[finalAttrName].push(upperScope);
            }
          }
          else {
            upperScope = [text2, largerFinalKeyScope[1] - largerFinalKeyScope[0] + 1]

            let SQL_in_list = []
            for(let key of finalKeyList) {
              SQL_in_list.push(`${obj.text[obj.data.indexOf(key)]}`)
            }
            SecondQueryText += `<br/>AND <span class="redFont">${finalAttrName} IN (${SQL_in_list.map(d => `'${d}'`).join(', ')})</span>`;
            this.SecondQueryCondition[finalAttrName] ? '' : this.SecondQueryCondition[finalAttrName] = [];
            this.SecondQueryCondition[finalAttrName].push(...SQL_in_list);
          }
        }
        else {
          if (obj.type !== 'numerical') {
            largerCategoricalFlag = false
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
                SecondQueryText += `<br/>AND <span class="redFont">OR ${finalAttrName} BETWEEN ${lowerScope[0]} AND ${lowerScope[1]})</span>`
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
            if(!largerCategoricalFlag) {
              let SQL_in_list = []
              for(let key of finalKeyList) {
                SQL_in_list.push(`${obj.text[obj.data.indexOf(key)]}`)
              }
              SecondQueryText += `<br/>AND <span class="redFont">${finalAttrName} IN (${SQL_in_list.map(d => `'${d}'`).join(', ')})</span>`;
              this.SecondQueryCondition[finalAttrName] ? '' : this.SecondQueryCondition[finalAttrName] = [];
              this.SecondQueryCondition[finalAttrName].push(...SQL_in_list);
            }
          }
        }
        else {
          if (obj.type === 'numerical') {
            SecondQueryText += '<span class="redFont">)</span>';
          }
        }
        let offset = 0;



        let us = JSON.parse(JSON.stringify(upperScope));
        let ls = JSON.parse(JSON.stringify(lowerScope))

        let finalMaskData = [us, ls];
        if(us[0] === 0 && us[1] === 0) {
          finalMaskData = [ls]
        }
        if(ls[0] === 0 && ls[1] === 0) {
          finalMaskData = [us]
        }
        // 第一次查询更正
        flag = false;
        largerCategoricalFlag = true;
        largerFinalKeyList = firstFinalKeyList.filter(d => d >= finalRiskKey);
        if(largerFinalKeyList.length !== 0 && largerFinalKeyList.length !== 1) {
          largerFinalKeyScope = [Math.min(...largerFinalKeyList), Math.max(...largerFinalKeyList)];
          let text1 = obj.text[obj.data.indexOf(largerFinalKeyScope[0])]
          let text2 = obj.text[obj.data.indexOf(largerFinalKeyScope[1])]
          if (obj.type === 'numerical') {
            upperScope = [text1.split('~')[0], text2.split('~')[1]]
            if(upperScope[0] !== upperScope[1]) {
              flag = true; // determine whether "or" is necessary for lower part
              FirstQueryText += `<br/>AND <span class="redFont">(${finalAttrName} BETWEEN ${upperScope[0]} AND ${upperScope[1]}</span>`
              this.FirstQueryCondition[finalAttrName] ? '' : this.FirstQueryCondition[finalAttrName] = [];
              this.FirstQueryCondition[finalAttrName].push(upperScope);
            }
          }
          else {
            upperScope = [text2, largerFinalKeyScope[1] - largerFinalKeyScope[0] + 1]

            let SQL_in_list = []
            for(let key of firstFinalKeyList) {
              SQL_in_list.push(`${obj.text[obj.data.indexOf(key)]}`)
            }
            FirstQueryText += `<br/>AND <span class="redFont">${finalAttrName} IN (${SQL_in_list.map(d => `'${d}'`).join(', ')})</span>`;
            this.FirstQueryCondition[finalAttrName] ? '' : this.FirstQueryCondition[finalAttrName] = [];
            this.FirstQueryCondition[finalAttrName].push(...SQL_in_list);
          }
        }
        else {
          if (obj.type !== 'numerical') {
            largerCategoricalFlag = false
          }
        }
        smallerFinalKeyList = firstFinalKeyList.filter(d => d <= finalRiskKey);
        if(smallerFinalKeyList.length !== 0 && smallerFinalKeyList.length !== 1) {
          smallerFinalKeyScope = [Math.min(...smallerFinalKeyList), Math.max(...smallerFinalKeyList)];
          let text1 = obj.text[obj.data.indexOf(smallerFinalKeyScope[0])]
          let text2 = obj.text[obj.data.indexOf(smallerFinalKeyScope[1])]
          if (obj.type === 'numerical') {
            lowerScope = [text1.split('~')[0], text2.split('~')[1]];
            if(lowerScope[0] !== lowerScope[1]) {
              if(flag) {
                FirstQueryText += `<br/>AND <span class="redFont">OR ${finalAttrName} BETWEEN ${lowerScope[0]} AND ${lowerScope[1]})</span>`
              }
              else {
                FirstQueryText += `<br/>AND <span class="redFont">${finalAttrName} BETWEEN ${lowerScope[0]} AND ${lowerScope[1]}</span>`
              }

              this.FirstQueryCondition[finalAttrName] ? '' : this.FirstQueryCondition[finalAttrName] = [];
              this.FirstQueryCondition[finalAttrName].push(lowerScope);
            }
            else {
              if(flag) {
                FirstQueryText.replace('(', '');
              }
            }
          }
          else {
            lowerScope = [text2, smallerFinalKeyScope[1] - smallerFinalKeyScope[0] + 1];
            if(!largerCategoricalFlag) {
              let SQL_in_list = []
              for(let key of firstFinalKeyList) {
                SQL_in_list.push(`${obj.text[obj.data.indexOf(key)]}`)
              }
              FirstQueryText += `<br/>AND <span class="redFont">${finalAttrName} IN (${SQL_in_list.map(d => `'${d}'`).join(', ')})</span>`;
              this.FirstQueryCondition[finalAttrName] ? '' : this.FirstQueryCondition[finalAttrName] = [];
              this.FirstQueryCondition[finalAttrName].push(...SQL_in_list);
            }
          }
        }
        else {
          if (obj.type === 'numerical') {
            FirstQueryText += '<span class="redFont">)</span>';
          }
        }

        d3.select("#SecondQueryText").html(SecondQueryText)
        d3.select("#FirstQueryText").html(FirstQueryText)

        // Make the last key mask alone
        // let svg = d3.select('#DataDistribution');

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
        let index = d[0];
        let finalData = this.TableData[index][finalAttrName];
        // Differential marker
        svg.select('.finalMaskCircle').remove();
        svg.select('.maskG').append('circle')
            .attr('class', 'finalMaskCircle')
            .attr('cx', this.scale_Xscale(finalAttr))
            .attr('cy', obj.type === 'numerical' ? this.scaleMap[finalAttrName](finalData) : this.scaleMap[finalAttrName](finalData) + this.scaleMap[finalAttrName].bandwidth() / 2)
            .attr('fill', this.colorMap['risk-opacity'])
            .attr('r', 5);
        let rectWidth = 6;
        finalMaskG
            .append('rect')
            .attr("x", 0)
            .attr("y", (d) => {
              if (obj.type === 'numerical') {
                return this.scaleMap[finalAttrName](d[1]) - this.scaleMap[finalAttrName](d[0]) + offset
              }
              else {
                return 0
              }
            })
            .attr('width', `${rectWidth}px`)
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

        // rect Upper and lower boundary
        svg.selectAll('.tickLine > *')
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

        // Upper boundary
        finalTickLineG.append('line')
            .attr('stroke-width', '2px')
            .attr('x1', 0)
            .attr('x2', rectWidth)
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
            .style('stroke', this.colorMap["deep-grey"]);
        // Center vertical line
        finalTickLineG.append('line')
            .attr('stroke-width', '2px')
            .attr('x1', 0)
            .attr('x2', 0)
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
                return 0
              }
              else {
                return this.scaleMap[finalAttrName].bandwidth() * d[1]
              }
            })
            .style('stroke', this.colorMap["deep-grey"]);
        // lower boundary
        finalTickLineG.append('line')
            .attr('stroke-width', '2px')
            .attr('x1', 0)
            .attr('x2', rectWidth)
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
            .style('stroke', this.colorMap["deep-grey"]);

        let MaskNodeData = svg.select('.maskG').selectAll('.MaskNodeG').data(valueList);
        MaskNodeData.exit().remove();
        let NewMaskNodeG = MaskNodeData.enter()
            .append('g')
            .attr('class', 'MaskNodeG');
        let MaskNodeG = d3.selectAll(".MaskNodeG")
            .attr('transform', (d, k) =>{
              k = normalIndices[k];
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
            .attr("x", 0)
            .attr("y", (d, k) => {
              k = normalIndices[k];
              if(typeof d !== 'string') {
                return this.scaleMap[this.curAttr[k]](d[1]) - this.scaleMap[this.curAttr[k]](d[0]) + offset
              }
              else {
                return 0
              }
            })
            .attr('width', `${rectWidth}px`)
            .attr("height", (d, k) => {
              k = normalIndices[k];
              if(typeof d !== 'string') {
                return this.scaleMap[this.curAttr[k]](d[0]) - this.scaleMap[this.curAttr[k]](d[1]) - offset
              }
              else {
                return this.scaleMap[this.curAttr[k]].bandwidth();
              }
            })
            .attr('fill', this.colorMap["selected"])
            .style('stroke', 'none');

        // rect upper boundary line
        svg.select('.tickLine')
            .selectAll('.TickLineG')
            .remove();
        let TickLineG = svg.select('.tickLine')
            .selectAll('.TickLineG')
            .data(valueList)
            .join('g')
            .attr('class', 'TickLineG')
            .attr('transform', (d, k) =>{
              k = normalIndices[k];
              let x
              if(typeof d !== 'string')
                x = d[0]
              else
                x = d
              return `translate(${this.scale_Xscale(this.curIndices[k])}, ${this.scaleMap[this.curAttr[k]](x)})`
            });
        TickLineG.append('line')
            .attr('stroke-width', '2px')
            .attr('x1', 0)
            .attr('x2', rectWidth)
            .attr('y1', (d, k) => {
              k = normalIndices[k];
              if(typeof d !== 'string') {
                return this.scaleMap[this.curAttr[k]](d[1]) - this.scaleMap[this.curAttr[k]](d[0]) + offset;
              }
              else {
                return 0
              }
            })
            .attr('y2', (d, k) => {
              k = normalIndices[k];
              if(typeof d !== 'string') {
                return this.scaleMap[this.curAttr[k]](d[1]) - this.scaleMap[this.curAttr[k]](d[0]) + offset
              }
              else {
                return 0
              }
            })
            .style('stroke', this.colorMap["deep-grey"]);
        // rect middle line
        TickLineG.append('line')
            .attr('stroke-width', '2px')
            .attr('x1', 0)
            .attr('x2', 0)
            .attr('y1', (d, k) => {
              k = normalIndices[k];
              if(typeof d !== 'string') {
                return this.scaleMap[this.curAttr[k]](d[1]) - this.scaleMap[this.curAttr[k]](d[0]) + offset;
              }
              else {
                return 0
              }
            })
            .attr('y2', (d, k) => {
              k = normalIndices[k];
              if (typeof d !== 'string') {
                return 0
              }
              else {
                return this.scaleMap[this.curAttr[k]].bandwidth();
              }
            })
            .style('stroke', this.colorMap["deep-grey"]);

        // rect lower boundary
        TickLineG.append('line')
            .attr('stroke-width', '2px')
            .attr('x1', 0)
            .attr('x2', rectWidth)
            .attr('y1', (d, k) => {
              k = normalIndices[k];
              if (typeof d !== 'string') {
                return 0
              }
              else {
                return this.scaleMap[this.curAttr[k]].bandwidth();
              }
            })
            .attr('y2', (d, k) => {
              k = normalIndices[k];
              if (typeof d !== 'string') {
                return 0
              }
              else {
                return this.scaleMap[this.curAttr[k]].bandwidth();
              }
            })
            .style('stroke', this.colorMap["deep-grey"]);


        console.log(this.FirstQueryCondition);
        console.log(this.SecondQueryCondition);

        if(this.availableSQL2) {
          this.initializeAttackSimulationViews(d);
        }
        else {
          this.cleanAttackSimulationView()
        }

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
          style = {"background": `${this.colorMap['risk-opacity']} !important`};
        }
        else {
          style = {"background": `${this.colorMap['blue-normal-opacity']} !important`};
        }
        return style;
      },
      headerCellStyle({ row, column, rowIndex, columnIndex }) {
        if(this.curDifferIndices.includes(columnIndex)) {
          return {'background': `${this.colorMap["selected"]}`};
        }
      },
      changeTickStatus() {
        let ticks = this.DE_tick ? 5 : 0;
        let that = this;
        let svg = d3.select('#DataDistribution');
        if(ticks) {
          d3.selectAll('#DataDistribution .axis')
              .each(function(d, k) {
                d3.select(this).call(that.PCP_tick_func[k]);
              });

          d3.selectAll('#DataDistribution .axis')
              .select('path')
              .attr('d', (d) => {
                let pathD = svg.select(`#axis-${d.name} path`).attr('d');
                pathD = pathD.replace('M-6,', 'M0,')
                pathD = pathD.slice(0, -3)
                return pathD;
              })
              .attr('stroke', this.colorMap["normal-grey"])
              .attr("marker-end","url(#ddarrow)");
        }
        else {
          d3.selectAll('#DataDistribution .axis > g').remove();
        }


      },
      initializeDataDistribution(response) {
        let data = response.data;
        this.AttrsKeyMap = data.AttrsKeyMap;
        console.log('AttrKeyMap:', this.AttrsKeyMap);
        let ScaleData = data.ScaleData;
        // this.MaxMap = data.MaxMap;
        let TableData = [];
        let LineData = [];
        this.TableData = data.TableData;
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
        let Line = d3.line()
            .x(function (d) {
              return d.x;
            })
            .y(function (d) {
              return d.y;
            });
        // TableData convert LineData
        this.LineData = this.TableData.map(d => {
          let temp = []
          for(let [i, key] of Object.entries(Object.keys(d))) {
            temp.push({
              x: scale_Xscale(i),
              y: ScaleData[i].type === 'numerical'? scaleMap[key](d[key]) : scaleMap[key](d[key]) + scaleMap[key].bandwidth() / 2
            })
          }
          return {'pathD': Line(temp)};
        });
        if(this.riskRecord.length === 0) {
          new Promise(resolve => {
            this.riskRecordResolve = resolve;
          }).then(() => {
            let riskLineData = this.riskRecord.map(index => this.LineData[index]);

            // sampling
            if(this.TableData.length > 2000) {
              // random sampling
              let N = this.TableData.length;
              let sampleNum = 2000;//9999 //Math.floor(N * 0.1)
              let posArray = [];
              for(let i = 0;i<N;i++) {
                posArray.push(i);
              }
              for(let i = 0;i<sampleNum;i++) {
                let newPos = Math.floor(Math.random() * N);
                [posArray[i], posArray[newPos]] = [posArray[newPos], posArray[i]]
              }
              let choseArray = [];//JSON.parse(JSON.stringify(this.riskRecord));
              for(let i = 0;i<sampleNum;i++) {
                choseArray.push(posArray[i]);
              }

              for(let i = 0;i<sampleNum;i++) {
                TableData.push(this.TableData[choseArray[i]]);
                LineData.push(this.LineData[choseArray[i]]);
              }
            }
            else {
              TableData = this.TableData;
              LineData = this.LineData;
            }
            this.TableKeyData = data.TableKeyData;




            svg.append("marker")
                .attr("id", "ddarrow")
                .attr("markerUnits","strokeWidth")
                .attr("viewBox", "0 0 12 12")
                .attr("refX", 6)
                .attr("refY", 6)
                .attr("markerWidth", 12)
                .attr("markerHeight", 12)
                .attr("orient", "auto")
                .append("path")
                .attr("d", "M2,2 L10,6 L2,10 L6,6 L2,2")
                .attr('fill', this.colorMap["deep-grey"]);


            this.PCP_tick_func = []
            let that = this;
            let maskG = svg.append('g').attr('class', 'maskG');




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
                .attr("stroke", this.colorMap["normal-grey"])
                .attr('stroke-opacity', 0.1)
                .attr("stroke-width", 1)
                .attr("fill", "none");

            svg.append('g').attr('class', 'blueLineContainer')

            svg.append("g")
                .attr('class', 'riskLineContainer')
                .selectAll('.riskLineG')
                .data(riskLineData)
                .enter()
                .append('g')
                .attr('class', 'riskLineG')
                .append("path")
                .attr('class', 'riskLinePath')
                .attr("d", d => d.pathD)
                .attr("stroke", this.colorMap["risk"])
                .attr('stroke-opacity', 0)
                .attr("stroke-width", 2)
                .attr("fill", "none");

            svg.append('g')
                .attr('class', 'tickLine');


            let axisG = svg.selectAll('.axis')
                .data(ScaleData)
                .enter()
                .append('g')
                .attr('class', 'axis')
                .attr('id', d => `axis-${d.name}`)
                .attr('transform', (d, k) => `translate(${scale_Xscale(k)}, ${0})`)
                .each(function(d, k) {
                  let tickfunc = d3.axisLeft().scale(scaleMap[d.name]).ticks(5).tickFormat(d => that.convert2word(d));
                  if(d.type === 'numerical') {
                    if(d.Tick_Values.length >= 20) {
                      if(d.Tick_Values.length & 1 === 1) {
                        svg.select(`#axis-${d.name}`)
                            .classed('hideHalfTickOdd', true)
                      }
                      else {
                        svg.select(`#axis-${d.name}`)
                            .classed('hideHalfTickEven', true)
                      }
                    }
                    tickfunc.tickValues(d.Tick_Values);
                  }
                  d3.select(this).call(tickfunc);
                  that.PCP_tick_func.push(tickfunc)
                });
            svg.selectAll('.axis')
                .select('path')
                .attr('d', (d) => {
                  let pathD = svg.select(`#axis-${d.name} path`).attr('d');
                  pathD = pathD.replace('M-6,', 'M0,')
                  pathD = pathD.slice(0, -3)
                  return pathD;
                })
                .attr('stroke', this.colorMap["deep-grey"])
                .attr("marker-end","url(#ddarrow)");

            let DDHighlightRects = axisG.append('rect')
                .attr('class', 'DDHighlightRect')
                .attr('id', d => `DDHighlightRect-${d.name}`);

            axisG.append('text')
                .attr("x", 0)
                .attr('y', 10)
                .style('text-anchor', 'middle')
                .style('fill', '#333')
                .attr('class', `DDAttrTitle`)
                .attr('id', d => `DDAttrTitle-${d.name}`)
                .text(d => d.name);

            DDHighlightRects
                .attr('x', d => -d3.select(`#DDAttrTitle-${d.name}`).node().getComputedTextLength() / 2)
                .attr('y', 0)
                .attr('width', d => d3.select(`#DDAttrTitle-${d.name}`).node().getComputedTextLength())
                .attr('height', 12)
                .attr('fill', this.colorMap["selected"])
                .style('opacity', 0);
          })
        }

      },

      // Attack Simulation method
      initializeAttackSimulationViews(d) {
        let data = this.TableData[d[0]];
        if(this.QueryType === 'count') {
          if(this.QueryAttrType === 'numerical') {
            this.privateVal = ((data[this.QueryAttr] > this.IntervalLeft) && (data[this.QueryAttr] < this.IntervalRight)) ? 1 : 0;
          }
          else {
            this.privateVal = data[this.QueryAttr] === this.QueryCountCondition ? 1 : 0;
          }
        }
        else {
          this.privateVal = data[this.QueryAttr]
        }
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
          'scope': -1,
          'privateVal': this.privateVal
        }
      }).then(response1 => {
        console.log(response1);
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
            'scope': response1.data.scope,  // the range obtained in the first query
            'privateVal': this.privateVal
          }
        }).then(response2 => {
          let data1 = response1.data;
          let data2 = response2.data;
          // data1 = typeof data1 === 'string' ? JSON.parse(data1) : data1;
          // data2 = typeof data2 === 'string' ? JSON.parse(data2) : data2;
          this.ExactVal['firstQuery'] = data1.ExactVal;
          this.ExactVal['secondQuery'] = data2.ExactVal;
          this.curB = data1.b;
          this.curB2 = data2.b;
          this.SensitivityList = [data1.sensitivities[0], data1.sensitivities[1] + ', ' + data2.sensitivities[1]];
          [this.curSensitivity1, this.curSensitivity2] = [data1.sensitivity, data2.sensitivity];
          d3.select('#FirstQuerySVG');
          this.firstQueryData = data1.distribution;
          this.secondQueryData = data2.distribution;
          this.setAttackTarget(this.TableData[d[0]])

        })
      })
      },
      cleanAttackSimulationView() {
        d3.selectAll('#FirstQuerySVG .container-left,.clipG,.outRangeG').remove();
        d3.selectAll('#DA_OutputSVG .container-right,.clipG,.outRangeG').remove();
        axios.create()
      },
      setAttackTarget(data) {

        let targetResult = this.privateVal;
        this.ExactVal['secondQuery'] = this.ExactVal['firstQuery'] - targetResult;
        let svg = d3.select('#FirstQuerySVG');
        // Plot the distribution of differential results
        this.MakeResultDistribution(svg, this.firstQueryData, 'left', false, '', this.secondQueryData);

        let scope;
        if(this.QueryType === 'count') {
          scope = [-1, 2]
        }
        else {
          scope = this.QueryAttrRange
          let scopeWidth = scope[1] - scope[0]
          scope = [scope[0] - 0.1 * scopeWidth, scope[1] + 0.1 * scopeWidth]
        }
        axios({
          url: 'http://127.0.0.1:8000/AttackSimulation/GetPrivacyDistribution/',
          method: 'post',
          data: {
            'b1': this.curB,
            'b2': this.curB2,
            'targetResult': targetResult,
            'scope': scope
          }
        }).then(response => {
          let svg = d3.select('#DA_OutputSVG');
          let lineData = response.data.distribution;
          let brushAble = this.QueryAttrType === 'numerical';
          [this.DA_OutputXscale, this.DA_OutputYscale] = this.MakeResultDistribution(svg, lineData, 'right', brushAble,'clip-privacy');
          if(this.QueryType === 'count') {
            let padding = 40, w = parseFloat(svg.style('width').split('px')[0]);
            let h = parseFloat(svg.style('height').split('px')[0]);
            let container = svg.select('.container-right');
            let deduceBarG = container.append('g').attr('class', 'deduceBarG');
            let dataset = this.deduceData = response.data.deduceBar;
            let rectWidth = 20;
            let rectYScale = d3.scaleLinear([0, Math.max(...dataset)], [h - padding, h / 2]);
            let deduceBar = deduceBarG.selectAll('.deduceBar')
                                      .data(dataset)
                                      .join('g');
            deduceBar.append('rect')
                      .attr('x',(d, i) => this.DA_OutputXscale(i) - rectWidth / 2)
                      .attr('y', d => rectYScale(d))
                      .attr('width', rectWidth)
                      .attr('height', d => h - padding - rectYScale(d))
                      .attr('fill', (d, i) => d > 0.5 ? this.colorMap["risk"] : this.colorMap["normal-grey"]);
            deduceBar.append('text')
                .attr('x',(d, i) => this.DA_OutputXscale(i))
                .attr('y', d => rectYScale(d) - 20)
                .style('text-anchor', 'middle')
                .text((d, i) => d > 0.5 ? `Yes` : `No`);
            deduceBar.append('text')
                .attr('x',(d, i) => this.DA_OutputXscale(i))
                .attr('y', d => rectYScale(d) - 5)
                .style('text-anchor', 'middle')
                .text((d, i) => d > 0.5 ? `${(d*100).toFixed(0)}%` : `${(d*100).toFixed(0)}%`);
                // .attr('fill', (d, i) => d > 0.5 ? this.colorMap["risk"] : this.colorMap["normal-grey"]);


          }
        })
        this.initializeGeneralQuerySimulationView();
      },
      MakeResultDistribution(svg, lineData, position, brushAble, clipId='', externalData=[]) {
        let padding = 40, w = parseFloat(svg.style('width').split('px')[0]);
        let h = parseFloat(svg.style('height').split('px')[0]);
        let yRange = [h - padding, padding / 4 * 3]
        let xRange;
        switch (position) {
          case 'left':
            xRange = [padding, w-padding]
            break;
          case 'right':
            xRange = [padding * 2 - 10, w - 10]
            break;
          case 'overall':
            xRange = [padding, w - padding]
        }
        let svgId = svg.attr('id');
        let lineDataLen = lineData.length;
        svg.selectAll(`.container-${position}`).remove();
        svg.selectAll('.clipG').remove();
        svg.selectAll('.outRangeG').remove();
        let xDomain = [externalData.length !== 0 ? externalData[0][0] : lineData[0][0], lineData[lineDataLen - 1][0]]
        let rightPaddingX = (xDomain[1] - xDomain[0]) * 0.05;
        xDomain[1] += rightPaddingX;
        let x = d3.scaleLinear()
            .domain(xDomain)
            .range(xRange)
            .clamp(true);
        let ymax = d3.max(lineData, d => d[1]);
        let ymin = d3.min(lineData, d => d[1]);
        if(externalData.length !== 0) {
          ymax = Math.max(ymax, d3.max(externalData, d => d[1]))
          ymin = Math.max(ymin, d3.min(externalData, d => d[1]))
        }

        let y = d3.scaleLinear()
            .domain([0, ymax])
            .range(yRange);

        let cnt = 0;
        let temp = ymax;
        while(temp < 1) {
          temp *= 10;
          cnt += 1;
        }
        if(position === 'left') {
          this.QueryPDensityPrecision = cnt;
        }
        else {
          this.AttackPDensityPrecision = cnt;
        }

        let cg = d3.line()
            .x(d => x(d[0]))
            .y(d => y(d[1]));

        let outRangeG = svg.append('g').attr('class', 'outRangeG');
        let clipG = svg.append('g').attr('class', 'clipG');
        let container = svg.append('g').attr('class', 'container-' + position);
        container.append('g').attr('class', 'historyPath')
        if (externalData.length !== 0) {
          container.append('path')
              .attr('d', cg(externalData))
              .attr('stroke', this.colorMap["normal-grey"])
              .attr('stroke-width', 2)
              .attr('fill', 'none');
        }
        let pathD;
        if(position === 'right') {
          let x1 = x(xDomain[1] - rightPaddingX);
          let x2 = xRange[0];
          pathD = cg(lineData) + `L${x1},${yRange[0]}L${x2},${yRange[0]}L${x2},${yRange[1]}`;
        }
        else {
          pathD = cg(lineData)
        }
        container.append('path')
            .attr('d', cg(lineData))
            .attr('stroke', externalData.length !== 0 ? this.colorMap["deep-grey"] : this.colorMap["blue-normal"])
            .attr('stroke-width', 2)
            .attr('fill', 'none');

        // deviation text should be placed above the path
        if(brushAble && this.QueryAttrType === 'numerical' && this.QueryType === 'sum') {
          if(clipId === 'clip-privacy') {
            // let deviationTextBgc = container.append('rect').attr('class', 'deviationTextBgc');
            let deviation1Text = container.append('text')
                .attr('class', 'deviationText')
                .attr('x', (xRange[1] + xRange[0]) / 2 - 25)
                .attr('y', (yRange[1] + yRange[0]) / 2 + 20)
                .style('text-anchor', 'middle')
                .attr('fill', this.colorMap['black'])
                // .attr('fill', this.deviationP1 > this.AttackSRT ? this.colorMap['risk'] : this.colorMap['black'])
                .text(`P`);
            container.append('text')
                .attr('class', 'deviationTextVal')
                .attr('x', (xRange[1] + xRange[0]) / 2 - 5)
                .attr('y', (yRange[1] + yRange[0]) / 2 + 20)
                .attr('fill', this.colorMap['black'])
                // .attr('fill', this.deviationP1 > this.AttackSRT ? this.colorMap['risk'] : this.colorMap['black'])
                .text(`: ${(this.deviationP1*100).toFixed(0)}%`);
            container.append('text')
                .attr('class', 'deviationText')
                .attr('x', (xRange[1] + xRange[0]) / 2 + 10 - 25)
                .attr('y', (yRange[1] + yRange[0]) / 2 + 20 + 3)
                .style('text-anchor', 'middle')
                .style('font-size', '9px')
                .attr('fill', this.colorMap['black'])
                // .attr('fill', this.deviationP1 > this.AttackSRT ? this.colorMap['risk'] : this.colorMap['black'])
                .text(`infer`);
            // deviationTextBgc.attr('width', deviation1Text.node().getComputedTextLength())
            //     .attr('height', 12)
            //     .attr('x', (xRange[1] + xRange[0]) / 2 - deviation1Text.node().getComputedTextLength() / 2)
            //     .attr('y', (yRange[1] + yRange[0]) / 2 - 10 + 20)
            //     .attr('fill', this.colorMap["selected"]);
          }
        }


        let trueVal = this.privateVal;

        let xAxis = d3.axisBottom().scale(x).tickSizeOuter(0).ticks(3).tickFormat(d => this.convert2word(d));
        if(position === 'right' && this.QueryType === 'count') {
          xAxis.tickValues([-1,0,1,2])
        }
        container.append("g")
            .attr("class", "x axis")
            .attr("transform", `translate(0, ${h - padding})`)
            .call(xAxis);

        let yAxis = d3.axisLeft().scale(y).tickSizeOuter(0).ticks(3).tickFormat(d => `${(d * Math.pow(10, cnt)).toFixed(1)}`);
        container.append("g")
            .attr("class", "y axis")
            .attr("transform", `translate(${position === 'right' ? 2 * padding - 10 : padding}, 0)`)
            .call(yAxis);

        svg.selectAll('.axis path,line')
            .attr('stroke', this.colorMap["normal-grey"]);
        svg.selectAll('.axis path')
            .attr("marker-end","url(#arrow)");

        if(brushAble && this.QueryAttrType === 'numerical' && this.QueryType === 'sum') {
          let deviation = clipId === 'clip-accuracy'? this.AccuracyDeviationVal : this.PrivacyDeviationVal;
          let func = clipId === 'clip-accuracy'? this.laplace_f : this.laplace_dv_f;
          let fillColor = clipId === 'clip-accuracy'? this.colorMap["green"] : this.colorMap["deep-red"];
          let fillOpacity = 0.7;
          let gapWidth = 0.2;
          // brush的边界
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
              .attr('d', pathD)
              .attr('stroke', 'none')
              .attr("fill", fillColor)
              .attr('fill-opacity', fillOpacity)
              .attr("fill-rule", "evenodd")
              .attr('clip-path', `url(#${clipId})`);



          // separate settings for the attack simulation view
          if(position === 'right') {
            let greyColor = this.colorMap['deep-grey'];
            let leftWidth = x(this.QueryAttrRange[0]) - xRange[0];
            let rightWidth = x(lineData[lineDataLen - 1][0]) - x(this.QueryAttrRange[1])
            outRangeG.append("clipPath")
                .attr("id", 'leftOutRange')
                .append("rect")
                .attr("x", xRange[0])
                .attr("y", 0)
                .attr("width", leftWidth)
                .attr("height", h);
            outRangeG.append("clipPath")
                .attr("id", 'rightOutRange')
                .append("rect")
                .attr("x", x(this.QueryAttrRange[1]))
                .attr("y", 0)
                .attr("width", rightWidth)
                .attr("height", h);

            outRangeG.append("path")
                .attr("stroke", 'none')
                .attr('d', pathD)
                .attr("fill", greyColor)
                .attr('fill-opacity', fillOpacity)
                .attr("fill-rule", "evenodd")
                .attr('clip-path', `url(#leftOutRange)`);

            outRangeG.append("path")
                .attr("stroke", 'none')
                .attr('d', pathD)
                .attr("fill", greyColor)
                .attr('fill-opacity', fillOpacity)
                .attr("fill-rule", "evenodd")
                .attr('clip-path', `url(#rightOutRange)`);

            // min tick
            let minTick = container.append('g').attr('class', 'minTick')
                .attr('transform', `translate(${xRange[0] + leftWidth}, ${yRange[0]})`);
            minTick.append('line')
                .attr('x1', 0).attr('y1', 0)
                .attr('x2', 0).attr('y2', -5)
                .style('stroke', this.colorMap["deep-grey"])
                .style('stroke-width', '2px');
            minTick.append('text')
                .attr('x', -10).attr('y', -10)
                .style('fill', this.colorMap["deep-grey"])
                .text('min');

            // max tick
            let maxTick = container.append('g').attr('class', 'minTick')
                .attr('transform', `translate(${x(this.QueryAttrRange[1])}, ${yRange[0]})`);
            maxTick.append('line')
                .attr('x1', 0).attr('y1', 0)
                .attr('x2', 0).attr('y2', -5)
                .style('stroke', this.colorMap["deep-grey"])
                .style('stroke-width', '2px');
            maxTick.append('text')
                .attr('x', -10).attr('y', -10)
                .style('fill', this.colorMap["deep-grey"])
                .text('max');
          }
        }
        return [x, y, trueVal];
      },

      // general query simulation method
      initializeGeneralQuerySimulationView() {
        let svg = d3.select('#GeneralQuery');
        let deviationData = [];
        let curS = 1; // The value of sensitivity does not matter because of using percentage mode
        let curB = curS / this.epsilon;
        console.log('initializeGeneralQuerySimulationView' + curB)
        let [width, height, padding] = [450, 250, 40];

        let epsilonArray = Object.keys(this.AccuracyEpsilonHistory[this.QueryAttr]);
        epsilonArray = epsilonArray.map(d => parseFloat(d));

        if(!epsilonArray.includes(this.epsilon)) {
          epsilonArray.push(this.epsilon)
        }
        epsilonArray.sort((x, y) => x-y)
        let maxEpsilon = epsilonArray[epsilonArray.length - 1];
        this.curEpsilonArray = epsilonArray;

        let func = this.generalQueryFunc = (d, epsilon) => this.laplace_P([-d, d], 1 / epsilon);
        let xDomain = [0, func(1, maxEpsilon) + 0.1];
        // let xDomain = [0, 1.05];
        let xScale = this.GQueryXscale = d3.scaleLinear(xDomain, [padding * 3 / 2, width / 4 * 3]);
        let yScale = this.GQueryYscale = d3.scaleLinear([0, 1.2], [height - padding, padding / 4 * 3]);
        let cg = d3.line()
            .x(d => xScale(d[0]))
            .y(d => yScale(d[1]));
        svg.selectAll('.container > *').remove();
        svg.selectAll('.curPointG > *').remove();
        let curPointG = svg.select('.curPointG');
        svg.selectAll('.curEventPoint > *').remove();
        let curEventPoint = svg.select('.curEventPoint');

        let container = svg.select('.container')
            // .attr('transform', 'translate(15, 0)');

        for(let deviation = 0 ; deviation <= 1.0; deviation += 0.01) {
          let curDeviation = curS * deviation;
          deviationData.push([func(curDeviation, this.epsilon), curDeviation]);
        }
        this.generalQueryLineData = deviationData;
        let generalLineData = cg(deviationData);

        let xAxisTickValues = [0, 0.2, 0.4 ,0.6, 0.8, 1.0].filter(d => d < xDomain[1]);
        let xAxis = d3.axisBottom().scale(xScale).tickSizeOuter(0)
            .tickValues(xAxisTickValues)
            .tickFormat(d => `${d * 100}%`);

        container.append("g")
            .attr("class", "x axis")
            .attr("transform", `translate(0, ${height - padding})`)
            .call(xAxis);


        let yAxis = d3.axisLeft().scale(yScale).tickSizeOuter(0)
            .tickValues([0, 0.2, 0.4 ,0.6, 0.8, 1.0])
            .tickFormat(d => `${d * 100}%`);
        container.append("g")
            .attr("class", "y axis")
            .attr("transform", `translate(${xScale.range()[0]}, 0)`)
            .call(yAxis);

        // deviation threshold scale mark
        svg.select('.decorationG > *').remove();
        svg.select('.decorationG').append('line')
                 .attr('class', 'AccuracyDeviationPercentTickLine')
                 .attr('x1', xScale(0))
                 .attr('y1', yScale(this.AccuracyDeviationPercent / 100))
                 .attr('x2', xScale.range()[1])
                 .attr('y2', yScale(this.AccuracyDeviationPercent / 100))
                 .style('stroke', this.colorMap["black"])
                 .style('stroke-width', '2px');

        let Accuracy = func(this.AccuracyDeviationPercent / 100, this.epsilon);
        curPointG.append('circle')
                 .attr('class', 'DeviationThresholdPoint')
                 .attr('epsilon', this.epsilon)
                 .attr('r', 5)
                 .attr('cx', xScale(func(this.AccuracyDeviationPercent / 100, this.epsilon)))
                 .attr('cy', yScale(this.AccuracyDeviationPercent / 100))
                 .attr('fill', Accuracy >= this.AccuracySRTPercent / 100 ? this.colorMap["green"] : 'rgb(216,216,216)')
        let e = this.epsilon;
        curEventPoint.append('circle')
            .attr('class', 'DeviationThresholdEventPoint')
            .attr('epsilon', this.epsilon)
            .attr('r', 5)
            .attr('cx', xScale(func(this.AccuracyDeviationPercent / 100, this.epsilon)))
            .attr('cy', yScale(this.AccuracyDeviationPercent / 100))
            .attr('fill', 'rgba(255,255,255,0)')
            .on('mouseover', (event) => {
              // closure for let e
              svg.select(`.pointExplanationLine1[epsilon='${e}']`).classed('hidden', false);
              svg.select(`.pointExplanationLine2[epsilon='${e}']`).classed('hidden', false);
            })
            .on('mouseout', event => {
              svg.selectAll(`.pointExplanationLine1[epsilon='${e}']`).classed('hidden', true);
              svg.selectAll(`.pointExplanationLine2[epsilon='${e}']`).classed('hidden', true);
            })


        container.append('text')
            .attr('class', 'DeviationThresholdText')
            .attr('epsilon', this.epsilon)
            .attr('x', this.GQueryXscale.range()[0] + 10)
            .attr('y', this.GQueryYscale(this.AccuracyDeviationPercent / 100) - 10)
            .style('fill', this.colorMap["black"])
            .text(`Deviation threshold`)

        // interpretation line
        let historyYScale = d3.scaleBand(d3.range(5), [padding, height - padding / 4])
        for(let i in epsilonArray) {
          i = parseInt(i);
          // update all coordinates
          let e = epsilonArray[i];
          svg.select(`.DeviationThresholdPoint[epsilon="${e}"]`)
              .attr('cx', this.GQueryXscale(this.generalQueryFunc(this.AccuracyDeviationPercent / 100, e)))
              .attr('cy', this.GQueryYscale(this.AccuracyDeviationPercent / 100));
          svg.select(`.DeviationThresholdEventPoint[epsilon="${e}"]`)
              .attr('cx', this.GQueryXscale(this.generalQueryFunc(this.AccuracyDeviationPercent / 100, e)))
              .attr('cy', this.GQueryYscale(this.AccuracyDeviationPercent / 100));
          if(parseFloat(e) !== this.epsilon) {
            svg.select(`.historyPath[epsilon="${e}"]`)
                .attr('d', cg(this.AccuracyEpsilonHistory[this.QueryAttr][e]))
          }
          container.append('line')
              .attr('class', 'pointExplanationLine1 hidden')
              .attr('epsilon', epsilonArray[i])
              .attr('x1', xScale(func(this.AccuracyDeviationPercent / 100, epsilonArray[i])))
              .attr('y1', yScale(this.AccuracyDeviationPercent / 100))
              .attr('x2', xScale.range()[1])
              .attr('y2', historyYScale(i))
              .style('stroke', this.colorMap["light-grey"])
              .style('stroke-width', '1px');
          container.append('line')
              .attr('class', 'pointExplanationLine2 hidden')
              .attr('epsilon', epsilonArray[i])
              .attr('x1', xScale.range()[1])
              .attr('y1', historyYScale(i))
              .attr('x2', xScale.range()[1] + 20)
              .attr('y2', historyYScale(i))
              .style('stroke', this.colorMap["light-grey"])
              .style('stroke-width', '1px');
          let rectWidth = 80, rectHeight = historyYScale.bandwidth() - 5;
          if(e === this.epsilon) {
            container.append('rect')
                .attr('epsilon', epsilonArray[i])
                .attr('class', 'historyTextBackRect')
                .attr('x', xScale.range()[1] + 20)
                .attr('y', historyYScale(i) - 10)
                .attr('width', 60)
                .attr('height', 24)
                .style('fill', this.colorMap["selected"])
          }
          container.append('text')
              .attr('epsilon', epsilonArray[i])
              .attr('x', xScale.range()[1] + 20 + 2)
              .attr('y', historyYScale(i))
              .text('\u03B5: ' +  epsilonArray[i]);
          container.append('text')
              .attr('epsilon', epsilonArray[i])
              .attr('class', 'historyDeviationText')
              .attr('x', xScale.range()[1] + 20 + 2)
              .attr('y', historyYScale(i) + 12)
              .text('Acc: ' +  (func(this.AccuracyDeviationPercent / 100, epsilonArray[i]) * 100).toFixed(0) + '%');
          container.append('rect')
              .attr('epsilon', epsilonArray[i])
              .attr('class', 'historyTextHoverRect')
              .attr('x', xScale.range()[1] + 20)
              .attr('y', historyYScale(i) - 10)
              .attr('width', 60)
              .attr('height', 24)
              .style('fill', 'rgba(255,255,255,0)')
              .on('mouseover', (event) => {
                // closure for let e
                container.select(`.pointExplanationLine1[epsilon='${e}']`).classed('hidden', false);
                container.select(`.pointExplanationLine2[epsilon='${e}']`).classed('hidden', false);
              })
              .on('mouseout', event => {
                container.selectAll(`.pointExplanationLine1[epsilon='${e}']`).classed('hidden', true);
                container.selectAll(`.pointExplanationLine2[epsilon='${e}']`).classed('hidden', true);
              })
        }

        container.append('path')
            .attr('d', generalLineData)
            .attr('class', 'deviationAccuracyLine')
            .attr('stroke', this.colorMap["blue-normal"])
            .attr('stroke-width', 2)
            .attr('fill', 'none');




        container.selectAll('.axis path,line')
            .attr('stroke', this.colorMap["normal-grey"]);
        container.selectAll('.axis path')
            .attr("marker-end","url(#arrow)");

        if (!this.initialSchemeHistory) {
          this.initialSchemeHistory = true;
          for(let attr of this.QueryAttrOption) {
            this.AccuracyEpsilonHistory[attr][this.epsilon] = deviationData;
          }
        }

      },
      getAttrRisk(indices) {
        let bitmap = indices.reduce((prev, cur) => {
          return prev += (1 << cur)
        }, 0);
        let ret;
        if(this.attrRiskMap[bitmap] !== undefined)  {
          ret = this.attrRiskMap[bitmap]
        }
        else {
          ret = Math.min(...indices.map(index => this.attrRiskMap[1 <<  index]));
        }
        return ret
      },
      // Attack simulation recommendation method
      UpdateEpsilonWithPrivacy() {
        // Invalid watcher trigger condition
        if(this.curSensitivity1 === 0) return;
        axios({
          url: 'http://127.0.0.1:8000/DpDecisionMaker/UpdateEpsilonWithPrivacy/',
          method: 'post',
          data: {
            'Deviation': this.PrivacyDeviationVal,
            'SRT': this.AttackSRT,
            'Sensitivity': this.curSensitivity1,
            'QueryType': this.QueryType,
            'b1': this.curB,
            'b2': this.curB2,
            'attrRisk': 1
          }
        }).then(response => {
          this.privacyEpsilon = response.data.epsilon;
        })
      },

      GetPrivacyDeviationP() {
        axios({
          url: 'http://127.0.0.1:8000/DpDecisionMaker/GetPrivacyDeviationP/',
          method: 'post',
          data: {
            'Deviation': this.PrivacyDeviationVal,
            'b1': this.curB,
            'b2': this.curB2
          }
        }).then(response => {
          this.deviationP1 = response.data.dp; //* this.attrRisk;
          let text = d3.select('#DA_OutputSVG .deviationTextVal')
          let w = parseFloat(d3.select('#DA_OutputSVG').style('width').split('px')[0]);
          if(text._groups[0][0] !== null) {
            text
                .attr('fill', this.colorMap['black'])
                // .attr('fill', this.deviationP1.toFixed(2) > this.AttackSRT ? this.colorMap['risk'] : this.colorMap['black'])
                .text(`: ${(this.deviationP1*100).toFixed(0)}%`);
            // bgc.attr('width', text.node().getComputedTextLength())
            //     .attr('height', 12)
            //     .attr('x', w / 2 + 30 - text.node().getComputedTextLength() / 2)
          }
        })
      },


      switchPercentage1() {
        this.isPercentage1 = !this.isPercentage1;
        if(this.isPercentage1) {
          this.PrivacyDeviation = (this.PrivacyDeviation / this.privateVal).toFixed(4) * 100;
        }
        else {
          this.PrivacyDeviation = parseFloat((this.PrivacyDeviation * this.privateVal / 100).toFixed(2));
        }
      },
      Update2PE() {
        this.epsilon = this.privacyEpsilon;
      },


      // General query recommendation method
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

        })
      },

      GetAccuracyDeviationP() {
        axios({
          url: 'http://127.0.0.1:8000/DpDecisionMaker/GetAccuracyDeviationP/',
          method: 'post',
          data: {
            'Deviation': this.AccuracyDeviationVal,
            'b': this.curB
          }
        }).then(response => {
          this.deviationP2 = response.data.dp.toFixed(3);
          if(typeof this.waitDeviationP2 !== 'object') {
            this.waitDeviationP2(this.deviationP2);
          }

          let deviationP2ListLen = this.deviationP2List.length;
          if(deviationP2ListLen === 0) {
            this.deviationP2List.push(this.deviationP2);
          }
          else {

          }
        })
      },

      switchPercentage2() {
        this.isPercentage2 = !this.isPercentage2;
        if(this.isPercentage2) {
          this.AccuracyDeviation = (this.AccuracyDeviation / this.curSensitivity1).toFixed(4) * 100;
        }
        else {
          this.AccuracyDeviation = this.AccuracyDeviation * this.curSensitivity1 / 100;
        }
      },
      Update2AE() {
        this.epsilon = this.accuracyEpsilon;
      },
      objectSpanMethod({ row, column, rowIndex, columnIndex }) {
        if(columnIndex === 0) {
          let attrPos = Object.values(this.SchemeHistoryAttrPosMap)
          let attrIndex = attrPos.indexOf(rowIndex);
          if(attrIndex !== -1) {
            return {
              rowspan: this.SchemeHistoryAttrNumMap[this.QueryAttrOption[attrIndex]],
              colspan: 1,
            }
          }
          else {
            return {
              rowspan: 0,
              colspan: 0,
            }
          }
        }
      },
      initializeSchemeHistory() {
        for(let [i, attr] of Object.entries(this.QueryAttrOption)) {
          this.SchemeHistoryAttrNumMap[attr] = 1;
          this.SchemeHistoryAttrPosMap[attr] = parseInt(i);
          // this.SchemeHistoryAttrDeviationMap[attr] = '50%';
          this.SchemeHistory.push({
            'DP scheme': this.epsilon.toFixed(2).toString() + ' ' + (this.SensitivityCalculationWay === 'Global sensitivity' ? 'Global' : 'Local'),
            // 'Victim Group Name': 'All',
            'Attribute': attr,
            // 'DP scheme-\u03B5': this.epsilon.toFixed(2).toString(),
            // 'DP scheme-Sensitivity': this.SensitivityCalculationWay === 'Global sensitivity' ? 'Global' : 'Local'
          });
          console.log(this.rawData)
          axios({
            url: 'http://127.0.0.1:8000/RiskTree/initializeSchemeHistory/',
            method: 'post',
            data: {
              'filename': this.curFile,
              'deviationRatio': this.PrivacyDeviationPercent / 100,
              'attrList': this.attrList,
              'epsilon': this.epsilon,
              // 'BSTMap': this.BSTMap,
              'sensitivity': this.SchemeHistoryColumnSensitivity,
              'attrOption': this.attrList.map(d => d['Name']),
              // 'attrRisk': this.attrRiskMap,
              // 'SensitivityCalculationWay': this.SensitivityCalculationWay,
              // 'AttrsKeyMap': this.AttrsKeyMap,
              // 'BSTKeyMap': this.BSTKeyMap,
              'curAttr': attr,
              'Attack': this.rawData['Attack'],
              // 'VictimFilter': this.VictimNameMap['All']
            }
          }).then(response => {
            let index = parseInt(i);
            let data = response.data.data;
            let avgRiskP1, attackRiskP1;
            // let maxRiskRecordMap = data['maxRiskRecordMap'];
            // let countMaxRiskRecord = data['countMaxRiskRecord'];
            if (data['sum'] === '-') {
              avgRiskP1 = '-';
              attackRiskP1 = '-';
            } else {
              avgRiskP1 = data['sum']['avgRiskList'];
              attackRiskP1 = data['sum']['attackRiskList'];
            }
            let attackRiskP2 = data['count'][1];
            let attackRiskListP2 = data['count'][2];
            let avgRiskP2 = data['count'][0];
            if (this.QueryType === 'sum') {
              this.SchemeHistory[index]['All'] = attackRiskP1;
            }
            else {
              this.SchemeHistory[index]['All'] = [attackRiskP2, attackRiskListP2];
            }

        })

            // initialize the history line
            let container = d3.select('#GeneralQuery .historyPath');
            d3.selectAll('#GeneralQuery .historyPath > *').remove();
            let historyPathG = container.append('g').attr('class', 'historyPathG');
            let historyPathPointG = container.append('g').attr('class', 'historyPathPointG');
            let svg = d3.select('#GeneralQuery');
            svg.selectAll('.historyPointG > *').remove();
            let historyPointG = svg.select('.historyPointG');

            svg.selectAll('.historyEventPoint > *').remove();
            let historyEventPoint = svg.select('.historyEventPoint');

            let cg = d3.line()
                .x(d => this.GQueryXscale(d[0]))
                .y(d => this.GQueryYscale(d[1]));
            historyPathG.append('path')
                .attr('d', cg(this.AccuracyEpsilonHistory[this.QueryAttr][this.epsilon]))
                .attr('stroke', this.colorMap["normal-grey"])
                .attr('stroke-width', 1)
                .attr('fill', 'none')
                .attr('class', `historyPath`)
                .attr('epsilon', this.epsilon);
            let Accuracy = this.generalQueryFunc(this.AccuracyDeviationPercent / 100, this.epsilon);
            historyPointG.append('circle')
                .attr('class', 'DeviationThresholdPoint')
                .attr('epsilon', this.epsilon)
                .attr('r', 5)
                .attr('cx', this.GQueryXscale(Accuracy))
                .attr('cy', this.GQueryYscale(this.AccuracyDeviationPercent / 100))
                .attr('fill', Accuracy >= this.AccuracySRTPercent / 100 ? this.colorMap["green"] : 'rgb(216,216,216)')
          let e = this.epsilon;
          historyEventPoint.append('circle')
              .attr('class', 'DeviationThresholdEventPoint')
              .attr('epsilon', this.epsilon)
              .attr('r', 5)
              .attr('cx', this.GQueryXscale(Accuracy))
              .attr('cy', this.GQueryYscale(this.AccuracyDeviationPercent / 100))
              .attr('fill', 'rgba(255,255,255,0)')
              .on('mouseover', (event) => {
                // closure for let e
                svg.select(`.pointExplanationLine1[epsilon='${e}']`).classed('hidden', false);
                svg.select(`.pointExplanationLine2[epsilon='${e}']`).classed('hidden', false);
              })
              .on('mouseout', event => {
                svg.selectAll(`.pointExplanationLine1[epsilon='${e}']`).classed('hidden', true);
                svg.selectAll(`.pointExplanationLine2[epsilon='${e}']`).classed('hidden', true);
              })
        }

        console.log(this.SchemeHistory);
      },
      getNewRow() {
        this.SchemeHistory.push({
          'DP scheme': this.epsilon.toFixed(2).toString() + ' ' + (this.SensitivityCalculationWay === 'Global sensitivity' ? 'Global' : 'Local'),
          'Attribute': this.QueryAttr,
        })
        let curIdx = this.SchemeHistory.length - 1;
        for(let column of this.SchemeHistoryColumn) {
          if(column !== 'DP scheme') {
            axios({
              url: 'http://127.0.0.1:8000/RiskTree/initializeSchemeHistory/',
              method: 'post',
              data: {
                'filename': this.curFile,
                'deviationRatio': this.PrivacyDeviationPercent / 100,
                'attrList': this.attrList,
                'epsilon': this.epsilon,
                'sensitivity': this.SensitivityCalculationWay,
                'attrOption': this.attrList.map(d => d['Name']),
                'curAttr': this.QueryAttr,
                'Attack': this.rawData['Attack'],
                'VictimFilter': this.VictimNameMap[column]
              }
            }).then(response => {
              let data = response.data.data;
              let avgRiskP1, attackRiskP1;
              if (data['sum'] === '-') {
                avgRiskP1 = '-';
                attackRiskP1 = '-';
              } else {
                avgRiskP1 = data['sum']['avgRiskList'];
                attackRiskP1 = data['sum']['attackRiskList'];
              }
              let attackRiskP2 = data['count'][1];
              let attackRiskListP2 = data['count'][2];
              let avgRiskP2 = data['count'][0];
              this.SchemeHistory[curIdx][column] = attackRiskP1;
            })
          }
        }
      },
      refreshAccuracyDeviationPercent() {
        let svg = d3.select('#GeneralQuery');
        // deviation percent tick line
        svg.select('.AccuracyDeviationPercentTickLine')
           .attr('y1', this.GQueryYscale(this.AccuracyDeviationPercent / 100))
           .attr('y2', this.GQueryYscale(this.AccuracyDeviationPercent / 100));
        svg.select('.DeviationThresholdText')
            .attr('x', this.GQueryXscale.range()[1] - 110)
            .attr('y', this.GQueryYscale(this.AccuracyDeviationPercent / 100) + 15)
            .text(`Deviation threshold`);
        // explanation line
        for(let e of this.curEpsilonArray) {
          // One way to solve the problem of not having a decimal point for id select
          let Accuracy = this.generalQueryFunc(this.AccuracyDeviationPercent / 100, e);
          svg.selectAll(`.DeviationThresholdPoint[epsilon='${e}']`)
              .attr('cx', this.GQueryXscale(Accuracy))
              .attr('cy', this.GQueryYscale(this.AccuracyDeviationPercent / 100))
          svg.selectAll(`.DeviationThresholdEventPoint[epsilon='${e}']`)
              .attr('cx', this.GQueryXscale(Accuracy))
              .attr('cy', this.GQueryYscale(this.AccuracyDeviationPercent / 100))
          svg.select(`.pointExplanationLine1[epsilon='${e}']`)
              .attr('x1', this.GQueryXscale(this.generalQueryFunc(this.AccuracyDeviationPercent / 100, e)))
              .attr('y1', this.GQueryYscale(this.AccuracyDeviationPercent / 100))
          svg.select(`.historyDeviationText[epsilon='${e}']`)
              .text('Acc: ' +  (this.generalQueryFunc(this.AccuracyDeviationPercent / 100, e) * 100).toFixed(0) + '%')
              // .text('Acc:' +  this.generalQueryFunc(this.AccuracyDeviationPercent / 100, e).toFixed(2));

        }
      },
      getNewAvgRiskP() {
        let insertPos = this.SchemeHistoryAttrPosMap[this.QueryAttr] + this.SchemeHistoryAttrNumMap[this.QueryAttr];
        // process SchemeHistoryAttrPosMap and SchemeHistoryAttrNumMap
        this.SchemeHistoryAttrNumMap[this.QueryAttr] += 1;
        for(let attr in this.SchemeHistoryAttrPosMap) {
          if(this.SchemeHistoryAttrPosMap[attr] >= insertPos) {
            this.SchemeHistoryAttrPosMap[attr] += 1;
          }
        }
        let attr = this.QueryAttr;
        // this.SchemeHistoryEpsilon[attr].push(this.epsilon.toFixed(2));
        this.AccuracyEpsilonHistory[attr][this.epsilon] = this.generalQueryLineData;
        let svg = d3.select("#GeneralQuery")
        svg.selectAll('.historyPath > *').remove();
        let container = svg.select('.historyPath');
        svg.selectAll('.historyPointG > *').remove();
        let historyPointG = svg.select('.historyPointG');
        svg.selectAll('.historyEventPoint > *').remove();
        let historyEventPoint = svg.select('.historyEventPoint');

        let historyPathG = container.append('g').attr('class', 'historyPathG');
        let keyNum = Object.keys(this.AccuracyEpsilonHistory[this.QueryAttr]).length;
        let cg = d3.line()
            .x(d => this.GQueryXscale(d[0]))
            .y(d => this.GQueryYscale(d[1]));
        for(let e in this.AccuracyEpsilonHistory[this.QueryAttr]) {
          historyPathG.append('path')
              .attr('d', cg(this.AccuracyEpsilonHistory[this.QueryAttr][e]))
              .attr('stroke', this.colorMap["normal-grey"])
              .attr('stroke-width', 1)
              .attr('fill', 'none')
              .attr('class', `historyPath`)
              .attr('epsilon', e);
          let Accuracy = this.generalQueryFunc(this.AccuracyDeviationPercent / 100, parseFloat(e));
          historyPointG.append('circle')
              .attr('class', 'DeviationThresholdPoint')
              .attr('epsilon', e)
              .attr('r', 5)
              .attr('cx', this.GQueryXscale(Accuracy))
              .attr('cy', this.GQueryYscale(this.AccuracyDeviationPercent / 100))
              .attr('fill', Accuracy >= this.AccuracySRTPercent / 100 ? this.colorMap["green"] : 'rgb(216,216,216)')
          historyEventPoint.append('circle')
              .attr('class', 'DeviationThresholdEventPoint')
              .attr('epsilon', e)
              .attr('r', 5)
              .attr('cx', this.GQueryXscale(Accuracy))
              .attr('cy', this.GQueryYscale(this.AccuracyDeviationPercent / 100))
              .attr('fill', 'rgba(255,255,255,0)')
              .on('mouseover', (event) => {
                // closure for let e
                svg.select(`.pointExplanationLine1[epsilon='${e}']`).classed('hidden', false);
                svg.select(`.pointExplanationLine2[epsilon='${e}']`).classed('hidden', false);
              })
              .on('mouseout', event => {
                svg.selectAll(`.pointExplanationLine1[epsilon='${e}']`).classed('hidden', true);
                svg.selectAll(`.pointExplanationLine2[epsilon='${e}']`).classed('hidden', true);
              })
        }


        let attrType = this.attrList.find(d => d.Name === attr).Type;
        let attrParams = this.attrList.find(d => d.Name === attr);
        this.SchemeHistory.splice(insertPos, 0, {
          'Victim Group Name': this.curVictimGroup,
          'Attribute': attr,
          'DP scheme-\u03B5': this.epsilon.toFixed(2)
        })
        let temp = this.SchemeHistory[insertPos];
        axios({
          url: 'http://127.0.0.1:8000/RiskTree/AvgRiskP/',
          method: 'post',
          data: {
            'filename': this.curFile,
            // 'deviationRatio': this.PrivacyDeviationPercent / 100,
            'attrParams': attrParams,
            'attr': attr,
            'epsilon': this.epsilon,
            'BSTMap': this.BSTMap,
            'sensitivity': this.SchemeHistoryColumnSensitivity[attr],
            'attrOption': this.attrList.map(d => d['Name']),
            'attrRisk': this.attrRiskMap,
            'SensitivityCalculationWay': this.SensitivityCalculationWay,
            'AttrsKeyMap': this.AttrsKeyMap,
            'BSTKeyMap': this.BSTKeyMap,
            'minSensitivityMap': this.minSensitivityMap[attr],
            'Attack': this.rawData['Attack'],
            // 'VictimFilter': this.VictimNameMap[this.curVictimGroup]

          }
        }).then(response => {
          let data = response.data.data;
          let avgRiskP1, attackRiskP1;
          if (data['sum'] === '-') {
            avgRiskP1 = '-';
            attackRiskP1 = '-';
          } else {
            avgRiskP1 = data['sum']['avgRiskList'];
            attackRiskP1 = data['sum']['attackRiskList'];
          }
          let attackRiskP2 = data['count'][1];
          let attackRiskListP2 = data['count'][2];
          let avgRiskP2 = data['count'][0];
          temp['maxRiskRecordMap'] = data['maxRiskRecordMap'];
          temp['DP scheme-Sensitivity'] = this.SensitivityCalculationWay === 'Global sensitivity' ? 'Global' : 'Local';
          temp['Sum-Succ rate'] = attackRiskP1;
          temp['Sum-Average risk'] = avgRiskP1;
          temp['Count-Succ rate'] = [attackRiskP2.toFixed(2), attackRiskListP2];
          temp['Count-Average risk'] = avgRiskP2.toFixed(2);
          temp['countMaxRiskRecord'] = data['countMaxRiskRecord'];

        })

      },
      refreshAvgRiskP() {
        for(let i = 0;i<this.SchemeHistory.length;i++) {
          let row = this.SchemeHistory[i];
          let epsilon = parseFloat(row['DP scheme-\u03B5']);
          let attr = row['Attribute'];
          let attrType = this.attrList.find(d => d.Name === attr).Type;
          let attrParams = this.attrList.find(d => d.Name === attr);
          axios({
            url: 'http://127.0.0.1:8000/RiskTree/AvgRiskP/',
            method: 'post',
            data: {
              'filename': this.curFile,
              'attrParams': attrParams,
              'attr': attr,
              'epsilon': epsilon,
              'BSTMap': this.BSTMap,
              'sensitivity': this.SchemeHistoryColumnSensitivity[attr],
              'attrOption': this.attrList.map(d => d['Name']),
              'attrRisk': this.attrRiskMap,
              'SensitivityCalculationWay': this.SensitivityCalculationWay,
              'AttrsKeyMap': this.AttrsKeyMap,
              'BSTKeyMap': this.BSTKeyMap
            }
          }).then(response => {
            let data = response.data.data;
            let avgRiskP1, attackRiskP1;
            if (data['sum'] === '-') {
              avgRiskP1 = '-';
              attackRiskP1 = '-';
            } else {
              avgRiskP1 = data['sum']['avgRiskList'];
              attackRiskP1 = data['sum']['attackRiskList'];
            }
            let attackRiskP2 = data['count'][1];
            let attackRiskListP2 = data['count'][2];
            let avgRiskP2 = data['count'][0];
            row['DP scheme-Sensitivity'] = this.SensitivityCalculationWay === 'Global sensitivity' ? 'Global' : 'Local';
            row['Sum-Succ rate'] = attackRiskP1;
            row['Sum-Average risk'] = avgRiskP1;
            row['Count-Succ rate'] = [attackRiskP2.toFixed(2), attackRiskListP2];
            row['Count-Average risk'] = avgRiskP2.toFixed(2);
            row['maxRiskRecordMap'] = data['maxRiskRecordMap'];
            row['countMaxRiskRecord'] = data['countMaxRiskRecord']
          })

        }
      },
      HeatmapCellClick(row, column, cell, event) {
        let attr = row['Attribute']
        if(column.property === 'Sum-Succ rate') {
          console.log(row['maxRiskRecordMap'])
          let percent = (this.PrivacyDeviationPercent / 100).toFixed(1);
          // if(row['maxRiskRecordMap'][percent].risk > this.sumAttackSRTPercent / 100) {
            let index = row['maxRiskRecordMap'][percent].index;
            let condition = row['maxRiskRecordMap'][percent].condition;
            this.shrinkageAllASNode();
            this.clickTargetRecord(index, condition);
          // }
        }
        else if(column.property === 'Count-Succ rate') {
          // if(row['countMaxRiskRecord'].risk > this.sumAttackSRTPercent / 100) {
            let index = row['countMaxRiskRecord'].index;
            let condition = row['countMaxRiskRecord'].condition;
            this.shrinkageAllASNode();
            this.clickTargetRecord(index, condition);
          // }
        }
      },

      hoverRowClassName({ row, rowIndex }) {
        let classNames = []
        if (row['Attribute'] === this.hoverRowAttr && this.hoverColumn === 'Attribute') {
          classNames.push('hover-row');
        }
        // if(this.AttrLockMap[row['Attribute']] !== -1 && rowIndex !== this.AttrLockMap[row['Attribute']]) {
        //   classNames.push('unlock-row');
        // }
        return classNames.join(' ');
      },
      hoverCellClassName({ row, column, rowIndex, columnIndex }) {
        if(row['Attribute'] === this.hoverRowAttr && (this.hoverColumn && this.hoverColumn !== 'Attribute') && columnIndex === 0) {
          return 'hover-cell'
        }
        else if(row['Attribute'] + '-' + row['DP scheme-\u03B5'] === this.hoverRowProp) {
          return 'hover-cell'
        }
      },

      deleteSchemeHistoryRow(index, row) {
        let attr = this.SchemeHistory[index]['Attribute'];
        let e = parseFloat(this.SchemeHistory[index]['DP scheme-\u03B5']);
        delete this.AccuracyEpsilonHistory[attr][e]
        // delete history line
        d3.selectAll(`#GeneralQuery [epsilon="${e}"]`).remove();

        this.SchemeHistory.splice(index, 1);
        this.SchemeHistoryAttrNumMap[attr] -= 1;
        let pos = this.SchemeHistoryAttrPosMap[attr];
        for(let attr in this.SchemeHistoryAttrPosMap) {
          if(this.SchemeHistoryAttrPosMap[attr] > pos) {
            this.SchemeHistoryAttrPosMap[attr] -= 1;
          }
        }
      },
      CellMouseEnter(row, column, cell, event) {
        this.hoverRowAttr = row['Attribute'];
        this.hoverColumn = column.label;
        this.hoverRowProp = row['Attribute'] + '-' + row['DP scheme-\u03B5'];
      },
      CellMouseLeave(row, column) {
        this.hoverRowAttr = '';
        this.hoverColumn = '';
        this.hoverRowProp = '';
      },

      RecordEpsilon() {
        this.getNewRow();
        // this.getNewAvgRiskP();
      },


      schemeHistoryRectColorScale(x) {
        const colorScale = d3.scaleLinear([0,1], ['#efefef', '#777']);
        if(x === 0) {
          return '#fff'
        }
        return colorScale(x);
      },
      schemeHistoryPathDGenerator(data) {
        let width = 70, height = 30, padding = 2;
        let xScale = d3.scaleLinear([0,1], [padding, width - padding]);
        let yScale = d3.scaleLinear([0,1], [height - padding, padding]);
        const cg = d3.line()
                     .x(d => xScale(d[0]))
                     .y(d => yScale(d[1]));
        let lineData = [];
        for(let i in data) {
          let index = parseInt(i);
          lineData.push([index/100, data[i]]);
        }
        return cg(lineData);
      },
      laplace_f(x) {
        let b = this.curB;
        return 1 / (2 * b) * Math.exp(-Math.abs(x) / b)
      },
      laplace_F(b, x) {
        return 1 / 2 + Math.sign(x) / 2 * (1 - Math.exp(-Math.abs(x) / b))
      },
      laplace_P(interval, b) {
        return this.laplace_F(b, interval[1]) - this.laplace_F(b, interval[0])
      },
      laplace_dv_f(x) {
        let b = this.curB === 0 ? 0.01 : this.curB;
        return this.laplace_f(x) / 2 + Math.abs(x) / (4 * b * b) * Math.exp(-Math.abs(x) / b)
      },
      lockScheme(attr, index) {
        this.AttrLockMap[attr] = index;
      },
      unlockScheme(attr) {
        this.AttrLockMap[attr] = -1;
      },
      convert2shortVersion(str) {
        // categorical
        if(str.indexOf('~') === -1) return str;
        let splitA = str.split('~');
        let left = this.convert2word(parseFloat(splitA[0]));
        let right = this.convert2word(parseFloat(splitA[1]));
        return `${left}~${right}`;
      },
      convert2word(num) {
        if((typeof num) === 'string') {
          return num;
        }
        if(num % 1 !== 0) {
          return '';
        }
        let sign = num < 0 ? '-' : '';
        let absNum = Math.abs(num)
        // if(absNum > 10000) {
        //   let t = num % 10000 === 0 ? 0 : 3;
        //   return (num / 10000).toFixed(t) + 'w'
        // }
        if(absNum > 1000) {
          if(absNum < 2100 && absNum === Math.round(absNum)) {
            return num
          }
          let t = num % 1000 === 0 ? 0 : 3;
          return (num / 1000).toFixed(t) + 'k'
        }
        return num.toString();
      },
      switchSQL() {
        if(this.isMinSQL) {
          this.clickQueryNode(this.curQueryNodeD);
        }
        else {
          this.convertSQL2HighRisk();
        }
      },
      convertSQL2HighRisk() {
        this.isMinSQL = true;
        this.availableSQL2 = true;
        // Gets the minimum sensitivity of the current target
        axios({
          url: 'http://127.0.0.1:8000/RiskTree/curHighRiskSQL/',
          method: 'post',
          data: {
            'filename': this.curFile,
            'attrList': this.attrList,
            'attrOption': this.QueryAttrOption,
            'AttrsKeyMap': this.AttrsKeyMap,
            'BSTKeyMap': this.BSTKeyMap,
            'QueryAttr': this.QueryAttr,
            'index': this.curDifferIndex,
            'attrIndex': this.QueryAttrIndex,
            'attrRiskMap': this.attrRiskMap,
            'epsilon': this.epsilon,
            'deviation': this.PrivacyDeviationVal,
            'privateVal': this.privateVal,
            'SensitivityCalculationWay': this.SensitivityCalculationWay,
            'sensitivity': this.SensitivityList[0] === 0 ? 1 : this.SensitivityList[0]
          }
        }).then((response) => {
          let curMinSensitivityMap = response.data.minSensitivityMap;
          let firstCondition = this.FirstQueryCondition = curMinSensitivityMap.firstSensitivityWay;
          let secondCondition = this.SecondQueryCondition = curMinSensitivityMap.secondSensitivityWay;
          let minSensitivityDataIndices = curMinSensitivityMap.minSensitivityDataIndices;
          d3.selectAll('.DDHighlightRect')
              .style('opacity', 0);
          for(let attr of Object.keys(secondCondition)) {
            d3.select(`#DDHighlightRect-${attr}`)
                .style('opacity', 1);
          }
          // modify curAttrRisk
          let curIndices = this.curDifferIndices = Object.keys(secondCondition).map(attr => {
            return this.attrList.findIndex(d => d.Name === attr)
          });
          let minP = 1;
          let bitmap = curIndices.reduce((prev, cur) => {
            return prev += 1 << cur;
          }, 0);
          if(this.attrRiskMap[bitmap] !== undefined)  {
            minP = this.attrRiskMap[bitmap]
          }
          else {
            for(let index of curIndices) {
              minP = Math.min(minP, this.attrRiskMap[1 << index]);
            }
          }
          this.curAttrRisk = minP;


          console.log(this.minSensitivityMap);


          let maskData = [];
          let differAttr = [], differAttrIndex = [];
          for(let attr in secondCondition) {
            if(firstCondition[attr] === undefined || firstCondition[attr].length === 2) {
              differAttr.push(attr);
              differAttrIndex.push(this.attrList.findIndex(d => d.Name === attr))
            }
            maskData.push({
              'attr': attr,
              'attrIndex': this.attrList.findIndex(d => d.Name === attr),
              'scope': this.convertCondition2Scope(secondCondition[attr], this.TableData[this.curDifferIndex][attr])
            })
          }
          let specialDiff = this.SensitivityCalculationWay === 'Local sensitivity';
          let firstQueryText;
          let secondQueryText;
          if(specialDiff) {
            firstQueryText = this.condition2Text(firstCondition, differAttr[0]);
            secondQueryText = this.condition2Text(secondCondition);
          }
          else {
            firstQueryText = this.condition2Text(firstCondition);
            secondQueryText = this.condition2Text(secondCondition, differAttr[0]);
          }
          console.log(maskData);
          let svg = d3.select('#DataDistribution');
          // draw the blue and red line
          this.OtherRecordNum = minSensitivityDataIndices.length;
          this.DifferentialRecordNum = 1;
          for(let d of this.LineData) {
            d['show'] = false;
          }
          let blueLineData = minSensitivityDataIndices.map((index) => this.LineData[index]);
          // sampling
          if(blueLineData.length > 500) {
            // random sampling
            let N = blueLineData.length;
            let sampleNum = 500;//9999 //Math.floor(N * 0.1)
            let posArray = [];
            for(let i = 0;i<N;i++) {
              posArray.push(i);
            }
            for(let i = 0;i<sampleNum;i++) {
              let newPos = Math.floor(Math.random() * N);
              [posArray[i], posArray[newPos]] = [posArray[newPos], posArray[i]]
            }
            let choseArray = [];//JSON.parse(JSON.stringify(this.riskRecord));
            for(let i = 0;i<sampleNum;i++) {
              choseArray.push(posArray[i]);
            }
            let temp = [];
            for(let i = 0;i<sampleNum;i++) {
              temp.push(blueLineData[choseArray[i]]);
            }
            blueLineData = temp;
          }
          this.LineData[this.curDifferIndex]['show'] = true;
          d3.selectAll('.blueLineContainer > *').remove();

          // record table
          let temp = [this.TableData[this.curDifferIndex]];
          let dataNum = Math.min(minSensitivityDataIndices.length, 1000);
          for(let i = 0;i<dataNum;i++) {
            let index = minSensitivityDataIndices[i];
            if(index !== this.curDifferIndex) {
              temp.push(this.TableData[index]);
            }
          }
          this.DifferentialRecordTableData = temp;
          // temp.push(...minSensitivityDataIndices.map(d => this.TableData[d]));

          svg.select('.blueLineContainer')
              .selectAll('.blueLineG')
              .data(blueLineData)
              .enter()
              .append('g')
              .attr('class', 'blueLineG')
              .append("path")
              .attr('class', 'blueLinePath')
              .attr("d", d => d.pathD)
              .attr("stroke", this.colorMap["blue-normal"])
              .attr('stroke-opacity', 0.7)
              .attr("stroke-width", 1)
              .attr("fill", "none");

          let resCloneLinePath = d3.selectAll('.riskLinePath')
              .attr('stroke-opacity', d => d.show ? 1 : 0);






          d3.select("#FirstQueryText").html(firstQueryText)
          d3.select("#SecondQueryText").html(secondQueryText)
          // Draws a yellow box for the data distribution

          let maskG = svg.select('.maskG');
          let height = parseFloat(d3.select('#DataDistribution').style('height').split('px')[0]);
          let padding = 20;
          maskG.selectAll('.finalMaskG').remove();
          maskG.selectAll('.MaskNodeG').remove();
          maskG.selectAll('.finalMaskG').remove();
          let MaskNodeG = maskG.selectAll('.MaskNodeG').data(maskData)
               .join('g')
               .attr('class', 'MaskNodeG')
               .attr('transform', d => `translate(${this.scale_Xscale(d.attrIndex)}, ${0})`)
          let offset = 0;
          let rectWidth = 6;
          MaskNodeG
              .selectAll('.MaskNode')
              .data(d => d.scope)
              .join('rect')
              .attr("class", 'MaskNode')
              .attr("x", 0)
              .attr("y", (d, k, node) => {
                let attr = node[0].parentNode.__data__.attr;
                if(typeof d[0] !== 'string') {
                  return this.scaleMap[attr](d[1]) + offset
                }
                else {
                  return this.scaleMap[attr](d[1]);
                }
              })
              .attr('width', `${rectWidth}px`)
              .attr("height", (d, k, node) => {
                let attr = node[0].parentNode.__data__.attr;
                if(typeof d[0] !== 'string') {
                  return this.scaleMap[attr](d[0]) - this.scaleMap[attr](d[1]) - offset;
                }
                else {
                  return this.scaleMap[attr].bandwidth() + this.scaleMap[attr](d[0]) - this.scaleMap[attr](d[1]);
                }
              })
              .attr('fill', this.colorMap["selected"])
              .style('stroke', 'none');


          svg.select('.tickLine').selectAll('.TickLineG').remove();
          svg.select('.tickLine').selectAll('.finalTickLineG').remove();
          let TickLineG = svg.select('.tickLine')
              .selectAll('.TickLineG')
              .data(maskData)
              .join('g')
              .attr('class', 'TickLineG')
              .attr('transform', d => `translate(${this.scale_Xscale(d.attrIndex)}, ${0})`)
          // rect upper boundary line
          TickLineG.selectAll('.upEdgeLine')
              .data(d => d.scope)
              .join('line')
              .attr("class", 'upEdgeLine')
              .attr('stroke-width', '2px')
              .attr('x1', 0)
              .attr('x2', rectWidth)
              .attr('y1', (d, k, node) => {
                let attr = node[0].parentNode.__data__.attr;
                if(typeof d[0] !== 'string') {
                  return this.scaleMap[attr](d[1]) + offset
                }
                else {
                  return this.scaleMap[attr](d[1]);
                }
              })
              .attr('y2', (d, k, node) => {
                let attr = node[0].parentNode.__data__.attr;
                if(typeof d[0] !== 'string') {
                  return this.scaleMap[attr](d[1]) + offset
                }
                else {
                  return this.scaleMap[attr](d[1]);
                }
              })
              .style('stroke', this.colorMap["deep-grey"]);
          // rect middle line
          TickLineG.selectAll('.middleEdgeLine')
              .data(d => d.scope)
              .join('line')
              .attr("class", 'middleEdgeLine')
              .attr('stroke-width', '2px')
              .attr('x1', 0)
              .attr('x2', 0)
              .attr('y1', (d, k, node) => {
                let attr = node[0].parentNode.__data__.attr;
                if(typeof d[0] !== 'string') {
                  return this.scaleMap[attr](d[1]) + offset
                }
                else {
                  return this.scaleMap[attr](d[1]);
                }
              })
              .attr('y2', (d, k, node) => {
                let attr = node[0].parentNode.__data__.attr;
                if(typeof d[0] !== 'string') {
                  return this.scaleMap[attr](d[0])
                }
                else {
                  return this.scaleMap[attr].bandwidth() + this.scaleMap[attr](d[0])
                }
              })
              .style('stroke', this.colorMap["deep-grey"]);

          // rect lower boundary
          TickLineG.selectAll('.downEdgeLine')
              .data(d => d.scope)
              .join('line')
              .attr("class", 'downEdgeLine')
              .attr('stroke-width', '2px')
              .attr('x1', 0)
              .attr('x2', rectWidth)
              .attr('y1', (d, k, node) => {
                let attr = node[0].parentNode.__data__.attr;
                if(typeof d[0] !== 'string') {
                  return this.scaleMap[attr](d[0])
                }
                else {
                  return this.scaleMap[attr].bandwidth() + this.scaleMap[attr](d[0])
                }
              })
              .attr('y2', (d, k, node) => {
                let attr = node[0].parentNode.__data__.attr;
                if(typeof d[0] !== 'string') {
                  return this.scaleMap[attr](d[0])
                }
                else {
                  return this.scaleMap[attr].bandwidth() + this.scaleMap[attr](d[0])
                }
              })
              .style('stroke', this.colorMap["deep-grey"]);

          // differential marker
          let finalData = differAttr.map(attr => this.TableData[this.curDifferIndex][attr]);
          svg.selectAll('.finalMaskCircle').remove();
          maskG.selectAll('.finalMaskCircle')
              .data(finalData)
              .join('circle')
              .attr('class', 'finalMaskCircle')
              .attr('cx', (d, i) => this.scale_Xscale(differAttrIndex[i]))
              .attr('cy', (d, i) => this.attrList[differAttrIndex[i]].Type === 'numerical' ? this.scaleMap[differAttr[i]](d) : this.scaleMap[differAttr[i]](d) + this.scaleMap[differAttr[i]].bandwidth() / 2)
              .attr('fill', this.colorMap['risk-opacity'])
              .attr('r', 5);
          this.initializeAttackSimulationViews(this.curQueryNodeD);
        })
      },
      convertCondition2Scope(condition, dcVal, ) {
        let conditionLen = condition.length;
         if(conditionLen === 1) {
           if(typeof condition[0] === 'string') {
             return [[condition[0], condition[0]]];
           }
           else {
             return condition
           }
         }
         else {
           // categorical attr
           if(typeof dcVal === 'string') {
             let curIndex = 0;
             let scope = [];
             if(dcVal < condition[0]) {
               scope = [[condition[0], condition[conditionLen-1]]]
             }
             else {
               while(curIndex < conditionLen && dcVal > condition[curIndex]) {
                 curIndex += 1;
               }
               if(curIndex === conditionLen) {
                 scope = [[condition[0], condition[conditionLen-1]]]
               }
               else {
                 scope = [[condition[0], condition[curIndex-1]], [condition[curIndex], condition[conditionLen-1]]]
               }
             }
             return scope
           }
           // numerical attr
           else {
             let curIndex = 0;
             let scope = [];
             if(dcVal < condition[0][0]) {
               scope = [[condition[0][0], condition[conditionLen-1][1]]]
             }
             else {
               while(curIndex < condition.length && dcVal > condition[curIndex][0]) {
                 curIndex += 1;
               }
               if(curIndex === conditionLen) {
                 scope = [[condition[0][0]], condition[conditionLen-1][1]]
               }
               else {
                 scope = [[condition[0][0], condition[curIndex-1][1]], [condition[curIndex][0], condition[conditionLen-1][1]]]
               }
             }
             return scope
           }
         }

      },
      condition2Text(condition, differAttr = '') {
        let text = 'WHERE ';
        let textList = [];
        for(let attr in condition) {
          let spanClass = differAttr === attr ? 'redFont' : 'blueFont';
          let attrType = this.attrList.filter(d => d.Name === attr)[0].Type;
          let attrText;
          let scope = condition[attr];
          if(attrType === 'numerical') {
            if (scope.length === 2) {
              attrText = `<span class="${spanClass}">(${attr} BETWEEN ${scope[0][0]} AND ${scope[0][1]} OR ${attr} BETWEEN ${scope[1][0]} AND ${scope[1][1]})</span>`;
            } else {
              if (scope.length === 1) {
                attrText = `<span class="${spanClass}">${attr} BETWEEN ${scope[0][0]} AND ${scope[0][1]}</span>`
              }
              else {
                let finalScope = [[scope[0][0], 0]];
                let startScope = scope[0]
                let curScopeIndex = 1;
                while (curScopeIndex < scope.length && startScope[1] === scope[curScopeIndex][0]) {
                  startScope = scope[curScopeIndex]
                  curScopeIndex += 1
                }
                finalScope[0][1] = startScope[1];
                if(curScopeIndex !== scope.length) {
                  startScope = scope[curScopeIndex];
                  curScopeIndex += 1;
                  finalScope.push([startScope[0], 0])
                  while (curScopeIndex < scope.length && startScope[1] === scope[curScopeIndex][0]) {
                    startScope = scope[curScopeIndex]
                    curScopeIndex += 1
                  }
                  finalScope[1][1] = startScope[1]
                  attrText = `<span class="${spanClass}">(${attr} BETWEEN ${finalScope[0][0]} AND ${finalScope[0][1]} OR ${attr} BETWEEN ${finalScope[1][0]} AND ${finalScope[1][1]})</span>`;
                }
                else {
                  attrText = `<span class="${spanClass}">${attr} BETWEEN ${finalScope[0][0]} AND ${finalScope[0][1]}</span>`
                }
              }
            }
          }
          else {
            if (scope.length > 1) {
              attrText = `<span class="${spanClass}">${attr} in (${scope.map(d => `'${d}'`).join(' ,')})</span>`;
            } else {
              attrText = `<span class="${spanClass}">${attr} = '${scope[0]}'</span>`
            }
          }
          textList.push(attrText);
        }
        text += textList.join('<br/>AND ')
        if(text === 'WHERE ') {
          text += '1 = 1'
        }
        return text;
      }
    },
    watch: {
      'isFreshSchemeHistory': {
        handler(newVal, oldVal) {
          this.freshSchemeHistory();
        },
        deep: true,
        immediate: false
      },
      'PrivacyDeviationVal': {
        handler(newVal, oldVal) {
          if(oldVal !== 0) {
            let svg = d3.select('#DA_OutputSVG')
            let x = this.DA_OutputXscale(this.privateVal - newVal);
            let width = this.DA_OutputXscale(this.privateVal + newVal) - this.DA_OutputXscale(this.privateVal - newVal)
            // svg.select('.clipG .bottomClipRect')
            //     .attr("x", x)
            //     .attr("width", width);

            svg.select('#clip-privacy rect')
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
          if(typeof this.GQueryXscale === 'object') {
            return;
          }
          let x = this.GQueryXscale(this.QueryAccurateVal - newVal);
          let width = this.GQueryXscale(this.QueryAccurateVal + newVal) - this.GQueryXscale(this.QueryAccurateVal - newVal)
          // svg.select('.bottomClipRect')
          //     .attr("x", x)
          //     .attr("width", width);

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
          if(this.availableSQL2) {
            if(Object.keys(this.curAttackTarget).length !== 0) {
              this.initializeAttackSimulationViews(this.curAttackTarget);
            }
          }
          else {
            this.cleanAttackSimulationView();
          }
        },
        deep: true,
        immediate: false
      },
      'isFreshHighRiskView': {
        handler(newVal, oldVal) {
          this.highRiskViewInit();
        },
        deep: true,
        immediate: false
      },
      'PrivacyDeviationPercent': {
        handler(newVal, oldVal) {
          this.SchemeHistoryAttrDeviationMap[this.QueryAttr] = newVal + '%';

        },
        deep: true,
        immediate: false
      },
      'AccuracyDeviationPercent': {
        handler(newVal, oldVal) {
          this.refreshAccuracyDeviationPercent();
        },
        deep: true,
        immediate: false
      },
      'AccuracySRTPercent': {
        handler(newVal, oldVal) {
          let svg = d3.select('#GeneralQuery');
          for(let e of this.curEpsilonArray) {
            let Accuracy = this.generalQueryFunc(this.AccuracyDeviationPercent / 100, e);

            svg.selectAll(`.DeviationThresholdPoint[epsilon='${e}']`)
                .attr('fill', (Accuracy >= this.AccuracySRTPercent / 100) ? this.colorMap["green"] : 'rgb(216,216,216)');
          }
        },
        deep: true,
        immediate: false
      },
      'isInitializeSchemeHistory': {
        handler(newVal, oldVal) {
          // acquirement sensitivity first
          // axios({
          //   url: 'http://127.0.0.1:8000/RiskTree/getSensitivity/',
          //   method: 'post',
          //   data: {
          //     'filename': this.curFile,
          //     'attrs': this.QueryAttrOption,
          //     'attrTypes': this.QueryAttrOptionType,
          //     'sensitivityWay': this.SensitivityCalculationWay
          //   }
          // }).then((response) => {
          //   this.SchemeHistoryColumnSensitivity = response.data.sensitivityMap;
            this.initializeSchemeHistory();

            // initialize minSensitivityMap
          //   this.minSensitivityMap = {}
          //   for(let attrParams of this.attrList) {
          //     let attr = attrParams.Name;
          //     let type = attrParams.Type;
          //     if(type !== 'numerical') continue
          //     axios({
          //       url: 'http://127.0.0.1:8000/RiskTree/minSensitivityMap/',
          //       method: 'post',
          //       data: {
          //         'filename': this.curFile,
          //         'attrList': this.attrList,
          //         'attrOption': this.attrList.map(d => d['Name']),
          //         'AttrsKeyMap': this.AttrsKeyMap,
          //         'BSTKeyMap': this.BSTKeyMap,
          //         'attr': attr,
          //       }
          //     }).then((response) => {
          //       this.minSensitivityMap[attr] = response.data.data;
          //     })
          //   }
          //
          // })

        },
        deep: true,
        immediate: false
      },
      'TopAttr': {
        handler(newVal, oldVal) {
          let rowLen = this.SchemeHistory.length;
          let temp = JSON.parse(JSON.stringify(this.SchemeHistory))
          if(rowLen !== 0) {
            let cnt = 0;
            let i = rowLen - 1;
            while(cnt <= rowLen) {
             if(this.SchemeHistory[i].Attribute === newVal) {
               this.SchemeHistory.unshift(this.SchemeHistory.splice(i , 1)[0]);
               i += 1;
             }
              cnt += 1;
              i -= 1;
            }

            for(let i=0;i<rowLen;i++) {
              let attr = this.SchemeHistory[i]['Attribute'];
              this.SchemeHistoryAttrPosMap[attr] = i;
              while(i+1 < rowLen && this.SchemeHistory[i+1]['Attribute'] === attr) {
                i += 1;
              }
              this.SchemeHistoryAttrNumMap[attr] = i - this.SchemeHistoryAttrPosMap[attr] + 1;
            }


          }
        },
        deep: true,
        immediate: false
      },
      'curAttrRiskStr': {
        handler(newVal, oldVal) {
          this.curAttrRisk = parseFloat(newVal.split('%')) / 100
          // d3.select('.attrRiskSlider')
          //   .attr('transform', `translate(${this.curAttrRisk * 70}, 0)`);
          let bitmap = this.curIndices.reduce((prev, d) => {
            return prev += 1 << d;
          }, 0);
          this.attrRiskMap[bitmap] = this.curAttrRisk;
          this.UpdateEpsilonWithPrivacy();

        },
        deep: true,
        immediate: false
      },
      'curAttrRisk': {
        handler(newVal, oldVal) {
          // Switch accuracy to the appropriate range
          let min =Math.round(this.curAttrRisk * 100 * 0.5) ;
          let max =Math.round(this.curAttrRisk * 100) ;
          // Adjust the countAttackSRT
          if(this.countAttackSRTPercent <= min || this.countAttackSRTPercent >= max) {
            // Delay adjustment
            setTimeout(() => {
              let temp = Math.round(min + (max - min) / 2);
              this.countAttackSRTPercent = temp - temp % 10;

            }, 1000)
          }
          // for sumAttackSRT
          if(this.sumAttackSRTPercent >= max) {
            // Delay adjustment
            setTimeout(() => {
              let temp = Math.round(max / 2);
              this.sumAttackSRTPercent = temp;

            }, 1000)
          }
        },
        deep: true,
        immediate: false
      },
      'attrRiskMap': {
        handler(newVal, oldVal) {
          // Modify the gray level of the circle
          let greyColorScale = d3.scaleLinear()
              .domain([0, 99])
              .range(this.greyGradient)
          // change the color of the gray inner circle
          d3.selectAll('.TreeNodePie .curNodeRiskPie_path path')
              .attr("fill",(d) => {
                let i = d.index;
                if(i === 1) {
                  let risk = 1;
                  let bitmap = d.key.reduce((prev, cur) => {
                    return prev += 1 << cur;
                  }, 0);
                  if(this.attrRiskMap[bitmap] !== undefined) {
                    risk = this.attrRiskMap[bitmap];
                  }
                  else {
                    for(let i of d.key) {
                      risk = Math.min(this.attrRiskMap[1 << i], risk)
                    }
                  }
                  return greyColorScale(Math.round(risk * 100))
                }
                return this.colorMap["risk"];
              })

          // update Scheme History
          if(Object.keys(this.minSensitivityMap).length !== 0) {
            this.refreshAvgRiskP();
          }

        },
        deep: true,
        immediate: false
      },
      'isFreshDeviationP1': {
        handler(newVal, oldVal) {
          this.GetPrivacyDeviationP();
        },
        deep: true,
        immediate: false
      },
      'isFreshDeviationP2': {
        handler(newVal, oldVal) {
          this.GetAccuracyDeviationP();
        },
        deep: true,
        immediate: false
      },
      'curVictimGroup': {
        handler(newVal, oldVal) {
          [this.attrGropeFilter, this.AttrFilterMap] = this.VictimNameMap[newVal];
        },
        deep: true,
        immediate: false
      }

    },
    created() {

    },
    mounted() {
      let ColorScale = d3.scaleLinear()
          .domain([0, 99])
          .range(this.greyGradient);


      for(let i = 0;i<=99;i++) {
        this.queryNumLegend.push(ColorScale(i));
        this.attrRiskLegend.push(ColorScale(i));
      }


    }
  }
</script>

<style scoped>
  /***************** 容器style ******************/
  #Container {
    width: 100%;
    height: 100vh;
    display: flex;
    flex-direction: row;
    background-color: #eff7fe;
    overflow: hidden;
  }
  .RowPartMain {
    width: calc(50% - 15px);
    height: calc(100vh - 20px);
    margin: 10px;
  }
  .RowPartMain:first-child {
    margin-right: 5px;
  }
  .RowPartMain:nth-child(2) {
    margin-left: 5px;
  }
  
  .BaseMain {
    font-size: 12px;
    background-color: #fff;
    position: relative;
  }
  
  #DifferentialRiskIdentification {
    width: 100%;
    height: calc(55% - 10px + 35px);
  }

  #DataExploration {
    width: 100%;
    height: calc(45% - 70px);
  }



  #DataExplorationLegend {
    position: absolute;
    top: 3px;
    left: 180px;
    width: 300px;
    height: 50px;
  }

  .switchTick {
    position: absolute;
    top: 7px;
    right: 203px;
    width: 200px;
    height: 10px;
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
    background-color: rgba(52, 152, 219,1.0) !important;
  }

  .legendLine {
    stroke-width: 2px;
  }
  /************************************************/

  /***************** 统一通用style ******************/
  .relativeDiv {
    position: relative;
  }

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
    line-height: 24px;
    padding: 2px 0 2px 10px;
    margin: 0 10px;
    border-radius: 10px;

    background-color: #efefef;

    position: relative;
    display: flex;
    align-items: center;
    flex-direction: row;
  }

  .halfPanel {
    width: calc(50% - 20px) !important;
    flex-direction: column;
    align-items: start;
  }

  .TextDivider {
    /*height: 70%;*/
    border-color: #333333;
    margin: 10px 10px;
  }

  .PanelTextDivider {
    height: 34px;
    border-color: #333333;
    margin: 0 10px;
  }

  .rightEdgeBtn {
    border-top-right-radius: inherit;
    border-bottom-right-radius: inherit;
    border-top-left-radius: 0;
    border-bottom-left-radius: 0;
    margin-right: 0;
    font-size: 12px;

    width: 100px;
    position: absolute;
    right: 0;
    top: 0;
    height: 100%;
  }

  .SQL {
    border-radius: 10px;
    background-color: #efefef;
    margin: 0 10px;
  }

  .SqlTitle {
    font-size: 14px;
    padding-left: 10px;
    text-align: center;
  }

  .SQLText {
    font-size: 10px;
    /*width: calc(75% - 30px);*/
    padding: 5px 0;
  }

  .paddingLeft5px {
    padding-left: 5px;
  }

  .paddingRight5px {
    padding-right: 5px;
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

  .marginBottomTop10px {
    margin-top: 10px;
    margin-bottom: 10px;
  }

  .percentageMasker {
    position: relative;
    top: 1px;
    right: 40px;
    z-index: 101;
  }


  .flexLayout {
    display: flex;
    align-items: center;
  }

  /***************** 树视图style ******************/
  .AttrFilterBtnGroup {
    margin-right: -15px;
  }
  .vgc {
    border: 3px solid #666;
    width: 160px;
    margin-left: 10px;
    position: relative;
    height: 40px;
  }
  .vgc .vgn {
    line-height: 40px;
    width: 100px;
    text-align: center;
  }
  .vgc .confirmVictimBtn {
    position: absolute;
    right: 0;
    width: 4px;
  }

  .vgcRadio {
    position: absolute;
    right: 10px;
    top: -2px;
  }
  .VictimGroups {
    width: 20%;
    height: 100%;
    position: relative;
  }
  .controlBar {
    width: 30%;
    height: 100%;
    position: relative;
    margin: 0 15px 0 -15px;
  }
  .attrRank {
    width: 22%;
    height: 100%;
    position: relative;
  }
  .highRisk {
    position: relative;
    width: calc(28% - 1px);
  }
  .addClickBtn {
    border: none;
  }
  .addCont {
    text-align: center;
  }
  #attrRankPlot, #highRiskPlot {
    height: calc(100% - 60px);
    width: 100%;
  }

  .leftHeader {
    text-align: left;
    position: relative;
    padding-left: 10px;
  }

  .leftHeader::after {
    content: '';
    width: 115%;
    height: 0px;
    position: absolute;
    border-bottom: 1px solid #999;
    top: 2px;
    left: -10px;
    transform: rotate(14deg);
  }
  .PanelDivider {
    margin-top: 20px;
    height: 90%;
  }

  .rightHeader {
    text-align: right;
    padding-right: 10px;
  }



  #AttributeSetTreeLegend {
    position: absolute;
    top: 15px;
    right: 0;
    width: 215px;
    height: 50px;
  }

  #DifferentialQueryTreeLegend {
    position: absolute;
    top: 14px;
    right: 7px;
    width: 190px;
    height: 30px;
  }

  #TreeView {
    display: flex;
    flex-direction: row;
    height: calc(100% - 120px);
  }






  #DataDistribution {
    width: 100%;
    height: calc(100% - 43px);
  }

  #DQTreeContainer {
    width: 100%;
    height: calc(100% - 37px - 40px - 30px - 120px - 40px);
    overflow-x: hidden;
    overflow-y: hidden;
    position: relative;
  }


  #DifferentialQueryTree {
    width: 100%;
  }
  #DQTreeAttrTitle {
    width: 100%;
    height: 30px;
    margin-top: -15px;
  }
  #CorrespondingSQLCommands {
    height: 170px;
  }

  #firstQuery {
    margin-bottom: 10px;
  }

  #firstQuery, #secondQuery {
    display: flex;
    flex-direction: column;
    align-items: center;
    position: relative;
    width: 50%;
  }

  .RelativeToDiv {
    position: absolute;
    left: 0px;
    top: 6px;
  }

  .SuccTextSvg {
    width: 200px;
    height: 40px;
  }

  .SuccTextSvg text{
    fill: #666;
  }

  .individualIcon {
    width: 20px;
    height: 20px;
    position: absolute;
  }

  .relativeTop5px {
    position: relative;
    top: -5px;
  }



  /**********************************************/
  .deviationIntervalPanel {
    /*padding: 7px 0 0 0;*/
  }
  /*.thresholdPanel {*/
  /*  padding: 0 0 7px 0;*/
  /*}*/


  .AS_view {
    /*flex: 1;*/
  }
  .QueryView {
    margin: 10px;
    margin-bottom: 4px;
    border: #dcdfe6 1px dashed;

    width: 255px;
    height: 255px;
    /*flex: 1;*/
  }
  .SimulationViews {
    margin: 10px 20px 0 20px;
    display: flex;
    flex-direction: row;
    width: 100%;
  }

  #FirstQuerySVG {
    border-right: none;
    margin-left: -10px;
  }

  #DA_OutputSVG {
    border-left: none;
    margin-left: -70px;
  }

  #GeneralQuery {
    width: calc(50% - 20px);
    margin-right: -20px;
  }

  #AccuracyHistoryChart {
    width: 130px;
    border-left: none;
  }

  .convertSQLBtn {
    position: absolute;
    right: 10px;
    top: -5px;
    height: 24px;
    width: 90px;
  }


/****************************************/
  #SchemeHistory {
    background-color: #fff;
    flex: 1;

    position: relative;
    left: 0;
    top: 10px;
    right: 0;
    height: calc(45% - 35px);
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
    margin-top: 6vh;
  }

  .DataInput {
    width: 72%;
    height: 75vh;
    margin: 0 auto;
    margin-top: 15px;
    padding: 20px;
    background-color: #fff;
    border: 3px solid #afafaf;
    border-radius: 20px;

  }


  /**************************************/
  #QT_Panel {
    margin-bottom: 1%;
  }
  .EpsilonInput {
    margin: 0 0 0 10px;
    width: 100px;
    border-radius: 7px;
    height: 24px;
  }
  .SCWO {
    margin-left: 10px;
    border-radius: 7px;
  }

  .SQL_panel {
    display: flex;
    flex-direction: row;
    /*justify-content: space-evenly;*/
    height: calc(15%);
  }

  .barChart {
    margin-top: 8px;
    width: 105px;
    height: 70px;
    margin-left: -5px;
    margin-bottom: 0;
  }

  .unLockBgc {
    position: absolute;
    top: 0;
    left: 0;
  }

  .lineChart {
    margin-top: 8px;
    width: 70px;
    height: 25px;
    margin-left: -2px;
    padding: 5px 0;
  }

  .lockRow {
    border: none;
    padding: 5px !important;
    margin-top: 3px;
    /*margin-left: -10px;*/
    width: 24px !important;
    height: 24px !important;
  }

  .closeRow {
    border: none;
    padding: 5px !important;
    margin-top: 3px;
    /*margin-left: -10px;*/
    width: 24px !important;
    height: 24px !important;
  }
  /*.closeRow:hover {*/
  /*  background-color: rgba(236, 204, 104,0.5);*/
  /*}*/

  .refreshBtn {
    width: 59px;
    margin-left: -5px;
    height: 24px;
  }

  .thresholdInput {
    width: 60px;
    margin-left: 75.5px;
  }

  .deviationInput, .percentDeviationInput{
    width: 60px;
  }


  .deviationTooltip {
    position: absolute;
    border: 3px solid #aaa;

  }

  .hidden {
    visibility: hidden;
  }

  .examplePng {
    width: 90px;
    position: absolute;
    top: 67px;
    right: 50px;
  }

  #SchemeHistoryLegend {
    position: absolute;
    right: 10px;
    top: 25px;

    width: 170px;
    height: 270px;
  }

  .SchemeHistoryLegendLine {
    stroke-width: 3px;
  }

  .oppositeDeviation {
    font-size: 12px;
    margin-left: 4px !important;
  }

  .SchemeHistoryTable {
    padding: 0 0 0 10px;
  }


/*  high risk view style*/
  .AttrFilters {
    display: flex;
    flex-direction: column;
    width: 100%;
  }
  .AttrFilter {
    /*flex: 1;*/
    text-align: center;
    margin: 0 0;
    width: 100%;

    display: flex;
    flex-direction: row;
    justify-content: space-around;
    align-items: center;
  }
  .AttrFilterContent {
    height: 20px;
    line-height: 20px;
  }

  .AttrFilterContent, .AttrL, .ScopeL {
    width: 25%;
    text-align: center;
  }
  .ScopeL {
    margin-left: 8px;
  }
  .AttrL {
    margin-left: 10px;
  }
  .cludeL {
    margin-right: 10px;
  }

  .AttrGropeFilter {
    width: 25%;
  }
  .controlLabel {
    width: 110%;
    display: flex;
    flex-direction: row;
    justify-content: space-around;
  }


  .selectFilter {
    background-color: #4c96d9;
  }



</style>

<style>
  svg text {
    font-size: 12px;
    /*fill: #666;*/
    font-family: "Helvetica Neue",Helvetica,"PingFang SC","Hiragino Sans GB","Microsoft YaHei","微软雅黑",Arial,sans-serif;
  }


  .hidden {
    visibility: hidden;
  }

  .attrRiskInput {
    font-size: 10px !important;
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

  .eventCircle {
    cursor: pointer;
  }

  .DimensionNodeG {
    cursor: pointer;
  }

  #DataExploration span{
    font-size: 12px !important;
    line-height: 14px;
  }

  .hoverPath {
    stroke: rgba(236, 204, 104,1.0);
  }
  .el-table__body .el-table__row.hover-row td{
    background-color: #fff;
  }
  .el-table__body .hover-cell {
    background-color: #fff;
  }

  .el-table tbody tr:hover>td {
    background-color:#fff !important;
  }


  /*.el-table__body .el-table__row.unlock-row td{*/
  /*  background-color: #fff !important;*/
  /*}*/


  .Panel .el-icon {
    font-size: 16px !important;
  }

  .convertSQLBtn .el-icon {
    font-size: 16px !important;
  }

  .percentDeviationInput .el-input__inner {
    margin-left: -10px;
  }
  .deviationInput .el-input__inner {
    margin-left: 0 !important;
  }

  .thresholdInput .el-input__inner {
    margin-left: -10px;
  }

  .attrRiskInput .el-input__wrapper {
    padding-left: 5px !important;
    padding-right: 5px !important;
  }

  .SCWO,#QT_Panel .el-input__wrapper {
    padding-top: 2px;
    padding-bottom: 2px;
  }

  .axis .tick text {
    fill: #333;
    /*stroke: #333;*/
    stroke-width: 0.2px;
  }

  /deep/.el-switch__label {
    font-size: 10px !important;
  }

  .el-switch.is-checked .el-switch__core {
    background-color: rgba(52, 152, 219,1.0);
  }

  .blueBtn {
    background-color: rgba(52, 152, 219,1.0) !important;
    border: rgba(52, 152, 219,1.0) !important;
  }

  .greyBtn {
    background-color: rgb(176,176,176) !important;
    border: rgb(176,176,176) !important;
  }


  .el-input-number.is-controls-right .el-input__wrapper {
    padding-right: 25px !important;
    padding-left: 0 !important;
  }

  #DQTreeContainer .el-scrollbar__view {
    position: relative;
  }

  .RecordTable tbody tr {
    pointer-events: none;
  }

  .TreeNodePie {
    cursor: pointer;
  }

  .hideHalfTickEven .tick:nth-child(odd) text {
    visibility: hidden;
  }
  .hideHalfTickEven .tick:nth-child(4n+4) text {
    visibility: hidden;
  }
  .hideHalfTickOdd .tick:nth-child(even) text {
    visibility: hidden;
  }
  .hideHalfTickOdd .tick:nth-child(4n+5) text {
    visibility: hidden;
  }

  .notAvailableIcon {
    position: absolute;
    left: 38px;
    /*width: 50%;*/
    height: 50%;
    font-size: 30px;
  }

  .el-radio__label {
    display: none;
  }

  .el-radio {
    margin-right: 35px;
  }
</style>