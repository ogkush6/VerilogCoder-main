module TopModule
(
  input  logic [7:0] code,
  output logic [3:0] out,
  output logic valid
);

  // Combinational logic

  logic [3:0] decoded_key;
  logic is_valid;

  always @(*) begin
    case ( code )
      8'h45: decoded_key = 4'b0000; // Key 0
      8'h16: decoded_key = 4'b0001; // Key 1
      8'h1e: decoded_key = 4'b0010; // Key 2
      8'h26: decoded_key = 4'b0011; // Key 3
      8'h25: decoded_key = 4'b0100; // Key 4
      8'h2e: decoded_key = 4'b0101; // Key 5
      8'h36: decoded_key = 4'b0110; // Key 6
      8'h3d: decoded_key = 4'b0111; // Key 7
      8'h3e: decoded_key = 4'b1000; // Key 8
      8'h46: decoded_key = 4'b1001; // Key 9
      default: decoded_key = 4'bxxxx; // Invalid key
    endcase
  end

  // Check if the decoded key is valid
  always @(*) begin
    is_valid = (decoded_key !== 4'bxxxx) ? 1'b1 : 1'b0;
  end

  // Assign the outputs
  always @(*) begin
    out = is_valid ? decoded_key : 4'b0000;
  end

  // Implement a logic block to set the 'valid' output port
  assign valid = is_valid;

endmodule