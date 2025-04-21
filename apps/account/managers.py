from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import UserManager, Group, models


class AccountQuerySet(models.query.QuerySet):

    def active(self):
        return self.filter(is_active=True)

    def not_active(self):
        return self.filter(is_active=False)


class CustomUserManager(UserManager):
    
    def create_user(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_active', True)
        user = super(CustomUserManager, self).create_user(username, email, password, **extra_fields)
        guest_group, _ = Group.objects.get_or_create(name='Guest')
        user.groups = guest_group
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        group, _ = Group.objects.get_or_create(name='Superusers')
        extra_fields.setdefault('groups', group)
        extra_fields.setdefault('is_active', True)
        super(CustomUserManager, self).create_superuser(username, email, password, **extra_fields)

    def get_query_set(self):
        return AccountQuerySet(self.model, using=self._db)

    def active(self):
        return self.get_query_set().active()

    def not_active(self):
        return self.get_query_set().not_active()
