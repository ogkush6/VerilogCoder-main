module TopModule
(
  input  logic clk,
  input  logic a,
  input  logic b,
  output logic out_assign,
  output logic out_always_comb,
  output logic out_always_ff
);

  // XOR operation using assign statement
  assign out_assign = a ^ b;

  // XOR operation using combinational always block
  always_comb begin
    out_always_comb = a ^ b;
  end

  // XOR operation using clocked always block
  always_ff @(posedge clk) begin
    out_always_ff <= a ^ b;
  end

endmodule