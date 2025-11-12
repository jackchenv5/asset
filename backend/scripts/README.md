# 数据导入脚本说明

这个目录包含了用于管理BarcodeSummary数据的各种Python脚本。

## 脚本列表

### 1. add_new_data.py
- **功能**: 将新增数据导入到BarcodeSummary表中，不会覆盖现有数据
- **数据源**: `/home/007101/Asset/data/新增.xlsx`
- **特点**: 
  - 自动标准化列名
  - 跳过已存在的条码
  - 数据清理和验证

### 2. import_barcode_summary.py
- **功能**: 批量导入条码汇总数据，会先清空现有数据
- **数据源**: `/home/007101/Asset/data/条码汇总.xlsx`
- **特点**:
  - 批量处理，性能优化
  - 显示进度条
  - 错误处理和统计

### 3. import_barcode_summary_parallel.py
- **功能**: 并行导入条码汇总数据（高性能版）
- **数据源**: `/home/007101/Asset/data/条码汇总.xlsx`
- **特点**:
  - 多进程并行处理
  - 批量数据库操作
  - 更高的导入性能

### 4. update_user_data.py
- **功能**: 更新BarcodeSummary表中的user字段和asset_type字段
- **数据源**: `/home/007101/Asset/data/资产数据(2025-11-11）.xlsx`
- **特点**:
  - 根据barcode匹配资产编号
  - 并行处理
  - 批量更新操作

## 使用方法

所有脚本都已经配置好Django环境，可以直接运行：

```bash
cd /home/007101/Asset/backend/scripts
python add_new_data.py
python import_barcode_summary.py
python import_barcode_summary_parallel.py
python update_user_data.py
```

## 注意事项

1. 运行脚本前请确保：
   - Django项目已正确配置
   - 数据库连接正常
   - 所需的Excel文件存在且格式正确

2. import脚本会清空现有数据，请谨慎操作

3. 建议在运行前备份数据库