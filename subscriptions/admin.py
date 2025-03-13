from django.contrib import admin
from .models import SubscriptionPlan, Subscription, Payment, QueuePosition
from agape.admin import admin_site

@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'amount', 'description')
    search_fields = ('name', 'description')
    ordering = ('amount',)

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'status', 'queue_position', 'created_at')
    list_filter = ('status', 'plan', 'created_at')
    search_fields = ('user__username', 'user__email')
    ordering = ('-created_at',)
    raw_id_fields = ('user', 'plan')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('subscription', 'amount', 'status', 'transaction_id', 'created_at', 'approved_at')
    list_filter = ('status', 'created_at', 'approved_at')
    search_fields = ('subscription__user__username', 'transaction_id')
    ordering = ('-created_at',)
    raw_id_fields = ('subscription',)

@admin.register(QueuePosition)
class QueuePositionAdmin(admin.ModelAdmin):
    list_display = ('subscription', 'position', 'payments_received', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('subscription__user__username',)
    ordering = ('position',)
    raw_id_fields = ('subscription',)

# Register with custom admin site
admin_site.register(SubscriptionPlan, SubscriptionPlanAdmin)
admin_site.register(Subscription, SubscriptionAdmin)
admin_site.register(Payment, PaymentAdmin)
admin_site.register(QueuePosition, QueuePositionAdmin)
