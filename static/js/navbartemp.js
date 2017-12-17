$(function() {
    function ETAModel(parameters) {
        var self = this;
        self.ETA = ko.observable("NA");
        self.onStartup = function() {
            var element = $("#state").find(".accordion-inner .progress");
            if (element.length) {
                var text = gettext("Cost");
                element.before(text + ": <strong data-bind=\"html: ETA\"></strong><br>");
            }
        };
        self.onDataUpdaterPluginMessage = function(plugin, data) {
            if (plugin != "helloworld") {
                return;
            }
            self.ETA(data.eta_string);
        };

    }

    OCTOPRINT_VIEWMODELS.push([
        ETAModel, 
        ["printerStateViewModel"],
        ["#navbar_plugin_helloworld"]
    ]);

});
