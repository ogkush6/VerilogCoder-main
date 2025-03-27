module TopModule
(
  input  logic a,
  input  logic b,
  output logic out_assign,
  output logic out_alwaysblock
);

  // Implement the AND gate logic using an assign statement for the output 'out_assign'.
  assign out_assign = a & b;

  // Implement the AND gate logic using a combinational always block for the output 'out_alwaysblock'.
  always @(*) begin
    out_alwaysblock = a & b;
  end

endmodule