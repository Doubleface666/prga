module myadder (
    input wire  clk,
    input wire  AD,
    output reg  AQ
    );

    always @(negedge clk)
        AQ <= ~AD;

endmodule
