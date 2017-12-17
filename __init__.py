# coding=utf-8
from __future__ import absolute_import

import octoprint.plugin
import time

class HelloWorldPlugin(octoprint.plugin.ProgressPlugin,
                       octoprint.plugin.TemplatePlugin,
                       octoprint.plugin.AssetPlugin,
                       octoprint.plugin.EventHandlerPlugin):
    def __init__(self):
        self.eta_string = "-"
        self.eta_strftime = "%H:%M:%S"

    def calculate_ETA(self):
        currentData = self._printer.get_current_data()
        if not currentData["progress"]["printTimeLeft"]:
            return "-"
        current_time = time.localtime(time.time())
        finish_time = time.localtime(time.time() + currentData["progress"]["printTimeLeft"])
        strtime = time.strftime(self.eta_strftime, finish_time)
        strdate = ""
        if finish_time.tm_mday > current_time.tm_mday:
            if finish_time.tm_mday == current_time.tm_mday + 1:
                strdate = " Tomorrow"
            else:
                strdate = " Day %s" % finish_time.tm_mday
        return strtime + strdate
            
        
        
    def on_print_progress(self,storage, path, progress):
        self.eta_string = self.calculate_ETA()
        self._plugin_manager.send_plugin_message(self._identifier, dict(eta_string=self.eta_string))
        
    def on_event(self,event, payload):
        if event.startswith('Print'):
            if event not in {"PrintStarted","PrintResumed"}:
                self.eta_string="-"
            else:
                self.eta_string = self.calculate_ETA()
            self._plugin_manager.send_plugin_message(self._identifier, dict(eta_string=self.eta_string))
            
    def get_assets(self):
        return {
            "js": ["js/navbartemp.js"],
            "css": ["css/navbartemp.css"],
            "less": ["less/navbartemp.less"]
        } 

__plugin_name__ = "Hello World"
__plugin_version__ = "1.0.0"
__plugin_description__ = "A quick \"Hello World\" example plugin for OctoPrint"
__plugin_implementation__ = HelloWorldPlugin()
