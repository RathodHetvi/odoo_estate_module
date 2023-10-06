from odoo import models, fields,api,_
from datetime import timedelta,datetime
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError


class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "estate training model"

    # _log_access =False
    # by default it is _auto
    # can't use in transient model

    name = fields.Char('name', required=True)
    sequence=fields.Char('sequence',readonly='1')
    description = fields.Text('description')

    postcode = fields.Char('postcode')
    date_availability = fields.Date('date', copy=False, default=lambda self: (datetime.now() + timedelta(days=90)).strftime('%Y-%m-%d'))
    expected_price = fields.Float('expected_price', required=True)
    active =fields.Boolean('active',default=True)
    state=fields.Selection(selection=[('new','New'),('offer received','Offer Received'),('offer accepted','Offer Accepted'),('sold','Sold'),('canceled','Canceled')],required=True,default='new')
    selling_price = fields.Float('selling_price', readonly=True)
    bedrooms = fields.Integer('bedrooms', default=2)
    living_area = fields.Integer('living_area')
    facades = fields.Integer('facades')
    garage = fields.Boolean('garage')
    garden = fields.Boolean('garden')
    garden_area = fields.Integer('garden_area')
    garden_orientation = fields.Selection(selection=[
        ('north', "North"),
        ('south', "South"),
        ('east', 'East'),
        ('west', "West"),

    ], )

    total_area = fields.Char(compute="_compute_total_area")
    best_price=fields.Float(compute='_compute_best_price')
    property_type_id =fields.Many2one('estate.property.type',string="property_type")

    salesperson=fields.Many2one('res.users',string="salesperson",default=lambda self: self.env.user)
    buyer=fields.Many2one('res.partner',string="buyer",copy=False,readonly=True)

    tag_ids=fields.Many2many('estate.property.tag',string='tags')

    offer_ids=fields.One2many('estate.property.offer','property_id',string=" ")

    # _sql_constraints=[('postive amount','CHECK(expected_price >= 0.0)','price should be positive')]


    @api.constrains('selling_price', 'expected_price')
    def _check_price_constraint(self):
        for rec in self:
            min_price = self.expected_price * 0.9
            if rec.selling_price < min_price:
                raise ValidationError("Selling price cannot be lower than 90% of the expected price.")

    @api.depends('living_area','garden_area')
    def _compute_total_area(self):
        for record in self:
            record.total_area =record.garden_area + record.living_area


    @api.depends('offer_ids')
    def _compute_best_price(self):
        for record in self:
            if record.offer_ids:
                #here also if you write offer_ids.price it will give sigleton error
                record.best_price= max(record.offer_ids.mapped('price'))
                # if record.offer_ids.status in ('accept'):
                #     record.best_price =record.offer_ids.price

            # if record.best_price=min(record.offer_ids.price) then it will give siglton error
            else:
                record.best_price =False


    @api.onchange('garden')
    def _onchange_garden(self):
        if self.garden:
            self.garden_area =10.0
            self.garden_orientation='north'
        else:
            self.garden_area = 0.0
            self.garden_orientation = False

    def action_cancle(self):
        for record in self:
            if record.state in ('new', 'offer received', 'offer accepted'):
                record.state='canceled'
            else:
                raise UserError(_("sold property cannot be cancled"))

    def action_sold(self):
        for record in self:
            if record.state in ('new','offer received','offer accepted'):
                record.state='sold'
            else:
                raise UserError(_("cancled property cannot be sold"))

    @api.ondelete(at_uninstall=False)
    def _unlink_except_state(self):
        for rec in self:
            if rec.state in ['new','canceled']:
                raise UserError(
                    _("can't delete when state is in new or canceled"))
        self.clear_caches()

    @api.model
    def create(self,vals):
        vals['sequence']=self.env['ir.sequence'].next_by_code('estate.property')
        return super(EstateProperty,self).create(vals)

class EstateInherit(models.Model):
    _inherit='res.users'

    property_ids=fields.One2many('estate.property','salesperson',domain="[('active','=',True)]")

