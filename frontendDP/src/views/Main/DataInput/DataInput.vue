<template>
  <el-upload
      drag
      action="http://127.0.0.1:8000/RiskTree/FileReceive/"
      v-model:file-list="fileList"
      :limit="1"
      style="margin: 10px"
      :show-file-list="false"
      :on-success="uploadSuccess"
  >
    <el-icon class="el-icon--upload"><upload-filled /></el-icon>
    <div class="el-upload__text">
      Drop file here or <em>click to upload</em>
    </div>
  </el-upload>

  <el-table
      :data="attrList"
      v-fit-columns
      ref="multipleTable"
      @selection-change="handleSelectionChange"
      style="width: 100%; height: 200px">
    <el-table-column type="selection" width="55" v-if="attrListColumn.length !== 0" />
    <el-table-column
        v-for="attr in attrListColumn"
        :prop="attr"
        :label="attr"
        align="center">
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
        multipleSelection: []
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
        axios({
          url: 'http://127.0.0.1:8000/RiskTree/RiskTreeData/',
          method: 'post',
          data: {
            'filename': this.curFile,
            'attrList': this.multipleSelection,
            'bitmap': 0
          }
        }).then((response) => {
          this.$emit('inputData', [response.data, this.curFile, this.attrList])
        })
      }
    },
    mounted() {

    }
  }
</script>

<style scoped>
  .ConfirmBtn {
    margin-top: 4vh;
    text-align: center;
  }
</style>