[![PRGA logo](/docs/source/_static/images/logo.png)](https://parallel.princeton.edu/prga)

# **P**rinceton **R**econfigurable **G**ate **A**rray

[![License](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)
[![Documentation Status](https://readthedocs.org/projects/prga/badge/?version=latest)](https://prga.readthedocs.io/en/latest/?badge=latest)
[![ci-install](https://github.com/PrincetonUniversity/prga/actions/workflows/checkinstall.yml/badge.svg?branch=release)](https://github.com/PrincetonUniversity/prga/actions/workflows/checkinstall.yml)
[![ci-dev](https://github.com/PrincetonUniversity/prga/actions/workflows/quickcheck.yml/badge.svg?branch=dev)](https://github.com/PrincetonUniversity/prga/actions/workflows/quickcheck.yml)

Build your own FPGA Chip or embedded FPGA IP with Python, and enjoy a fully
open-source, auto-generated CAD flow specifically for your custom FPGA.

#### Find out more
* [Documentation](https://prga.rtfd.io)
* [Website](https://parallel.princeton.edu/prga/)
* [Cite PRGA](https://dl.acm.org/doi/abs/10.1145/3431920.3439294)

## Quickstart

```bash
# Install PRGA and dependencies
cd /path/to/prga/
./envscr/install

# Install iverilog (Icarus Verilog) if Synopsys VCS is not available
# ...

# Activate Python virtual environment
source ./envscr/activate

# build an example FPGA
make -C examples/fpga/magic/k4_N2_8x8

# create CAD & verification project
make -C examples/app/bcd2bin/magic_k4_N2_8x8

# run RTL-to-bitstream flow and post-implementation simulation
make -C examples/app/bcd2bin/magic_k4_N2_8x8/tests/basic
```
