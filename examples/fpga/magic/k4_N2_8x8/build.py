from prga import *
from itertools import product

import sys

ctx = Context()
gbl_clk = ctx.create_global("clk", is_clock = True)
gbl_clk.bind((0, 1), 0)
ctx.create_segment('L1', 20, 1)

builder = ctx.build_slice("slice")
clk = builder.create_clock("clk")
i = builder.create_input("i", 4)
o = builder.create_output("o", 1)
lut = builder.instantiate(ctx.primitives["lut4"], "lut")
ff = builder.instantiate(ctx.primitives["flipflop"], "ff")
builder.connect(clk, ff.pins['clk'])
builder.connect(i, lut.pins['in'])
builder.connect(lut.pins['out'], o)
builder.connect(lut.pins['out'], ff.pins['D'], vpr_pack_patterns = ('lut_dff', ))
builder.connect(ff.pins['Q'], o)
cluster = builder.commit()

builder = ctx.build_io_block("iob")
o = builder.create_input("outpad", 1)
i = builder.create_output("inpad", 1)
builder.connect(builder.instances['io'].pins['inpad'], i)
builder.connect(o, builder.instances['io'].pins['outpad'])
iob = builder.commit()

builder = ctx.build_logic_block("clb")
clk = builder.create_global(gbl_clk, Orientation.south)
for i, inst in enumerate(builder.instantiate(cluster, "cluster", 2)):
    builder.connect(clk, inst.pins['clk'])
    builder.connect(builder.create_input("i{}".format(i), 4, Orientation.west), inst.pins['i'])
    builder.connect(inst.pins['o'], builder.create_output("o{}".format(i), 1, Orientation.east))
clb = builder.commit()

clbtile = ctx.build_tile(clb).fill( (0.4, 0.25) ).auto_connect().commit()

iotiles = {}
for ori in Orientation:
    builder = ctx.build_tile(iob, 4, name = "t_io_{}".format(ori.name[0]),
            edge = OrientationTuple(False, **{ori.name: True}))
    iotiles[ori] = builder.fill( (1., 1.) ).auto_connect().commit()

builder = ctx.build_array('top', 8, 8, set_as_top = True)
for x, y in product(range(builder.width), range(builder.height)):
    if x in (0, builder.width - 1) and y in (0, builder.height - 1):
        pass
    elif x == 0:
        builder.instantiate(iotiles[Orientation.west], (x, y))
    elif x == builder.width - 1:
        builder.instantiate(iotiles[Orientation.east], (x, y))
    elif y == 0:
        builder.instantiate(iotiles[Orientation.south], (x, y))
    elif y == builder.height - 1:
        builder.instantiate(iotiles[Orientation.north], (x, y))
    else:
        builder.instantiate(clbtile, (x, y))
top = builder.fill( SwitchBoxPattern.cycle_free ).auto_connect().commit()

Flow(
        VPRArchGeneration('vpr/arch.xml'),
        VPR_RRG_Generation('vpr/rrg.xml'),
        YosysScriptsCollection('syn'),
        Materialization('magic'),
        Translation(),
        SwitchPathAnnotation(),
        ProgCircuitryInsertion(),
        VerilogCollection('rtl'),
        ).run(ctx)

ctx.pickle("ctx.pkl" if len(sys.argv) < 2 else sys.argv[1])
