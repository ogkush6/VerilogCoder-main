module TopModule
(
  input  logic [31:0] in,
  output logic [31:0] out
);

  // Internal wire to hold the reversed byte order of the input
  logic [31:0] reversed_in;

  assign reversed_in[31:24] = in[7:0];
  assign reversed_in[23:16] = in[15:8];
  assign reversed_in[15:8] = in[23:16]; // Assign the third 8 bits of the input to the second 8 bits of the internal wire
  assign reversed_in[7:0] = in[31:24]; // Assign the last 8 bits of the input to the first 8 bits of the internal wire

  // Connect the internal wire to the output port
  assign out = reversed_in;

endmodule