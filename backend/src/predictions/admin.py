from django.contrib import admin
from predictions.models import ExpensePrediction


@admin.register(ExpensePrediction)
class ExpensePredictionAdmin(admin.ModelAdmin):
    """Custom admin view for ExpensePrediction model."""

    list_display = ('period', 'category', 'value')
    list_filter = ('period__budget__name', 'period__budget__owner__email')
