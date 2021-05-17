# coding=utf-8
from __future__ import absolute_import

import octoprint.plugin
from octoprint.util import RepeatedTimer
import datetime
import logging
from babel.dates import format_date, format_time
import flask


class DisplayETAPlugin(octoprint.plugin.AssetPlugin,
                       octoprint.plugin.EventHandlerPlugin,
                       octoprint.plugin.ProgressPlugin,
                       octoprint.plugin.SettingsPlugin,
                       octoprint.plugin.StartupPlugin,
                       octoprint.plugin.TemplatePlugin,
                       octoprint.plugin.SimpleApiPlugin,
                       octoprint.plugin.RestartNeedingPlugin,):

    def __init__(self):
        # This allows us to store and display our logs with the rest of the OctoPrint logs
        self.logger = logging.getLogger('octoprint.plugins.display_eta')
        return

    #######################
    # StartupPlugin Mixin #
    #######################
    # Function to run after Octoprint starts, used to initialise variables
    def on_after_startup(self):
        # Create a string to store the latest ETA
        self.eta_string = "-"

        # Check if the user has chosen to display the ETA on the printer LCD
        self.doM117 = self._settings.get(['displayOnPrinter'])

        # Check if the user has chosen to use 24hr time
        if self._settings.get(['time24hr']) is True:
            # See http://babel.pocoo.org/en/latest/dates.html#time-fields
            self.CustomTimeFormat = "HH:mm:ss"
        else:
            # See http://babel.pocoo.org/en/latest/dates.html#time-fields
            self.CustomTimeFormat = "hh:mm:ss a"

        # Check if the user has chosen to remove colons from the ETA displayed on the printer LCD
        self.replaceColons = self._settings.get(['removeColons'])

        # Load the set interval in seconds between updating the ETA value
        self.update_interval = self._settings.get(['updateInterval'])
        # Create a RepeatedTimer object to run calculate_eta every update_interval seconds, eg every 10 seconds
        self.timer = RepeatedTimer(self.update_interval, DisplayETAPlugin.calculate_eta, args=[self], run_first=True, )

    ########################
    # SettingsPlugin Mixin #
    ########################
    # Function to return the default values for all settings for this plugin
    def get_settings_defaults(self):
        return dict(
            time24hr=False,
            displayOnPrinter=True,
            removeColons=False,
            updateInterval=10.0
        )

    # Function to run when the settings are saved
    def on_settings_save(self, data):
        # Store the new settings values for easy access
        octoprint.plugin.SettingsPlugin.on_settings_save(self, data)

        # Check if the user has chosen to use 24hr time
        if self._settings.get(["time24hr"]) is True:
            self.logger.debug('24HR = True')
            # See http://babel.pocoo.org/en/latest/dates.html#time-fields for details on the time format
            self.CustomTimeFormat = "HH:mm:ss"
            pass
        else:
            self.logger.debug('24HR = False')
            # See http://babel.pocoo.org/en/latest/dates.html#time-fields for details on the time format
            self.CustomTimeFormat = "hh:mm:ss a"

        # Check if the user has chosen to display the ETA on the printer LCD
        if self._settings.get(["displayOnPrinter"]) is True:
            self.logger.debug('M117 = True')
            self.doM117 = True
        else:
            self.doM117 = False
            self.logger.debug('M117 = False')

        # Check if the user has chosen to remove colons from the ETA displayed on the printer LCD
        if self._settings.get(["removeColons"]) is True:
            self.replaceColons = True
            self.logger.debug('self.replaceColons = True')
        else:
            self.replaceColons = False

        # Store what the new updateInterval is
        self.update_interval = self._settings.get(['updateInterval'])

    ########################
    # TemplatePlugin Mixin #
    ########################
    # Function to inform OctoPrint what parts of the UI we will be binding to
    def get_template_configs(self):
        return [
            # We bind to the navbar to allow us to manipulate the main Web UI
            dict(type="navbar", custom_bindings=False),
            # We bind to the settings to allow us to show a settings page to the user
            dict(type="settings", custom_bindings=False)
        ]

    ########################
    # ProgressPlugin Mixin #
    ########################
    # Function to be called by Octoprint on print progress
    def on_print_progress(self, storage, path, progress):
        self.logger.debug('on_print_progress called')
        # Calculate the ETA and push it to the Web UI and printer LCD (if enabled)
        self.calculate_eta()
        self.logger.debug('reached end of on_print_progress')

    ############################
    # EventHandlerPlugin Mixin #
    ############################
    # Fucntion to be called by Octoprint when an event occurs
    def on_event(self, event, payload):
        self.logger.debug('on_event called')
        self.logger.debug('event is {}'.format(event))
        # Check if the event is PrintStarted or PrintResumed
        if event in ('PrintStarted', 'PrintResumed'):
            self.logger.debug('event is PrintStarted or PrintResumed. Calling calculate_eta')
            # Calculate the ETA and push it to the Web UI and printer LCD (if enabled)
            self.calculate_eta()
            # Stop the timer
            self.timer.cancel()
            # Get the updateInterval from the settings
            self.update_interval = self._settings.get(['updateInterval'])
            # Redefine the timer with the new updateInterval
            self.timer = RepeatedTimer(self.update_interval, DisplayETAPlugin.calculate_eta, args=[self], run_first=True,)
            # Start the timer
            self.timer.start()
            self.logger.debug('reached end of on_event')
            return

        # If the even starts with Print but isn't PrintStarted or PrintResumed
        elif event.startswith("Print"):
            # Set the current ETA to "-"
            self.eta_string = "-"
            # Stop the timer
            self.timer.cancel()
            self.logger.debug('event starts with Print but is not PrintStarted or PrintResumed')
            return
        else:
            return

    #########################
    # SimpleApiPlugin Mixin #
    #########################
    # Function to return a list of commands that we accept through the POST endpoint of the API for this plugin
    def get_api_commands(self):
        return dict(
            current_eta=[],
            update_eta=[]
        )

    # Function for Octoprint to call when a request is sent to the POST endpoint of the API for this plugin
    def on_api_command(self, command, data):
        # If the command sent to the API is current_eta
        if command == 'current_eta':
            # Return the current eta_string
            return flask.jsonify({'eta': self.eta_string}), 200
        # If the command sent to the API is update_eta
        if command == 'update_eta':
            # Store the current eta_string
            old_eta = self.eta_string
            # Calculate the ETA and push it to the Web UI and printer LCD (if enabled)
            self.calculate_eta()
            # Return the old eta_string and the newly calculated eta_string
            return flask.jsonify({'eta': self.eta_string, 'old_eta': old_eta}), 200

    # Function for Octoprint to call when a request is sent to the GET endpoint of the API for this plugin
    def on_api_get(self, request):
        # Check if the request includes the command parameter
        if 'command' not in request.values:
            # If the command parameter is not present, return an error
            return "Error, please include the command parameter", 400
        # Create a list of command that we accept
        recognised_commands = ['current_eta', 'update_eta']
        # Store the value of the command parameter
        command = request.values['command']
        # Check if the command is a supported one
        if command not in recognised_commands:
            # If the command isn't supported, return an error
            return "Error, unrecognised command", 400
        # If the command sent ot the API is current_eta
        if command == 'current_eta':
            # Return the current eta_string
            return flask.jsonify({'eta': self.eta_string}), 200
        # If the command sent to the API is update_eta
        if command == 'update_eta':
            # Store the current eta_string
            old_eta = self.eta_string
            # Calculate the ETA and push it to the Web UI and printer LCD (if enabled)
            self.calculate_eta()
            # Return the old eta_string and the newly calculated eta_string
            return flask.jsonify({'eta': self.eta_string, 'old_eta': old_eta}), 200

    #####################
    # AssetPlugin Mixin #
    #####################
    # Function to tell Octoprint what assets we need loaded in the Web UI
    def get_assets(self):
        return {
            "js": ["js/display_eta.js"]
        }

    ####################
    # Custom functions #
    ####################
    # Function to calculate and update the ETA
    def calculate_eta(self, do_update_eta=True):
        self.logger.debug('calculate_eta called')
        # Get the current printer data, which should include the time left for the current print
        current_data = self._printer.get_current_data()
        # Check if the time left for the current print is included in the data returned
        if not current_data["progress"]["printTimeLeft"]:
            self.logger.debug("calculate_eta() returning blank string")
            return "-"
        # Get the current time and date
        current_time = datetime.datetime.today()
        # Add the time left for the current print to the current time and date
        finish_time = current_time + datetime.timedelta(0, current_data["progress"]["printTimeLeft"])
        # Format the time according to the users choice (either 12hr or 24hr time)
        strtime = format_time(finish_time, self.CustomTimeFormat)
        self.logger.debug('strtime = ' + strtime)
        # Create an empty string to store the finish date for the print
        strdate = ""
        # Check if the print will finish today
        if finish_time.day > current_time.day:
            # If the print will finish tomorrow
            if finish_time.day == current_time.day + 1:
                # Set strdate to Tomorrow
                strdate = " Tomorrow"
            # If the print will finish after tomorrow
            else:
                # Set strdate to the finish date for the print
                strtime = " " + format_date(finish_time, "EEE d")
        self.logger.debug('reached end of calculate_eta')

        # Join strtime and strdate and store it as eta_string
        self.eta_string = strtime + strdate
        if do_update_eta is True:
            # Push the ETA to the Web UI and printer LCD(If enabled)
            self.update_eta()
        return

    # Function to push the current ETA to the Web UI and printer LCD (If enabled)
    def update_eta(self):
        # Send the current ETA to the Web UI
        self._plugin_manager.send_plugin_message(self._identifier, dict(eta_string=self.eta_string))
        # Check if the user has chosen to display the ETA on the printer LCD
        if self.doM117 is True:
            # Check if the user has chosen to remove colons from the output to the printer LCD
            if self.replaceColons is True:
                # Send the ETA to the printer LCD, minus the colons
                self._printer.commands("M117 ETA is {}".format(self.eta_string.replace(":", " ")))
            else:
                # Send the ETA to the printer LCD
                self._printer.commands("M117 ETA is {}".format(self.eta_string))
        return

    # Function to tell Octoprint how to update the plugin
    def get_update_information(self):
        return dict(
            display_eta=dict(
                displayName=self._plugin_name,
                displayVersion=self._plugin_version,
                type="github_release",
                current=self._plugin_version,
                user="AlexVerrico",
                repo="Octoprint-Display-ETA",
                pip="https://github.com/AlexVerrico/Octoprint-Display-ETA/archive/{target}.zip"
            )
        )


__plugin_name__ = "Octoprint Display ETA"
__plugin_identifier__ = "display_eta"
__plugin_description__ = "Display finish time (ETA) for current print."
__plugin_implementation__ = DisplayETAPlugin()
__plugin_pythoncompat__ = ">=2.7,<4"

__plugin_hooks__ = {
    "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
}
