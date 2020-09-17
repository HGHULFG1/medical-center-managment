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
         * Called when an activity record has been updated on the server
         *
         * @private
         * @param {Object} data key, value to decide activity created or deleted
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
        },
    });
    
    return MailManager;
    
    });
    