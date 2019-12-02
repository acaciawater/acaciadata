from django.core.validators import RegexValidator
from django.utils.translation import ugettext_lazy as _
        
ChamberOfCommerceValidator = RegexValidator(regex=r'\d{8}',message=_('Illegal chamber of commerce number'))

