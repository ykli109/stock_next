// 根据列类型返回适当的筛选控件HTML
function getFilterControlHtml(col) {
  // 判断列类型的函数
  function getColumnType(col) {
    const numericColumns = [
      "change_rate",
      "ups_downs",
      "speed_increase",
      "speed_increase_5",
      "speed_increase_60",
      "speed_increase_all",
    ];
    if (col.value === "date") return "date";
    if (numericColumns.includes(col.value)) return "number";
    return "text";
  }

  const type = getColumnType(col);

  switch (type) {
    case "date":
      return `
          <div class="form-group">
            <label for="filter_${col.value}">${col.caption}</label>
            <input type="text" class="form-control date-picker" id="filter_${col.value}" placeholder="选择日期">
          </div>
        `;

    case "number":
      return `
          <div class="form-group">
            <label for="filter_${col.value}">${col.caption}</label>
            <div class="input-group">
              <select class="form-control" id="filter_${col.value}_operator">
                <option value="">全部</option>
                <option value=">">大于</option>
                <option value="<">小于</option>
                <option value="=">等于</option>
                <option value=">=">大于等于</option>
                <option value="<=">小于等于</option>
                <option value="between">区间</option>
              </select>
            </div>
            <div class="input-group mt-2" id="filter_${col.value}_value_container">
              <input type="number" class="form-control" id="filter_${col.value}_value" placeholder="输入值">
              <input type="number" class="form-control d-none" id="filter_${col.value}_value2" placeholder="结束值">
            </div>
          </div>
        `;

    case "text":
      return `
          <div class="form-group">
            <label for="filter_${col.value}">${col.caption}</label>
            <div class="input-group">
              <select class="form-control" id="filter_${col.value}_operator">
                <option value="contains">包含</option>
                <option value="equals">等于</option>
                <option value="startsWith">开头是</option>
                <option value="endsWith">结尾是</option>
              </select>
            </div>
            <input type="text" class="form-control mt-2" id="filter_${col.value}" placeholder="输入${col.caption}">
          </div>
        `;
  }
}

// 动态生成筛选表单
function generateFilterFields() {
  const filterFieldsDiv = document.getElementById("filterFields");
  filterFieldsDiv.innerHTML = ""; // 清空现有内容
  console.log('debug 清空');

  // 创建搜索框
  const searchHtml = `
      <div class="form-group">
        <input type="text" class="form-control" id="quickSearch" placeholder="快速搜索...">
      </div>
      <hr>
    `;
  filterFieldsDiv.insertAdjacentHTML("beforeend", searchHtml);

  // 为每个列创建筛选控件
  colInfos.forEach((col) => {
    const filterHtml = getFilterControlHtml(col);
    filterFieldsDiv.insertAdjacentHTML("beforeend", filterHtml);
  });

  // 初始化所有日期选择器
  initFilterDatePickers();

  // 初始化数值型字段的区间选择
  initNumberRangeSelectors();
}

// 初始化模态中的日期选择器
function initFilterDatePickers() {
    $(".date-picker").datepicker({
        language: 'zh-CN',
        format: "yyyy-mm-dd",
        showOtherMonths: true,
        selectOtherMonths: false,
        autoclose: true,
        todayHighlight: true,
    });
}

// 初始化数值型字段的区间选择
function initNumberRangeSelectors() {
  document.querySelectorAll('select[id$="_operator"]').forEach((select) => {
    select.addEventListener("change", function () {
      const valueContainer = this.closest(".form-group").querySelector(
        '[id$="_value_container"]'
      );
      const value2Input = valueContainer.querySelector('[id$="_value2"]');

      if (this.value === "between") {
        value2Input.classList.remove("d-none");
      } else {
        value2Input.classList.add("d-none");
      }
    });
  });
}

// 修改应用筛选的逻辑
function applyFilters() {
  const filterModel = {};

  // 处理快速搜索
  const quickSearch = document.getElementById("quickSearch").value;
  console.log('quick_search', quickSearch);
  if (quickSearch) {
    colInfos.forEach((col) => {
      if (col.value !== "date") {
        // 排除日期列的快速搜索
        filterModel[col.value] = {
          type: "contains",
          filter: quickSearch,
        };
      }
    });
  }

  // 处理每个列的筛选条件
  colInfos.forEach((col) => {
    const operator = document.getElementById(`filter_${col.value}_operator`);
    const value = document.getElementById(`filter_${col.value}_value`);
    const value2 = document.getElementById(`filter_${col.value}_value2`);

    if (!value || !value.value) return;

    if (col.value === "date") {
      filterModel[col.value] = {
        type: "equals",
        filter: value.value,
      };
    } else if (operator) {
      switch (operator.value) {
        case "between":
          if (value.value && value2.value) {
            filterModel[col.value] = {
              type: "inRange",
              filter: Number(value.value),
              filterTo: Number(value2.value),
            };
          }
          break;
        case ">":
          filterModel[col.value] = {
            type: "greaterThan",
            filter: Number(value.value),
          };
          break;
        case "<":
          filterModel[col.value] = {
            type: "lessThan",
            filter: Number(value.value),
          };
          break;
        case ">=":
          filterModel[col.value] = {
            type: "greaterThanOrEqual",
            filter: Number(value.value),
          };
          break;
        case "<=":
          filterModel[col.value] = {
            type: "lessThanOrEqual",
            filter: Number(value.value),
          };
          break;
        case "contains":
        case "equals":
        case "startsWith":
        case "endsWith":
          filterModel[col.value] = {
            type: operator.value,
            filter: value.value,
          };
          break;
      }
    }
  });

  // 应用筛选
  if (gridApi) {
    gridApi.setFilterModel(filterModel);
    gridApi.onFilterChanged();
    updateStatusBar();
  }

  // 关闭模态
  $("#filterModal").modal("hide");
}

// 重置筛选时也清空表单
function resetFilters() {
  // 清空快速搜索
  document.getElementById("quickSearch").value = "";

  // 清空所有筛选字段
  colInfos.forEach((col) => {
    const operator = document.getElementById(`filter_${col.value}_operator`);
    const value = document.getElementById(`filter_${col.value}_value`);
    const value2 = document.getElementById(`filter_${col.value}_value2`);

    if (operator) operator.value = "";
    if (value) value.value = "";
    if (value2) value2.value = "";
  });

  // 重置 AG Grid 筛选
  if (gridApi && gridApi.api) {
    gridApi.setFilterModel(null);
    gridApi.onFilterChanged();
  }
}

// 防抖函数
function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}
