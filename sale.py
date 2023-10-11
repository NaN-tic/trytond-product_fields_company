from trytond.model import fields
from trytond.pool import PoolMeta


class SaleLine(metaclass=PoolMeta):
    __name__ = 'sale.line'

    company_salable = fields.Function(fields.Boolean('Company Salable'),
        'on_change_with_company_salable', searcher='search_company_salable')


    @classmethod
    def __setup__(cls):
        super().__setup__()
        cls.product.domain += [('company_salable', '=' , True)]
        cls.product.depends.add('company_salable')

    @fields.depends('product')
    def on_change_with_company_salable(self, name=None):
        return self.product and self.product.template.company_salable or False

    @classmethod
    def search_company_salable(cls, name, clause):
        return [('product.template.company_salable',) + tuple(clause[1:])]

