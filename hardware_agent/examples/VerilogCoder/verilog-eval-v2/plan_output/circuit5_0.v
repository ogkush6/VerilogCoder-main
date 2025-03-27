module TopModule
(
  input  logic [3:0] a,
  input  logic [3:0] b,
  input  logic [3:0] c,
  input  logic [3:0] d,
  input  logic [3:0] e,
  output logic [3:0] q
);

  // Combinational logic
  always @(*) begin
    if (c == 4'b0000)
      q = b;
    else if (c == 4'b0001)
      q = e;
    else if (c == 4'b0010)
      q = a;
    else if (c == 4'b0011)
      q = d;
    else
      q = 4'b1111; // Default value 'f' for all other values of 'c'
  end

endmodule