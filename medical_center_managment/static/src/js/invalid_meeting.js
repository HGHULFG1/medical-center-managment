odoo.define('web.CrashManagerInvalidMeeting', function (require) {
    "use strict";
    // var Swal = require('sweetalert');
    var WebCrashManager = require('web.CrashManager');
    var core = require('web.core');
    var _t = core._t;
    var rpc = require('web.rpc');
    WebCrashManager.CrashManager.include({
        show_warning: function (error, options) {
            // if (!this.active) {
            //     return;
            // }
            var title = _.str.capitalize(error.type) || _t("Something went wrong !");
            var message = error.data ? error.data.message : error.message;
            
            if (error.data.name == "odoo.addons.medical_center_managment.models.exceptions.custom_exceptions.InvalidMeeting")
                {
                title = _t("Invalid Meeting")
                var html = `<table class="o_list_table table table-sm table-hover table-striped o_list_table_ungrouped">
                <tr>
                <th>From</th>
                <th>To</th>
                </tr>`;
                var availibility = error.data.arguments[1]
                availibility.forEach(element => {
                    if (element.availibility.state == "available") {
                    html = html + `
                    <tr>
                    <td>${element.start_time}</td>
                    <td>${element.end_time}</td>
                    </tr>
                    `
                    };
                });
                html = html+"</table>"

                return Swal.fire({
                    icon: 'error',
                    title: 'Invalid Meeting...',
                    text: message,
                    backdrop: false,
                    showCancelButton: true,
                    confirmButtonColor: '#3085d6',
                    cancelButtonColor: '#d33',
                    confirmButtonText: _t("Show Available Times")
                  }).then((result) => {
                      if (result.isConfirmed) {

                              Swal.fire({
                                  icon: 'info',
                                  title: _t('Available times...'),
                                  html: html,
                                  backdrop: false,
                              })

                    }


                  })
                }
                
            
            return this._displayWarning(message, title, options);
        },
    })

})