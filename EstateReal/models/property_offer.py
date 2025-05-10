from odoo import fields, models, api, _, exceptions
from datetime import timedelta
from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_compare, float_is_zero
from datetime import datetime


class PropertyOffer(models.Model):
    _name = 'estate.property.offer'
    _description = 'Property Offer'
    _order = "price desc"

    name = fields.Char(string="Offers")
    price = fields.Float(string="Price")
    status = fields.Selection(string="Status", selection=[('accepted', 'Accepted'), ('refused', 'Refused')], copy=False)
    _price_rounding = 0.01

    # Relations
    property_type_id = fields.Many2one('estate.property.type', related='property_id.property_id', store=True)
    property_id = fields.Many2one('real.estate', string="Property", required=True, readonly=True,
                                  domain="[('state', 'not in', ('accepted', 'sold', 'canceled'))]")
    partner_id = fields.Many2one('res.partner', string="Partner", required=True)

    validity = fields.Integer(string="Validity", default=7)
    date_deadline = fields.Date(string="Deadline", compute="_compute_deadline", inverse="_inverse_date_deadline")
    create_date = fields.Date(string="Create Date", default=fields.Date.today())

    # ------------------------------------------ CRUD Methods -------------------------------------
    @api.model
    def create(self, vals):
        property_id = vals.get('property_id')

        existing_offers = self.search([('property_id', '=', property_id)])
        if existing_offers and vals.get('price') < min(existing_offers.mapped('price')):
            raise ValidationError("The offer amount is lower than existing offers.")

        property_obj = self.env['real.estate'].browse(property_id)
        property_obj.write({'state': 'offer received'})

        module_install = self.date_set_year()
        vals['create_date'] = module_install

        return super(PropertyOffer, self).create(vals)

    def action_accept(self):
        for offer in self:
            if offer.status == 'accepted':
                raise exceptions.UserError("This offer has already been accepted.")
            else:
                offer.status = 'accepted'
                offer.property_id.selling_price = offer.price
                offer.property_id.buyer_id = offer.partner_id

    def action_refuse(self):
        self.status = 'refused'

    def date_set_year(self):
        return datetime.now()

    @api.depends('create_date', 'validity')
    def _compute_deadline(self):
        for offer in self:
            if offer.create_date and offer.validity:
                offer.date_deadline = offer.create_date + timedelta(days=offer.validity)

    def _inverse_date_deadline(self):
        for offer in self:
            if offer.date_deadline and offer.create_date:
                offer.validity = (offer.date_deadline - offer.create_date).days
