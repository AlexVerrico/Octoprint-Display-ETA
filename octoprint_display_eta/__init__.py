# coding=utf-8
from __future__ import absolute_import

import octoprint.plugin
from octoprint.util import RepeatedTimer
import time
import datetime
from babel.dates import format_date, format_datetime, format_time

class DisplayETAPlugin(octoprint.plugin.ProgressPlugin,
                       octoprint.plugin.TemplatePlugin,
                       octoprint.plugin.AssetPlugin,
                       octoprint.plugin.EventHandlerPlugin):

    def __init__(self):
        self.eta_string = "-"
        self.timer = RepeatedTimer(15.0, DisplayETAPlugin.fromTimer, args=[self], run_first=True,)

    def fromTimer(self):
        self.eta_string = self.calculate_ETA()
        self._plugin_manager.send_plugin_message(self._identifier, dict(eta_string=self.eta_string))
        
        
    def calculate_ETA(self):
        currentData = self._printer.get_current_data()
        if not currentData["progress"]["printTimeLeft"]:
            return "--"
        current_time = datetime.datetime.today()
        finish_time = current_time + datetime.timedelta(0,currentData["progress"]["printTimeLeft"])
        strtime = format_time(finish_time)
        strdate = ""
        if finish_time.day > current_time.day:
            if finish_time.day == current_time.day + 1:
                strdate = " Tomorrow"
            else:
                strtime = " " + format_date(finish_time,"EEE d")
        return strtime + strdate
            
        
        
    def on_print_progress(self,storage, path, progress):
        self.eta_string = self.calculate_ETA()
        self._printer.commands("M117 ETA is {}".format(self.eta_string))
        self._plugin_manager.send_plugin_message(self._identifier, dict(eta_string=self.eta_string))
        
    def on_event(self,event, payload):
        if event.startswith('Print'):
            if event not in {"PrintStarted","PrintResumed"}:
                self.eta_string="---"
                self.timer.cancel()
            else:
                self.eta_string = self.calculate_ETA()
                self.timer.cancel()
                self.timer = RepeatedTimer(10.0, DisplayETAPlugin.fromTimer, args=[self], run_first=True,)
                self.timer.start()
            self._plugin_manager.send_plugin_message(self._identifier, dict(eta_string=self.eta_string))
            
    def get_assets(self):
        return {
            "js": ["js/display_eta.js"]
        } 


    def get_update_information(self):
        return dict(
            display_eta=dict(
            #Octoprint-Display-ETA=dict(
                displayName=self._plugin_name,
                displayVersion=self._plugin_version,
                type="github_release",
                current=self._plugin_version,
                user="AlexVerrico",
                repo="Octoprint-Display-ETA",
                pip="https://github.com/AlexVerrico/Octoprint-Display-ETA/archive/{target}.zip"
            )
        )

__plugin_name__ = "Octoprint-Display-ETA"
__plugin_identifier__ = "display_eta"
__plugin_version__ = "1.0.5"
__plugin_description__ = "Show finish time (ETA) for current print."
__plugin_implementation__ = DisplayETAPlugin()
__plugin_pythoncompat__ = ">=2.7,<4"

__plugin_hooks__ = {
    "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
}

