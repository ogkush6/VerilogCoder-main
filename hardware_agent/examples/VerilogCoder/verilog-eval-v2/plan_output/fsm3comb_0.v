module TopModule
(
  input  logic       in,
  input  logic [1:0] state,
  output logic [1:0] next_state,
  output logic       out
);

  // State encoding
  localparam STATE_A = 2'b00;
  localparam STATE_B = 2'b01;
  localparam STATE_C = 2'b10;
  localparam STATE_D = 2'b11;

  // Next state combinational logic
  always @(*) begin
    case ( state )
      STATE_A: next_state = ( in ) ? STATE_B : STATE_A;
      STATE_B: next_state = ( in ) ? STATE_B : STATE_C;
      STATE_C: next_state = ( in ) ? STATE_D : STATE_A;
      STATE_D: next_state = ( in ) ? STATE_B : STATE_C; // Updated for state D
    endcase
  end

  // Output combinational logic
  always @(*) begin
    case ( state )
      STATE_A: out = 1'b0; // Output for state A is always 0
      STATE_B: out = 1'b0; // Output for state B is always 0
      STATE_C: out = 1'b0; // Output for state C is always 0
      STATE_D: out = 1'b1; // Output for state D is always 1
    endcase
  end

endmodule