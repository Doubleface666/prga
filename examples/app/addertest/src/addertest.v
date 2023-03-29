module addertest(
  input [31:0] a,
  input [31:0] b,
  output [31:0] sum
);

reg [31:0] temp[0:9];
reg [31:0] final_sum;

assign sum = final_sum;

always @(*) begin
  temp[0] = a + b;
  temp[1] = temp[0] + a;
  temp[2] = temp[1] + b;
  temp[3] = temp[2] + a;
  temp[4] = temp[3] + b;
  temp[5] = temp[4] + a;
  temp[6] = temp[5] + b;
  temp[7] = temp[6] + a;
  temp[8] = temp[7] + b;
  temp[9] = temp[8] + a;
  final_sum = temp[9];
end

endmodule