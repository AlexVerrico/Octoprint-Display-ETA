$(function() {
    function ETAModel(parameters) {
        var self = this;
        self.ETA = ko.observable("-");
		self.settings = parameters[0];
        self.onBeforeBinding = function() {
            var element = $("#state").find(".accordion-inner .progress");
            if (element.length) {
                element.before(gettext("ETA") + ": <strong id='ETA_string' data-bind=\"html: ETA\"></strong><br>");
            }
        };
        self.onDataUpdaterPluginMessage = function(plugin, data) {
            if (plugin === "display_eta") {
                self.ETA(data.eta_string);
            }
        };
    }

    OCTOPRINT_VIEWMODELS.push({
        construct: ETAModel,
        dependencies: ["printerStateViewModel", "settingsViewModel"],
        elements: ["#ETA_string"]
    });
});


