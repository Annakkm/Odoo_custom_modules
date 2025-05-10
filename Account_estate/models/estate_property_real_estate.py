from odoo import fields, models, api, exceptions
from odoo import Command


class Real_Estate_Inherited(models.Model):
    _inherit = 'real.estate'

    def action_sold(self):
        res = super().action_sold()
        print("Sale action overridden")

        selling_price = self.selling_price * 0.06
        move_type = 'out_invoice'
        journal = self.env['account.journal'].search([('type', '=', 'sale')], limit=1)

        if not journal:
            raise ValueError("No sale journal found")

        for prop in self:
            invoice_list = {
                'partner_id': prop.buyer_id.id,
                'move_type': move_type,
                'journal_id': journal.id,
                'invoice_line_ids': [
                    (0, 0, {
                        'name': prop.name,
                        'quantity': 1.0,
                        'price_unit': prop.selling_price * 0.06,  # 6% of selling price
                    }),
                    (0, 0, {
                        'name': 'Administrative fees',
                        'quantity': 1.0,
                        'price_unit': 100.0,
                    }),
                ],
            }

        new_invoice = self.env['account.move'].create(invoice_list)

        return res



