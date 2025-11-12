from rest_framework import serializers
from .models import BarcodeSummary

class BarcodeSummarySerializer(serializers.ModelSerializer):
    """条码汇总数据序列化器"""
    
    class Meta:
        model = BarcodeSummary
        fields = '__all__'
        read_only_fields = ['barcode', 'model', 'location', 'scanner', 'scan_time', 'created_at', 'updated_at']