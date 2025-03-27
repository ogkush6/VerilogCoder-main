`timescale 1 ps/1 ps
`define OK 12
`define INCORRECT 13


module stimulus_gen (
	input clk,
	output logic in,
	output logic reset
);

	initial begin
		reset <= 1;
		in <= 1;
		@(posedge clk);
		reset <= 0;
		in <= 0;
		repeat(9) @(posedge clk);
		in <= 1;
		@(posedge clk);
		in <= 0;
		repeat(9) @(posedge clk);
		in <= 1;
		@(posedge clk);
		in <= 0;
		repeat(10) @(posedge clk);
		in <= 1;
		@(posedge clk);
		in <= 0;
		repeat(10) @(posedge clk);
		in <= 1;
		@(posedge clk);
		in <= 0;
		repeat(9) @(posedge clk);
		in <= 1;
		@(posedge clk);
		
		
		
		repeat(800) @(posedge clk, negedge clk) begin
			in <= $random;
			reset <= !($random & 31);
		end

		#1 $finish;
	end
	
endmodule

module tb();

	typedef struct packed {
		int errors;
		int errortime;
		int errors_out_byte;
		int errortime_out_byte;
		int errors_done;
		int errortime_done;

		int clocks;
	} stats;
	
	stats stats1;
	
	
	wire[511:0] wavedrom_title;
	wire wavedrom_enable;
	int wavedrom_hide_after_time;
	
	reg clk=0;
	initial forever
		#5 clk = ~clk;

	logic in;
	logic reset;
	logic [7:0] out_byte_ref;
	logic [7:0] out_byte_dut;
	logic done_ref;
	logic done_dut;

	initial begin 
		$dumpfile("wave.vcd");
		$dumpvars();
	end


	wire tb_match;		// Verification
	wire tb_mismatch = ~tb_match;
	
	stimulus_gen stim1 (
		.clk,
		.* ,
		.in,
		.reset );
	RefModule good1 (
		.clk,
		.in,
		.reset,
		.out_byte(out_byte_ref),
		.done(done_ref) );
		
	TopModule top_module1 (
		.clk,
		.in,
		.reset,
		.out_byte(out_byte_dut),
		.done(done_dut) );

	
	bit strobe = 0;
	task wait_for_end_of_timestep;
		repeat(5) begin
			strobe <= !strobe;  // Try to delay until the very end of the time step.
			@(strobe);
		end
	endtask	

	
	final begin
		if (stats1.errors_out_byte) $display("Hint: Output '%s' has %0d mismatches. First mismatch occurred at time %0d.", "out_byte", stats1.errors_out_byte, stats1.errortime_out_byte);
		else $display("Hint: Output '%s' has no mismatches.", "out_byte");
		if (stats1.errors_done) $display("Hint: Output '%s' has %0d mismatches. First mismatch occurred at time %0d.", "done", stats1.errors_done, stats1.errortime_done);
		else $display("Hint: Output '%s' has no mismatches.", "done");

		$display("Hint: Total mismatched samples is %1d out of %1d samples\n", stats1.errors, stats1.clocks);
		$display("Simulation finished at %0d ps", $time);
		$display("Mismatches: %1d in %1d samples", stats1.errors, stats1.clocks);
	end
	
	// Verification: XORs on the right makes any X in good_vector match anything, but X in dut_vector will only match X.
	assign tb_match = ( { out_byte_ref, done_ref } === ( { out_byte_ref, done_ref } ^ { out_byte_dut, done_dut } ^ { out_byte_ref, done_ref } ) );
	// Use explicit sensitivity list here. @(*) causes NetProc::nex_input() to be called when trying to compute
	// the sensitivity list of the @(strobe) process, which isn't implemented.
	always @(posedge clk, negedge clk) begin

		stats1.clocks++;
		if (!tb_match) begin
			if (stats1.errors == 0) stats1.errortime = $time;
			stats1.errors++;
		end
		if (out_byte_ref !== ( out_byte_ref ^ out_byte_dut ^ out_byte_ref ))
		begin if (stats1.errors_out_byte == 0) stats1.errortime_out_byte = $time;
			stats1.errors_out_byte = stats1.errors_out_byte+1'b1; end
		if (done_ref !== ( done_ref ^ done_dut ^ done_ref ))
		begin if (stats1.errors_done == 0) stats1.errortime_done = $time;
			stats1.errors_done = stats1.errors_done+1'b1; end

	end

   // add timeout after 100K cycles
   initial begin
     #1000000
     $display("TIMEOUT");
     $finish();
   end

endmodule



module RefModule (
  input clk,
  input in,
  input reset,
  output [7:0] out_byte,
  output done
);

  parameter B0=0, B1=1, B2=2, B3=3, B4=4, B5=5, B6=6, B7=7, START=8, STOP=9, DONE=10, ERR=11;
  reg [3:0] state;
  reg [3:0] next;

  reg [9:0] byte_r;

  always_comb begin
    case (state)
      START: next = in ? START : B0;  // start bit is 0
      B0: next = B1;
      B1: next = B2;
      B2: next = B3;
      B3: next = B4;
      B4: next = B5;
      B5: next = B6;
      B6: next = B7;
      B7: next = STOP;
      STOP: next = in ? DONE : ERR;  // stop bit is 1. Idle state is 1.
      DONE: next = in ? START : B0;
      ERR: next = in ? START : ERR;
    endcase
  end

  always @(posedge clk) begin
    if (reset) state <= START;
      else state <= next;
  end

  always @(posedge clk) begin
    byte_r <= {in, byte_r[9:1]};
  end

  assign done = (state==DONE);
  assign out_byte = done ? byte_r[8:1] : 8'hx;

endmodule


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