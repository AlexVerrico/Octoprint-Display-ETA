$(function() {
    function ETAModel(parameters) {
        var self = this;
        self.ETA = ko.observable("-");
		self.settings = parameters[0];
		
		//self.options = {
		time24hr : ko.observable(),
		//	sendToPrinter : ko.observable()
		//};
		
		// self.updateOptions = function(){
	        // var keys = Object.keys(self.options);
	        // var result = [];
	        // keys.forEach(function(key){
	            // if (self.options[key]()) result.push("."+key);
	        // });
	        // $('#gcode_upload').attr('accept', result.join(','));
	    // };
		
        self.onBeforeBinding = function() {
            var element = $("#state").find(".accordion-inner .progress");
			
			// var keys = Object.keys(self.options);
            // Initialize each element in model
            // keys.forEach(function(key) {
                // self.options[key](self.settings.settings.plugins.display_eta[key]());
            // });
            // Bind subscriber to views.
            // keys.forEach(function(key) {
                // self.options[key].subscribe(self.updateOptions);
            // });
		    // self.updateOptions();
			
            if (element.length) {
                // console.log("Found required elements");
                var text = gettext("ETA");
                // console.log(text);
                element.before(text + ": <strong id='ETA_string' data-bind=\"html: ETA\"></strong><br>");
            }
            /*else {
                // console.log("could not find required elements");
            }*/
        };
        self.onDataUpdaterPluginMessage = function(plugin, data) {
            if (plugin != "display_eta") {
                // console.log("wrong plugin");
                return;
            }
            self.ETA(data.eta_string);
        };

    }

    OCTOPRINT_VIEWMODELS.push({
        construct: ETAModel,
        dependencies: ["printerStateViewModel", "settingsViewModel"],
        elements: ["#navbar_plugin_octoprint_display_eta","#ETA_string","#settings_plugin_display_eta"]
    });

});


