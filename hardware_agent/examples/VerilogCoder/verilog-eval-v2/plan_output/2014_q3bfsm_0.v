module TopModule
(
  input  logic clk,
  input  logic reset,
  input  logic x,
  output logic z
);

  // State enum
  localparam STATE_0 = 3'b000;
  localparam STATE_1 = 3'b001;
  localparam STATE_2 = 3'b010;
  localparam STATE_3 = 3'b011;
  localparam STATE_4 = 3'b100;

  // State register
  logic [2:0] state;
  logic [2:0] state_next;

  always @(posedge clk) begin
    if ( reset )
      state <= STATE_0;
    else
      state <= state_next;
  end

  // Next state combinational logic
  always @(*) begin
    case ( state )
      STATE_0: state_next = ( x ) ? STATE_1 : STATE_0;
      STATE_1: state_next = ( x ) ? STATE_4 : STATE_1;
      STATE_2: state_next = ( x ) ? STATE_1 : STATE_2;
      STATE_3: state_next = ( x ) ? STATE_2 : STATE_1;
      STATE_4: state_next = ( x ) ? STATE_4 : STATE_3;
    endcase
  end

  // Output combinational logic
  always @(*) begin
    case ( state )
      STATE_0: z = 1'b0;
      STATE_1: z = 1'b0;
      STATE_2: z = 1'b0;
      STATE_3: z = 1'b1;
      STATE_4: z = 1'b1;
    endcase
  end

endmodule