# Two-stage approach for the AD5M nozzle-contact probe.
# Uses the installed Klipper probe/homing interfaces; no upstream file changes.
# SPDX-License-Identifier: GPL-3.0-or-later
from . import homing


class TwoStageProbe:
    def __init__(self, config):
        self.printer = config.get_printer()
        self.approach_speed = config.getfloat('approach_speed', 10., above=0.)
        self.slow_distance = config.getfloat('slow_distance', 1., minval=1.)
        self.clearance = config.getfloat('clearance', 3., above=0.)
        self.reference_z = None
        self.printer.register_event_handler('klippy:connect', self._connect)

    def _connect(self):
        probe = self.printer.lookup_object('probe')
        wrapper = getattr(probe, 'mcu_probe', None)
        helper = getattr(wrapper, 'homing_helper', None)
        if helper is None or not hasattr(helper, 'descend_until_trigger'):
            raise self.printer.config_error(
                'two_stage_probe requires the standard endstop-based probe')
        self.wrapper = wrapper
        self.helper = helper
        self.original_start = wrapper.start_probe_session
        self.original_descend = helper.descend_until_trigger
        # SampleAveragingHelper already holds a bound start callback: replace
        # that callback as well as the public wrapper entry point.
        wrapper.start_probe_session = self._start_session
        probe.probe_session.start_session_cb = self._start_session
        helper.descend_until_trigger = self._descend

    def _start_session(self, gcmd):
        self.reference_z = None
        return self.original_start(gcmd)

    def _descend(self, gcmd):
        toolhead = self.printer.lookup_object('toolhead')
        pos = list(toolhead.get_position())
        eventtime = self.printer.get_reactor().monotonic()
        if 'z' not in toolhead.get_status(eventtime)['homed_axes']:
            raise gcmd.error('Must home before two-stage probing')
        if self.reference_z is not None:
            target_z = self.reference_z + self.slow_distance
            if pos[2] > target_z + .01:
                print_time = toolhead.get_last_move_time()
                if self.wrapper.query_endstop(print_time):
                    raise gcmd.error('Probe already triggered before approach')
                pos[2] = target_z
                zmax = toolhead.get_kinematics().max_z_velocity
                speed = min(self.approach_speed, zmax)
                # Endstop remains armed. A trigger before the slow zone stops
                # the approach and aborts; it is never accepted as a sample.
                move = homing.HomingMove(
                    self.printer, [(self.helper.mcu_probe, 'probe')])
                move.homing_move(pos, speed, probe_pos=True,
                                 check_triggered=False)
                now = list(toolhead.get_position())
                if (now[2] > target_z + .005
                        or self.wrapper.query_endstop(
                            toolhead.get_last_move_time())):
                    now[2] += self.clearance
                    toolhead.manual_move(now, speed)
                    raise gcmd.error(
                        'Probe triggered during fast approach; lowered bed '
                        'clearance and stopped. Check plate/nozzle/Z reference.')
        # Original code retains the configured slow speed, sampling, MCU
        # trigger position, offset handling and no-trigger errors.
        self.original_descend(gcmd)
        contact_z = self.helper.results[-1].test_z
        if contact_z > self.clearance - self.slow_distance:
            now = list(toolhead.get_position())
            now[2] += self.clearance
            toolhead.manual_move(now, min(self.approach_speed,
                toolhead.get_kinematics().max_z_velocity))
            raise gcmd.error('Contact height leaves insufficient mesh clearance; '
                             'check Z reference before continuing')
        self.reference_z = (contact_z if self.reference_z is None
                            else max(self.reference_z, contact_z))


def load_config(config):
    return TwoStageProbe(config)
