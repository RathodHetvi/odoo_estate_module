from odoo import fields,models,api
from datetime import timedelta
import datetime

class EstatePropertyType(models.Model):
    _name='estate.property.type'
    _order='sequence,id'

    name=fields.Char('name',required=True)
    property_ids=fields.One2many('estate.property','property_type_id',string='property')
    sequence=fields.Integer('Sequence')
    offer_ids=fields.One2many('estate.property.offer','property_type_id')
    offer_count=fields.Integer(compute='compute_offer')

    @api.depends('offer_ids')
    def compute_offer(self):
        for rec in self:
            rec.offer_count = len(rec.offer_ids)


class EstatePropertyOffer(models.Model):
    _name='estate.property.offer'

    price=fields.Float('price')
    status=fields.Selection([('accepted','Accepted'),('refused','Refused')])
    partner_id=fields.Many2one('res.partner',required=True)
    property_id =fields.Many2one('estate.property')
    validity=fields.Integer(string="validity",default=7)
    date_deadline =fields.Date(string="Date Deadline",compute='_compute_deadline',inverse='_inverse_deadline',store=True)
    #,inverse="_inverse_deadline"

    property_type_id=fields.Many2one(related='property_id.property_type_id',depends=['property_id'])
    #reletaed=m2o.m2m or o2m  or m2o

    @api.model
    @api.depends('validity','create_date')
    def _compute_deadline(self):
        for record in self:
            if record.create_date:
                record.date_deadline=timedelta(days=record.validity) + record.create_date
            else:
                record.date_deadline = False

    def _inverse_deadline(self):
        for record in self:
            if record.date_deadline and record.create_date:
                record.validity=(record.date_deadline - record.create_date.date()).days
                # record.validity=(record.date_deadline - record.create_date).days
                # if you write like this then you will get error , because date_deadline is a date field and
                # create_Date is datetime field that's why you should covert create_date datetime to date
            else:
                record.validity=False


    def action_accept(self):
        for record in self:
            record.status='accepted'
            self.property_id.selling_price =self.price
            self.property_id.buyer=self.partner_id
            self.property_id.state='offer accepted'


    def action_refuse(self):
        for record in self:
            record.status='refused'


    @api.model
    def create(self,vals):
        e=self.env['estate.property'].browse(vals['property_id'])
        e.state='offer received'
        return super(EstatePropertyOffer,self).create(vals)