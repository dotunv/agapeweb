from django.contrib import admin
from .models import Plan, Subscription, Contribution, Queue, Wallet, Referral
from agape.admin import admin_site

@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'plan_type', 'contribution_amount', 'total_received', 'max_members', 
                   'deduction_repurchase', 'deduction_maintenance', 'withdrawable_amount', 'next_plan')
    search_fields = ('name', 'plan_type')
    ordering = ('contribution_amount',)
    raw_id_fields = ('next_plan',)

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

@admin.register(Queue)
class QueueAdmin(admin.ModelAdmin):
    list_display = ('plan', 'subscription', 'position', 'payments_received', 'created_at', 'updated_at')
    list_filter = ('plan', 'position', 'created_at')
    search_fields = ('subscription__user__username', 'plan__name')
    ordering = ('plan', 'position')
    raw_id_fields = ('plan', 'subscription')

    actions = ['shift_queue']

    def shift_queue(self, request, queryset):
        for queue in queryset:
            if queue.position == 1:
                try:
                    queue.shift_queue()
                    self.message_user(request, f"Queue shifted for {queue.plan.name}")
                except Exception as e:
                    self.message_user(request, f"Error shifting queue: {str(e)}", level='error')
            else:
                self.message_user(request, f"Only position #1 can be shifted", level='error')

    shift_queue.short_description = "Shift selected queue entries (position #1 only)"

@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('user', 'wallet_type', 'plan', 'balance', 'created_at', 'updated_at')
    list_filter = ('wallet_type', 'created_at')
    search_fields = ('user__username', 'user__email', 'plan__name')
    ordering = ('-updated_at',)
    raw_id_fields = ('user', 'plan')

    actions = ['deposit_funds']

    def deposit_funds(self, request, queryset):
        # This is a placeholder - in a real implementation, you would use a custom form
        for wallet in queryset:
            try:
                wallet.deposit(100, "Admin deposit")
                self.message_user(request, f"Deposited $100 to {wallet.user.username}'s {wallet.get_wallet_type_display()}")
            except Exception as e:
                self.message_user(request, f"Error depositing funds: {str(e)}", level='error')

    deposit_funds.short_description = "Deposit $100 to selected wallets"

@admin.register(Referral)
class ReferralAdmin(admin.ModelAdmin):
    list_display = ('referrer', 'referred_user', 'subscription', 'bonus_amount', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('referrer__username', 'referred_user__username')
    ordering = ('-created_at',)
    raw_id_fields = ('referrer', 'referred_user', 'subscription')

# Register with custom admin site
admin_site.register(Plan, PlanAdmin)
admin_site.register(Subscription, SubscriptionAdmin)
admin_site.register(Contribution, ContributionAdmin)
admin_site.register(Queue, QueueAdmin)
admin_site.register(Wallet, WalletAdmin)
admin_site.register(Referral, ReferralAdmin)
