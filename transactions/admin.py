from django.contrib import admin
from .models import Transaction, Withdrawal

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'transaction_type', 'amount', 'status', 'transaction_id', 'created_at', 'completed_at')
    list_filter = ('transaction_type', 'status', 'created_at', 'completed_at')
    search_fields = ('user__username', 'transaction_id', 'description')
    ordering = ('-created_at',)
    raw_id_fields = ('user',)

@admin.register(Withdrawal)
class WithdrawalAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'withdrawal_fee', 'status', 'created_at', 'processed_at')
    list_filter = ('status', 'created_at', 'processed_at')
    search_fields = ('user__username',)
    ordering = ('-created_at',)
    raw_id_fields = ('user', 'transaction')
