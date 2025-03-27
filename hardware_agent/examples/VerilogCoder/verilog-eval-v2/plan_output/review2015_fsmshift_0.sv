`timescale 1 ps/1 ps
`define OK 12
`define INCORRECT 13


module stimulus_gen (
	input clk,
	output reg reset
);

	
	initial begin
		repeat(100) @(negedge clk) begin
			reset <= !($random & 31);
		end

		#1 $finish;
	end
	
endmodule

module tb();

	typedef struct packed {
		int errors;
		int errortime;
		int errors_shift_ena;
		int errortime_shift_ena;

		int clocks;
	} stats;
	
	stats stats1;
	
	
	wire[511:0] wavedrom_title;
	wire wavedrom_enable;
	int wavedrom_hide_after_time;
	
	reg clk=0;
	initial forever
		#5 clk = ~clk;

	logic reset;
	logic shift_ena_ref;
	logic shift_ena_dut;

	initial begin 
		$dumpfile("wave.vcd");
		$dumpvars();
	end


	wire tb_match;		// Verification
	wire tb_mismatch = ~tb_match;
	
	stimulus_gen stim1 (
		.clk,
		.* ,
		.reset );
	RefModule good1 (
		.clk,
		.reset,
		.shift_ena(shift_ena_ref) );
		
	TopModule top_module1 (
		.clk,
		.reset,
		.shift_ena(shift_ena_dut) );

	
	bit strobe = 0;
	task wait_for_end_of_timestep;
		repeat(5) begin
			strobe <= !strobe;  // Try to delay until the very end of the time step.
			@(strobe);
		end
	endtask	

	
	final begin
		if (stats1.errors_shift_ena) $display("Hint: Output '%s' has %0d mismatches. First mismatch occurred at time %0d.", "shift_ena", stats1.errors_shift_ena, stats1.errortime_shift_ena);
		else $display("Hint: Output '%s' has no mismatches.", "shift_ena");

		$display("Hint: Total mismatched samples is %1d out of %1d samples\n", stats1.errors, stats1.clocks);
		$display("Simulation finished at %0d ps", $time);
		$display("Mismatches: %1d in %1d samples", stats1.errors, stats1.clocks);
	end
	
	// Verification: XORs on the right makes any X in good_vector match anything, but X in dut_vector will only match X.
	assign tb_match = ( { shift_ena_ref } === ( { shift_ena_ref } ^ { shift_ena_dut } ^ { shift_ena_ref } ) );
	// Use explicit sensitivity list here. @(*) causes NetProc::nex_input() to be called when trying to compute
	// the sensitivity list of the @(strobe) process, which isn't implemented.
	always @(posedge clk, negedge clk) begin

		stats1.clocks++;
		if (!tb_match) begin
			if (stats1.errors == 0) stats1.errortime = $time;
			stats1.errors++;
		end
		if (shift_ena_ref !== ( shift_ena_ref ^ shift_ena_dut ^ shift_ena_ref ))
		begin if (stats1.errors_shift_ena == 0) stats1.errortime_shift_ena = $time;
			stats1.errors_shift_ena = stats1.errors_shift_ena+1'b1; end

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
  input reset,
  output shift_ena
);

  parameter B0=0, B1=1, B2=2, B3=3, Done=4;

  reg [2:0] state, next;

  always_comb begin
    case (state)
      B0: next = B1;
      B1: next = B2;
      B2: next = B3;
      B3: next = Done;
      Done: next = Done;
    endcase
  end

  always @(posedge clk)
    if (reset) state <= B0;
    else state <= next;

  assign shift_ena = (state == B0 || state == B1 || state == B2 || state == B3);

endmodule


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