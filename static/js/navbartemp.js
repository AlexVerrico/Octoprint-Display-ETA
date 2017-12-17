$(function() {
    function NavbarTempViewModel(parameters) {
        var self = this;

        self.navBarTempModel = parameters[0];
        self.global_settings = parameters[1];

    }

    ADDITIONAL_VIEWMODELS.push([
        NavbarTempViewModel, 
        ["temperatureViewModel", "settingsViewModel"],
        ["#navbar_plugin_helloworld", "#settings_plugin_helloworld"]
    ]);
});
