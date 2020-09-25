"""Add wizard to allow email creation and sending.

Added models:
MedicalSendEmail: inherits the email composer, but has its own template id.

"""

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class MedicalSendEmail(models.TransientModel):
    """Wizard for creation and sending emails.

    fiedls:
    composer_id: the model inherits the email composer, in this field
    template_id: the email template.
    """

    _name = 'medical.email.send'
    _inherits = {'mail.compose.message':'composer_id'}
    _description = 'Medical Email Send'

    is_email = fields.Boolean('Email', default=lambda self: self.env.company.invoice_is_email)
    is_print = fields.Boolean('Print', default=lambda self: self.env.company.invoice_is_print)
    printed = fields.Boolean('Is Printed', default=False)
    composer_id = fields.Many2one('mail.compose.message', string='Composer', required=True, ondelete='cascade')
    template_id = fields.Many2one(
        'mail.template', 'Use template', index=True,
        domain="[('model', '=', 'doctor.appointment')]"
        )

    @api.onchange('template_id')
    def onchange_template_id(self):
        """Recompute the email html body when the user changes the template, this is \
            done by changing the template of the composer_id and invoke his onchange on the template, this \
            will recompute the body of the composer witch is the same body of the this model."""
        for wizard in self:
            if wizard.composer_id:
                wizard.composer_id.template_id = wizard.template_id.id
                wizard.composer_id.onchange_template_id_wrapper()
    
    @api.model
    def default_get(self, fields):
        """Creaate the email composer and assigned it to the active records."""
        res = super(MedicalSendEmail, self).default_get(fields)
        res_ids = self._context.get('active_ids')
        composer = self.env['mail.compose.message'].create({
            'composition_mode': 'comment' if len(res_ids) == 1 else 'mass_mail',
        })
        res.update({
            'composer_id': composer.id,
        })
        return res
    
    def _send_email(self):
        if self.is_email:
            self.composer_id.send_mail()
    
    def send_and_print_action(self):
        """Compute the language of each email (actually it will be the language set on the patient level) \
            then send the email."""
        self.ensure_one()
        # Send the mails in the correct language by splitting the ids per lang.
        # This should ideally be fixed in mail_compose_message, so when a fix is made there this whole commit should be reverted.
        # basically self.body (which could be manually edited) extracts self.template_id,
        # which is then not translated for each customer.
        if self.composition_mode == 'mass_mail' and self.template_id:
            active_ids = self.env.context.get('active_ids', self.res_id)
            active_records = self.env[self.model].browse(active_ids)
            langs = active_records.mapped('patient_id.lang')
            default_lang = self.env.user.lang
            for lang in (set(langs) or [default_lang]):
                active_ids_lang = active_records.filtered(lambda r: r.partner_id.lang == lang).ids
                self_lang = self.with_context(active_ids=active_ids_lang, lang=lang)
                self_lang.onchange_template_id()
                self_lang._send_email()
        else:
            self._send_email()
        # if self.is_print:
        #     return self._print_document()
        return {'type': 'ir.actions.act_window_close'}