from trytond.model import Index, ModelView, ModelSQL, fields, Unique
from trytond.pool import PoolMeta
from trytond.transaction import Transaction
from trytond.pyson import Eval
from sql import Table


class Template(metaclass=PoolMeta):
    __name__ = 'product.template'

    company_fields = fields.One2Many('product.template.company_fields',
        'template', 'Company Fields')
    company_salable = fields.Function(fields.Boolean('Company Salable'),
        'get_company_salable', searcher='search_company_salable')


    @classmethod
    def get_query(cls, templates):

        template = Table('product_template')
        company_template = Table('product_template_company_fields')

        join = template.join(company_template, type_='LEFT')
        join.condition = ((template.id == company_template.template))

        select = join.select(join.left.id, company_template.salable,
                join.right.company)

        select.where = ((template.salable == True) &
            ((company_template.salable == True) |
             (company_template.salable == None)))

        if templates:
            select.where &= template.id.in_([p.id for p in templates])

        return select

    @classmethod
    def get_company_salable(cls, templates, name):
        company = Transaction().context.get('company')
        transaction = Transaction()
        connection = transaction.connection

        select = cls.get_query(templates)
        subselect = select.select(select.id, select.salable)
        subselect.where = ((select.company == company) |
            (select.company == None))

        product_company = []
        with connection.cursor() as cursor:
            cursor.execute(*subselect)
            for template, salable in cursor:
                product_company.append(template)

        salable = {}
        for template in templates:
            salable[template.id] = template.id in product_company or False

        return salable


    @classmethod
    def search_company_salable(cls, name, clause):
        company = Transaction().context.get('company')

        select = cls.get_query(None)
        subselect = select.select(select.id)
        subselect.where = ((select.company == company) |
            (select.company == None))

        return [('id', 'in', subselect)]


class Product(metaclass=PoolMeta):
    __name__ = 'product.product'

    company_salable = fields.Function(fields.Boolean('Company Salable'),
        'on_change_with_company_salable', searcher='search_company_salable')

    @fields.depends('template', '_parent_template.company_salable')
    def on_change_with_company_salable(self, name=None):
        return self.template and self.template.company_salable or False

    @classmethod
    def search_company_salable(cls, name, clause):
        return [('template.company_salable',) + tuple(clause[1:])]


class ProductCompanyFields(ModelSQL, ModelView):
    'Product Template Company Fields'
    __name__ = 'product.template.company_fields'
    template = fields.Many2One('product.template', 'Template',
            context={
                'company': Eval('company', -1),
            }, depends=['company'], ondelete='CASCADE', required=True)
    company = fields.Many2One('company.company', 'Company', ondelete='CASCADE',
        required=True)
    salable = fields.Boolean('Salable', states={
        'readonly': ~Eval('template_salable', False)
        }, depends=['template_salable'])
    template_salable = fields.Function(fields.Boolean('Template Salable'),
        'on_change_with_template_salable')

    @fields.depends('template', 'company', '_parent_template.salable')
    def on_change_with_template_salable(self, name=None):
        return self.template and self.template.salable or False

    @classmethod
    def __setup__(cls):
        super().__setup__()
        table = cls.__table__()
        cls._sql_constraints += [
            ('template_company_uniq', Unique(table, table.template,
                    table.company),
                'product_fields_company.msg_company_unique'),
        ]
        cls._sql_indexes.update({
                Index(table, (table.template, Index.Equality())),
                Index(table, (table.company, Index.Equality())),
                })


class ProductCompanyFieldsPurchase(metaclass=PoolMeta):
    __name__ = 'product.template.company_fields'

    purchasable = fields.Boolean('Purchasable', states={
        'readonly': ~Eval('template_purchasable', False)},
        depends=['template_purchasable'])
    template_purchasable = fields.Function(fields.Boolean(
        'Template Purchasable'),'on_change_with_template_purchasable')

    @fields.depends('template', 'company', '_parent_template.purchasable')
    def on_change_with_template_purchasable(self, name=None):
        return self.template and self.template.purchasable or False



class TemplatePurchase(metaclass=PoolMeta):
    __name__ = 'product.template'

    company_purchasable = fields.Function(fields.Boolean('Company Purchasable'),
        'get_company_purchasable', searcher='search_company_purchasable')

    @classmethod
    def get_purchase_query(cls, templates):
        template = Table('product_template')
        template_company = Table('product_template_company_fields')

        join = template.join(template_company, type_='LEFT')
        join.condition = ((template.id == template_company.template))

        select = join.select(template.id, template_company.purchasable,
                template_company.company)
        select.where = ((template.purchasable== True) &
            ((template_company.purchasable == True) |
             (template_company.purchasable == None)))

        if templates:
            select.where &= template.id.in_([p.id for p in templates])

        return select

    @classmethod
    def get_company_purchasable(cls, templates, name):
        company = Transaction().context.get('company')
        transaction = Transaction()
        connection = transaction.connection

        select = cls.get_purchase_query(templates)

        subselect = select.select(select.id, select.purchasable)
        subselect.where = ((select.company == company) |
            (select.company == None))

        product_company = []
        with connection.cursor() as cursor:
            cursor.execute(*subselect)
            for template, purchasable in cursor:
                product_company.append(template)

        purchasable = {}
        for template in templates:
            purchasable[template.id] = template.id in product_company or False

        return purchasable


    @classmethod
    def search_company_purchasable(cls, name, clause):
        company = Transaction().context.get('company')
        select = cls.get_purchase_query(None)
        subselect = select.select(select.id)
        subselect.where = ((select.company == company) |
            (select.company == None))

        return [('id', 'in', subselect)]


class ProductPurchase(metaclass=PoolMeta):
    __name__ = 'product.product'

    company_purchasable = fields.Function(fields.Boolean('Company Purchasable'),
        'get_company_purchasable',
        searcher='search_product_company_purchasable')


    @fields.depends('template', '_parent_template.company_purchasable')
    def get_company_purchasable(self, name=None):
        return self.template and self.template.company_purchasable or False

    @classmethod
    def search_product_company_purchasable(cls, name, clause):
        return [('template.company_purchasable',) + tuple(clause[1:])]


