from django.contrib import admin
from .models import Plan, Subscription, Contribution, Withdrawal
from agape.admin import admin_site

@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'plan_type', 'price', 'max_members', 'maintenance_fee', 'withdrawal_limit')
    search_fields = ('name', 'plan_type')
    ordering = ('price',)

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'status', 'queue_position', 'joined_at', 'total_received', 'available_for_withdrawal')
    list_filter = ('status', 'plan', 'joined_at')
    search_fields = ('user__username', 'user__email')
    ordering = ('-joined_at',)
    raw_id_fields = ('user', 'plan')

@admin.register(Contribution)
class ContributionAdmin(admin.ModelAdmin):
    list_display = ('from_subscription', 'to_subscription', 'amount', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('from_subscription__user__username', 'to_subscription__user__username')
    ordering = ('-created_at',)
    raw_id_fields = ('from_subscription', 'to_subscription')

@admin.register(Withdrawal)
class WithdrawalAdmin(admin.ModelAdmin):
    list_display = ('subscription', 'amount', 'status', 'requested_at', 'completed_at')
    list_filter = ('status', 'requested_at', 'completed_at')
    search_fields = ('subscription__user__username',)
    ordering = ('-requested_at',)
    raw_id_fields = ('subscription',)

# Register with custom admin site
admin_site.register(Plan, PlanAdmin)
admin_site.register(Subscription, SubscriptionAdmin)
admin_site.register(Contribution, ContributionAdmin)
admin_site.register(Withdrawal, WithdrawalAdmin)
