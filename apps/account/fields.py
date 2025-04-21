from django.db import models
from django.db.models.fields import CharField, EmailField
from django.utils.translation import gettext_lazy as _
from django.forms import forms
from django.forms.fields import EmailField
from django.core.validators import EmailValidator, ValidationError


class CompanyEmailValidator(EmailValidator):

    message = _('Enter the Innowave email address')
    code = 'Invalid'
    _company = 'innowave.tech'

    def __call__(self, value):
        super().__call__(value)  # Perform basic email validation
        if '@' not in value:
            raise ValidationError(_('Enter a valid email address.'), code='invalid', params={'value': value})

        user_part, domain_part = value.rsplit('@', 1)

        if domain_part != self._company:
            raise ValidationError(_('Email domain must be "innowave.tech".'), code='invalid', params={'value': value})

        # If both user and domain checks pass, return True
        return True

    # def validate_domain_part(self, domain_part):
    #     company, domain = domain_part.rsplit('.', 1)
    #     if company == self._company and domain == self._domain:
    #         return True
    #     return super(CompanyEmailValidator, self).validate_domain_part(domain_part)


class CompanyEmail(CharField):

    default_validators = [CompanyEmailValidator]
    description = _("Innowave Email address")

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', 200)
        super(CompanyEmail, self).__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        return name, path, args, kwargs

    def formfield(self, **kwargs):
        return super(CompanyEmail, self).formfield(**{
            'form_class': forms.EmailField,
            **kwargs,
        })
