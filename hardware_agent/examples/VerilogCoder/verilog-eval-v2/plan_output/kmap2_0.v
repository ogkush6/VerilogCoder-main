module TopModule
(
  input  logic a,
  input  logic b,
  input  logic c,
  input  logic d,
  output logic out
);

  assign out = (~a & ~b & ~c) | (~a & b & ~c & ~d) | (a & ~b & ~c) | (~a & ~b & c & ~d) | (b & c & d) | (~a & b & c & ~d) | (a & ~b & c & d);

endmodule