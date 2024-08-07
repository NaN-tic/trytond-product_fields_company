import unittest
from decimal import Decimal

from proteus import Model
from trytond.modules.account.tests.tools import (create_chart,
                                                 create_fiscalyear, create_tax,
                                                 get_accounts)
from trytond.modules.account_invoice.tests.tools import \
    set_fiscalyear_invoice_sequences
from trytond.modules.company.tests.tools import create_company, get_company
from trytond.modules.currency.tests.tools import get_currency
from trytond.tests.test_tryton import drop_db
from trytond.tests.tools import activate_modules, set_user
from trytond.model.modelstorage import DomainValidationError


class Test(unittest.TestCase):

    def setUp(self):
        drop_db()
        super().setUp()

    def tearDown(self):
        drop_db()
        super().tearDown()

    def test(self):

        # Activate modules
        config = activate_modules('product_fields_company')

        # Create company
        _ = create_company()
        company = get_company()

        # Set employee
        User = Model.get('res.user')
        Party = Model.get('party.party')
        Employee = Model.get('company.employee')
        employee_party = Party(name="Employee")
        employee_party.save()
        employee = Employee(party=employee_party)
        employee.company = company
        employee.save()
        user = User(config.user)
        user.employees.append(employee)
        user.employee = employee
        user.company = company
        user.save()
        set_user(user.id)

        # Create fiscal year
        fiscalyear = set_fiscalyear_invoice_sequences(
            create_fiscalyear(company))
        fiscalyear.click('create_period')

        # Create chart of accounts
        _ = create_chart(company)
        accounts = get_accounts(company)
        revenue = accounts['revenue']
        expense = accounts['expense']
        cash = accounts['cash']
        Journal = Model.get('account.journal')
        PaymentMethod = Model.get('account.invoice.payment.method')
        cash_journal, = Journal.find([('type', '=', 'cash')])
        cash_journal.save()
        payment_method = PaymentMethod()
        payment_method.name = 'Cash'
        payment_method.journal = cash_journal
        payment_method.credit_account = cash
        payment_method.debit_account = cash
        payment_method.save()

        # Create tax
        tax = create_tax(Decimal('.10'))
        tax.save()

        # Create parties
        Party = Model.get('party.party')
        supplier = Party(name='Supplier')
        supplier.save()
        customer = Party(name='Customer')
        customer.save()

        # create_company2
        party2 = Party(name='Party2')
        party2.save()
        Company = Model.get('company.company')
        company2 = Company()
        company2.party = party2
        company2.currency = get_currency()
        company2.save()

        # Create account categories
        ProductCategory = Model.get('product.category')
        account_category = ProductCategory(name="Account Category")
        account_category.accounting = True
        account_category.account_expense = expense
        account_category.account_revenue = revenue
        account_category.save()
        account_category_tax, = account_category.duplicate()
        account_category_tax.customer_taxes.append(tax)
        account_category_tax.save()

        # Create product
        ProductUom = Model.get('product.uom')
        unit, = ProductUom.find([('name', '=', 'Unit')])
        ProductTemplate = Model.get('product.template')
        template = ProductTemplate()
        template.name = 'product-1'
        template.default_uom = unit
        template.type = 'goods'
        template.salable = True
        template.list_price = Decimal('10')
        template.account_category = account_category_tax
        tc = template.company_fields.new()
        tc.company = company
        tc.salable = True
        template.save()
        product_sc1, = template.products
        self.assertEqual(template.company_salable, True)

        template = ProductTemplate()
        template.name = 'product-2'
        template.default_uom = unit
        template.type = 'goods'
        template.salable = True
        template.list_price = Decimal('10')
        template.account_category = account_category_tax
        tc = template.company_fields.new()
        tc.company = company2
        tc.salable = True
        template.save()
        product_sc2, = template.products
        self.assertEqual(template.company_salable, False)

        template = ProductTemplate()
        template.name = 'product-3'
        template.default_uom = unit
        template.type = 'goods'
        template.salable = True
        template.list_price = Decimal('10')
        template.account_category = account_category_tax
        tc = template.company_fields.new()
        tc.company = company2
        tc.salable = True
        tc = template.company_fields.new()
        tc.company = company
        tc.salable = False
        template.save()
        product_sc2n1, = template.products
        self.assertEqual(template.company_salable, False)

        template = ProductTemplate()
        template.name = 'product-4'
        template.default_uom = unit
        template.type = 'goods'
        template.salable = True
        template.list_price = Decimal('10')
        template.account_category = account_category_tax
        tc = template.company_fields.new()
        tc.company = company2
        tc.salable = False
        tc = template.company_fields.new()
        tc.company = company
        tc.salable = True
        template.save()
        product_sc2n2, = template.products
        self.assertEqual(template.company_salable, True)

        template = ProductTemplate()
        template.name = 'product-5'
        template.default_uom = unit
        template.type = 'goods'
        template.salable = True
        template.list_price = Decimal('10')
        template.account_category = account_category_tax
        tc = template.company_fields.new()
        tc.company = company2
        tc.salable = True
        tc = template.company_fields.new()
        tc.company = company
        tc.salable = True
        template.save()
        product_all, = template.products
        self.assertEqual(template.company_salable, True)

        template = ProductTemplate()
        template.name = 'product-6'
        template.default_uom = unit
        template.type = 'goods'
        template.salable = True
        template.list_price = Decimal('10')
        template.account_category = account_category_tax
        template.save()
        product_none, = template.products
        self.assertEqual(template.company_salable, True)

        template = ProductTemplate()
        template.name = 'product-7'
        template.default_uom = unit
        template.type = 'goods'
        template.salable = False
        template.list_price = Decimal('10')
        template.account_category = account_category_tax
        tc = template.company_fields.new()
        tc.company = company2
        tc.salable = True
        tc = template.company_fields.new()
        tc.company = company
        tc.salable = True
        template.save()
        product_all_ns, = template.products
        self.assertEqual(template.company_salable, False)

        # Sale 1 products
        Sale = Model.get('sale.sale')
        SaleLine = Model.get('sale.line')
        sale = Sale()
        sale.party = customer
        sale.invoice_method = 'order'
        sale_line = SaleLine()
        sale.lines.append(sale_line)
        sale_line.product = product_sc1
        sale_line.quantity = 2.0
        self.assertEqual(sale_line.company_salable, True)

        sale.click('quote')
        sale = Sale()
        sale.party = customer
        sale.invoice_method = 'order'
        sale_line = SaleLine()
        sale.lines.append(sale_line)
        sale_line.product = product_sc2
        sale_line.quantity = 2.0
        self.assertEqual(sale_line.company_salable, False)

        with self.assertRaises(DomainValidationError):
            sale.click('quote')

        sale = Sale()
        sale.party = customer
        sale.invoice_method = 'order'
        sale_line = SaleLine()
        sale.lines.append(sale_line)
        sale_line.product = product_sc2n1
        sale_line.quantity = 2.0
        self.assertEqual(sale_line.company_salable, False)

        with self.assertRaises(DomainValidationError):
            sale.click('quote')

        sale = Sale()
        sale.party = customer
        sale.invoice_method = 'order'
        sale_line = SaleLine()
        sale.lines.append(sale_line)
        sale_line.product = product_sc2n2
        sale_line.quantity = 2.0
        self.assertEqual(sale_line.company_salable, True)

        sale.click('quote')
        sale = Sale()
        sale.party = customer
        sale.invoice_method = 'order'
        sale_line = SaleLine()
        sale.lines.append(sale_line)
        sale_line.product = product_all
        sale_line.quantity = 2.0
        self.assertEqual(sale_line.company_salable, True)

        sale.click('quote')
        sale = Sale()
        sale.party = customer
        sale.invoice_method = 'order'
        sale_line = SaleLine()
        sale.lines.append(sale_line)
        sale_line.product = product_none
        sale_line.quantity = 2.0
        self.assertEqual(sale_line.company_salable, True)

        sale.click('quote')
        sale = Sale()
        sale.party = customer
        sale.invoice_method = 'order'
        sale_line = SaleLine()
        sale.lines.append(sale_line)
        sale_line.product = product_all_ns
        sale_line.quantity = 2.0
        self.assertEqual(sale_line.company_salable, False)

        with self.assertRaises(DomainValidationError):
            sale.click('quote')
