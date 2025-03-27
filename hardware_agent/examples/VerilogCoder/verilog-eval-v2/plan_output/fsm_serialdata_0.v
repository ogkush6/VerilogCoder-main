module TopModule (
    input  logic clk,
    input  logic in,
    input  logic reset,
    output logic [7:0] out_byte,
    output logic done
);

    // State definitions
    localparam IDLE = 3'b000;
    localparam RECEIVE = 3'b001;
    localparam CHECK_STOP = 3'b010;
    localparam ERROR = 3'b011;

    // State register
    logic [2:0] state;
    logic [2:0] next_state;

    // Data bit counter
    logic [3:0] bit_count;

    // Data storage
    logic [7:0] data_buffer;

    // FSM logic to handle state transitions and outputs
    always @(posedge clk) begin
        if (reset) begin
            state <= IDLE;
            bit_count <= 0;
            data_buffer <= 0;
            done <= 0;
        end else begin
            state <= next_state;
            if (state == CHECK_STOP && in == 1) begin
                done <= 1; // Set done only for one cycle when stop bit is correct
            end else begin
                done <= 0;
            end
        end
    end

    // Combinational logic for next state and output control
    always @(*) begin
        next_state = state; // Default to stay in current state
        case (state)
            IDLE: begin
                if (in == 0) begin
                    next_state = RECEIVE;
                end
            end
            RECEIVE: begin
                if (bit_count == 7) begin // Check if 8 bits have been received
                    next_state = CHECK_STOP;
                end
            end
            CHECK_STOP: begin
                if (in == 1) begin
                    next_state = IDLE;
                    out_byte = data_buffer;
                end else begin
                    next_state = ERROR;
                end
            end
            ERROR: begin
                if (in == 1) begin
                    next_state = IDLE;
                end
            end
        endcase
    end

    // Data reception logic
    always @(posedge clk) begin
        if (state == RECEIVE) begin
            bit_count <= bit_count + 1;
            data_buffer <= {in, data_buffer[7:1]}; // Shift register operation
        end else begin
            bit_count <= 0;
        end
    end

endmodule