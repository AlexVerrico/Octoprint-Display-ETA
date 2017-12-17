$(function() {
    function NavbarTempViewModel(parameters) {
        var self = this;
        self.ETA = ko.observable("NA");
        self.onDataUpdaterPluginMessage = function(plugin, data) {
            if (plugin != "helloworld") {
                return;
            }
            self.ETA(data.eta_string);
        };
    }

    ADDITIONAL_VIEWMODELS.push([
        NavbarTempViewModel, 
        ["temperatureViewModel", "settingsViewModel"],
        ["#navbar_plugin_helloworld", "#settings_plugin_helloworld"]
    ]);
});
