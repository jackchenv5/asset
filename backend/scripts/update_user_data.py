#!/usr/bin/env python3
"""
脚本功能：遍历BarcodeSummary模型中的所有记录，
根据barcode字段查询对应的Excel文件中的"资产编号"，
将查询到的记录用"当前使用人"填充user字段，
并将asset_type字段设置为"工厂借用"
"""

from concurrent.futures._base import Future


from typing import Any


import os
import sys
import django
import pandas as pd
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
import time

# 设置Django环境
project_path = Path(__file__).parent.parent
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asset.settings')
sys.path.append(str(project_path))
django.setup()

from asset_code.models import BarcodeSummary

# 线程安全的计数器
updated_count = 0
not_found_count = 0
count_lock = Lock()

# 批量更新缓存
batch_updates = []
batch_lock = Lock()
BATCH_SIZE = 100  # 每批处理100条记录

def read_excel_data(file_path):
    """读取Excel文件数据"""
    try:
        df = pd.read_excel(file_path)
        # 检查必要的列是否存在
        if '资产编号' not in df.columns:
            print("错误：Excel文件中未找到'资产编号'列")
            return None
        
        if '当前使用人' not in df.columns:
            print("错误：Excel文件中未找到'当前使用人'列")
            return None
        
        # 创建字典映射：资产编号 -> 当前使用人
        mapping = {}
        for index, row in df.iterrows():
            asset_code = str(row['资产编号']).strip() if pd.notna(row['资产编号']) else ''
            current_user = str(row['当前使用人']).strip() if pd.notna(row['当前使用人']) else ''
            device_type = str(row['设备型号']).strip() if pd.notna(row['设备型号']) else ''
            
            if asset_code:  # 只保存非空的资产编号
                mapping[asset_code] = [current_user,device_type]
        
        print(f"从Excel文件读取了 {len(mapping)} 条有效数据")
        return mapping
        
    except Exception as e:
        print(f"读取Excel文件失败: {e}")
        return None

def process_single_record(record, excel_mapping):
    """处理单个记录"""
    global updated_count, not_found_count
    
    barcode = record.barcode
    
    if not barcode:
        with count_lock:
            not_found_count += 1
        return None
    
    # 在Excel映射中查找对应的用户
    barcode_str = str(barcode).strip()
    
    if barcode_str in excel_mapping:
        current_user = excel_mapping[barcode_str][0]
        device_type = excel_mapping[barcode_str][1]
        
        # 准备更新数据
        update_data = {
            'id': record.id,
            'user': current_user,
            'model': device_type,
            'asset_type': '工厂借用'
        }
        
        return update_data
    else:
        with count_lock:
            not_found_count += 1
        return None

def batch_update_records(updates):
    """批量更新记录"""
    global updated_count
    
    if not updates:
        return
    
    try:
        # 批量获取记录
        record_ids = [update['id'] for update in updates]
        records = BarcodeSummary.objects.filter(id__in=record_ids)
        
        # 批量更新
        for record in records:
            update_data = next((u for u in updates if u['id'] == record.id), None)
            if update_data:
                record.user = update_data['user']
                record.model = update_data['model']
                record.asset_type = update_data['asset_type']
        
        # 批量保存
        BarcodeSummary.objects.bulk_update(records, ['user', 'model', 'asset_type'])
        
        with count_lock:
            updated_count += len(updates)
        
    except Exception as e:
        print(f"批量更新失败: {e}")
        # 如果批量更新失败，回退到单个更新
        for update_data in updates:
            try:
                record = BarcodeSummary.objects.get(id=update_data['id'])
                record.user = update_data['user']
                record.model = update_data['model']
                record.asset_type = update_data['asset_type']
                record.save()
                
                with count_lock:
                    updated_count += 1
                    
            except Exception as single_e:
                print(f"单个更新失败 (ID: {update_data['id']}): {single_e}")

def update_user_fields():
    """更新BarcodeSummary表中的user字段"""
    # Excel文件路径
    excel_file = '/home/007101/Asset/data/资产数据(2025-11-11）.xlsx'
    
    # 检查文件是否存在
    if not os.path.exists(excel_file):
        print(f"错误：Excel文件不存在: {excel_file}")
        return
    
    # 读取Excel数据
    excel_mapping = read_excel_data(excel_file)
    if not excel_mapping:
        return
    
    # 获取所有BarcodeSummary记录
    all_records = BarcodeSummary.objects.all()
    total_records = all_records.count()

    print(f"开始处理 {total_records} 条记录...")
    
    # 重置计数器
    updated_count = 0
    not_found_count = 0
    
    # 开始计时
    start_time = time.time()
    
    # 使用线程池进行并行处理
    max_workers = min(8, os.cpu_count() or 4)  # 根据CPU核心数调整线程数
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 提交所有任务
        futures = []
        for record in all_records:
            future = executor.submit(process_single_record, record, excel_mapping)
            futures.append(future)
        
        # 处理完成的任务
        for future in as_completed(futures):
            try:
                update_data = future.result()
                
                if update_data:
                    # 添加到批量更新缓存
                    with batch_lock:
                        batch_updates.append(update_data)
                        
                        # 当缓存达到批量大小时，执行批量更新
                        if len(batch_updates) >= BATCH_SIZE:
                            batch_update_records(batch_updates[:])
                            batch_updates.clear()
                    
            except Exception as e:
                print(f"处理记录时出错: {e}")
    
    # 处理剩余的记录
    if batch_updates:
        batch_update_records(batch_updates)
    
    # 结束计时
    end_time = time.time()
    total_time = end_time - start_time
    
    # 统计结果
    print("\n" + "="*50)
    print("更新完成！")
    print(f"总记录数: {total_records}")
    print(f"已更新: {updated_count}")
    print(f"未找到匹配: {not_found_count}")
    print(f"处理时间: {total_time:.2f} 秒")
    print(f"平均处理速度: {total_records/total_time:.1f} 条/秒")

if __name__ == '__main__':
    try:
        update_user_fields()
    except Exception as e:
        print(f"脚本执行失败: {e}")
        import traceback
        traceback.print_exc()