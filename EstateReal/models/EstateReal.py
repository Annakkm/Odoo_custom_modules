from odoo import api, fields, models, exceptions
# from odoo.exceptions import ValidationError
import datetime
from odoo.tools.float_utils import float_compare, float_is_zero


class RealEstate(models.Model):
    _name = 'real.estate'
    _description = "Real Estate"
    _order = "id desc"

    # -------------------------------------- Fields -------------------------------------
    name = fields.Char(string="Title", required=True)
    description = fields.Text(string="Description", compute='_compute_description')
    postcode = fields.Char(string="Postcode")
    date_availability = fields.Date(string="Date Availability", default=fields.Date.today(), copy="False")
    expected_price = fields.Float(string="Expected Price", required=True, default="0.00")
    best_offer = fields.Float(string="Best Offer", compute="_compute_best_offer")
    selling_price = fields.Float(string="Selling Price", readonly=True, default="0.00", copy="False",compute='_compute_selling_price')
    bedrooms = fields.Integer(string="Bedrooms", default="2")
    living_area = fields.Integer(string="Living Area", default="0")
    facades = fields.Integer(string="Facades", default="0")
    garage = fields.Boolean(string="Garage")
    garden = fields.Boolean(string="Garden", default=False)
    total_area = fields.Float(string="Total Area", compute='_compute_total_area')
    garden_area = fields.Integer(string="Garden Area", default="0")
    active = fields.Boolean(string="Active", default="True")
    last_seen = fields.Datetime("Last Seen", default=fields.Datetime.now)

    # -------------------------------------- Selection fields -------------------------------------
    status = fields.Selection(string="Status", selection=[('accepted', 'Accepted'),
                                                          ('refused', 'Refused')])
    garden_orientation = fields.Selection(string="Garden Orientation",
                                          selection=[("north", "North"),
                                                     ("south", "South"),
                                                     ("east", "East"),
                                                     ("west", "West")])
    state = fields.Selection(string="State", required=True, default="new",
                             selection=[("new", "New"), ("offer received", "Offer Received"),
                                        ("offer accepted", "Offer Accepted"),
                                        ("sold", "Sold"),
                                        ("canceled", "Canceled")])

    # -------------------------------------- Relational Many2one -------------------------------------
    property_id = fields.Many2one('estate.property.type', string="Property Type", required=True)
    salesman_id = fields.Many2one('res.users', string="Salesman", required=True, default=lambda self: self.env.user)
    buyer_id = fields.Many2one('res.partner', string="Buyer", required=True, copy="False")
    partner_id = fields.Many2one("res.partner", related="offer_ids.partner_id")

    # -------------------------------------- Relational Many2many -------------------------------------
    tags_ids = fields.Many2many('estate.property.tags', string="Tags")

    # -------------------------------------- Relational One2many -------------------------------------
    offer_ids = fields.One2many('estate.property.offer', 'property_id', string="Offers")

    # -------------------------------------- SQL Constraints -------------------------------------
    _sql_constraints = [
        ('name_unique', 'UNIQUE(name)', 'Title must be unique.'),
        ('check_selling_price', 'CHECK(selling_price >= 0 )', 'Selling price must be positive.'),
        ('check_expected_price', 'CHECK(expected_price >= 0 )', 'Expected price must be strictly positive.'),
        ('check_best_offer', 'CHECK(best_offer >= 0 )', 'Offer must be strictly positive.')
    ]

    # ------------------------------------------ CRUD Methods -------------------------------------
    @api.model
    def create(self, vals):
        print("Hello", vals)
        return super(RealEstate, self).create(vals)

    def unlink(self):
        for record in self:
            if record.state not in ['new', 'canceled']:
                raise exceptions.UserError('You cannot delete property that is not in New or Canceled state.')
        return super(RealEstate, self).unlink()

    # --------------------------------------- Constrains Methods -------------------------------------
    # @api.constrains('selling_price', 'expected_price')
    # def _check_selling_price(self):
    #     for record in self:
    #         if not float_is_zero(record.expected_price, precision_rounding=record.offer_ids._price_rounding):
    #             if float_compare(record.selling_price, record.expected_price * 0.9,
    #                              precision_rounding=record.offer_ids._price_rounding) < 0:
    #                 raise exceptions.ValidationError(
    #                     'The selling price cannot be lower than 90% of the expected price.')

    # Return (float_compare)
    # -1: If the first value is less than the second value.
    # 0: If the  first value is equal to the second value.
    # 1: If the first value is greater than the second value.

    def date_set_year(self):
        return datetime.now()

    @api.constrains('date_availability')
    def check_date_availability(self):
        for record in self:
            if record.date_availability < fields.Date.today():
                raise exceptions.ValidationError("The end date cannot be set in the past")

    # -------------------------------------- Action Methods -------------------------------------
    def action_cancel(self):
        for rec in self:
            if rec.state == 'sold':
                raise exceptions.UserError("A sold property cannot be canceled.")
            rec.state = 'canceled'

    def action_sold(self):
        for rec in self:
            if rec.state == 'canceled':
                raise exceptions.UserError("A canceled property cannot be set as sold.")
            rec.state = 'sold'

    def action_done(self):
        self.state = 'sold'
        return True

    # ------------------------------------------ Onchange Methods -------------------------------------
    @api.onchange('garden')
    def onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = 'north'
        else:
            self.garden_area = 0
            self.garden_orientation = False

    # ------------------------------------------ Compute Methods -------------------------------------
    def _compute_total_area(self):
        self.total_area = self.living_area + self.garden_area

    # ------------------------------------------ Depends Methods -------------------------------------
    @api.depends('selling_price')
    def _compute_selling_price(self):
        for rec in self:
            accepted_offers = rec.offer_ids.filtered(lambda offer: offer.status == 'accepted')
            if accepted_offers:
                rec.selling_price = max(accepted_offers.mapped('price'))
            else:
                rec.selling_price = 0

    @api.depends('best_offer', "offer_ids")
    def _compute_best_offer(self):
        for record in self:
            offers_accepted = record.offer_ids.filtered(lambda offer: offer.status == "accepted")
            highest_price = 0
            for offer in offers_accepted:
                if offer.price > highest_price:
                    highest_price = offer.price
            record.best_offer = highest_price

    @api.depends('offer_ids')
    def _compute_description(self):
        for record in self:
            offers_accepted = record.offer_ids.filtered(lambda offer: offer.status == 'accepted')
            if offers_accepted:
                highest_price = max(offers_accepted, key=lambda offer: offer.price).price
                record.description = f"Highest price: {highest_price} $"
            else:
                record.description = "No partner selected"
                print("No partner selected")


def copy(self, default=None):
    default = dict(default or {})
    default['buyer_id'] = False
    return super(RealEstate, self).copy(default)
