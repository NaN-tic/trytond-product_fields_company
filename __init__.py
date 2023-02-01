# This file is part product_fields_company module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.pool import Pool
from .product import (Template, ProductCompanyFields, Product, ProductPurchase,
    ProductCompanyFieldsPurchase, TemplatePurchase)
from .sale import SaleLine
from .purchase import PurchaseLine

def register():
    Pool.register(
        ProductCompanyFields,
        Template,
        Product,
        SaleLine,
        module='product_fields_company', type_='model')
    Pool.register(
        TemplatePurchase,
        ProductCompanyFieldsPurchase,
        ProductPurchase,
        PurchaseLine,
        depends = ['purchase'],
        module='product_fields_company', type_='model')
