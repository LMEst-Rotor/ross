import numpy as np
from scipy.signal import argrelextrema

from ross.rotor_assembly import Rotor, rotor_example
from ross.bearing_seal_element import BearingElement
import ross as rs

import bokeh.palettes as bp
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, HoverTool, Span, Label

# set bokeh palette of colors
bokeh_colors = bp.RdGy[11]


class Report:
    def __init__(self, rotor, minspeed, maxspeed, speed_units="rpm"):
        """Report according to standard analysis.

        - Perform Stability_level1 analysis
        - Apply Level 1 Screening Criteria
        - Perform Stability_level2 analysis

        Parameters
        ----------
        rotor : object
            A rotor built from rotor_assembly.
        maxspeed : float
            Maximum operation speed.
        minspeed : float
            Minimum operation speed.
        speed_units : str
            String defining the unit for rotor speed.
            Default is "rpm".

        Attributes
        ----------
        rotor_type : str
            Defines if the rotor is between bearings or overhung

        Return
        ------

        Example
        -------
        >>> rotor = rotor_example()
        >>> report = Report(rotor=rotor,
        ...                 minspeed=400,
        ...                 maxspeed=1000,
        ...                 speed_units="rad/s")
        """
        self.rotor = rotor
        self.speed_units = speed_units

        if speed_units == "rpm":
            minspeed = minspeed * np.pi / 30
            maxspeed = maxspeed * np.pi / 30

        # check if rotor is between bearings, single or double overhung
        # fmt: off
        if(
            all(i > min(rotor.df_bearings["n"]) for i in rotor.df_disks["n"]) and
            all(i < max(rotor.df_bearings["n"]) for i in rotor.df_disks["n"])
        ):
            rotor_type = "between_bearings"
        elif(
            any(i < min(rotor.df_bearings["n"]) for i in rotor.df_disks["n"]) and
            all(i < max(rotor.df_bearings["n"]) for i in rotor.df_disks["n"])
        ):
            rotor_type = "left_overhung"
        elif(
            all(i > min(rotor.df_bearings["n"]) for i in rotor.df_disks["n"]) and
            any(i > max(rotor.df_bearings["n"]) for i in rotor.df_disks["n"])
        ):
            rotor_type = "right_overhung"
        elif(
            any(i < min(rotor.df_bearings["n"]) for i in rotor.df_disks["n"]) and
            any(i > max(rotor.df_bearings["n"]) for i in rotor.df_disks["n"])
        ):
            rotor_type = "double_overhung"
        # fmt: on

        self.rotor_type = rotor_type

        self.maxspeed = maxspeed
        self.minspeed = minspeed

    @classmethod
    def from_saved_rotors(cls, path, minspeed, maxspeed, speed_units="rpm"):
        """Instantiate a rotor from a previously saved rotor model

        Parameters
        ----------
        path : str
            File name
        maxspeed : float
            Maximum operation speed.
        minspeed : float
            Minimum operation speed.
        speed_units : str
            String defining the unit for rotor speed.
            Default is "rpm".

        Returns
        -------
        Report : obj
            A report object based on the rotor loaded

        Examples
        --------
        >>> rotor = rotor_example()
        >>> rotor.save('rotor_example')
        >>> report = Report.from_saved_rotors(
        ...     path='rotor_example', minspeed=400, maxspeed=1000, speed_units="rad/s"
        ... )
        >>> Rotor.remove('rotor_example')
        """
        rotor = rs.Rotor.load(path)
        return cls(rotor, minspeed, maxspeed, speed_units="rpm")

    def static_forces(self):
        """Method to calculate the bearing reaction forces.

        Parameters
        ----------

        Returns
        -------
        Fb : list
            Bearing reaction forces.

        Example
        -------
        >>> rotor = rotor_example()
        >>> report = Report(rotor=rotor,
        ...                 minspeed=400,
        ...                 maxspeed=1000,
        ...                 speed_units="rad/s")
        >>> report.static_forces()
        array([44.09320349, 44.09320349])
        """
        # get reaction forces on bearings
        self.rotor.run_static()
        Fb = self.rotor.bearing_reaction_forces
        Fb = np.array(Fb) / 9.8065

        return Fb

    def unbalance_forces(self, mode):
        """Method to calculate the unbalance forces.
        The unbalance forces are calculated base on the rotor type:
            between_bearings :
                The unbalance forces derives from the reaction bearing forces.
            single_overung_l :
                The unbalance forces derives from the disk's masses on the
                shaft left end.
            single_overung_r :
                The unbalance forces derives from the disk's masses on the
                shaft right end.
            double_overung :
                The unbalance forces derives from the disk's masses on the
                shaft left and right ends.

        Parameters
        ----------
        mode : int
            n'th mode shape.

        Returns
        -------
        U : list
            Unbalancing forces.

        Example
        -------
        >>> rotor = rotor_example()
        >>> report = Report(rotor=rotor,
        ...                 minspeed=400,
        ...                 maxspeed=1000,
        ...                 speed_units="rad/s")
        >>> report.unbalance_forces(mode=0)
        [58.641354289961676]
        """
        N = 60 * self.maxspeed / (2 * np.pi)

        # get reaction forces on bearings
        if self.rotor_type == "between_bearings":
            Fb = self.static_forces()
            if mode == 0 or mode == 1:
                U_force = [max(6350 * np.sum(Fb) / N, 254e-6 * np.sum(Fb))]

            if mode == 2 or mode == 3:
                U_force = [max(6350 * f / N, 254e-6 * f) for f in Fb]

        # get disk masses
        elif self.rotor_type == "single_overhung_l":
            Wd = [
                disk.m
                for disk in self.rotor.disk_elements
                if disk.n < min(self.rotor.df_bearings["n"])
            ]
            Ws = [
                sh.m
                for sh in self.rotor.shaft_elements
                if sh.n_l < min(self.rotor.df_bearings["n"])
            ]
            W3 = np.sum(Wd + Ws)

            U_force = [6350 * W3 / N]

        elif self.rotor_type == "single_overhung_r":
            Wd = [
                disk.m
                for disk in self.rotor.disk_elements
                if disk.n > max(self.rotor.df_bearings["n"])
            ]
            Ws = [
                sh.m
                for sh in self.rotor.shaft_elements
                if sh.n_r > max(self.rotor.df_bearings["n"])
            ]
            W3 = np.sum(Wd + Ws)

            U_force = [6350 * W3 / N]

        elif self.rotor_type == "double_overhung":
            Wd_l = [
                disk.m
                for disk in self.rotor.disk_elements
                if disk.n < min(self.rotor.df_bearings["n"])
            ]
            Ws_l = [
                sh.m
                for sh in self.rotor.shaft_elements
                if sh.n_l < min(self.rotor.df_bearings["n"])
            ]
            Wd_r = [
                disk.m
                for disk in self.rotor.disk_elements
                if disk.n > max(self.rotor.df_bearings["n"])
            ]
            Ws_r = [
                sh.m
                for sh in self.rotor.shaft_elements
                if sh.n_r > max(self.rotor.df_bearings["n"])
            ]
            W3 = np.array([np.sum(Wd_l + Ws_l), np.sum(Wd_r + Ws_r)])

            U_force = 6350 * W3 / N

        return U_force

    def unbalance_response(self, clearances, mode):
        """Evaluates the unbalance response for the rotor.

        This analysis takes the critical speeds of interest, calculates the
        position and weight of the required unbalance and performs the analysis
        including:
         - Check if vibration at MCS is below the limit with the applied weight;
         - Check if the clearances are ok if the vibration deteriorate to the
         limit level;

        Parameters
        ----------
        clearances : dict
            Dict mapping between node and its clearance in meters.
            (e.g. clearances = dict(3=0.001, 5=0.002...)
        mode : int
            n'th mode shape.

        Returns
        -------
        mag_plot : bokeh axes
            Bokeh axes with unbalance response plot.

        Example
        -------
        >>> rotor = rotor_example()
        >>> report = Report(rotor=rotor,
        ...                 minspeed=400,
        ...                 maxspeed=1000,
        ...                 speed_units="rad/s")
        >>> clearances = {3:0.001, 5:0.002}
        >>> report.unbalance_response(clearances=clearances, mode=0) # doctest: +ELLIPSIS
        Figure...
        """
        maxspeed = self.maxspeed
        minspeed = self.minspeed
        freq_range = np.linspace(0, 1.25 * maxspeed, 201)

        # returns de nodes where forces will be applied
        node_min, node_max = self.mode_shape(mode)

        nodes = [int(node) for sub_nodes in [node_min, node_max] for node in sub_nodes]

        force = self.unbalance_forces(mode)

        phase = []
        for node in nodes:
            phase.append(np.pi)

        response = self.rotor.unbalance_response(nodes, force, phase, freq_range)
        mag = response.magnitude

        for node in nodes:
            dof = 4 * node + 1
            mag_plot = response.plot_magnitude_bokeh(dof)

        magnitude = mag[dof]
        idx_max = argrelextrema(magnitude, np.greater)[0].tolist()
        wn = freq_range[idx_max]

        for i, peak in enumerate(magnitude[idx_max]):
            peak_n = 0.707 * peak
            peak_aux = np.linspace(peak_n, peak_n, len(freq_range))

            idx = np.argwhere(np.diff(np.sign(peak_aux - magnitude))).flatten()
            idx = np.sort(np.append(idx, idx_max[i]))

            # if speed range is not long enough to catch the magnitudes
            try:
                idx_aux = [
                    list(idx).index(idx_max[i]) - 1,
                    list(idx).index(idx_max[i]) + 1,
                ]
                idx = idx[idx_aux]
            except IndexError:
                idx = [list(idx).index(idx_max[i]) - 1, len(freq_range) - 1]

            # Amplification Factor (AF) - API684 - SP6.8.2.1
            AF = wn[i] / (freq_range[idx[1]] - freq_range[idx[0]])

            # Separation Margin (SM) - API684 - SP6.8.2.10
            if AF > 2.5 and wn[i] < minspeed:
                SM = min([16, 17 * (1 - 1 / (AF - 1.5))]) / 100
                SMspeed = wn[i] * (1 + SM)
                SM_ref = (minspeed - wn[i]) / wn[i]
                source = ColumnDataSource(
                    dict(
                        top=[max(magnitude[idx_max])],
                        bottom=[0],
                        left=[wn[i]],
                        right=[SMspeed],
                        tag1=[wn[i]],
                        tag2=[SMspeed],
                    )
                )

                mag_plot.quad(
                    top="top",
                    bottom="bottom",
                    left="left",
                    right="right",
                    source=source,
                    line_color=bokeh_colors[8],
                    line_width=0.8,
                    fill_alpha=0.2,
                    fill_color=bokeh_colors[8],
                    legend="Separation Margin",
                    name="SM2",
                )
                hover = HoverTool(names=["SM2"])
                hover.tooltips = [
                    ("Critical Speed :", "@tag1"),
                    ("Speed at 0.707 x peak amplitude :", "@tag2"),
                ]
                mag_plot.add_tools(hover)

            elif AF > 2.5 and wn[i] > maxspeed:
                SM = min([26, 10 + 17 * (1 - 1 / (AF - 1.5))]) / 100
                SMspeed = wn[i] * (1 - SM)
                SM_ref = (wn[i] - maxspeed) / maxspeed
                source = ColumnDataSource(
                    dict(
                        top=[max(magnitude[idx_max])],
                        bottom=[0],
                        left=[SMspeed],
                        right=[wn[i]],
                        tag1=[wn[i]],
                        tag2=[SMspeed],
                    )
                )

                mag_plot.quad(
                    top="top",
                    bottom="bottom",
                    left="left",
                    right="right",
                    source=source,
                    line_color=bokeh_colors[8],
                    line_width=0.8,
                    fill_alpha=0.2,
                    fill_color=bokeh_colors[8],
                    legend="Separation Margin",
                    name="SM2",
                )
                hover = HoverTool(names=["SM2"])
                hover.tooltips = [
                    ("Critical Speed :", "@tag1"),
                    ("Speed at 0.707 x peak amplitude :", "@tag2"),
                ]
                mag_plot.add_tools(hover)

            else:
                SM = None
                SM_ref = None
                SMspeed = None

        # amplitude limit in micrometers (A1) - API684 - SP6.8.2.11
        A1 = 25.4 * np.sqrt(12000 / (30 * maxspeed / np.pi))

        # amplitude from mode shape analysis
        Amax = max(mag[dof])

        # Scale Factor (Scc) - API684 - SP6.8.2.11 / API617 - 4.8.2.11
        Scc = max(A1 / Amax, 0.5)
        Scc = min(Scc, 6.0)

        mag_plot.quad(
            top=max(mag[dof]),
            bottom=0,
            left=minspeed,
            right=maxspeed,
            line_color="green",
            line_width=0.8,
            fill_alpha=0.2,
            fill_color="green",
            legend="Operation Speed Range",
        )

        source = ColumnDataSource(dict(x=freq_range, y=mag[dof]))
        mag_plot.line(
            x="x",
            y="y",
            source=source,
            line_color=bokeh_colors[0],
            line_alpha=1.0,
            line_width=3,
        )
        mag_plot.line(
            x=[minspeed, maxspeed],
            y=[A1, A1],
            line_dash="dotdash",
            line_width=2.0,
            line_color=bokeh_colors[1],
            legend="Av1 - Mechanical test vibration limit",
        )
        mag_plot.add_layout(
            Label(
                x=(minspeed + maxspeed) / 2,
                y=A1,
                angle=0,
                text="Av1",
                text_font_style="bold",
                text_font_size="12pt",
                text_baseline="top",
                text_align="center",
                y_offset=20,
            )
        )
        mag_plot.width = 1280
        mag_plot.height = 720
        mag_plot.title.text_font_size = "14pt"

        return mag_plot

    def mode_shape(self, mode):
        """Evaluates the mode shapes for the rotor.

        This analysis presents the vibration mode for each critical speed.
        The importance is to locate the critical node, where the displacement
        is the greatest, then apply loads for unbalance response (stability
        level 1)

        Parameters
        ----------
        mode : int
            the n'th vibration mode

        Returns
        -------
        node_min, node_max : list
            List with nodes where the largest absolute displacements occur

        Example
        -------
        >>> rotor = rotor_example()
        >>> report = Report(rotor=rotor,
        ...                 minspeed=400,
        ...                 maxspeed=1000,
        ...                 speed_units="rad/s")
        >>> report.mode_shape(mode=0)
        ([], array([3.]))
        """
        nodes_pos = self.rotor.nodes_pos
        df_bearings = self.rotor.df_bearings
        df_disks = self.rotor.df_disks

        # TODO: Add mcs speed to evaluate mode shapes
        modal = self.rotor.run_modal(speed=0)
        xn, yn, zn, xc, yc, zc_pos, nn = modal.calc_mode_shape(mode=mode)

        # reduce 3D view to 2D view
        vn = np.zeros(len(zn))
        for i in range(len(zn)):
            theta = np.arctan(xn[i] / yn[i])
            vn[i] = xn[i] * np.sin(theta) + yn[i] * np.cos(theta)

        # remove repetitive values from zn and vn
        idx_remove = []
        for i in range(1, len(zn)):
            if zn[i] == zn[i - 1]:
                idx_remove.append(i)
        zn = np.delete(zn, idx_remove)
        vn = np.delete(vn, idx_remove)

        node_min = []
        node_max = []

        if self.rotor_type == "between_bearings":

            aux_idx_max = argrelextrema(vn, np.greater)[0].tolist()
            aux_idx_min = argrelextrema(vn, np.less)[0].tolist()

            # verification of rigid modes
            if len(aux_idx_max) == 0 and len(aux_idx_min) == 0:
                idx_max = np.argmax(vn)
                idx_min = np.argmin(vn)

                # corrects the index by the removed points
                for i in idx_remove:
                    if idx_min > i:
                        idx_min += 1
                    if idx_max > i:
                        idx_max += 1
                node_max = np.round(np.array([idx_max]) / nn)
                node_min = np.round(np.array([idx_min]) / nn)

            if len(aux_idx_min) != 0:
                idx_min = np.where(vn == min(vn[aux_idx_min]))[0].tolist()

                # corrects the index by the removed points
                for i in idx_remove:
                    if idx_min[0] > i:
                        idx_min[0] += 1
                node_min = np.round(np.array(idx_min) / nn)

            if len(aux_idx_max) != 0:
                idx_max = np.where(vn == max(vn[aux_idx_max]))[0].tolist()

                # corrects the index by the removed points
                for i in idx_remove:
                    if idx_max[0] > i:
                        idx_max[0] += 1
                node_max = np.round(np.array(idx_max) / nn)

        elif self.rotor_type == "double_overhung":
            node_max = [max(df_disks['n'])]
            node_min = [min(df_disks['n'])]

        elif self.rotor_type == "single_overhung_l":
            node_min = [min(df_disks['n'])]

        elif self.rotor_type == "single_overhung_r":
            node_max = [max(df_disks['n'])]

        plot = figure(
            tools="pan,wheel_zoom,box_zoom,reset,save,box_select",
            width=1400,
            height=700,
            title="Undamped Mode Shape",
            x_axis_label="Rotor lenght",
            y_axis_label="Non dimensional rotor deformation",
        )
        plot.xaxis.axis_label_text_font_size = "12pt"
        plot.yaxis.axis_label_text_font_size = "12pt"
        plot.title.text_font_size = "14pt"

        nodes_pos = np.array(nodes_pos)

        plot.line(
            x=zn,
            y=vn,
            line_width=4,
            line_color="red",
            legend="Mode = %s, Speed = %.1f RPM" % (mode+1, 9.55*self.rotor.wn[mode]),
        )
        plot.line(
            x=nodes_pos,
            y=np.zeros(len(nodes_pos)),
            line_dash="dotdash",
            line_width=4.0,
            line_color="black",
        )
        plot.circle(
            x=nodes_pos[df_bearings["n"]],
            y=np.zeros(len(df_bearings)),
            size=12,
            fill_color="black",
        )

        pos0 = nodes_pos[min(df_bearings["n"])]
        pos1 = nodes_pos[max(df_bearings["n"])]
        plot.add_layout(
            Label(
                x=np.mean(nodes_pos[df_bearings["n"]]),
                y=0,
                angle=0,
                text="Bearing Span = %.2f" % (pos1 - pos0),
                text_font_style="bold",
                text_font_size="12pt",
                text_baseline="top",
                text_align="center",
                y_offset=20,
            )
        )
        for node in nodes_pos[df_bearings["n"]]:
            plot.add_layout(
                Span(
                    location=node,
                    dimension="height",
                    line_color="green",
                    line_dash="dashed",
                    line_width=3,
                )
            )

        return node_min, node_max

    def stability_level_1(self):
        """Stability analysis level 1.

        This analysis consider a anticipated cross coupling QA based on
        conditions at the normal operating point and the cross-coupling
        required to produce a zero log decrement, Q0.

        Components such as seals and impellers are not considered in this
        analysis.

        Parameters
        ----------
        (Check what we need to calculate the applied cross coupling and list
         them as parameters)
        """
        pass

    def stability_level_2(self):
        """Stability analysis level 2.

        For the level 2 stability analysis additional sources that contribute
        to the rotor stability shall be considered such as:
        a)  labyrinth seals;
        b)  damper seals;
        c)  impeller/blade flow aerodynamic effects;
        d)  internal friction.

        Parameters
        ----------
        (Check what we need to calculate the applied cross coupling and list
        them as parameters)
        """
