from trytond.model import fields
from trytond.pool import PoolMeta


class PurchaseLine(metaclass=PoolMeta):
    __name__ = 'purchase.line'

    company_purchasable = fields.Function(fields.Boolean('Company Purchasable'),
        'on_change_with_company_purchasable',
        searcher='search_company_purchasable')


    @classmethod
    def __setup__(cls):
        super().__setup__()
        cls.product.domain += [('company_purchasable', '=' , True)]
        cls.product.depends.add('company_purchasable')

    @fields.depends('product')
    def on_change_with_company_purchasable(self, name=None):
        return self.product and self.product.template.company_purchasable or False

    @classmethod
    def search_company_purchasable(cls, name, clause):
        return [('product.template.company_purchasable',) + tuple(clause[1:])]

