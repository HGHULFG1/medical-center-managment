odoo.define('mail.Manager.Notification.Medical', function (require) {
    "use strict";
    var core = require('web.core');

var _t = core._t;

    var MailManager = require('mail.Manager');
    MailManager.include({
    
        //--------------------------------------------------------------------------
        // Private
        //--------------------------------------------------------------------------


        /**
         * Called when adding a non age suitable medication for a patient
         *
         * @private
         * @param {Object} data 
         */
        _handlePartnerMedicamentsInvalidAge: function (data) {

             Swal.fire({
                icon: 'warning',
                title: _t('Invalid medicaments...'),
                text: data.message,
                backdrop: false,
                confirmButtonText: _t("Ok")
              })
        },        
        _handlePartnerMedicamentsSideEffects: function (data) {
            var sideEffects = data.side_effects;
            var html = `<table class="o_list_table table table-sm table-hover table-striped o_list_table_ungrouped">
            <tr>
            <th>Because of Having</th>
            <th>Lead To</th>
            </tr>`;
            sideEffects.forEach(element => {
                    html = html + `
                    <tr>
                    <td>${element.caused_by}</td>
                    <td>${element.causing}</td>
                    </tr>
                    `
            });
            Swal.fire({
                icon: 'warning',
                title: _t('Side Effects...'),
                html: html,
                backdrop: false,
            });
       },   
        /**
         * On receiving a notification that is specific to a user
         *
         * @private
         * @param {Object} data structure depending on the type
         * @param {integer} data.id
         */
        
        _handlePartnerNotification: function (data) {
            this._super.apply(this, arguments);
            if (data.type === 'medicaments_age_invalid') {
                this._handlePartnerMedicamentsInvalidAge(data);
            }
            else if (data.type === 'medicaments_side_effects') {
                this._handlePartnerMedicamentsSideEffects(data);
            }
        },
    });
    
    return MailManager;
    
    });
    