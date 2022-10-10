
"""Shows the preferences window for pyRevit"""
#pylint: disable=E0401,W0703,W0613,C0111,C0103
import os
import os.path as op
import re

from pyrevit import HOST_APP, EXEC_PARAMS
from pyrevit.framework import System, Windows, Controls, Documents
from pyrevit.runtime.types import EventType, EventUtils
from pyrevit.loader import hooks
from pyrevit import coreutils
from pyrevit import routes
from pyrevit import telemetry
from pyrevit import script
from pyrevit import forms
from pyrevit import output
from pyrevit.labs import TargetApps, PyRevit
from pyrevit.coreutils import envvars
from pyrevit.coreutils import apidocs
from pyrevit.coreutils import applocales
from pyrevit.userconfig import user_config
from pyrevit.revit import tabs

import pyrevitcore_globals


logger = script.get_logger()


class EnvVariable(object):
    """List item for an environment variable.

    Attributes:
        Id (str): Env Variable name
        Value (str): Env Variable value
    """

    def __init__(self, var_id, value):
        self.Id = var_id
        self._value = value

    @property
    def Value(self):
        # if its the hook, get a list of hooks and display in human-readable
        if self.Id == envvars.HOOKS_ENVVAR:
            return coreutils.join_strings(
                [x.UniqueId for x in hooks.get_event_hooks()]
            )
        else:
            return self._value

    def __repr__(self):
        return '<EnvVariable Name: {} Value: {}>' \
                .format(self.Id, self._value)


class PyRevitEngineConfig(object):
    def __init__(self, engine):
        self.engine = engine

    @property
    def name(self):
        return '{} ({}): {}'.format(self.engine.KernelName,
                                    self.engine.Version,
                                    self.engine.Description)


class SettingsWindow(forms.WPFWindow):
    """pyRevit Settings window that handles setting the pyRevit configs"""

    def __init__(self, xaml_file_name):
        """Sets up the settings ui"""
        forms.WPFWindow.__init__(self, xaml_file_name)
        try:
            self._setup_core_options()
        except Exception as setup_params_err:
            logger.error('Error setting up a parameter. Please update '
                         'pyRevit again. | {}'.format(setup_params_err))

        self.reload_requested = False
        self.textchange_timer = None
        self._setup_engines()
        self._setup_user_extensions_list()
        self._setup_env_vars_list()

        # check boxes for each version of Revit
        # this could be automated but it pushes me to verify and test
        # before actually adding a new Revit version to the list
        self._addinfiles_cboxes = {
            '2017': self.revit2017_cb,
            '2018': self.revit2018_cb,
            '2019': self.revit2019_cb,
            '2020': self.revit2020_cb,
            '2021': self.revit2021_cb,
            '2022': self.revit2022_cb,
            }

        self.set_image_source(self.lognone, 'lognone.png')
        self.set_image_source(self.logverbose, 'logverbose.png')
        self.set_image_source(self.logdebug, 'logdebug.png')

        self._setup_uiux()
        self._setup_routes()
        self._setup_telemetry()
        self._setup_addinfiles()

    def _setup_core_options(self):
        """Sets up the pyRevit core configurations"""
        if user_config.bin_cache:
            self.bincache_rb.IsChecked = True
            self.asciicache_rb.IsChecked = False
        else:
            self.bincache_rb.IsChecked = False
            self.asciicache_rb.IsChecked = True

        self.checkupdates_cb.IsChecked = user_config.check_updates

        self.rocketmode_cb.IsChecked = user_config.rocket_mode

        if user_config.log_level == PyRevit.PyRevitLogLevels.Quiet:
            self.noreporting_rb.IsChecked = True
            self.verbose_rb.IsChecked = False
            self.debug_rb.IsChecked = False
        elif user_config.log_level == PyRevit.PyRevitLogLevels.Verbose:
            self.noreporting_rb.IsChecked = False
            self.verbose_rb.IsChecked = True
            self.debug_rb.IsChecked = False
        elif user_config.log_level == PyRevit.PyRevitLogLevels.Debug:
            self.noreporting_rb.IsChecked = False
            self.verbose_rb.IsChecked = False
            self.debug_rb.IsChecked = True

        self.filelogging_cb.IsChecked = user_config.file_logging

        self.startup_log_timeout.Text = str(user_config.startuplog_timeout)
        self.requiredhostbuild_tb.Text = str(user_config.required_host_build)
        self.minhostdrivefreespace_tb.Text = \
            str(user_config.min_host_drivefreespace)

        self.loadbetatools_cb.IsChecked = user_config.load_beta

    def _setup_engines(self):
        attachment = user_config.get_current_attachment()
        if attachment and attachment.Clone:
            engine_cfgs = \
                [PyRevitEngineConfig(x) for x in attachment.Clone.GetEngines()]
            engine_cfgs = \
                sorted(engine_cfgs,
                       key=lambda x: x.engine.Version, reverse=True)

            # add engines to ui
            self.availableEngines.ItemsSource = \
                [x for x in engine_cfgs if x.engine.Runtime]
            self.cpythonEngines.ItemsSource = \
                [x for x in engine_cfgs if not x.engine.Runtime]

            # now select the current runtime engine
            for engine_cfg in self.availableEngines.ItemsSource:
                if engine_cfg.engine.Version == int(EXEC_PARAMS.engine_ver):
                    self.availableEngines.SelectedItem = engine_cfg
                    break

            # if addin-file is not writable, lock changing of the engine
            if attachment.IsReadOnly():
                self.availableEngines.IsEnabled = False

            # now select the current runtime engine
            self.active_cpyengine = user_config.get_active_cpython_engine()
            if self.active_cpyengine:
                for engine_cfg in self.cpythonEngines.ItemsSource:
                    if engine_cfg.engine.Version == \
                            self.active_cpyengine.Version:
                        self.cpythonEngines.SelectedItem = engine_cfg
                        break
            else:
                logger.debug('Failed getting active cpython engine.')
                self.cpythonEngines.IsEnabled = False
        else:
            logger.debug('Error determining current attached clone.')
            self.disable_element(self.availableEngines)

    def _setup_user_extensions_list(self):
        """Reads the user extension folders and updates the list"""
        self.extfolders_lb.ItemsSource = \
            user_config.get_thirdparty_ext_root_dirs(include_default=False)

    def _setup_env_vars_list(self):
        """Reads the pyRevit environment variables and updates the list"""
        env_vars_list = \
            [EnvVariable(k, v)
             for k, v in sorted(envvars.get_pyrevit_env_vars().items())]

        self.envvars_lb.ItemsSource = env_vars_list

    def _setup_uiux(self):
        applocale = applocales.get_current_applocale()
        sorted_applocales = \
            sorted(applocales.APP_LOCALES, key=lambda x: str(x.lang_type))
        self.applocales_cb.ItemsSource = [str(x) for x in sorted_applocales]
        self.applocales_cb.SelectedItem = str(applocale)

        # colorize docs
        self.colordocs_cb.IsChecked = user_config.colorize_docs

        # tab style color themes
        theme = tabs.get_tabcoloring_theme(user_config)
        self.tab_theme = theme
        self.filtercolor_counter = 1

        self.doc_ordercolor_lb.ItemsSource = theme.TabOrderRules
        self.doc_filtercolor_lb.ItemsSource = theme.TabFilterRules

        # tab styles (must set after the color themes)
        self.project_tabstyle_cb.ItemsSource = theme.AvailableStyles
        self.project_tabstyle_cb.SelectedItem = theme.TabStyle

        self.family_tabstyle_cb.ItemsSource = theme.AvailableStyles
        self.family_tabstyle_cb.SelectedItem = theme.FamilyTabStyle

        self.sortdocs_cb.IsChecked = theme.SortDocTabs

        # output settings
        self.cur_stylesheet_tb.Text = output.get_stylesheet()
        # pyrevit gui settings
        self.loadtooltipex_cb.IsChecked = user_config.tooltip_debug_info

    def _get_event_telemetry_checkboxes(self):
        return list([x for x in self.event_telemetry_sp.Children
                     if isinstance(x, Controls.CheckBox)])

    def _setup_event_telemetry_checkboxes(self):
        supportedEvents = EventUtils.GetSupportedEventTypes()
        for event_type in coreutils.get_enum_values(EventType):
            # verify event type is supported in telemetry system
            # grab the two parts of the event type name
            api_name, api_event = str(event_type).split('_')

            # figure out the namespace
            api_namespace = 'Autodesk.Revit.ApplicationServices.'
            if api_name in ['UIApplication', 'AddInCommandBinding']:
                api_namespace = 'Autodesk.Revit.UI.'

            # figure out the ui title
            api_title = api_event
            api_obj = api_name + '.' + api_event

            cbox = Controls.CheckBox()
            cbox.Margin = Windows.Thickness(0, 10, 0, 0)
            cbox.FontFamily = Windows.Media.FontFamily("Consolas")
            cbox.IsChecked = False
            tblock = Controls.TextBlock()
            tblock.Margin = Windows.Thickness(0, 2, 0, 0)
            # if event does not have interesting telemetry data, hide from user
            if event_type in [EventType.AddInCommandBinding_BeforeExecuted,
                              EventType.AddInCommandBinding_CanExecute,
                              EventType.AddInCommandBinding_Executed,
                              EventType.Application_JournalUpdated]:
                cbox.IsEnabled = False
                cbox.Visibility = Windows.Visibility.Collapsed

            # if the event type is not supported in running revit, inform user
            elif event_type not in supportedEvents:
                cbox.IsEnabled = False
                tblock.Inlines.Add(Documents.Run(
                    "{}\n".format(' '.join(
                        coreutils.split_words(str(api_title))
                    ))))
                tblock.Inlines.Add(Documents.Run(
                    "Not Supported in this Revit Version\n"
                ))

            # if event is JournalCommandExecuted, create better user interface
            elif event_type == EventType.Application_JournalCommandExecuted:
                tblock.Inlines.Add(Documents.Run("Command Executed\n"))
                tblock.Inlines.Add(Documents.Run(
                    "Event Type:               journal-command-exec\n"
                    ))
                tblock.Inlines.Add(
                    Documents.Run(
                        "Tracks execution of commands from active "
                        "journal file. Includes:\n"))
                tblock.Inlines.Add(
                    Documents.Run(
                        "  Builtin Commands (e.g. ID_OBJECTS_WALL)\n"))
                tblock.Inlines.Add(
                    Documents.Run(
                        "  Thirdparty Commands (e.g. CustomCtrl_%CustomCtrl_"
                        "%Site Designer%Modify%Sidewalk)\n"))
                tblock.Inlines.Add(
                    Documents.Run(
                        "  pyRevit Commands (e.g. CustomCtrl_%CustomCtrl_"
                        "%pyRevit%pyRevit%Settings)\n"))

            # otherwise prepare the option for the event type
            elif event_type in supportedEvents:
                tblock.Inlines.Add(Documents.Run(
                    "{}\n".format(' '.join(
                        coreutils.split_words(str(api_title))
                    ))))
                tblock.Inlines.Add(Documents.Run(
                    "API Event Type:           "
                    ))
                hyperlink = Documents.Hyperlink(Documents.Run(api_obj + "\n"))
                hyperlink.NavigateUri = \
                    System.Uri(apidocs.make_event_uri(api_namespace + api_obj))
                hyperlink.Click += self.handle_url_click
                tblock.Inlines.Add(hyperlink)
                tblock.Inlines.Add(Documents.Run(
                    "pyRevit Event/Hook Name:  {}".format(
                        EventUtils.GetEventName(event_type)
                    )))
            cbox.Content = tblock
            self.event_telemetry_sp.Children.Add(cbox)

    def _setup_routes(self):
        self.routes_cb.IsChecked = user_config.routes_server
        self.coreapi_cb.IsChecked = user_config.load_core_api
        active_server = routes.get_active_server()
        if active_server:
            self.update_status_lights(
                {
                    "status": "pass",
                    "message": str(active_server)
                },
                self.routesserver_statusbox,
                self.routesserver_statusmsg
            )
            # setup example
            self.show_element(self.routes_exampleblock)
            self.routes_example.Text = \
                "GET http://{}:{}/routes/status".format(
                    coreutils.get_my_ip(),
                    user_config.routes_port
                )

    def _setup_telemetry(self):
        """Reads the pyRevit telemetry config and updates the ui"""
        self._setup_event_telemetry_checkboxes()

        self.telemetry_timestamp_cb.IsChecked = \
            telemetry.get_telemetry_utc_timestamp()
        self.telemetry_cb.IsChecked = telemetry.get_telemetry_state()
        self.cur_telemetryfile_tb.Text = \
            telemetry.get_telemetry_file_path()
        self.cur_telemetryfile_tb.IsReadOnly = True
        self.telemetryfile_tb.Text = \
            telemetry.get_telemetry_file_dir()
        self.telemetry_hooks_cb.IsChecked = \
            telemetry.get_telemetry_include_hooks()

        self.telemetryserver_tb.Text = \
            telemetry.get_telemetry_server_url()

        self.apptelemetry_cb.IsChecked = telemetry.get_apptelemetry_state()
        self.apptelemetryserver_tb.Text = \
            telemetry.get_apptelemetry_server_url()
        event_flags = telemetry.get_apptelemetry_event_flags()
        for event_checkbox, event_type in zip(
                self._get_event_telemetry_checkboxes(),
                telemetry.get_apptelemetry_event_types()):
            event_checkbox.IsChecked = \
                telemetry.get_apptelemetry_event_state(event_flags, event_type)

    def _make_product_name(self, product, note):
        return '_{} | {}({}) {}'.format(
            product.Name,
            product.BuildNumber,
            product.BuildTarget,
            note
            )

    def _setup_addinfiles(self):
        """Gets the installed Revit versions and sets up the ui"""
        installed_revits = \
            {str(x.ProductYear):x
             for x in TargetApps.Revit.RevitProduct.ListInstalledProducts()}
        attachments = \
            {str(x.Product.ProductYear):x
             for x in PyRevit.PyRevitAttachments.GetAttachments()}

        for rvt_ver, checkbox in self._addinfiles_cboxes.items():
            if rvt_ver in attachments:
                if rvt_ver != HOST_APP.version:
                    checkbox.Content = \
                        self._make_product_name(
                            attachments[rvt_ver].Product,
                            ''
                            )
                else:
                    checkbox.Content = \
                        self._make_product_name(
                            attachments[rvt_ver].Product,
                            '<current>'
                            )

                checkbox.IsChecked = True
                if attachments[rvt_ver].AttachmentType == \
                        PyRevit.PyRevitAttachmentType.AllUsers:
                    checkbox.IsEnabled = False
                    checkbox.Content += " <all users>"
                else:
                    checkbox.IsEnabled = True
            else:
                if rvt_ver in installed_revits:
                    checkbox.Content = \
                        self._make_product_name(
                            installed_revits[rvt_ver],
                            '<Not attached>'
                            )
                    checkbox.IsEnabled = True
                    checkbox.IsChecked = False
                else:
                    checkbox.Content = \
                        'Revit {} <Not installed>'.format(rvt_ver)
                    checkbox.IsEnabled = False
                    checkbox.IsChecked = False

    def is_same_version_as_running(self, version):
        return str(version) == EXEC_PARAMS.engine_ver

    def update_addinfiles(self):
        """Enables/Disables the adding files for different Revit versions."""
        # update active engine
        attachment = user_config.get_current_attachment()
        if attachment:
            # if attachment is for all users dont attempt at making changes
            # user probably does not have write access and this fails
            if attachment.AttachmentType == \
                    PyRevit.PyRevitAttachmentType.AllUsers:
                return

            # notify use to restart if engine has changed
            if self.availableEngines.SelectedItem:
                new_engine = self.availableEngines.SelectedItem.engine.Version
                if not self.is_same_version_as_running(new_engine):
                    forms.alert('Active engine has changed. '
                                'Restart Revit for this change to take effect.')
                # configure the engine on this version
                PyRevit.PyRevitAttachments.Attach(
                    int(HOST_APP.version),
                    attachment.Clone,
                    new_engine,
                    False
                    )

                # now setup the attachments for other versions
                for rvt_ver, checkbox in self._addinfiles_cboxes.items():
                    if checkbox.IsEnabled:
                        if checkbox.IsChecked:
                            PyRevit.PyRevitAttachments.Attach(
                                int(rvt_ver),
                                attachment.Clone,
                                new_engine,
                                False
                                )
                        else:
                            PyRevit.PyRevitAttachments.Detach(int(rvt_ver))
        else:
            logger.error('Error determining current attached clone.')

    def resetreportinglevel(self, sender, args):
        """Callback method for resetting logging levels to defaults"""
        self.verbose_rb.IsChecked = True
        self.noreporting_rb.IsChecked = False
        self.debug_rb.IsChecked = False
        self.filelogging_cb.IsChecked = False

    def reset_requiredhostbuild(self, sender, args):
        """Callback method for resetting requried host version to current"""
        self.requiredhostbuild_tb.Text = HOST_APP.build

    def resetcache(self, sender, args):
        """Callback method for resetting cache config to defaults"""
        self.bincache_rb.IsChecked = True

    def copy_envvar_value(self, sender, args):
        """Callback method for copying selected env var value to clipboard"""
        script.clipboard_copy(self.envvars_lb.SelectedItem.Value)

    def copy_envvar_id(self, sender, args):
        """Callback method for copying selected env var name to clipboard"""
        script.clipboard_copy(self.envvars_lb.SelectedItem.Id)

    def addfolder(self, sender, args):
        """Callback method for adding extension folder to configs and list"""
        new_path = forms.pick_folder(owner=self)
        if new_path:
            new_path = os.path.normpath(new_path)

        if self.extfolders_lb.ItemsSource:
            uniq_items = set(self.extfolders_lb.ItemsSource)
            uniq_items.add(new_path)
            self.extfolders_lb.ItemsSource = list(uniq_items)
        else:
            self.extfolders_lb.ItemsSource = [new_path]

    def removefolder(self, sender, args):
        """Callback method for removing extension folder from configs"""
        selected_path = self.extfolders_lb.SelectedItem
        if selected_path and self.extfolders_lb.ItemsSource:
            uniq_items = set(self.extfolders_lb.ItemsSource)
            uniq_items.remove(selected_path)
            self.extfolders_lb.ItemsSource = list(uniq_items)

    def removeallfolders(self, sender, args):
        """Callback method for removing all extension folders"""
        self.extfolders_lb.ItemsSource = []

    def openextfolder(self, sender, args):
        selected_path = self.extfolders_lb.SelectedItem
        if selected_path:
            script.show_file_in_explorer(selected_path)

    def pick_telemetry_folder(self, sender, args):
        """Callback method for picking destination folder for telemetry files"""
        new_path = forms.pick_folder(owner=self)
        if new_path:
            self.telemetryfile_tb.Text = os.path.normpath(new_path)

    def reset_telemetry_folder(self, sender, args):
        """Callback method for resetting telemetry file folder to defaults"""
        self.telemetryfile_tb.Text = telemetry.get_default_telemetry_filepath()

    def open_telemetry_folder(self, sender, args):
        """Callback method for opening destination folder for telemetry files"""
        cur_log_folder = op.dirname(self.cur_telemetryfile_tb.Text)
        if cur_log_folder:
            coreutils.open_folder_in_explorer(cur_log_folder)

    def validate_telemetry_url(self, urlbox):
        url = urlbox.Text
        if url and not url.endswith("/"):
            urlbox.Text = url + "/"

    def update_status_lights(self, status, serverbox, servermsg):
        """Update given status light by given status"""
        if status and status["status"] == "pass":
            serverbox.Background = self.Resources['pyRevitAccentBrush']
            custom_msg = status.get("message", None)
            servermsg.Text = ""
            if custom_msg:
                servermsg.Text = custom_msg
            else:
                for check, check_status in status["checks"].items():
                    servermsg.Text += \
                        u'\u2713 {} ({})'.format(
                            check,
                            check_status["version"]
                            )
            return
        serverbox.Background = self.Resources['pyRevitDarkBrush']
        servermsg.Text = "Unknown Status. Click Here to Test"

    def telemetryserver_changed(self, sender, args):
        """Reset telemetry server status light"""
        self.validate_telemetry_url(self.telemetryserver_tb)
        self.update_status_lights(
            None,
            self.telemetryserver_statusbox,
            self.telemetryserver_statusmsg
            )

    def apptelemetryserver_changed(self, sender, args):
        """Reset app telemetry server status light"""
        self.validate_telemetry_url(self.apptelemetryserver_tb)
        self.update_status_lights(
            None,
            self.apptelemetryserver_statusbox,
            self.apptelemetryserver_statusmsg
        )

    def update_telemetry_status(self, status):
        """Update telemetry server status light"""
        self.update_status_lights(
            status,
            self.telemetryserver_statusbox,
            self.telemetryserver_statusmsg
            )

    def update_apptelemetry_status(self, status):
        """Update app telemetry server status light"""
        self.update_status_lights(
            status,
            self.apptelemetryserver_statusbox,
            self.apptelemetryserver_statusmsg
            )

    def update_all_telemetry_status_lights(self):
        """Check the status of all telemetry servers and update status lights"""
        # test telemetry server status
        server_stat = \
            telemetry.get_status_from_url(
                telemetry.get_telemetry_server_url()
                )
        self.dispatch(self.update_telemetry_status, server_stat)
        # test telemetry app-server status
        appserver_status = \
            telemetry.get_status_from_url(
                telemetry.get_apptelemetry_server_url()
            )
        self.dispatch(self.update_apptelemetry_status, appserver_status)

    def update_telemetry_status_lights(self, sender, args):
        """Check the status of all telemetry servers"""
        self.dispatch(self.update_all_telemetry_status_lights)

    def update_telemetryserver_status_lights(self, sender, args):
        """Check the status of telemetry server"""
        status = telemetry.get_status_from_url(self.telemetryserver_tb.Text)
        self.update_telemetry_status(status)

    def update_apptelemetryserver_status_lights(self, sender, args):
        """Check the status of app telemetry server"""
        status = telemetry.get_status_from_url(self.apptelemetryserver_tb.Text)
        self.update_apptelemetry_status(status)

    def toggle_event_cbs(self, sender, args):
        for event_db in self._get_event_telemetry_checkboxes():
            event_db.IsChecked = not event_db.IsChecked

    def pick_stylesheet(self, sender, args):
        """Callback method for picking custom style sheet file"""
        new_stylesheet = forms.pick_file(file_ext='css')
        if new_stylesheet:
            self.cur_stylesheet_tb.Text = os.path.normpath(new_stylesheet)

    def reset_stylesheet(self, sender, args):
        """Callback method for resetting custom style sheet file"""
        self.cur_stylesheet_tb.Text = output.get_default_stylesheet()

    # tab styles
    def tabstyling_changed(self, sender, args):
        # update theme settings
        self.tab_theme.SortDocTabs = self.sortdocs_cb.IsChecked
        if self.project_tabstyle_cb.SelectedItem:
            tabs.update_tabstyle(
                self.tab_theme, self.project_tabstyle_cb.SelectedItem
                )
        if self.family_tabstyle_cb.SelectedItem:
            tabs.update_family_tabstyle(
                self.tab_theme, self.family_tabstyle_cb.SelectedItem
                )
        # refresh previews
        self.update_tab_previews()

    def prompt_for_color(self, default=None):
        color = forms.ask_for_color(default=default or "#FF000000")
        if color and color.lower() != "#ffffffff":
            return color

    # project order and filter colors
    def add_ordercolor(self, sender, args):
        color = self.prompt_for_color()
        if color:
            tabs.add_tab_orderrule(self.tab_theme, color)
            self.doc_ordercolor_lb.ItemsSource = \
                list(self.tab_theme.TabOrderRules)
            self.update_tab_previews()

    def remove_ordercolor(self, sender, args):
        selected_ordercolor_idx = self.doc_ordercolor_lb.SelectedIndex
        if selected_ordercolor_idx >= 0:
            tabs.remove_tab_orderrule(self.tab_theme, selected_ordercolor_idx)
            self.doc_ordercolor_lb.ItemsSource = \
                list(self.tab_theme.TabOrderRules)
            new_count = len(self.tab_theme.TabOrderRules)
            new_index = \
                selected_ordercolor_idx \
                    if selected_ordercolor_idx < new_count else (new_count - 1)
            self.doc_ordercolor_lb.SelectedIndex = new_index
            self.update_tab_previews()

    def reset_ordercolors(self, sender, args):
        tabs.reset_tab_ordercolors(user_config, self.tab_theme)
        new_rules = list(self.tab_theme.TabOrderRules)
        if new_rules:
            self.doc_ordercolor_lb.ItemsSource = new_rules
            self.update_tab_previews()

    def selected_ordercolor_changed(self, sender, args):
        pass

    def doc_ordercolor_changecolor(self, sender, args):
        selected_ordercolor_idx = self.doc_ordercolor_lb.SelectedIndex
        if selected_ordercolor_idx >= 0:
            rule_color = \
                tabs.get_tab_orderrule(self.tab_theme, selected_ordercolor_idx)
            new_color = self.prompt_for_color(rule_color)
            if new_color:
                tabs.update_tab_orderrule(
                    self.tab_theme,
                    selected_ordercolor_idx,
                    new_color
                    )
            self.doc_ordercolor_lb.ItemsSource = \
                list(self.tab_theme.TabOrderRules)
            self.update_tab_previews()

    def add_filtercolor(self, sender, args):
        color = self.prompt_for_color()
        if color:
            tabs.add_tab_filterrule(
                self.tab_theme,
                color,
                "Project %s" % self.filtercolor_counter
                )
            self.doc_filtercolor_lb.ItemsSource = \
                list(self.tab_theme.TabFilterRules)
            self.filtercolor_counter += 1
            self.update_tab_previews()

    def remove_filtercolor(self, sender, args):
        selected_filtercolor_idx = self.doc_filtercolor_lb.SelectedIndex
        if selected_filtercolor_idx >= 0:
            tabs.remove_tab_filterrule(
                self.tab_theme,
                selected_filtercolor_idx
                )
            self.doc_filtercolor_lb.ItemsSource = \
                list(self.tab_theme.TabFilterRules)
            new_count = len(self.tab_theme.TabFilterRules)
            new_index = \
                selected_filtercolor_idx \
                    if selected_filtercolor_idx < new_count else (new_count - 1)
            self.doc_filtercolor_lb.SelectedIndex = new_index
            # updateing filter text will trigger a preview
            self.filtercolor_filter_tb.Text = ""

    def selected_filtercolor_changed(self, sender, args):
        selected_filtercolor_idx = self.doc_filtercolor_lb.SelectedIndex
        if selected_filtercolor_idx >= 0:
            _, rule_title_filter = \
                tabs.get_tab_filterrule(self.tab_theme,
                                         selected_filtercolor_idx)
            self.filtercolor_filter_tb.Text = rule_title_filter

    def filtercolor_filter_changed(self, sender, args):
        self.hide_element(self.filtercolor_filter_warn)
        selected_filtercolor_idx = self.doc_filtercolor_lb.SelectedIndex
        if selected_filtercolor_idx >= 0:
            try:
                re.compile(self.filtercolor_filter_tb.Text)
                tabs.update_tab_filterrule(
                    self.tab_theme,
                    selected_filtercolor_idx,
                    title_filter=self.filtercolor_filter_tb.Text
                    )
                self.update_tab_previews()
            except Exception:
                self.show_element(self.filtercolor_filter_warn)

    def doc_filtercolor_changecolor(self, sender, args):
        selected_filtercolor_idx = self.doc_filtercolor_lb.SelectedIndex
        if selected_filtercolor_idx >= 0:
            rule_color, _ = \
                tabs.get_tab_filterrule(self.tab_theme,
                                         selected_filtercolor_idx)
            color = self.prompt_for_color(rule_color)
            if color:
                tabs.update_tab_filterrule(
                    self.tab_theme,
                    selected_filtercolor_idx,
                    color=color
                    )
            self.doc_filtercolor_lb.ItemsSource = \
                list(self.tab_theme.TabFilterRules)
            self.update_tab_previews()

    # tab previews
    def update_tab_previews(self):
        coloring_rules = list(self.doc_ordercolor_lb.ItemsSource)
        coloring_rules_count = len(coloring_rules)
        # project preview controls
        prj_tab_ctrls = [self.tabProjA, self.tabProjB]
        # project preview controls
        family_tab_ctrls = [self.tabFamilyA, self.tabFamilyB]

        # current project tab style
        prj_tabstyle = self.project_tabstyle_cb.SelectedItem
        if prj_tabstyle:

            # reset all
            for tab_ctrl in prj_tab_ctrls:
                tab_ctrl.Style = self.Resources["revitTab"]

            # apply by order - project
            for idx, tab_ctrl in enumerate(prj_tab_ctrls):
                if idx < coloring_rules_count:
                    coloring_rule = coloring_rules[idx]
                    style = prj_tabstyle.CreateStyle(tab_ctrl, coloring_rule)
                    tab_ctrl.Style = style

        # current project tab style
        family_tabstyle = self.family_tabstyle_cb.SelectedItem
        if family_tabstyle:

            # reset all
            for tab_ctrl in family_tab_ctrls:
                tab_ctrl.Style = self.Resources["revitTab"]

            # apply by order - project
            for idx, tab_ctrl in enumerate(family_tab_ctrls):
                if idx + len(prj_tab_ctrls) < coloring_rules_count:
                    coloring_rule = coloring_rules[idx + len(prj_tab_ctrls)]
                    style = family_tabstyle.CreateStyle(tab_ctrl, coloring_rule)
                    tab_ctrl.Style = style

    # save configs
    def _save_core_options(self):
        # update the logging system changes first and update.
        user_config.bin_cache = self.bincache_rb.IsChecked

        # set config values to values set in ui items
        user_config.check_updates = self.checkupdates_cb.IsChecked

        user_config.rocket_mode = self.rocketmode_cb.IsChecked

        if self.verbose_rb.IsChecked:
            logger.set_verbose_mode()
        if self.debug_rb.IsChecked:
            logger.set_debug_mode()

        if self.noreporting_rb.IsChecked:
            user_config.log_level = PyRevit.PyRevitLogLevels.Quiet
        elif self.verbose_rb.IsChecked:
            user_config.log_level = PyRevit.PyRevitLogLevels.Verbose
        elif self.debug_rb.IsChecked:
            user_config.log_level = PyRevit.PyRevitLogLevels.Debug

        user_config.file_logging = self.filelogging_cb.IsChecked
        user_config.startuplog_timeout = int(self.startup_log_timeout.Text)
        user_config.required_host_build = self.requiredhostbuild_tb.Text
        try:
            min_freespace = int(self.minhostdrivefreespace_tb.Text)
            user_config.min_host_drivefreespace = min_freespace
        except ValueError:
            logger.error('Minimum free space value must be an integer.')
            user_config.min_host_drivefreespace = 0

        user_config.load_beta = self.loadbetatools_cb.IsChecked

    def _save_engines(self):
        # set active cpython engine
        engine_cfg = self.cpythonEngines.SelectedItem
        if engine_cfg:
            user_config.set_active_cpython_engine(engine_cfg.engine)
            if self.active_cpyengine.Version != engine_cfg.engine.Version \
                    and not self.reload_requested:
                forms.alert('Active CPython engine has changed. '
                            'Restart Revit for this change to take effect.')

    def _save_user_extensions_list(self):
        # set extension folders from the list, after cleanup empty items
        if isinstance(self.extfolders_lb.ItemsSource, list):
            user_config.set_thirdparty_ext_root_dirs(
                coreutils.filter_null_items(self.extfolders_lb.ItemsSource)
            )
        else:
            user_config.set_thirdparty_ext_root_dirs([])

    def _save_uiux(self):
        request_reload = False
        current_applocale = applocales.get_current_applocale()
        if self.applocales_cb.SelectedItem:
            for applocale in applocales.APP_LOCALES:
                if str(applocale) == self.applocales_cb.SelectedItem:
                    user_config.user_locale = applocale.locale_code
                    if current_applocale != applocale \
                            and not self.reload_requested:
                        request_reload = forms.alert(
                            'UI language has changed. Reloading pyRevit is '
                            'required for this change to take effect. Do you '
                            'want to reload now?', yes=True, no=True)
        # colorize docs
        user_config.colorize_docs = self.colordocs_cb.IsChecked

        # save colorize theme
        tabs.set_tabcoloring_theme(user_config, self.tab_theme)
        tabs.init_doc_colorizer(user_config)

        # output settings
        output.set_stylesheet(self.cur_stylesheet_tb.Text)
        default_stylesheet = output.get_default_stylesheet()
        if self.cur_stylesheet_tb.Text != default_stylesheet:
            user_config.output_stylesheet = self.cur_stylesheet_tb.Text
        elif user_config.output_stylesheet != default_stylesheet:
            user_config.output_stylesheet = None
        # pyrevit gui settings
        if self.loadtooltipex_cb.IsChecked != user_config.tooltip_debug_info \
                and not self.reload_requested:
            request_reload = forms.alert(
                'pyRevit UI Configuration has changed. Reloading pyRevit is '
                'required for this change to take effect. Do you '
                'want to reload now?', yes=True, no=True)
        user_config.tooltip_debug_info = self.loadtooltipex_cb.IsChecked

        return request_reload

    def _save_routes(self):
        request_reload = False

        # decide to turn off or on
        if self.routes_cb.IsChecked:
            if not user_config.routes_server:
                request_reload = forms.alert(
                    'Routes server setting has changed. '
                    'Reloading pyRevit is required for this change to take '
                    'effect. Do you want to reload now?', yes=True, no=True)
        else:
            routes.deactivate_server()

        if user_config.load_core_api != self.coreapi_cb.IsChecked \
                and not request_reload:
            request_reload = forms.alert(
                'pyRevit Core REST API setting has changed. '
                'Reloading pyRevit is required for this change to take effect. '
                'Do you want to reload now?', yes=True, no=True)

        # save configs
        user_config.routes_server = self.routes_cb.IsChecked
        user_config.load_core_api = self.coreapi_cb.IsChecked

        return request_reload

    def _save_telemetry(self):
        # set telemetry configs
        # pyrevit telemetry
        telemetry.set_telemetry_utc_timestamp(
            self.telemetry_timestamp_cb.IsChecked)
        telemetry.set_telemetry_state(self.telemetry_cb.IsChecked)
        telemetry.set_telemetry_file_dir(self.telemetryfile_tb.Text)
        telemetry.set_telemetry_server_url(self.telemetryserver_tb.Text)
        telemetry.set_telemetry_include_hooks(self.telemetry_hooks_cb.IsChecked)
        # host app telemetry
        telemetry.set_apptelemetry_state(self.apptelemetry_cb.IsChecked)
        telemetry.set_apptelemetry_server_url(self.apptelemetryserver_tb.Text)

        event_flags = telemetry.get_apptelemetry_event_flags()
        for event_checkbox, event_type in zip(
                self._get_event_telemetry_checkboxes(),
                telemetry.get_apptelemetry_event_types()):
            if event_checkbox.IsChecked:
                event_flags = telemetry.set_apptelemetry_event_state(
                    event_flags,
                    event_type
                    )
            else:
                event_flags = telemetry.unset_apptelemetry_event_state(
                    event_flags,
                    event_type
                    )
        telemetry.set_apptelemetry_event_flags(event_flags)
        telemetry.setup_telemetry()

    def _reload(self):
        from pyrevit.loader.sessionmgr import execute_command #pylint: disable=import-outside-toplevel
        execute_command(pyrevitcore_globals.PYREVIT_CORE_RELOAD_COMMAND_NAME)

    def save_settings(self, sender, args):
        """Callback method for saving pyRevit settings"""
        self.reload_requested = \
            self._save_core_options() or self.reload_requested
        self.reload_requested = \
            self._save_engines() or self.reload_requested
        self.reload_requested = \
            self._save_user_extensions_list() or self.reload_requested
        self.reload_requested = \
            self._save_uiux() or self.reload_requested
        self.reload_requested = \
            self._save_routes() or self.reload_requested
        self.reload_requested = \
            self._save_telemetry() or self.reload_requested

        # save all new values into config file
        user_config.save_changes()

        # update addin files
        self.update_addinfiles()
        self.Close()
        # if reload requested by any of the save methods, then reload
        if self.reload_requested:
            self._reload()

    def save_settings_and_reload(self, sender, args):
        """Callback method for saving pyRevit settings and reloading"""
        self.reload_requested = True
        self.save_settings(sender, args)


# decide if the settings should load or not
def __selfinit__(script_cmp, ui_button_cmp, __rvt__):
    # do not load the tool if user should not config
    if not user_config.user_can_config:
        return False

# handles tool click in Revit interface:
# if Shift-Click on the tool, opens the pyRevit config file in
# windows explorer
# otherwise, will show the Settings user interface
if __name__ == '__main__':
    if __shiftclick__:  #pylint: disable=E0602
        script.show_file_in_explorer(user_config.config_file)
    else:
        SettingsWindow('SettingsWindow.xaml').show_dialog()
