# coding=utf-8
from __future__ import absolute_import

import octoprint.plugin
import time

class HelloWorldPlugin(octoprint.plugin.ProgressPlugin):
    def on_print_progress(self,storage, path, progress):
        currentData = self._printer.get_current_data()
        eta_strftime = "%H %M %S Day %d"
        self._logger.info("Hello World! %s" % time.strftime(eta_strftime, time.localtime(time.time() + currentData["progress"]["printTimeLeft"])))


__plugin_name__ = "Hello World"
__plugin_version__ = "1.0.0"
__plugin_description__ = "A quick \"Hello World\" example plugin for OctoPrint"
__plugin_implementation__ = HelloWorldPlugin()
