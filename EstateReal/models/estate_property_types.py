from odoo import fields, models, api, _

class EstateProperty(models.Model):
    _name = 'estate.property.type'
    _description = 'Estate property types'
    _order = "name"

    # -------------------------------------- Fields -------------------------------------
    name = fields.Char(string="Name")
    number = fields.Integer(string="Number")
    sequence = fields.Integer(string="Sequence", default=1)
    offer_count = fields.Integer(string="Count", compute="_compute_offer_count")

    # -------------------------------------- Relational One2many -------------------------------------
    property_ids = fields.One2many('real.estate', 'property_id')
    offer_ids = fields.One2many('estate.property.offer', 'property_id', string="Offers")


    def action_view_offers(self):
        return {
            'name': _('Property Offers'),
            'type': 'ir.actions.act_window',
            'res_model': 'estate.property.offer',
            'view_mode': 'tree,form',
            'domain': [('property_id', '=', self.id)],
            'target': 'current',
        }

    def _compute_offer_count(self):
        for record in self:
            record.offer_count = len(record.offer_ids)
