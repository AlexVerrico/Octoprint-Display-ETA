# OctoPrint-Display-Print-ETA

Display the finish time of the current print as estimated by Octoprint. The day of finish is displayed only when the current print will not finish today.
You can configure if you want to display the ETA on the printer, as well as if you want to use 12HR or 24HR time.
If this plugin causes your printer to report errors, try enabling the option "remove all colons"

![alt text](./extras/img/screenshot.png)

## Setup

Install via the bundled [Plugin Manager](https://github.com/foosel/OctoPrint/wiki/Plugin:-Plugin-Manager)
or manually using this URL:

    https://github.com/AlexVerrico/Octoprint-Display-ETA/archive/master.zip

You must have the time zone configured on the host, otherwise you will see the time in UTC.
In Debian, use the following command to set time zone:
```bash
sudo dpkg-reconfigure tzdata
```
then follow the wizard.

Day and time are printed according to the host locales.
In Debian they are configured using
```bash
sudo dpkg-reconfigure locales
```
then follow the wizard.

## Contributing

All Pull Requests **<u>MUST</u>** be made to the devel branch, otherwise they will be ignored.<br/>
Please ensure that you follow the style of the code (eg. use spaces not tabs, etc)<br/>
For now, all code must be backwards compatible with Python 2, unless you can provide a _very_ compelling reason to drop Python 2 support.<br/>
Please open an issue to discuss what you features you want to add / bugs you want to fix _before_ working on them, as this avoids 2 people submitting a PR for the same feature/bug.