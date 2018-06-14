# MP-Shop | Attributes

## Installation

### Install using PIP:
```
pip install django-mp-shop-attrs
```

### Add attributes to settings.py:
```
INSTALLED_APPS = [
    ...
    'attributes',
]
```

### Add attributes to product admin:
```
from attributes.admin import ProductAdminMixin
from attributes.forms import ProductFormMixin

class ProductForm(ProductFormMixin, forms.ModelForm):
    ...

class ProductAdmin(ProductAdminMixin, ModelAdmin):

    form = ProductForm
    ...

```

## Usage

```
product = Product.objects.get(...)

for attr_val in product.attr_values.visible():
    
    print(attr_val.attr.name)
    print(attr_val.value)
    
    attr_val.value = 'example'
    attr_val.save()
```

## Custom product models

```
from django.apps import AppConfig

from attributes import AttributesAppConfig


class CustomAttributesAppConfig(AttributesAppConfig):

    product_model = 'custom_app.CustomProductModel'
    product_category_model = 'custom_app.CustomProductCategoryModel'
```

settings.py
```
INSTALLED_APPS = [
    ...
    'CustomAttributesAppConfig',
]
```

### App requires this packages:
* django
* awesome-slugify

### App compatible with:
* django-modeltranslation
* django-mptt
* django-suit

### Screenshots
Attributes list
![Attrs list](https://user-images.githubusercontent.com/4138122/41437785-1867b074-702e-11e8-940f-504cae19ca22.png)

Attribute change
![Attr change](https://user-images.githubusercontent.com/4138122/41437857-444bd580-702e-11e8-9340-72c301582695.png)
