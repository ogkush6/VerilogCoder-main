module TopModule
(
  input  logic clk,
  input  logic x,
  output logic z
);

  // Declare D flip-flops
  logic xor_ff, and_ff, or_ff;

  // Initialize D flip-flops to zero
  initial begin
    xor_ff = 1'b0;
    and_ff = 1'b0;
    or_ff  = 1'b0;
  end

  // XOR gate logic
  logic xor_out;
  assign xor_out = x ^ xor_ff;

  // AND gate logic
  logic and_out;
  assign and_out = x & ~and_ff;

  // OR gate logic
  logic or_out;
  assign or_out = x | ~or_ff;

  // Sequential logic for D flip-flops
  always @(posedge clk) begin
    xor_ff <= xor_out;
    and_ff <= and_out;
    or_ff  <= or_out;
  end

  // NOR gate logic
  assign z = ~(xor_ff | and_ff | or_ff);

endmodule