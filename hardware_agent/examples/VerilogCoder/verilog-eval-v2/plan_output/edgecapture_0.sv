`timescale 1 ps/1 ps
`define OK 12
`define INCORRECT 13


module stimulus_gen (
	input clk,
	input tb_match,
	output reg [31:0] in,
	output reg reset,
	output reg[511:0] wavedrom_title,
	output reg wavedrom_enable	
);


// Add two ports to module stimulus_gen:
//    output [511:0] wavedrom_title
//    output reg wavedrom_enable

	task wavedrom_start(input[511:0] title = "");
	endtask
	
	task wavedrom_stop;
		#1;
	endtask	


	
	initial begin
		in <= 0;
		reset <= 1;
		@(posedge clk);
		reset <= 1;
		in = 0;
		@(negedge clk) wavedrom_start("Example");
		repeat(1) @(posedge clk);
		reset = 0;
		@(posedge clk) in = 32'h2;
		repeat(4) @(posedge clk);
		in = 32'he;
		repeat(2) @(posedge clk);
		in = 0;
		@(posedge clk) in = 32'h2;
		repeat(2) @(posedge clk);
		reset = 1;
		@(posedge clk);
		reset = 0; in = 0;
		repeat(3) @(posedge clk);

		@(negedge clk) wavedrom_stop();


		@(negedge clk) wavedrom_start("");
		repeat(2) @(posedge clk);
		in <= 1;
		repeat(2) @(posedge clk);
		in <= 0;
		repeat(2) @(negedge clk);
		in <= 6;
		repeat(1) @(negedge clk);
		in <= 0;		
		repeat(2) @(posedge clk);
		in <= 32'h10;		
		repeat(2) @(posedge clk);
		reset <= 1;
		repeat(1) @(posedge clk);
		in <= 32'h0;
		repeat(1) @(posedge clk);
		reset <= 0;
		repeat(1) @(posedge clk);
		reset <= 1;
		in <= 32'h20;
		repeat(1) @(posedge clk);
		reset <= 0;
		in <= 32'h00;
	
		repeat(2) @(posedge clk);

		@(negedge clk) wavedrom_stop();
	
		repeat(200)
			@(posedge clk, negedge clk) begin
				in <= $random;
				reset <= !($random & 15);
			end
		$finish;
	end
	
endmodule

module tb();

	typedef struct packed {
		int errors;
		int errortime;
		int errors_out;
		int errortime_out;

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
	logic [31:0] in;
	logic [31:0] out_ref;
	logic [31:0] out_dut;

	initial begin 
		$dumpfile("wave.vcd");
		$dumpvars();
	end


	wire tb_match;		// Verification
	wire tb_mismatch = ~tb_match;
	
	stimulus_gen stim1 (
		.clk,
		.* ,
		.reset,
		.in );
	RefModule good1 (
		.clk,
		.reset,
		.in,
		.out(out_ref) );
		
	TopModule top_module1 (
		.clk,
		.reset,
		.in,
		.out(out_dut) );

	
	bit strobe = 0;
	task wait_for_end_of_timestep;
		repeat(5) begin
			strobe <= !strobe;  // Try to delay until the very end of the time step.
			@(strobe);
		end
	endtask	

	
	final begin
		if (stats1.errors_out) $display("Hint: Output '%s' has %0d mismatches. First mismatch occurred at time %0d.", "out", stats1.errors_out, stats1.errortime_out);
		else $display("Hint: Output '%s' has no mismatches.", "out");

		$display("Hint: Total mismatched samples is %1d out of %1d samples\n", stats1.errors, stats1.clocks);
		$display("Simulation finished at %0d ps", $time);
		$display("Mismatches: %1d in %1d samples", stats1.errors, stats1.clocks);
	end
	
	// Verification: XORs on the right makes any X in good_vector match anything, but X in dut_vector will only match X.
	assign tb_match = ( { out_ref } === ( { out_ref } ^ { out_dut } ^ { out_ref } ) );
	// Use explicit sensitivity list here. @(*) causes NetProc::nex_input() to be called when trying to compute
	// the sensitivity list of the @(strobe) process, which isn't implemented.
	always @(posedge clk, negedge clk) begin

		stats1.clocks++;
		if (!tb_match) begin
			if (stats1.errors == 0) stats1.errortime = $time;
			stats1.errors++;
		end
		if (out_ref !== ( out_ref ^ out_dut ^ out_ref ))
		begin if (stats1.errors_out == 0) stats1.errortime_out = $time;
			stats1.errors_out = stats1.errors_out+1'b1; end

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
  input [31:0] in,
  output reg [31:0] out
);

  reg [31:0] d_last;

  always @(posedge clk) begin
    d_last <= in;
    if (reset)
      out <= '0;
    else
      out <= out | (~in & d_last);
  end

endmodule


module TopModule (
  input  logic clk,
  input  logic reset,
  input  logic [31:0] in,
  output logic [31:0] out
);

  // Define a 32-bit register to store the previous state of the input vector 'in'
  logic [31:0] prev_in;

  // Sequential logic to update the previous state register and the output register
  always @(posedge clk) begin
    if (reset) begin
      // When reset is active, clear the 'out' register and store the current 'in' for the next capture
      out <= 32'b0;
      prev_in <= in;
    end else begin
      // Update the previous state register with the current 'in' vector
      prev_in <= in;
      // Capture the changes from 1 to 0 by comparing 'in' with 'prev_in'
      out <= out | (prev_in & ~in);
    end
  end

endmodule