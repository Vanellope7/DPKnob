<template>
  <el-upload
      drag
      action="http://127.0.0.1:8000/RiskTree/FileReceive/"
      v-model:file-list="fileList"
      :limit="1"
      style="margin: 10px;height: calc(50% - 30px - 40px)"
      :on-success="uploadSuccess"
  >
    <el-icon class="el-icon--upload"><upload-filled /></el-icon>
    <div class="el-upload__text">
      Drop file here or <em>click to upload</em>
    </div>
  </el-upload>

  <el-table
      table-layout="fixed"
      :data="attrList"
      ref="multipleTable"
      @selection-change="handleSelectionChange"
      @cell-click="handleCellClick"
      @cell-mouse-enter="handleCellEnter"
      @cell-mouse-leave="handleCellLeave"
      style="width: 100%; height: calc(50% - 30px)">
<!--    <el-table-column type="selection" width="30" v-if="attrListColumn.length !== 0" />-->
    <el-table-column label="Sensitive"
                     align="center"
                     width="150" v-if="attrListColumn.length !== 0">
      <template #default="scope">
        <el-radio v-model="SensitiveAttr" :label="scope.row['Attribute']">&nbsp;</el-radio>
<!--        <el-checkbox v-model="scope.row['Sensitive']" size="large" />-->
      </template>
    </el-table-column>
    <el-table-column
        v-for="(attr, i) in attrListColumn"
        :prop="attr"
        :label="attr"

        align="center">
      <template #default="scope">
        <div class="item">
          <el-input class="item__input" v-model="scope.row[attr]"></el-input>
          <div :class="{item__txt: true, 'item__txt--hover': editProp.includes(attr)}">{{scope.row[attr]}}</div>
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
  import {ElNotification} from "element-plus";
  import { h } from 'vue'

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
        editProp: ['Query granularity'],
        // columnWidth: [140, 130, 200, 160, 190, 190],
        // 保存进入编辑的cell
        clickCellMap: {},
        lastCell: 0,
        lastEnterCell: 0,
        SensitiveAttr: ''
      }
    },
    computed: {
      curFile() {
        return this.fileList === [] ? '' : this.fileList[0].name;
      },
      attrListColumn() {
        return this.attrList.length === 0 ? [] : ['Attribute', 'Type', 'Range', 'Query granularity'];
      }
    },
    methods: {
      uploadSuccess(response, file, fileList) {
        if(response.data === 'wrong file type') {
          // ElNotification({
          //   title: 'Title',
          //   message: h('i', { style: 'color: teal' }, 'This is a reminder'),
          // })
          return;
        }
        this.attrList = response.data;
        this.SensitiveAttr = this.attrList[0]['Attribute']
        this.attrList[0]['Sensitive'] = true;
        // this.attrList.find(d => d['Name'] === 'charges')['Sensitive'] = true;
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
                  'indices': [],
                  'DescriptionNum': this.attrList.length
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
                  'attrList': this.multipleSelection,
                }
              }).then(response => {
                resolve(response)
              })
            })
        ]).then(result => {
          this.$emit('inputData', [result[0].data, this.curFile, this.multipleSelection, this.attrList.length])
          this.$emit('drawPCP', result[1])
        })
      },



      // 表格方法
      handleCellClick (row, column, cell, event) {
        const property = column.property
        if (this.editProp.includes(property)) {
          if(this.lastCell !== 0 && this.lastCell !== cell) {
            this.lastCell.querySelector('.item__input').style.display = 'none'
            this.lastCell.querySelector('.item__txt').style.display = 'block'
          }
          cell.querySelector('.item__input').style.display = 'block';
          cell.querySelector('.item__txt').style.display = 'none';
          this.lastCell = cell;
        }
      },
      handleCellEnter(row, column, cell, event) {
        const property = column.property
        if (this.editProp.includes(property)) {
          if(this.lastEnterCell !== 0 && this.lastEnterCell !== cell && this.lastEnterCell !== this.lastCell) {
            this.lastEnterCell.querySelector('.item__input').style.display = 'none'
            this.lastEnterCell.querySelector('.item__txt').style.display = 'block'
          }
          cell.querySelector('.item__input').style.display = 'block';
          cell.querySelector('.item__txt').style.display = 'none';
          this.lastEnterCell = cell;
        }
      },
      /** 鼠标移出cell */
      handleCellLeave (row, column, cell, event) {
        // const property = column.property
        // if (this.editProp.includes(property)) {
        //   cell.querySelector('.item__input').style.display = 'none'
        //   cell.querySelector('.item__txt').style.display = 'block'
        // }
      }
    },
    watch: {
      'SensitiveAttr': {
        handler(newVal, oldVal) {
          let idx = this.attrList.findIndex(d => d['Attribute'] === this.SensitiveAttr);
          for(let i in this.attrList) {
            let ii = parseInt(i);
            if(ii === idx) {
              this.attrList[ii]['Sensitive'] = true;
            }
            else {
              this.attrList[ii]['Sensitive'] = false;
            }
          }
        },
        deep: true,
        immediate: false
      },

    },
    mounted() {

    }
  }
</script>

<style scoped>
  .ConfirmBtn {
    height: 60px;
    margin-top: 35px;
    text-align: center;
  }




  .item .item__input {
    line-height: 25px;
    display: none;
    width: 100%;
    height: 100%;
  }

  /* 调整elementUI中样式 如果不需要调整请忽略 */
  .item .item__input .el-input__suffix i{
    font-size: 12px !important;
    line-height: 26px !important;
  }


</style>

<style>
  /* 调整elementUI中样式 如果不需要调整请忽略 */
  .item .item__input .el-input__inner{
    height: 23px!important;
    text-align: center;
    padding: 0 30px;
    font-size: 20px !important;
  }

  .item .item__txt{
    box-sizing: border-box;
    border: 1px solid transparent;
    line-height: 24px;
    padding: 0 8px;
    text-align: center;
  }
  .item .item__txt--hover{
    border: 1px solid #dddddd;
    border-radius: 4px;
    cursor: text;
  }

  .DescriptionNum {
    text-align: center;
    margin-bottom: 10px;
    vertical-align: center;
  }


  .DataInput .el-table .cell{
    font-size: 20px !important;
  }

  .el-upload-list__item-file-name {
    font-size: 20px;
  }

  .DataInput .el-table th .cell {
    padding-bottom: 5px;
  }

</style>