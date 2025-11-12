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
    def field_options(self, request):
        """获取字段选项（包含新增字段）"""
        fields = [
            {'field': 'barcode', 'label': '条码', 'type': 'string'},
            {'field': 'model', 'label': '型号', 'type': 'string'},
            {'field': 'location', 'label': '位置', 'type': 'string'},
            {'field': 'scanner', 'label': '扫描人员', 'type': 'string'},
            {'field': 'scan_time', 'label': '时间', 'type': 'string'},
            {'field': 'remarks', 'label': '备注', 'type': 'string'},
            {'field': 'user', 'label': '使用人', 'type': 'string'},
            {'field': 'asset_type', 'label': '资产类型', 'type': 'string'},
            {'field': 'result', 'label': '处理状态', 'type': 'boolean'},
        ]
        return Response(fields)
    
    @action(detail=False, methods=['get'])
    def import_template(self, request):
        """下载导入模板"""
        # 创建模板文件
        df = pd.DataFrame(columns=['条码', '型号', '位置', '扫描人员', '时间', '备注'])
        
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename="条码汇总导入模板_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx"'
        
        df.to_excel(response, index=False)
        return response
    
    @action(detail=False, methods=['post'])
    def bulk_import(self, request):
        """批量导入数据"""
        try:
            file = request.FILES.get('file')
            if not file:
                return Response({'error': '请上传文件'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 读取Excel文件
            df = pd.read_excel(file)
            
            # 检查必要的列
            required_columns = ['条码', '型号', '位置', '扫描人员', '时间']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                return Response({'error': f'缺少必要列: {", ".join(missing_columns)}'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 处理空值
            df = df.fillna('')
            
            success_count = 0
            error_count = 0
            errors = []
            
            for index, row in df.iterrows():
                try:
                    BarcodeSummary.objects.create(
                        barcode=str(row.get('条码', '')),
                        model=str(row.get('型号', '')),
                        location=str(row.get('位置', '')),
                        scanner=str(row.get('扫描人员', '')),
                        scan_time=str(row.get('时间', '')),
                        remarks=str(row.get('备注', ''))
                    )
                    success_count += 1
                except Exception as e:
                    error_count += 1
                    errors.append(f'第{index + 2}行: {str(e)}')
            
            return Response({
                'message': f'导入完成，成功{success_count}条，失败{error_count}条',
                'success_count': success_count,
                'error_count': error_count,
                'errors': errors[:10]  # 只返回前10个错误
            })
            
        except Exception as e:
            return Response({'error': f'导入失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['delete'])
    def bulk_delete(self, request):
        """批量删除数据"""
        try:
            ids = request.data.get('ids', [])
            if not ids:
                return Response({'error': '请选择要删除的记录'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 批量删除
            deleted_count, _ = BarcodeSummary.objects.filter(id__in=ids).delete()
            
            return Response({
                'message': f'成功删除 {deleted_count} 条记录',
                'deleted_count': deleted_count
            })
            
        except Exception as e:
            return Response({'error': f'批量删除失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
