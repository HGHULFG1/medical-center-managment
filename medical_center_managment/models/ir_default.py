from odoo import api, fields, models, _
from odoo import api, fields, models, tools, _

import json
class IrDefault(models.Model):
    """User-defined default values for fields."""
    
    _inherit = 'ir.default'
    @api.model
    @tools.ormcache('self.env.uid', 'self.env.company.id', 'model_name', 'condition')
    # Note about ormcache invalidation: it is not needed when deleting a field,
    # a user, or a company, as the corresponding defaults will no longer be
    # requested. It must only be done when a user's company is modified.
    def get_model_defaults(self, model_name, condition=False, company = False):
        """Return the available default values for the given model (for the\
            current user), as a dict mapping field names to values."""
        cr = self.env.cr
        if not self.env.uid or not self.env.company.id : 
          return {}
        params = [model_name, self.env.uid, self.env.company.id]

        query = """ SELECT f.name, d.json_value
                    FROM ir_default d
                    JOIN ir_model_fields f ON d.field_id=f.id
                    WHERE f.model=%s
                        AND (d.user_id IS NULL OR d.user_id=%s)
                        AND (d.company_id IS NULL OR d.company_id=%s)
                        AND {}
                    ORDER BY d.user_id, d.company_id, d.id
                """

        if condition:
            query = query.format("d.condition=%s")
            params.append(condition)
        else:
            query = query.format("d.condition IS NULL")
        cr.execute(query, params)
        result = {}
        for row in cr.fetchall():
            # keep the highest priority default for each field
            if row[0] not in result:
                result[row[0]] = json.loads(row[1])

        return result
