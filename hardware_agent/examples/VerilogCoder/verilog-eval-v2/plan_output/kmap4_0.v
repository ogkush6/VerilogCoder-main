module TopModule
(
  input  logic a,
  input  logic b,
  input  logic c,
  input  logic d,
  output logic out
);

  always @(*) begin
    out = (a ^ b) ^ (c ^ d);
  end
endmodule