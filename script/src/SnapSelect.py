from __future__ import with_statement
from typing import List

import Live
from _Framework.ControlSurface import ControlSurface
from .DeviceSelectButton import DeviceSelectButton
from .SnapSelectButton import SnapSelectButton

from .mappings import *
from .enums import *


class SnapSelect(ControlSurface):
    __module__ = __name__
    __doc__ = "SnapSelect"

    def __init__(self, c_instance):
        ControlSurface.__init__(self, c_instance)
        with self.component_guard():
            self.log_message("Init")
            live = Live.Application.get_application()
            self._live_major_version = live.get_major_version()
            self._live_minor_version = live.get_minor_version()
            self._live_bugfix_version = live.get_bugfix_version()

            self.devices_with_snaps()

            self.device_select_button = DeviceSelectButton(
                channel=CHANNEL,
                identifier=DEVICE_SELECT_BUTTON,
                next_device=self.next_device,
                log=self.log_message,
            )

            self.snap_select_button = SnapSelectButton(
                channel=CHANNEL, identifier=SNAP_SELECT_BUTTON, log=self.log_message
            )

    def song(self) -> Live.Song.Song:
        return super().song()

    def song_view(self) -> Live.Song.Song.View:
        return self.song().view

    def tracks(self) -> List[Live.Track.Track]:
        return self.song().tracks

    def get_appointed_device(self) -> Live.Device.Device:
        return self.song().appointed_device

    def set_appointed_device(self, device: Live.Device.Device) -> None:
        self.song().appointed_device = device

    def devices_with_snaps(self) -> List[Live.Device.Device]:
        devices_with_snaps = []

        for track in self.tracks():
            devices = track.devices

            for device in devices:
                if (
                    isinstance(device, Live.RackDevice.RackDevice)
                    and device.variation_count > 0
                ):
                    devices_with_snaps.append(device)

        return devices_with_snaps

    def set_device(self, device: Live.Device.Device) -> None:
        song = self.song()
        song.view.select_device(device)
        song.view.selected_track = device.canonical_parent

    def next_device(self) -> None:
        # if any device is the appointed device
        devices = self.devices_with_snaps()
        try:
            index = devices.index(self.get_appointed_device())
            if index + 1 == len(devices):
                self.set_device(devices[0])
            else:
                self.set_device(devices[index + 1])

        except ValueError:
            self.set_device(devices[0])

    def disconnect(self):
        """clean up on disconnect"""
        ControlSurface.disconnect(self)
        return None
