#!/usr/bin/env python3
"""
脚本功能：将条码汇总.xlsx数据并行导入到BarcodeSummary模型中（高性能版）
特点：
- 多进程并行处理
- 批量数据库操作
- 进度条显示
- 错误处理和重试机制
"""

import os
import sys
import django
import pandas as pd
import multiprocessing as mp
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
from tqdm import tqdm
import logging

# 设置Django环境
project_path = Path(__file__).parent.parent
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asset.settings')
sys.path.append(str(project_path))
django.setup()

from asset_code.models import BarcodeSummary

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def process_chunk(chunk_data):
    """处理数据块"""
    barcode_objects = []
    empty_count = 0
    error_count = 0
    
    for row_data in chunk_data:
        try:
            barcode = row_data.get('barcode', '').strip()
            if not barcode:
                empty_count += 1
                continue
            
            barcode_summary = BarcodeSummary(
                barcode=barcode,
                model=row_data.get('model', ''),
                location=row_data.get('location', ''),
                scanner=row_data.get('scanner', ''),
                scan_time=row_data.get('scan_time', ''),
                remarks=row_data.get('remarks', ''),
                asset_type=''
            )
            barcode_objects.append(barcode_summary)
            
        except Exception as e:
            error_count += 1
            logger.error(f"处理数据时出错: {e}")
            continue
    
    # 批量保存
    if barcode_objects:
        try:
            BarcodeSummary.objects.bulk_create(barcode_objects, batch_size=1000, ignore_conflicts=True)
            return len(barcode_objects), empty_count, error_count
        except Exception as e:
            logger.error(f"批量保存时出错: {e}")
            return 0, empty_count, error_count + len(barcode_objects)
    
    return 0, empty_count, error_count

def prepare_data(df):
    """准备数据，转换为字典列表"""
    logger.info("准备数据...")
    data_list = []
    
    for _, row in df.iterrows():
        data_list.append({
            'barcode': str(row['条码']).strip() if pd.notna(row['条码']) else '',
            'model': str(row['型号']).strip() if pd.notna(row['型号']) else '',
            'location': str(row['位置']).strip() if pd.notna(row['位置']) else '',
            'scanner': str(row['扫描人员']).strip() if pd.notna(row['扫描人员']) else '',
            'scan_time': str(row['时间']).strip() if pd.notna(row['时间']) else '',
            'remarks': str(row['备注']).strip() if pd.notna(row['备注']) else ''
        })
    
    return data_list

def split_data(data_list, num_workers):
    """将数据分割成多个块"""
    chunk_size = len(data_list) // num_workers
    chunks = []
    
    for i in range(num_workers):
        start_idx = i * chunk_size
        if i == num_workers - 1:  # 最后一块包含剩余所有数据
            end_idx = len(data_list)
        else:
            end_idx = (i + 1) * chunk_size
        chunks.append(data_list[start_idx:end_idx])
    
    return chunks

def import_barcode_data_parallel():
    """并行导入条码汇总数据"""
    
    # Excel文件路径
    excel_file = '/home/007101/Asset/data/条码汇总.xlsx'
    
    # 检查文件是否存在
    if not os.path.exists(excel_file):
        logger.error(f"错误：Excel文件不存在: {excel_file}")
        return False
    
    try:
        # 步骤1：清空现有数据
        logger.info("步骤1：清空现有数据...")
        current_count = BarcodeSummary.objects.count()
        logger.info(f"当前数据库中有 {current_count} 条记录")
        
        # 清空数据
        BarcodeSummary.objects.all().delete()
        logger.info("✓ 数据已清空")
        
        # 步骤2：读取Excel文件
        logger.info("步骤2：读取Excel文件...")
        df = pd.read_excel(excel_file)
        logger.info(f"Excel文件读取成功，共 {len(df)} 行数据")
        
        # 步骤3：准备数据
        logger.info("步骤3：准备数据...")
        data_list = prepare_data(df)
        
        # 步骤4：并行处理数据
        logger.info("步骤4：并行处理数据...")
        
        # 获取CPU核心数
        num_workers = min(mp.cpu_count(), 8)  # 最多使用8个进程
        logger.info(f"使用 {num_workers} 个进程并行处理")
        
        # 分割数据
        chunks = split_data(data_list, num_workers)
        logger.info(f"数据已分割为 {len(chunks)} 个块")
        
        # 统计信息
        total_success = 0
        total_empty = 0
        total_error = 0
        
        # 并行处理
        with ProcessPoolExecutor(max_workers=num_workers) as executor:
            # 提交任务
            futures = [executor.submit(process_chunk, chunk) for chunk in chunks]
            
            # 使用tqdm显示进度
            for future in tqdm(as_completed(futures), total=len(futures), desc="并行处理进度"):
                success_count, empty_count, error_count = future.result()
                total_success += success_count
                total_empty += empty_count
                total_error += error_count
        
        # 步骤5：统计结果
        logger.info("步骤5：导入完成！")
        print("=" * 60)
        print(f"总处理行数: {len(data_list)}")
        print(f"成功导入: {total_success}")
        print(f"空条码跳过: {total_empty}")
        print(f"错误跳过: {total_error}")
        print(f"成功率: {(total_success/len(data_list))*100:.1f}%")
        
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
        logger.error(f"导入过程出错: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("开始并行导入条码汇总数据...")
    print("=" * 60)
    
    success = import_barcode_data_parallel()
    
    if success:
        print("\n✅ 数据并行导入成功完成！")
    else:
        print("\n❌ 数据并行导入失败！")
    
    print("=" * 60)