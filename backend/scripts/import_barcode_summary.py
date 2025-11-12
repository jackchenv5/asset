#!/usr/bin/env python3
"""
脚本功能：将条码汇总.xlsx数据导入到BarcodeSummary模型中（优化版）
步骤：
1. 清空现有数据
2. 读取Excel文件
3. 批量处理数据并导入到数据库
"""

import os
import sys
import django
import pandas as pd
from datetime import datetime
from pathlib import Path
from tqdm import tqdm

# 设置Django环境
project_path = Path(__file__).parent.parent
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asset.settings')
sys.path.append(str(project_path))
django.setup()

from asset_code.models import BarcodeSummary

def process_batch(batch_data):
    """批量处理数据"""
    barcode_objects = []
    
    for row_data in batch_data:
        try:
            barcode_summary = BarcodeSummary(
                barcode=row_data['barcode'],
                model=row_data['model'],
                location=row_data['location'],
                scanner=row_data['scanner'],
                scan_time=row_data['scan_time'],
                remarks=row_data['remarks'],
                asset_type=''  # 默认空字符串
            )
            barcode_objects.append(barcode_summary)
        except Exception as e:
            print(f"创建对象时出错: {e}")
            continue
    
    # 批量创建
    if barcode_objects:
        BarcodeSummary.objects.bulk_create(barcode_objects, batch_size=1000)
    
    return len(barcode_objects)

def import_barcode_data():
    """导入条码汇总数据（优化版）"""
    
    # Excel文件路径
    excel_file = '/home/007101/Asset/data/条码汇总.xlsx'
    
    # 检查文件是否存在
    if not os.path.exists(excel_file):
        print(f"错误：Excel文件不存在: {excel_file}")
        return False
    
    try:
        # 步骤1：清空现有数据
        print("步骤1：清空现有数据...")
        current_count = BarcodeSummary.objects.count()
        print(f"当前数据库中有 {current_count} 条记录")
        
        # 清空数据
        BarcodeSummary.objects.all().delete()
        print("✓ 数据已清空")
        
        # 步骤2：读取Excel文件
        print("\n步骤2：读取Excel文件...")
        df = pd.read_excel(excel_file)
        print(f"Excel文件读取成功，共 {len(df)} 行数据")
        
        # 步骤3：批量处理并导入数据
        print("\n步骤3：批量处理并导入数据...")
        
        # 统计信息
        total_rows = len(df)
        success_count = 0
        error_count = 0
        empty_barcode_count = 0
        
        # 准备批量数据
        batch_data = []
        batch_size = 1000  # 每批处理1000条
        
        # 使用tqdm显示进度条
        for index, row in tqdm(df.iterrows(), total=total_rows, desc="处理进度"):
            try:
                # 获取数据
                barcode = str(row['条码']).strip() if pd.notna(row['条码']) else ''
                model = str(row['型号']).strip() if pd.notna(row['型号']) else ''
                location = str(row['位置']).strip() if pd.notna(row['位置']) else ''
                scan_person = str(row['扫描人员']).strip() if pd.notna(row['扫描人员']) else ''
                time_str = str(row['时间']).strip() if pd.notna(row['时间']) else ''
                remark = str(row['备注']).strip() if pd.notna(row['备注']) else ''
                
                # 跳过空条码的记录
                if not barcode:
                    empty_barcode_count += 1
                    continue
                
                # 处理时间字段 - 保持原始字符串格式
                scan_time = time_str if time_str else ''
                
                # 添加到批量数据
                batch_data.append({
                    'barcode': barcode,
                    'model': model,
                    'location': location,
                    'scanner': scan_person,
                    'scan_time': scan_time,
                    'remarks': remark
                })
                
                # 当批次达到指定大小时，处理该批次
                if len(batch_data) >= batch_size:
                    processed_count = process_batch(batch_data)
                    success_count += processed_count
                    batch_data = []  # 清空批次数据
                
            except Exception as e:
                error_count += 1
                if error_count <= 5:  # 只显示前5个错误
                    print(f"处理第 {index + 1} 行时出错: {e}")
                continue
        
        # 处理剩余的批次数据
        if batch_data:
            processed_count = process_batch(batch_data)
            success_count += processed_count
        
        # 步骤4：统计结果
        print(f"\n步骤4：导入完成！")
        print("=" * 50)
        print(f"总处理行数: {total_rows}")
        print(f"成功导入: {success_count}")
        print(f"空条码跳过: {empty_barcode_count}")
        print(f"错误跳过: {error_count}")
        print(f"成功率: {(success_count/total_rows)*100:.1f}%")
        
        # 验证导入结果
        final_count = BarcodeSummary.objects.count()
        print(f"\n数据库验证:")
        print(f"当前数据库中有 {final_count} 条记录")
        
        # 显示一些统计信息
        print(f"\n数据统计:")
        print(f"有型号的记录: {BarcodeSummary.objects.exclude(model='').count()}")
        print(f"有位置的记录: {BarcodeSummary.objects.exclude(location='').count()}")
        print(f"有扫描人员的记录: {BarcodeSummary.objects.exclude(scanner='').count()}")
        
        # 显示一些示例数据
        print(f"\n示例数据（前5条）:")
        samples = BarcodeSummary.objects.all()[:5]
        for i, record in enumerate(samples, 1):
            print(f"{i}. barcode: {record.barcode}, model: {record.model}, location: {record.location}")
        
        return True
        
    except Exception as e:
        print(f"导入过程出错: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("开始导入条码汇总数据...")
    print("=" * 60)
    
    success = import_barcode_data()
    
    if success:
        print("\n✅ 数据导入成功完成！")
    else:
        print("\n❌ 数据导入失败！")
    
    print("=" * 60)