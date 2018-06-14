
from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


__version__ = '1.0'


class AttributesAppConfig(AppConfig):

    name = 'attributes'
    verbose_name = _('Attributes')


default_app_config = 'attributes.AttributesAppConfig'
