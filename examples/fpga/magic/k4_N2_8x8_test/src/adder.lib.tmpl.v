// Automatically generated by PRGA's blackbox library generator
`timescale 1ns/1ps
module {{ module.vpr_model }} (
    input wire [0:0] a
    , input wire [0:0] b
    , input wire [0:0] cin_fabric
    , input wire [0:0] cin

    , output reg [0:0] cout
    , output reg [0:0] s
    , output wire [0:0] cout_fabric
    );

    localparam  CIN_MODE_CONST0 = 2'b00,
                CIN_MODE_CONST1 = 2'b01,
                CIN_MODE_CHAIN  = 2'b10,
                CIN_MODE_FABRIC = 2'b11;

    parameter CIN_MODE = CIN_MODE_CONST0;

    assign cout_fabric = cout;

    always @* begin
        case (CIN_MODE)
            CIN_MODE_CONST0: {cout, s} = a + b;
            CIN_MODE_CONST1: {cout, s} = a + b + 1;
            CIN_MODE_CHAIN:  {cout, s} = a + b + cin;
            CIN_MODE_FABRIC: {cout, s} = a + b + cin_fabric;
        endcase
    end

endmodule
