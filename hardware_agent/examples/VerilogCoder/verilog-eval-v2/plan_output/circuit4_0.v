module TopModule
(
  input  logic a,
  input  logic b,
  input  logic c,
  input  logic d,
  output logic q
);

  // Combinational logic
  always @(*) begin
    q = b | c;
  end

endmodule