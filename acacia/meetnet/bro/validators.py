from django.core.validators import RegexValidator
        
ChamberOfCommerceValidator = RegexValidator(regex=r'\d{8}',message=_('Illegal chamber of commerce number'))

