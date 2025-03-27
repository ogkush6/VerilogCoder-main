module TopModule(
    input  logic [7:0] in,
    output logic [31:0] out
);

// Define a wire to extract the most significant bit (sign bit) from the 8-bit input.
wire sign_bit;
assign sign_bit = in[7];

// Replicate the sign bit 24 times to create a 24-bit wire.
wire [23:0] replicated_sign_bits;
assign replicated_sign_bits = {24{sign_bit}};

// Concatenate the 24-bit replicated sign bits with the original 8-bit input to form the 32-bit output.
assign out = {replicated_sign_bits, in};

endmodule