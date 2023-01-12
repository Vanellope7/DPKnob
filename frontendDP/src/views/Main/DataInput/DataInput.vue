<template>
  <el-upload
      drag
      action="http://127.0.0.1:8000/RiskTree/FileReceive/"
      v-model:file-list="fileList"
      :limit="1"
      style="margin: 10px;height: calc(50% - 30px)"
      :show-file-list="false"
      :on-success="uploadSuccess"
  >
    <el-icon class="el-icon--upload"><upload-filled /></el-icon>
    <div class="el-upload__text">
      Drop file here or <em>click to upload</em>
    </div>
  </el-upload>

  <el-table
      v-fit-columns
      :data="attrList"
      ref="multipleTable"
      @selection-change="handleSelectionChange"
      @cell-mouse-enter="handleCellEnter"
      @cell-mouse-leave="handleCellLeave"
      style="width: 100%; height: calc(50% - 30px)">
    <el-table-column type="selection" width="30" v-if="attrListColumn.length !== 0" />
    <el-table-column
        v-for="attr in attrListColumn"
        :prop="attr"
        :label="attr"
        align="center">
      <template #default="scope">
        <div class="item">
          <el-input class="item__input" v-model="scope.row[attr]" placeholder="请输入内容"></el-input>
          <div :class="{item__txt: true, 'item__txt--hover': this.editProp.includes(attr)}">{{scope.row[attr]}}</div>
        </div>
      </template>
    </el-table-column>
  </el-table>

  <div class="ConfirmBtn">
    <el-button
        @click="ConfirmAttr"
        type="primary">
      Confirm
    </el-button>
  </div>

</template>

<script>
  import {UploadFilled} from "@element-plus/icons-vue/";
  import axios from "axios";

  export default {
    name: "DataInput",
    components: {
      UploadFilled
    },
    data() {
      return {
        fileList: [],
        attrList: [],
        multipleSelection: [],

        // 需要编辑的属性
        editProp: ['Search Min Edge', 'Search Max Edge', 'DAable Window Width', 'Exposure Probability'],
        // 保存进入编辑的cell
        clickCellMap: {}
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
    methods: {
      uploadSuccess(response, file, fileList) {
        this.attrList = response.data;
        this.$nextTick(() => {
          this.toggleSelection(this.attrList);
        })
      },
      handleSelectionChange(val) {
        this.multipleSelection = val;
      },
      toggleSelection(rows) { // 选中当前页的数据
        if (rows) {
          rows.forEach(row => {
            this.$refs.multipleTable.toggleRowSelection(row);
          });
        } else {
          this.$refs.multipleTable.clearSelection();
        }
      },
      ConfirmAttr() {
        Promise.all([
            new Promise(resolve => {
              axios({
                url: 'http://127.0.0.1:8000/RiskTree/RiskTreeData/',
                method: 'post',
                data: {
                  'filename': this.curFile,
                  'attrList': this.multipleSelection,
                  'indices': []
                }
              }).then((response) => {
                resolve(response)

              })
            }),
            new Promise(resolve => {
              axios({
                url: 'http://127.0.0.1:8000/RiskTree/DataDistribution/',
                method: 'post',
                data: {
                  'filename': this.curFile,
                  'attrList': this.attrList,
                }
              }).then(response => {
                resolve(response)
              })
            })
        ]).then(result => {
          this.$emit('inputData', [result[0].data, this.curFile, this.attrList])
          this.$emit('drawPCP', result[1])
        })
      },



      // 表格方法
      handleCellEnter (row, column, cell, event) {
        const property = column.property
        if (this.editProp.includes(property)) {
          cell.querySelector('.item__input').style.display = 'block'
          cell.querySelector('.item__txt').style.display = 'none'
        }
      },
      /** 鼠标移出cell */
      handleCellLeave (row, column, cell, event) {
        const property = column.property
        if (this.editProp.includes(property)) {
          cell.querySelector('.item__input').style.display = 'none'
          cell.querySelector('.item__txt').style.display = 'block'
        }
      }
    },
    mounted() {

    }
  }
</script>

<style scoped>
  .ConfirmBtn {
    height: 60px;
    margin: 15px 0;
    text-align: center;
  }




  .item .item__input {
    display: none;
    width: 100px;
  }
  /* 调整elementUI中样式 如果不需要调整请忽略 */
  .item .item__input .el-input__inner{
    height: 24px!important;
  }
  /* 调整elementUI中样式 如果不需要调整请忽略 */
  .item .item__input .el-input__suffix i{
    font-size: 12px !important;
    line-height: 26px !important;
  }

  .item .item__txt{
    box-sizing: border-box;
    border: 1px solid transparent;
    width: 100px;
    line-height: 24px;
    padding: 0 8px;
    text-align: center;
  }
  .item .item__txt--hover{
    border: 1px solid #dddddd;
    border-radius: 4px;
    cursor: text;
  }


</style>