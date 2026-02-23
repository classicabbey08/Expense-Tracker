from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Custom user model with role field.
    This replaces the default User so we can add role early.
    """
    ROLE_CHOICES = (
        ('parent', 'Parent'),
        ('child', 'Child'),
    )

    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='child',
        help_text=_("Parent or Child role - cannot be changed after creation.")
    )

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def __str__(self):
        return f"{self.username} ({self.role})"

    def clean(self):
        # Prevent changing role after creation
        if self.pk:
            original = User.objects.get(pk=self.pk)
            if original.role != self.role:
                raise ValidationError(_("Role cannot be changed after creation."))

    # Fix reverse accessor clashes with built-in auth.User
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_groups',
        blank=True,
        help_text=_('The groups this user belongs to.'),
        verbose_name=_('groups'),
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_permissions',
        blank=True,
        help_text=_('Specific permissions for this user.'),
        verbose_name=_('user permissions'),
    )


class Profile(models.Model):
    """
    One-to-one profile extension for parent-child relationship.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    parent = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='children',
        limit_choices_to={'role': 'parent'},
        verbose_name=_("Parent (if child)"),
        help_text=_("Only parents can be assigned here.")
    )

    class Meta:
        verbose_name = _("profile")
        verbose_name_plural = _("profiles")

    def __str__(self):
        if self.user.role == 'child' and self.parent:
            return f"{self.user.username} (child of {self.parent.username})"
        return f"{self.user.username} ({self.user.role})"

    def clean(self):
        if self.user.role == 'parent' and self.parent:
            raise ValidationError(_("Parents cannot have a parent assigned."))
        # Uncomment if you want to force parents to assign children
        # if self.user.role == 'child' and not self.parent:
        #     raise ValidationError(_("Children must have a parent assigned."))


class Wallet(models.Model):
    """
    Wallet / balance for children only.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'child'},
        related_name='wallet'
    )
    balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        help_text=_("Current pocket money balance")
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("wallet")
        verbose_name_plural = _("wallets")

    def __str__(self):
        return f"{self.user.username}'s wallet - ₦{self.balance:,.2f}"

    def can_spend(self, amount):
        """Check if user can afford an expense"""
        return self.balance >= amount

    def add_funds(self, amount, description="Top-up by parent"):
        """Helper method - usually called from view/form"""
        if amount <= 0:
            raise ValueError("Amount must be positive.")
        self.balance += amount
        self.save()
        # Later: create Transaction record here

    def spend(self, amount, description):
        """Helper method for expenses"""
        if amount <= 0:
            raise ValueError("Amount must be positive.")
        if not self.can_spend(amount):
            raise ValidationError(_("Insufficient balance."))
        self.balance -= amount
        self.save()
        # Later: create Transaction record here


class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('income', _('Income (Top-up)')),
        ('expense', _('Expense')),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    description = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = _("transaction")
        verbose_name_plural = _("transactions")

    def __str__(self):
        sign = '+' if self.transaction_type == 'income' else '-'
        return f"{sign}₦{self.amount:,.2f} - {self.description} ({self.created_at.date()})"

    def clean(self):
        if self.amount <= 0:
            raise ValidationError(_("Amount must be greater than zero."))