from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db import models
from .models import BarcodeSummary
from .serializers import BarcodeSummarySerializer
import pandas as pd
from django.http import HttpResponse
from datetime import datetime

class BarcodeSummaryViewSet(viewsets.ModelViewSet):
    """条码汇总数据视图集"""
    queryset = BarcodeSummary.objects.all()
    serializer_class = BarcodeSummarySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    # 支持所有字段的搜索（新增user、asset_type、result字段）
    search_fields = ['barcode', 'model', 'location', 'scanner', 'scan_time', 'remarks', 'user', 'asset_type']
    
    # 支持所有字段的过滤（新增user、asset_type、result字段）
    filterset_fields = ['barcode', 'model', 'location', 'scanner', 'scan_time', 'remarks', 'user', 'asset_type', 'result']
    
    # 支持所有字段的排序（新增user、asset_type、result字段）
    ordering_fields = ['barcode', 'model', 'location', 'scanner', 'scan_time', 'user', 'asset_type', 'result', 'created_at', 'updated_at']
    
    # 默认排序
    ordering = ['-created_at']
    
    @action(detail=False, methods=['get'])
    def export(self, request):
        """按当前搜索条件导出Excel"""
        try:
            # 获取查询参数（包含新增字段）
            search = request.query_params.get('search', '')
            barcode = request.query_params.get('barcode', '')
            model = request.query_params.get('model', '')
            location = request.query_params.get('location', '')
            scanner = request.query_params.get('scanner', '')
            scan_time = request.query_params.get('scan_time', '')
            remarks = request.query_params.get('remarks', '')
            user = request.query_params.get('user', '')
            asset_type = request.query_params.get('asset_type', '')
            result = request.query_params.get('result', '')
            
            # 构建查询集
            queryset = BarcodeSummary.objects.all()
            
            # 应用搜索条件（包含新增字段）
            if search:
                queryset = queryset.filter(
                    models.Q(barcode__icontains=search) |
                    models.Q(model__icontains=search) |
                    models.Q(location__icontains=search) |
                    models.Q(scanner__icontains=search) |
                    models.Q(scan_time__icontains=search) |
                    models.Q(remarks__icontains=search) |
                    models.Q(user__icontains=search) |
                    models.Q(asset_type__icontains=search)
                )
            
            # 应用筛选条件（包含新增字段）
            if barcode:
                queryset = queryset.filter(barcode__icontains=barcode)
            if model:
                queryset = queryset.filter(model__icontains=model)
            if location:
                queryset = queryset.filter(location__icontains=location)
            if scanner:
                queryset = queryset.filter(scanner__icontains=scanner)
            if scan_time:
                queryset = queryset.filter(scan_time__icontains=scan_time)
            if remarks:
                queryset = queryset.filter(remarks__icontains=remarks)
            if user:
                queryset = queryset.filter(user__icontains=user)
            if asset_type:
                queryset = queryset.filter(asset_type__icontains=asset_type)
            if result is not None and result != '':
                # 将字符串转换为布尔值
                if result.lower() in ('true', '1', 'yes', '是'):
                    result_bool = True
                elif result.lower() in ('false', '0', 'no', '否'):
                    result_bool = False
                else:
                    result_bool = bool(result)
                queryset = queryset.filter(result=result_bool)
            
            # 获取所有数据（不分页）
            data = list(queryset.values(
                'barcode', 'model', 'location', 'scanner', 
                'scan_time', 'remarks', 'user', 'asset_type', 
                'result', 'expected_time', 'result_remarks', 
                'created_at', 'updated_at'
            ))
            
            # 创建DataFrame
            df = pd.DataFrame(data)
            
            # 重命名列
            df.columns = ['条码', '型号', '位置', '扫描人员', '时间', '备注', 
                         '使用人', '资产类型', '处理状态', '预计处理时间', 
                         '处理结果备注', '创建时间', '更新时间']
            
            # 处理布尔值
            df['处理状态'] = df['处理状态'].map({True: '已完成', False: '处理中', None: '未处理'})
            
            # 处理空值
            df = df.fillna('')
            
            # 处理时间格式
            for col in ['预计处理时间', '创建时间', '更新时间']:
                df[col] = pd.to_datetime(df[col]).dt.strftime('%Y-%m-%d %H:%M:%S')
            
            # 创建响应
            response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = f'attachment; filename="条码汇总导出_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx"'
            
            # 写入Excel文件
            df.to_excel(response, index=False)
            
            return response
            
        except Exception as e:
            return Response({'error': f'导出失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
