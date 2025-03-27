module TopModule (
    input  logic clk,
    input  logic load,
    input  logic [255:0] data,
    output logic [255:0] q
);
    // The internal register to hold the state of the game
    logic [255:0] state;

    // Sequential logic to load new data or update the game state
    always @(posedge clk) begin
        if (load) begin
            state <= data;
        end else begin
            // The game state update logic will be implemented here
            for (int i = 0; i < 256; i = i + 1) begin
                case (neighbours[i])
                    8'd0, 8'd1: state[i] <= 1'b0;
                    8'd2: state[i] <= state[i];
                    8'd3: state[i] <= 1'b1;
                    default: state[i] <= 1'b0;
                endcase
            end
        end
    end

    // Output assignment
    assign q = state;

    // Combinational logic to calculate the number of neighbours for each cell
    logic [7:0] neighbours [255:0]; // Array to hold the number of neighbours for each cell

    integer i, j;
    always @(*) begin
        for (i = 0; i < 16; i = i + 1) begin
            for (j = 0; j < 16; j = j + 1) begin
                neighbours[i*16 + j] = state[((i+15)%16)*16 + ((j+15)%16)] + // Top-left
                                        state[((i+15)%16)*16 + j] +          // Top
                                        state[((i+15)%16)*16 + ((j+1)%16)] + // Top-right
                                        state[i*16 + ((j+15)%16)] +          // Left
                                        state[i*16 + ((j+1)%16)] +           // Right
                                        state[((i+1)%16)*16 + ((j+15)%16)] + // Bottom-left
                                        state[((i+1)%16)*16 + j] +           // Bottom
                                        state[((i+1)%16)*16 + ((j+1)%16)];   // Bottom-right
            end
        end
    end
endmodule