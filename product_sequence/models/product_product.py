# -*- coding: utf-8 -*-
# Copyright 2004 Tiny SPRL
# Copyright 2016 Sodexis
# Copyright 2018 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _


class ProductProduct(models.Model):
    _inherit = "product.product"

    default_code = fields.Char(required=True, default="/")

    _sql_constraints = [
        (
            "uniq_default_code",
            "unique(default_code)",
            "The reference must be unique"
        )
    ]

    @api.model
    def create(self, vals):
        if "default_code" not in vals or vals["default_code"] == "/":
            categ_id = vals.get("categ_id")
            template_id = vals.get("product_tmpl_id")
            categ = sequence = False
            if categ_id:
                # Created as a product.product
                categ = self.env["product.category"].browse(categ_id)
            elif template_id:
                # Created from a product.template
                template = self.env["product.template"].browse(template_id)
                categ = template.categ_id
            if categ:
                sequence = categ.sequence_id
            if not sequence:
                sequence = self.env.ref("product_sequence.seq_product_auto")
            vals["default_code"] = sequence.next_by_id()
        return super(ProductProduct, self).create(vals)

    @api.multi
    def write(self, vals):
        """To assign a new internal reference, just write '/' on the field.
        Note this is up to the user, if the product category is changed,
        she/he will need to write '/' on the internal reference to force the
        re-assignment."""
        if vals.get("default_code", "") in [False, "/"]:
            for product in self:
                sequence = product.categ_id.sequence_id
                if not sequence:
                    sequence = self.env.ref("product_sequence.seq_product_auto")
                ref = sequence.next_by_id()
                vals["default_code"] = ref
                super(ProductProduct, product).write(vals)
                if len(product.product_tmpl_id.product_variant_ids) == 1:
                    # default code must match for variant and template.
                    product.product_tmpl_id.default_code = ref
            return True
        return super(ProductProduct, self).write(vals)

    @api.multi
    def copy(self, default=None):
        if default is None:
            default = {}
        if self.default_code:
            default.update({"default_code": self.default_code + _("-copy")})
        return super(ProductProduct, self).copy(default)
