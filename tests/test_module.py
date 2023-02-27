# This file is part product_fields_company module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.

from trytond.modules.company.tests import CompanyTestMixin
from trytond.tests.test_tryton import ModuleTestCase


class ProductFieldsCompanyTestCase(CompanyTestMixin, ModuleTestCase):
    'Test Product Fields Company module'
    module = 'product_fields_company'
    extras = ['purchase']


del ModuleTestCase