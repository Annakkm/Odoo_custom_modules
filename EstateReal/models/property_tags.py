from odoo import fields, models, api

class PropertyTags(models.Model):
    _name = 'estate.property.tags'
    _description = 'Property Tags'
    _order = "name"

    name = fields.Char(string="Name", required=True)
    color = fields.Integer(string="Color")

    _sql_constraints = [
        ('name_unique', 'UNIQUE(name)', 'Tag must be unique.'),
    ]
