# Speed control and staged homing for Z axis on Flashforge AD5M
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
from . import homing


_ORIG_DO_HOME_RAILS = getattr(homing.Homing, '_orig_do_home_rails', homing.Homing._do_home_rails)
homing.Homing._orig_do_home_rails = _ORIG_DO_HOME_RAILS


class ZSpeedControl:
    def __init__(self, config):
        self.printer = config.get_printer()
        self.slow_speed = config.getfloat('slow_speed', 10.0, above=0.)
        self.fast_speed = config.getfloat('fast_speed', 40.0, above=0.)
        self.nozzle_clearance = config.getfloat('nozzle_clearance', 15.0, above=0.)
        self.bottom_margin = config.getfloat('bottom_margin', 10.0, above=0.)

        self.toolhead = None
        self.z_max = 220.929
        self.in_homing = False
        self.orig_th_move = None
        self.orig_check_move = None
        self.orig_do_home_rails = None

        self.printer.register_event_handler('klippy:connect', self._connect)

    def _connect(self):
        self.toolhead = self.printer.lookup_object('toolhead')

        kin = self.toolhead.get_kinematics()
        z_rail = None
        for rail in getattr(kin, 'rails', []):
            for s in rail.get_steppers():
                if s.get_name() == 'stepper_z':
                    z_rail = rail
                    break
            if z_rail is not None:
                break

        if z_rail is not None:
            pos_min, pos_max = z_rail.get_range()
            self.z_max = pos_max
        elif hasattr(kin, 'axes_max') and len(kin.axes_max) > 2:
            self.z_max = kin.axes_max[2]

        # Wrap kin.check_move to enforce zone-based speed limits
        self.orig_check_move = kin.check_move
        kin.check_move = self._check_move

        # Wrap toolhead.move to split moves crossing zone boundaries
        self.orig_th_move = self.toolhead.move
        self.toolhead.move = self._toolhead_move

        # Wrap homing.Homing._do_home_rails for staged Z homing
        self.orig_do_home_rails = _ORIG_DO_HOME_RAILS
        ctrl = self
        def home_rails_wrapper(homing_state, rails, forcepos, movepos):
            return ctrl._custom_do_home_rails(homing_state, rails, forcepos, movepos)
        homing.Homing._do_home_rails = home_rails_wrapper

        logging.info(
            "z_speed_control: active (slow=%.1f fast=%.1f clearance=%.1f "
            "bottom_margin=%.1f z_max=%.3f)",
            self.slow_speed, self.fast_speed, self.nozzle_clearance,
            self.bottom_margin, self.z_max)

    def _check_move(self, move):
        kin = self.toolhead.get_kinematics()
        limits = kin.limits
        xpos, ypos = move.end_pos[:2]
        if (xpos < limits[0][0] or xpos > limits[0][1]
                or ypos < limits[1][0] or ypos > limits[1][1]):
            kin._check_endstops(move)
        if not move.axes_d[2]:
            return
        kin._check_endstops(move)

        if self.in_homing:
            # During staged homing, each stage passes its own explicit speed
            z_ratio = move.move_d / abs(move.axes_d[2])
            move.limit_speed(kin.max_z_velocity * z_ratio, kin.max_z_accel * z_ratio)
            return

        z_start = move.start_pos[2]
        z_end = move.end_pos[2]
        z_min = min(z_start, z_end)
        z_max = max(z_start, z_end)

        z_top_limit = self.nozzle_clearance
        z_bot_limit = self.z_max - self.bottom_margin

        if z_min < (z_top_limit - 0.001) or z_max > (z_bot_limit + 0.001):
            target_v = self.slow_speed
        else:
            target_v = self.fast_speed

        z_ratio = move.move_d / abs(move.axes_d[2])
        move.limit_speed(target_v * z_ratio, kin.max_z_accel * z_ratio)

    def _toolhead_move(self, newpos, speed):
        if self.in_homing:
            return self.orig_th_move(newpos, speed)

        kin = self.toolhead.get_kinematics()
        if kin.limits[2][0] > kin.limits[2][1]:
            # Z axis not homed yet; pass through to let check_move raise error
            return self.orig_th_move(newpos, speed)

        startpos = list(self.toolhead.commanded_pos)
        start_z = startpos[2]
        end_z = newpos[2]
        dz = end_z - start_z

        if abs(dz) < 0.0001:
            return self.orig_th_move(newpos, speed)

        z_low = self.nozzle_clearance
        z_high = self.z_max - self.bottom_margin

        if dz > 0:
            splits = [b for b in (z_low, z_high)
                      if (start_z + 0.001) < b < (end_z - 0.001)]
        else:
            splits = [b for b in (z_high, z_low)
                      if (end_z + 0.001) < b < (start_z - 0.001)]

        if not splits:
            return self.orig_th_move(newpos, speed)

        for sz in splits:
            t = (sz - start_z) / dz
            midpos = [s + t * (e - s) for s, e in zip(startpos, newpos)]
            midpos[2] = sz
            self.orig_th_move(midpos, speed)

        self.orig_th_move(newpos, speed)

    def _custom_do_home_rails(self, homing_state, rails, forcepos, movepos):
        is_z = any(s.get_name() == 'stepper_z'
                   for r in rails for s in r.get_steppers())
        if not is_z or forcepos[2] is None:
            return self.orig_do_home_rails(homing_state, rails, forcepos, movepos)

        reactor = self.printer.get_reactor()
        eventtime = reactor.monotonic()
        th_status = self.toolhead.get_status(eventtime)
        was_homed = ('z' in th_status['homed_axes'])
        if not was_homed:
            # The physical starting height is unknown after restart/motor-off.
            # Use native endstop homing at the configured homing speed; a
            # distance travelled from an unknown start cannot identify zones.
            # Bypass ordinary move splitting during native homing as well.
            self.in_homing = True
            try:
                return self.orig_do_home_rails(
                    homing_state, rails, forcepos, movepos)
            finally:
                self.in_homing = False

        prior_z = self.toolhead.get_position()[2]
        homing_state.printer.send_event("homing:home_rails_begin", homing_state, rails)
        homepos = homing_state._fill_coord(movepos)

        # Set axis limits as homed for the duration of homing moves
        homing_state._set_start_position(forcepos)

        endstops = [es for rail in rails for es in rail.get_endstops()]
        homing_info = rails[0].get_homing_info()

        z_endstop = homepos[2]
        z_slow_top = self.nozzle_clearance
        z_slow_bottom = z_endstop - self.bottom_margin

        cur_z = max(0.0, prior_z)
        d1 = max(0.0, min(z_slow_top - cur_z, z_endstop - cur_z))
        d2 = max(0.0, min(z_slow_bottom - max(cur_z, z_slow_top),
                          z_endstop - cur_z - d1))
        d3 = max(15.0, (z_endstop - cur_z - d1 - d2) + 10.0)

        last_hmove = None
        triggered = False

        def run_stage(dist, speed, check_trig=False):
            nonlocal last_hmove, triggered
            if dist <= 0.001 or triggered:
                return
            # Position start relative to homepos so target is always homepos (in range)
            stage_start = list(homepos)
            stage_start[2] = homepos[2] - dist
            homing_state.toolhead.set_position(stage_start)

            hmove = homing.HomingMove(homing_state.printer, endstops)
            last_hmove = hmove

            trig_flags = []
            orig_waits = []
            for es, name in hmove.endstops:
                orig_wait = es.home_wait
                orig_waits.append((es, orig_wait))

                def make_wrapper(orig_w):
                    def wrapped_wait(m_time):
                        t = orig_w(m_time)
                        if t > 0.:
                            trig_flags.append(True)
                        return t
                    return wrapped_wait

                es.home_wait = make_wrapper(orig_wait)

            try:
                hmove.homing_move(homepos, speed, check_triggered=check_trig)
            finally:
                for es, orig_wait in orig_waits:
                    es.home_wait = orig_wait

            if trig_flags:
                triggered = True

        self.in_homing = True
        try:
            # Stage 1: Slow speed clearance near nozzle (10 mm/s)
            run_stage(d1, self.slow_speed, check_trig=False)

            # Stage 2: Fast travel across middle (25 mm/s)
            if not triggered:
                run_stage(d2, self.fast_speed, check_trig=False)

            # Stage 3: Slow approach to endstop for final 10 mm (10 mm/s)
            if not triggered:
                run_stage(d3, self.slow_speed, check_trig=True)

            # Perform second home if retract_dist is configured
            if homing_info.retract_dist:
                homepos = homing_state._retract_move(homing_info, forcepos, movepos)
                hmove = homing.HomingMove(homing_state.printer, endstops)
                hmove.homing_move(homepos, homing_info.second_homing_speed)
                if hmove.check_no_movement() is not None:
                    raise homing_state.printer.command_error(
                        "Endstop %s still triggered after retract"
                        % (hmove.check_no_movement(),))
                last_hmove = hmove
        finally:
            self.in_homing = False

        # Signal home operation complete
        homing_state.toolhead.flush_step_generation()
        homing_state.trigger_mcu_pos = {sp.stepper_name: sp.trig_pos
                                        for sp in last_hmove.stepper_positions}
        homing_state.adjust_pos = {}
        homing_state.printer.send_event("homing:home_rails_end", homing_state, rails)
        if any(homing_state.adjust_pos.values()):
            kin = homing_state.toolhead.get_kinematics()
            homepos = homing_state.toolhead.get_position()
            kin_spos = {s.get_name(): (s.get_commanded_position()
                                       + homing_state.adjust_pos.get(s.get_name(), 0.))
                        for s in kin.get_steppers()}
            newpos = kin.calc_position(kin_spos)
            for axis in range(3):
                if forcepos[axis] is not None:
                    if newpos[axis] is None:
                        raise homing_state.printer.command_error(
                            "Cannot determine position of toolhead on "
                            "axis %s after homing" % "xyz"[axis])
                    homepos[axis] = newpos[axis]
            homing_state.toolhead.set_position(homepos)


def load_config(config):
    return ZSpeedControl(config)
