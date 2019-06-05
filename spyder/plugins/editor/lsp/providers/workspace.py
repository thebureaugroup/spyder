# -*- coding: utf-8 -*-

# Copyright © Spyder Project Contributors
# Licensed under the terms of the MIT License
# (see spyder/__init__.py for details)

"""Spyder Language Server Protocol Client workspace handler routines."""

import logging

from spyder.plugins.editor.lsp.providers.utils import path_as_uri
from spyder.plugins.editor.lsp import LSPRequestTypes, ClientConstants
from spyder.plugins.editor.lsp.decorators import (
    handles, send_request, send_response, send_notification)

logger = logging.getLogger(__name__)


class WorkspaceProvider:
    @send_notification(method=LSPRequestTypes.WORKSPACE_CONFIGURATION_CHANGE)
    def send_plugin_configurations(self, configurations, *args):
        self.plugin_configurations = configurations
        params = {
            'settings': configurations
        }
        return params

    @handles(LSPRequestTypes.WORKSPACE_FOLDERS)
    @send_notification(method=LSPRequestTypes.WORKSPACE_FOLDERS)
    def send_workspace_folders(self, response):
        workspace_folders = []
        for folder_name in self.watched_folders:
            folder_uri = self.watched_folders[folder_name]
            workspace_folders.append({
                'uri': folder_uri,
                'name': folder_name
            })
        return workspace_folders

    @send_notification(method=LSPRequestTypes.WORKSPACE_FOLDERS_CHANGE)
    def send_workspace_folders_change(self, params):
        folder = params['folder']
        folder_uri = path_as_uri(folder)
        added_folders = []
        removed_folders = []
        if params['addition']:
            if folder not in self.watched_folders:
                self.watched_folders[folder] = folder_uri
                added_folders.append({
                    'uri': folder_uri,
                    'name': folder
                })
        elif params['deletion']:
            if folder not in self.watched_folders:
                self.watched_folders.pop(folder)
                removed_folders.append({
                    'uri': folder_uri,
                    'name': folder
                })
        workspace_settings = self.server_capabilites['workspace']
        request_params = {
            'added': added_folders,
            'removed': removed_folders
        }
        if not workspace_settings['workspaceFolders']['supported']:
            request_params[ClientConstants.CANCEL] = True
        return request_params

    @handles(LSPRequestTypes.WORKSPACE_CONFIGURATION)
    @send_response
    def send_workspace_configuration(self, params):
        logger.debug(params)
        return self.plugin_configurations
