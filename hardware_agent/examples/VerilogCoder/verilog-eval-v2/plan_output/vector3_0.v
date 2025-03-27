module TopModule
(
  input  logic [4:0] a,
  input  logic [4:0] b,
  input  logic [4:0] c,
  input  logic [4:0] d,
  input  logic [4:0] e,
  input  logic [4:0] f,
  output logic [7:0] w,
  output logic [7:0] x,
  output logic [7:0] y,
  output logic [7:0] z
);

  // Concatenate all input vectors a, b, c, d, e, and f into a single 30-bit vector.
  logic [29:0] concatenated_input;

  assign concatenated_input = {a, b, c, d, e, f};

  // Append two '1' bits to the least significant bit (LSB) positions of the 30-bit concatenated vector to form a 32-bit vector.
  logic [31:0] concatenated_input_with_ones;

  assign concatenated_input_with_ones = {concatenated_input, 2'b11};

  // Split the 32-bit vector into four 8-bit output vectors w, x, y, and z.
  assign w = concatenated_input_with_ones[31:24];
  assign x = concatenated_input_with_ones[23:16];
  assign y = concatenated_input_with_ones[15:8];
  assign z = concatenated_input_with_ones[7:0];
  
endmodule