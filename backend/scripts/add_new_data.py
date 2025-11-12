#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
新增数据导入脚本
用于将新增.xlsx文件中的数据导入到BarcodeSummary表中，不会覆盖现有数据
"""

import os
import sys
import django
from datetime import datetime
import pandas as pd
from django.db import transaction

# 设置Django环境
project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_path)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asset.settings')
django.setup()

from asset_code.models import BarcodeSummary

def read_excel_file(file_path):
    """读取Excel文件"""
    try:
        df = pd.read_excel(file_path)
        print(f"成功读取Excel文件，共 {len(df)} 行数据")
        print(f"列名: {list(df.columns)}")
        return df
    except Exception as e:
        print(f"读取Excel文件失败: {e}")
        return None

def normalize_column_names(df):
    """标准化列名"""
    # 移除列名中的空格和特殊字符
    df.columns = df.columns.str.strip()
    
    # 定义列名映射关系
    column_mapping = {
        '条码': 'barcode',
        '条形码': 'barcode',
        'barcode': 'barcode',
        'BARCODE': 'barcode',
        
        '型号': 'model',
        'model': 'model',
        'MODEL': 'model',
        '产品型号': 'model',
        
        '位置': 'location',
        'location': 'location',
        'LOCATION': 'location',
        '存放位置': 'location',
        
        '扫描人员': 'scanner',
        'scanner': 'scanner',
        'SCANNER': 'scanner',
        '扫描人': 'scanner',
        '操作员': 'scanner',
        
        '时间': 'scan_time',
        '扫描时间': 'scan_time',
        'scan_time': 'scan_time',
        'SCAN_TIME': 'scan_time',
        '时间戳': 'scan_time',
        
        '备注': 'remarks',
        'remarks': 'remarks',
        'REMARKS': 'remarks',
        '说明': 'remarks',
        '注释': 'remarks'
    }
    
    # 重命名列
    df.rename(columns=column_mapping, inplace=True)
    return df

def validate_required_fields(df):
    """验证必需字段"""
    required_fields = ['barcode', 'model']
    missing_fields = []
    
    for field in required_fields:
        if field not in df.columns:
            missing_fields.append(field)
    
    if missing_fields:
        print(f"错误：缺少必需字段 {missing_fields}")
        return False
    
    # 检查空值
    empty_barcodes = df[df['barcode'].isna() | (df['barcode'] == '')]
    if len(empty_barcodes) > 0:
        print(f"警告：发现 {len(empty_barcodes)} 行条码为空，将被跳过")
    
    return True

def check_existing_barcodes(df):
    """检查已存在的条码"""
    barcodes = df['barcode'].dropna().astype(str).tolist()
    existing_barcodes = set(
        BarcodeSummary.objects.filter(barcode__in=barcodes)
        .values_list('barcode', flat=True)
    )
    
    if existing_barcodes:
        print(f"发现 {len(existing_barcodes)} 个已存在的条码，将被跳过")
        # 过滤掉已存在的条码
        df = df[~df['barcode'].isin(existing_barcodes)]
    
    return df, existing_barcodes

def clean_data(df):
    """清理数据"""
    # 移除空行
    df = df.dropna(subset=['barcode'])
    
    # 清理字符串字段
    string_fields = ['barcode', 'model', 'location', 'scanner', 'scan_time', 'remarks']
    for field in string_fields:
        if field in df.columns:
            df[field] = df[field].astype(str).str.strip()
            # 将空字符串替换为None
            df[field] = df[field].replace('', None)
    
    return df

def import_data(df):
    """导入数据到数据库"""
    success_count = 0
    error_count = 0
    errors = []
    
    # 获取可选字段
    available_fields = set(df.columns) & set([
        'barcode', 'model', 'location', 'scanner', 
        'scan_time', 'remarks', 'user', 'asset_type'
    ])
    
    with transaction.atomic():
        for index, row in df.iterrows():
            try:
                # 准备数据
                data = {}
                for field in available_fields:
                    if pd.notna(row[field]):
                        data[field] = str(row[field]).strip()
                
                # 创建记录
                BarcodeSummary.objects.create(**data)
                success_count += 1
                
                if success_count % 100 == 0:
                    print(f"已导入 {success_count} 条记录...")
                    
            except Exception as e:
                error_count += 1
                error_msg = f"第 {index + 2} 行导入失败: {str(e)}"
                errors.append(error_msg)
                print(error_msg)
    
    return success_count, error_count, errors

def main():
    """主函数"""
    print("=== 新增数据导入脚本 ===")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Excel文件路径
    excel_file = os.path.join(os.path.dirname(project_path), 'data', '新增.xlsx')
    
    if not os.path.exists(excel_file):
        print(f"错误：文件 {excel_file} 不存在")
        return
    
    print(f"正在读取文件: {excel_file}")
    
    # 读取Excel文件
    df = read_excel_file(excel_file)
    if df is None:
        return
    
    # 标准化列名
    df = normalize_column_names(df)
    print("列名标准化完成")
    
    # 验证必需字段
    if not validate_required_fields(df):
        return
    
    # 清理数据
    df = clean_data(df)
    print("数据清理完成")
    
    # 检查已存在的条码
    df, existing_barcodes = check_existing_barcodes(df)
    print(f"过滤后剩余 {len(df)} 条新记录")
    
    if len(df) == 0:
        print("没有新数据需要导入")
        return
    
    # 确认导入
    response = input(f"\n确认导入 {len(df)} 条新记录吗? (y/N): ")
    if response.lower() != 'y':
        print("导入已取消")
        return
    
    # 导入数据
    print("开始导入数据...")
    success_count, error_count, errors = import_data(df)
    
    # 输出结果
    print("\n=== 导入结果 ===")
    print(f"成功导入: {success_count} 条")
    print(f"导入失败: {error_count} 条")
    print(f"跳过的已存在条码: {len(existing_barcodes)} 条")
    
    if errors:
        print("\n错误详情:")
        for error in errors[:10]:  # 只显示前10个错误
            print(f"  - {error}")
        if len(errors) > 10:
            print(f"  ... 还有 {len(errors) - 10} 个错误")
    
    print(f"\n结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=== 导入完成 ===")

if __name__ == "__main__":
    main()