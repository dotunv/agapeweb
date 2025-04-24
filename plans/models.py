from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings


class Plan(models.Model):
    name = models.CharField(_("Plan Name"), max_length=100)
    description = models.TextField(_("Description"))
    price = models.DecimalField(_("Price"), max_digits=10, decimal_places=2)
    duration_days = models.PositiveIntegerField(_("Duration in Days"))
    features = models.JSONField(_("Features"), default=list)
    is_active = models.BooleanField(_("Is Active"), default=True)
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)

    class Meta:
        verbose_name = _("Plan")
        verbose_name_plural = _("Plans")
        ordering = ["price"]

    def __str__(self):
        return f"{self.name} (${self.price})"


class Subscription(models.Model):
    class SubscriptionStatus(models.TextChoices):
        ACTIVE = "active", _("Active")
        CANCELLED = "cancelled", _("Cancelled")
        EXPIRED = "expired", _("Expired")
        PENDING = "pending", _("Pending")

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="subscriptions",
        verbose_name=_("User")
    )
    plan = models.ForeignKey(
        Plan,
        on_delete=models.PROTECT,
        related_name="subscriptions",
        verbose_name=_("Plan")
    )
    status = models.CharField(
        _("Status"),
        max_length=20,
        choices=SubscriptionStatus.choices,
        default=SubscriptionStatus.PENDING
    )
    start_date = models.DateTimeField(_("Start Date"))
    end_date = models.DateTimeField(_("End Date"))
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)

    class Meta:
        verbose_name = _("Subscription")
        verbose_name_plural = _("Subscriptions")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} - {self.plan.name} ({self.status})"
