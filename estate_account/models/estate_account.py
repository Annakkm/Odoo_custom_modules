from odoo import fields, models, api, exceptions

class EstateAccount(models.Model):
    _name = 'estate.account'

    name = fields.Char(string="Name", required=True)
