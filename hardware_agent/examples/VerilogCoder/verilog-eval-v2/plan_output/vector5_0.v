module TopModule
(
  input  logic a,
  input  logic b,
  input  logic c,
  input  logic d,
  input  logic e,
  output logic [24:0] out
);

  // Combinational logic for comparison between signal 'a' and itself
  assign out[24] = ~a ^ a;

  // Combinational logic for comparison between signal 'a' and signal 'b'
  assign out[23] = ~a ^ b;

  // Combinational logic for comparison between signal 'a' and signal 'c'
  assign out[22] = ~a ^ c;

  // Combinational logic for comparison between signal 'a' and signal 'd'
  assign out[21] = ~a ^ d;

  // Combinational logic for comparison between signal 'a' and signal 'e'
  assign out[20] = ~a ^ e;

  // Combinational logic for comparison between signal 'b' and signal 'a'
  assign out[19] = ~b ^ a;

  // Combinational logic for comparison between signal 'b' and itself
  assign out[18] = ~b ^ b;

  // Combinational logic for comparison between signal 'b' and signal 'c'
  assign out[17] = ~b ^ c;

  // Combinational logic for comparison between signal 'b' and signal 'd'
  assign out[16] = ~b ^ d;

  // Combinational logic for comparison between signal 'b' and signal 'e'
  assign out[15] = ~b ^ e;

  // Combinational logic for comparison between signal 'c' and signal 'a'
  assign out[14] = ~c ^ a;

  // Combinational logic for comparison between signal 'c' and signal 'b'
  assign out[13] = ~c ^ b;

  // Combinational logic for comparison between signal 'c' and itself
  assign out[12] = ~c ^ c;

  // Combinational logic for comparison between signal 'c' and signal 'd'
  assign out[11] = ~c ^ d;

  // Combinational logic for comparison between signal 'c' and signal 'e'
  assign out[10] = ~c ^ e;

  // Combinational logic for comparison between signal 'd' and signal 'a'
  assign out[9] = ~d ^ a;

  // Combinational logic for comparison between signal 'd' and signal 'b'
  assign out[8] = ~d ^ b;

  // Combinational logic for comparison between signal 'd' and signal 'c'
  assign out[7] = ~d ^ c;

  // Combinational logic for comparison between signal 'd' and itself
  assign out[6] = ~d ^ d;

  // Combinational logic for comparison between signal 'd' and signal 'e'
  assign out[5] = ~d ^ e;

  // Combinational logic for comparison between signal 'e' and signal 'a'
  assign out[4] = ~e ^ a;

  // Combinational logic for comparison between signal 'e' and signal 'b'
  assign out[3] = ~e ^ b;

  // Combinational logic for comparison between signal 'e' and signal 'c'
  assign out[2] = ~e ^ c;

  // Combinational logic for comparison between signal 'e' and signal 'd'
  assign out[1] = ~e ^ d;

  // Combinational logic for comparison between signal 'e' and itself
  assign out[0] = ~e ^ e;

endmodule