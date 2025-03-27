module TopModule
(
  input  logic clk,
  input  logic reset,
  output logic shift_ena
);

  localparam IDLE     = 2'b00;
  localparam COUNTING = 2'b01;
  localparam DONE     = 2'b10;

  logic [1:0] state;
  logic [1:0] state_next;

  logic [2:0] counter;

  always @(posedge clk) begin
    if (reset) begin
      state <= COUNTING;
      counter <= 3'b000;
    end else begin
      state <= state_next;
      if (state == COUNTING && counter < 3'b100)
        counter <= counter + 1;
      else if (state == DONE)
        counter <= 3'b000;
    end
  end

  always @(*) begin
    case (state)
      IDLE: state_next = (reset) ? COUNTING : IDLE;
      COUNTING: state_next = (counter == 3'b011) ? DONE : COUNTING; // Transition to DONE when counter reaches 4
      DONE: state_next = IDLE;
    endcase
  end

  assign shift_ena = (state == COUNTING);

endmodule