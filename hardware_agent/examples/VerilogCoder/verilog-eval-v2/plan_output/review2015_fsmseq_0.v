module TopModule
(
  input  logic clk,
  input  logic reset,
  input  logic data,
  output logic start_shifting
);

  // State types for the finite-state machine
  localparam IDLE  = 3'b000, // Idle state, looking for '1'
             S1    = 3'b001, // Found first '1'
             S2    = 3'b010, // Found '11'
             S3    = 3'b011, // Found '110'
             FOUND = 3'b100; // Found '1101', sequence complete

  // State variables
  reg [2:0] state, next_state;

  // State register
  always @(posedge clk) begin
    if (reset) begin
      state <= IDLE;
      start_shifting <= 1'b0; // Reset start_shifting synchronously
    end else begin
      state <= next_state;
      if (next_state == FOUND) begin
        start_shifting <= 1'b1; // Set start_shifting immediately when FOUND
      end
    end
  end

  // Next state logic
  always @(*) begin
    case (state)
      IDLE: begin
        next_state = data ? S1 : IDLE;
      end
      S1: begin
        next_state = data ? S2 : IDLE;
      end
      S2: begin
        next_state = data ? S2 : S3; // Transition to S3 on '0', stay in S2 on '1'
      end
      S3: begin
        next_state = data ? FOUND : S1; // Transition to FOUND on '1', back to S1 on '0'
      end
      FOUND: begin
        next_state = FOUND; // Once FOUND, stay in this state until reset
      end
      default: begin
        next_state = IDLE;
      end
    endcase
  end

endmodule