Architecture & Customizability
==============================

PRGA Tile Grid
--------------

.. image:: /_static/images/grid.png
   :width: 600px
   :alt: PRGA Tile Grid
   :align: center

The figure above shows PRGA's grid.
Each tile in the grid (not to be confused with :ref:`arch:Tile`) contains four
:ref:`Switch Box<arch:Connection and Switch Box>` slots (one per corner) and one
:ref:`arch:Tile` slot (the blue cross-shaped box wrapping the CLB and the C-Boxes).
The :ref:`arch:Tile` slot contains four :ref:`Connection Box<arch:Connection and Switch Box>`
slots (one per edge) and one :ref:`block<arch:Logic and IO Block>` slot.
Note that we are using the word "slot" here, because the actual usage depends on
the architecture.
For example, a 2x2 block occupies 4 block slots, and
obstructs certain switch box and connection box slots.

**TODO**: explain why we need the redundant slots.
In a nutshell, the redundant slots are related to design regularity and silicon
implementation flexibility.

It's still possible to emulate the conventional FPGA grid which contains only
one connection box per routing channel, and one switch box per routing channel
crosspoint.
This is done by leaving the unused slots empty, as shown in the figure below.

.. image:: /_static/images/convgrid.png
   :width: 600px
   :alt: Conventional FPGA Grid Emulated by the PRGA Tile Grid
   :align: center

.. _VPR: https://verilogtorouting.org/

Module View
-----------

Before diving into each type of modules listed above, let's get familiar with an
important concept in PRGA first: **Module Views** (`ModuleView`).

The ultimate goal of PRGA's :ref:`workflow:FPGA Design` flow is to generate synthesizable
RTL (register-transfer level) Verilog for a customized FPGA architecture, and
produce FPGA CAD scripts (**NOT** ASIC implementation scripts) that correspond
to the FPGA.
However, FPGA CAD tools only need, and only take, a functional abstraction of
the FPGA, ignoring most of the implementation details.
For example, different modes of a multi-modal :ref:`arch:Logic Primitive` are typically
modeled as different blocks in `VPR`_ despite that the whole primitive is
usually a single module in RTL.
The figure below shows a fracturable ``LUT3`` that can be used as two ``LUT2`` s
with shared inputs.

.. figure:: /_static/images/FracLUT3_Abstract.png
    :width: 400px
    :alt: Two Abstract Modes of Fracturable LUT3
    :align: center
   
    Abstract modes of Fracturable LUT3


.. figure:: /_static/images/FracLUT3_Design.png
    :width: 400px
    :alt: Design view of Fracturable LUT3
    :align: center

    Design view (schematic) of Fracturable LUT3. Mode selection bit highlighted
    by red circle

.. _Yosys: http://www.clifford.at/yosys
.. _VPR: https://verilogtorouting.org/

To incorporate various information needed by different third-party tools, PRGA
adopts the concept of ``View`` s widely used in the EDA world.
Each module may have different views, and different views are used in different
steps.

Currently, PRGA uses two views: `ModuleView.abstract`, and `ModuleView.design`.

Abstract View
^^^^^^^^^^^^^

The **abstract** view describes the nets, connections and logic of a
module that are used and visible to the implemented application.
It is mostly used during the :ref:`workflow:Architecture Customization` step, and in
FPGA CAD script generation passes.

Modules in the abstract view have the following features:

- **Allows any net to be driven by multiple drivers.** PRGA uses this to
  represent reconfigurable connections.
- **Does not contain configuration nets or modules.**

Design View
^^^^^^^^^^^

The **design** view is used in RTL generation, therefore contains
accurate information about all the nets and modules in the FPGA.
Except for :ref:`arch:Logic Primitive` s, the design view of most modules
is generated by the `Translation` pass based on the user-specified
abstract view, and then completed by the ``*.InsertProgCircuitry``
pass.

Access Modules in Different Views
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To access modules in different views, simply add the `ModuleView` when you
access the ``database`` property of a `Context` object.

.. code-block:: python

    abstract_lut4 = ctx.database[ModuleView.abstract, "lut4"]
    design_lut4 = ctx.database[ModuleView.design, "lut4"]

Logic Primitive
---------------

**Logic Primitive**, also known as logic elements or logic resources, are the
building blocks of FPGAs.
In PRGA, all hard logic that can be targeted by technology mapping and synthesis
are categorized as **Logic Primitive** s, including but not limited to LUTs,
flip-flops, hard arithmetic units, SRAM macros, or even complex IP cores like
memory controllers, hard processors, etc.
They also correspond to the leaf-level `pb_type`_ s in VPR's terminology.

.. _pb_type: https://docs.verilogtorouting.org/en/latest/arch/reference/#pb-type

Logic Primitive Types
^^^^^^^^^^^^^^^^^^^^^

Logic primitives are further classified into three types:

- *Non-Programmable* primitives. They are hard components that are used in the
  application **as is**, e.g. simple flip-flops. Their :ref:`abstract<arch:Module View>`
  view and :ref:`design<arch:Module View>` view are typically very similar or even the same.
- *Programmable* primitives. Their functionality is programmable. Currently only
  LUTs belong to this category.
- *Multi-Modal* primitives. They have multiple modes, each emulating one or
  multiple other primitives. One and only one of the modes can be activated and
  used after the FPGA is programmed. Multi-Modal primitives are not directly
  targeted by synthesis. Instead, logic primitives emulated by their modes are
  targeted by synthesis, and eventually mapped back to the multi-modal
  primitives during the packing step of the RTL-to-bitstream flow. They are
  usually one single module in the :ref:`design<arch:Module View>` view, but may contain
  multiple submodules in the :ref:`abstract<arch:Module View>` view, making the two views
  very different.

These types are only conceptual categories and not explicitly implemented 
in the PRGA API.

Module Views of Logic Primitives
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

As explained in the :ref:`arch:Module View` section, each logic primitive has two
views: the :ref:`abstract<arch:Module View>` view and the :ref:`design<arch:Module View>` view.
Most logic primitives are associated with two RTL Verilog files, each
corresponding to one of the two views.
The RTL corresponding to the :ref:`abstract<arch:Module View>` view is used during
synthesis and post-synthesis simulation.
The RTL corresponding to the :ref:`design<arch:Module View>` view is the one used in the
final ASIC-compatible RTL, i.e. the one that will eventually be mapped onto
transistors on your chip.

A good example is the `lut.lib.tmpl.v`_ and `lut.tmpl.v`_ pair for LUTs.
Both the files might seem a bit strange, because they are file rendering
templates (reference: :ref:`workflow:File Rendering`), not the final RTL.

.. _lut.lib.tmpl.v: https://github.com/PrincetonUniversity/prga.py/blob/master/prga/renderer/templates/builtin/lut.lib.tmpl.v
.. _lut.tmpl.v: https://github.com/PrincetonUniversity/prga.py/blob/master/prga/renderer/templates/builtin/lut.tmpl.v

+-------------------------------------------+---------------------------------------------------------------------------+
|                                           | .. code-block:: Verilog                                                   |
|                                           |                                                                           |
|                                           |     // Automatically generated by PRGA's RTL generator                    |
|                                           |     `timescale 1ns/1ps                                                    |
|                                           |     module {{ module.vpr_model }} #(                                      |
|                                           |         parameter   WIDTH   = 6                                           |
|                                           |         , parameter LUT     = 64'b0                                       |
| `lut.lib.tmpl.v`_                         |     ) (                                                                   |
|                                           |         input wire [WIDTH - 1:0] in                                       |
| (:ref:`abstract<arch:Module View>` view)  |         , output reg [0:0] out                                            |
|                                           |         );                                                                |
|                                           |                                                                           |
|                                           |         always @* begin                                                   |
|                                           |             out = LUT >> in;                                              | 
|                                           |         end                                                               |
|                                           |                                                                           |
|                                           |     endmodule                                                             |
+-------------------------------------------+---------------------------------------------------------------------------+
|                                           | .. code-block:: Verilog                                                   |
|                                           |                                                                           |
|                                           |     // Automatically generated by PRGA's RTL generator                    |
|                                           |     {% set width = module.ports.in|length -%}                             |
|                                           |     `timescale 1ns/1ps                                                    |
|                                           |     module {{ module.name }} (                                            |
|                                           |         input wire [{{ width - 1 }}:0] in                                 |
|                                           |         , output reg [0:0] out                                            |
|                                           |                                                                           |
|                                           |         , input wire [0:0] prog_done                                      |
|                                           |         , input wire [{{ 2 ** width }}:0] prog_data                       |
|                                           |             // prog_data[ 0 +: {{ 2 ** width - 1}}]: LUT content          |
|                                           |             // prog_data[{{ 2 ** width }}]: LUT enabled (not disabled)    |
|                                           |         );                                                                | 
| `lut.tmpl.v`_                             |                                                                           |
|                                           |         localparam  IDX_LUT_ENABLE = {{ 2 ** width }};                    |
| (:ref:`design<arch:Module View>` view)    |                                                                           |
|                                           |         always @* begin                                                   |
|                                           |             if (~prog_done || ~prog_data[IDX_LUT_ENABLE]) begin           |
|                                           |                 out = 1'b0;                                               |
|                                           |             end else begin                                                |
|                                           |                 case (in)                                                 |
|                                           |                     {%- for i in range(2 ** width) %}                     |
|                                           |                     {{ width }}'d{{ i }}: out = prog_data[{{ i }}];       |
|                                           |                     {%- endfor %}                                         |
|                                           |                 endcase                                                   |
|                                           |             end                                                           |
|                                           |         end                                                               |
|                                           |                                                                           |
|                                           |     endmodule                                                             |
+-------------------------------------------+---------------------------------------------------------------------------+

Some multi-modal primitives may not have the RTL for the :ref:`abstract<arch:Module View>`
view, because their :ref:`abstract<arch:Module View>` view is composed of other primitives.
Moreover, there are :ref:`abstract<arch:Module View>` -only primitives as well, often
used as part of a single mode of a multi-modal primitive.
``FLE6`` (:ref:`design<arch:Module View>` view RTL: `fle6.tmpl.v`_) and its submodule, ``adder`` (:ref:`abstract<arch:Module View>`
view RTL: `adder.lib.tmpl.v`_ are a good example.

.. _fle6.tmpl.v: https://github.com/PrincetonUniversity/prga.py/blob/master/prga/renderer/templates/fle6/fle6.tmpl.v
.. _adder.lib.tmpl.v: https://github.com/PrincetonUniversity/prga.py/blob/master/prga/renderer/templates/builtin/adder.lib.tmpl.v

To learn more, check out the
:ref:`PicoSOC<tutorial/bring_your_own_ip:Bring Your Own IP Core>` tutorial.

Logic Primitives in Synthesis
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

There are three ways that logic primitives are
used during technology mapping and synthesis:

- **Explicit Instantiation**: The :ref:`abstract<arch:Module View>` view of a logic
  primitive may be directly instantiated in the application RTL.
  `Yosys`_ will treat explicitly instantiated logic primitives as black boxes
  and leave them as is in the synthesized netlist.
  To learn more, check out the
  :ref:`PicoSOC<tutorial/bring_your_own_ip:Bring Your Own IP Core>` tutorial.
- **Technology Mapping**: High-level operations used in the application (for
  example, additions, multiplications, rising-edge-triggered non-blocking
  assignments) may be implemented with logic primitives via technology mapping.
  To enable this during synthesis, we need to provide `Yosys`_ some extra
  technology mapping rules (which are also written in Verilog and pretty
  confusing at the beginning).
  For example, to enable the technology mapping onto the ``adder`` primitive
  (:ref:`abstract<arch:Module View>` view RTL: `adder.lib.tmpl.v`_), we provive `Yosys`_ with the
  technology mapping rule file `adder.techmap.tmpl.v`_, which defines a set of
  rules to map additions, subtractions, comparisons to ``adder`` s.
  To learn more, check out the
  :ref:`PicoSOC<tutorial/bring_your_own_ip:Bring Your Own IP Core>` tutorial,
  and check out the documentation of `Yosys`_.
- **Logic Synthesis**: After technology mapping, the remaining logic has no
  choice but to be synthesized to LUTs.

.. _adder.techmap.tmpl.v: https://github.com/PrincetonUniversity/prga.py/blob/master/prga/renderer/templates/builtin/adder.techmap.tmpl.v

Slice
-----

Slices are optional levels of hierarchy between :ref:`arch:Logic Primitive` s and
:ref:`arch:Logic and IO Block` s.
They correspond to the intermediate levels of `pb_type`_ in VPR's terminology.

As a user, you only need to describe the :ref:`abstract<arch:Module View>` view of a slice.
The :ref:`design<arch:Module View>` view will be automatically generated by the `Translation` pass,
and configuration memory will be automatically inserted by the
``*.InsertProgCircuitry`` passes.
RTL will only be generated for the :ref:`design<arch:Module View>` view.

Logic and IO Block
------------------

Logic blocks and IO blocks are clusters of :ref:`arch:Slice` s and
:ref:`arch:Logic Primitive` s with programmable local interconnects.
They correspond to the top-level `pb_type`_ s in VPR's terminology.

Logic and IO Blocks in Packing
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

As explained in the :ref:`arch:Logic Primitive` section, an application RTL is
first synthesized to a netlist composed of :ref:`arch:Logic Primitive` s and
wire connections.
Then, during the packing step, the :ref:`arch:Logic Primitive` s are clustered
and packed into blocks, which will be placed and routed onto the physical
fabric later in the RTL-to-bitstream flow.
The quality of the packing result determines the utilization rate of the
logic resources that are physically on your chip, and determines the difficulty
of the placement and routing steps.

Connection and Switch Box
-------------------------

Work in progress.

Tile
----

Work in progress.

Array
-----

Work in progress.
