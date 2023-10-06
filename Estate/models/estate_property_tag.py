from odoo import fields,models

class EstatePropertyTag(models.Model):
    _name='estate.property.tag'

    name=fields.Char(string='name',required=True)
    color=fields.Integer(string='color')