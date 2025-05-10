from odoo import fields, models, api, exceptions
# from odoo.exceptions import ValidationError


class ResUserInherited(models.Model):
    _inherit = 'res.users'

    property_ids = fields.One2many('real.estate', 'salesman_id', string="Properties", domain=lambda self: [('salesman_id', '=', self.id)])
    invoice_id = fields.Many2one('account.move', string="Invoice")
