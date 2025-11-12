from django.db import models
from django.utils import timezone

class BarcodeSummary(models.Model):
    """条码汇总数据模型"""
    
    # 条码基本信息
    barcode = models.CharField('条码', max_length=100, blank=True, null=True)
    model = models.CharField('型号', max_length=200, blank=True, null=True)
    location = models.CharField('位置', max_length=500, blank=True, null=True)
    scanner = models.CharField('扫描人员', max_length=100, blank=True, null=True)
    scan_time = models.CharField('时间', max_length=100, blank=True, null=True)  # 字符串类型，保持原格式
    remarks = models.TextField('备注', blank=True, null=True)
    
    # 系统字段
    created_at = models.DateTimeField('创建时间', default=timezone.now)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    #扩展字段
    # 用于自动填充
    user = models.CharField('使用人', max_length=100, blank=True, null=True)
    asset_type = models.CharField('资产类型', max_length=100, blank=True, null=True,default='')
    
    # 用于用户编辑
    result = models.BooleanField('处理状态', default=False) # True 表示处理完成，False 表示处理中
    expected_time = models.DateTimeField('预计处理时间', blank=True, null=True)
    result_remarks = models.CharField('处理结果备注', max_length=100, blank=True, null=True)
    
    class Meta:
        verbose_name = '条码汇总'
        verbose_name_plural = '条码汇总'
        db_table = 'asset_code_barcode_summary'
    
    def __str__(self):
        return f"{self.barcode} - {self.model}"
